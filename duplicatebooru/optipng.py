import os
from asyncio import to_thread
from subprocess import CalledProcessError, run
from tempfile import TemporaryDirectory


def _optipng(image: bytes) -> bytes:
    with TemporaryDirectory() as d:
        out = os.path.join(d, "out.png")
        in_ = os.path.join(d, "in.png")

        with open(in_, "wb") as f:
            f.write(image)

        try:
            run(
                ["optipng", "-quiet", "-o1", "-zs0", "-f0", "-out", out, in_],
                check=True,
                input=image,
            )
        except (CalledProcessError, FileNotFoundError):
            return image

        with open(out, "rb") as f:
            return f.read()


async def optipng(image: bytes) -> bytes:
    if image[:4] != b'\x89PNG':
        return image

    return await to_thread(_optipng, image)
