from asyncio import gather
from re import split as re_split
from traceback import format_exception
from typing import Any, Dict, List

from aiohttp import ClientSession, ClientTimeout
from aiohttp.web import Request, Response, RouteTableDef, View, json_response

from aiohttp_jinja2 import render_template, template

from .process import Info, process


routes = RouteTableDef()
DEFAULT_TIMEOUT = ClientTimeout(total=30)


def extract_urls(s: str) -> List[str]:
    return re_split(r'\s+(?=https?://)', s.strip())


@routes.view("/api")
async def magick(request: Request) -> Response:
    url = request.query["url"]

    async with ClientSession(timeout=DEFAULT_TIMEOUT) as session:
        info = await process(
            session, url,
            fetch=request.app['fetcher'],
            cache=request.app['cache'],
        )

    return json_response(info.magick)


@routes.view("/")
class Index(View):
    @template('index.jinja2')
    async def get(self) -> Dict[str, Any]:
        return {
            "debug": self.request.app["debug"],
        }

    async def post(self) -> Response:
        data = await self.request.post()
        urls = sorted(set(extract_urls(data['urls'])))

        if len(urls) > 5:
            return render_template(
                'error.jinja2',
                self.request,
                {"message": "too many urls"},
            )

        if len(urls) < 2:
            return render_template(
                'error.jinja2',
                self.request,
                {"message": "too few urls"},
            )

        async with ClientSession(timeout=DEFAULT_TIMEOUT) as session:
            raw_infos = await gather(*[
                process(
                    session, url,
                    fetch=self.request.app['fetcher'],
                    cache=self.request.app['cache'],
                )
                for url in urls
            ], return_exceptions=True)

        hashes = set()
        infos = []

        for url, info in zip(urls, raw_infos):
            if isinstance(info, Exception):
                info = Info(
                    url=url,
                    error='\n'.join(format_exception(
                        type(info),
                        value=info,
                        tb=info.__traceback__,
                    )),
                )
            else:
                h = info.hash
                info.dupe = h in hashes
                hashes.add(h)

            infos.append(info)

        return render_template(
            'result.jinja2',
            self.request,
            {
                "debug": self.request.app["debug"],
                "infos": infos,
            },
        )
