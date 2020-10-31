from asyncio import gather

from aiohttp import ClientSession
from aiohttp.web import RouteTableDef, View, json_response

from aiohttp_jinja2 import render_template, template


from .process import Info, process


routes = RouteTableDef()


@routes.view("/api")
async def magick(request):
    url = request.query["url"]

    async with ClientSession() as session:
        info = await process(session, url)

    return json_response(info)


@routes.view("/")
class Index(View):
    @template('index.jinja2')
    async def get(self):
        return {}

    async def post(self):
        data = await self.request.post()
        urls = data['urls']
        urls = sorted(set(urls.splitlines()) - {''})

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

        async with ClientSession() as session:
            raw_infos = await gather(*[
                process(session, url, self.request.app['cache'])
                for url in urls
            ], return_exceptions=True)

        hashes = set()
        infos = []

        for url, info in zip(urls, raw_infos):
            if isinstance(info, Exception):
                info = Info(url=url, error=repr(info))
            else:
                h = info.hash
                info.dupe = h in hashes
                hashes.add(h)

            infos.append(info)

        return render_template(
            'result.jinja2',
            self.request,
            {"infos": infos},
        )
