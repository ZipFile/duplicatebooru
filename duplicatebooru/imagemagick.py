from asyncio import CancelledError, TimeoutError, wait_for
from asyncio.subprocess import PIPE, create_subprocess_shell
from json import loads as json_loads
from typing import Any

from .optipng import optipng


class MagickError(Exception):
    def __init__(self, returncode: int, message: str) -> None:
        self.returncode = returncode
        self.message = message

        super().__init__(returncode, message)

    def __str__(self) -> str:
        return f'Exit Code: {self.returncode}\nMessage:\n{self.message}'


async def get_info(image: bytes, timeout: int = 30) -> Any:
    image = await optipng(image)
    proc = await create_subprocess_shell(
        "convert - json:-",
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
    )

    try:
        stdout, stderr = await wait_for(proc.communicate(image), timeout)
    except (TimeoutError, CancelledError):
        proc.kill()

        raise

    assert proc.returncode is not None

    if proc.returncode == 0:
        return json_loads(stdout.decode('utf-8', 'replace'))

    raise MagickError(proc.returncode, stderr.decode('utf-8', 'replace'))
