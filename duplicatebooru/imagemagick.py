from asyncio import CancelledError, TimeoutError, wait_for
from asyncio.subprocess import PIPE, create_subprocess_shell
from json import loads as json_loads


class MagickError(Exception):
    def __init__(self, returncode: int, message: str):
        self.returncode = returncode
        self.message = message

        super().__init__(returncode, message)

    def __str__(self) -> str:
        return f'Exit Code: {self.returncode}\nMessage:\n{self.message}'


async def get_info(image: bytes, timeout: int = 30):
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
        return json_loads(stdout)

    raise MagickError(proc.returncode, stderr)
