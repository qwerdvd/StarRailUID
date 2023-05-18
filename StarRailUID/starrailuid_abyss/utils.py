from io import BytesIO
from typing import TypeVar

from PIL import Image
from aiohttp import ClientSession
from gsuid_core.data_store import get_res_path

T = TypeVar("T")

ROLEINFO_PATH = get_res_path() / 'StarRailUID' / 'roleinfo'
ROLEINFO_PATH.mkdir(parents=True, exist_ok=True)


async def get_icon(url: str) -> Image.Image:
    name = url.split('/')[-1]
    path = ROLEINFO_PATH / name
    if (path).exists():
        content = path.read_bytes()
    else:
        async with ClientSession() as client:
            async with client.get(url) as resp:
                content = await resp.read()
                with open(path, "wb") as f:
                    f.write(content)
    return Image.open(BytesIO(content)).convert("RGBA")
