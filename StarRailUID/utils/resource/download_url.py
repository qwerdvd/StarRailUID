from typing import Tuple, Optional

import aiofiles
from gsuid_core.logger import logger
from aiohttp.client import ClientSession
from aiohttp.client_exceptions import ClientConnectorError

from .RESOURCE_PATH import WIKI_PATH, RESOURCE_PATH

PATHDICT = {
    'resource': RESOURCE_PATH,
    'wiki': WIKI_PATH,
}


async def download(
    url: str,
    res_type: str,
    resource_type: str,
    name: str,
) -> Optional[Tuple[str, int, str]]:
    """
    :说明:
      下载URL保存入目录
    :参数:
      * url: `str`
            资源下载地址。
      * res_type: `str`
            资源类型，`resource`或`wiki`。
      * resource_type: `str`
            资源文件夹名
      * name: `str`
            资源保存名称
    :返回(失败才会有返回值):
        url: `str`
        resource_type: `str`
        name: `str`
    """
    async with ClientSession() as sess:
        return await download_file(url, res_type, resource_type, name, sess)


async def download_file(
    url: str,
    res_type: str,
    resource_type: str,
    name: str,
    sess: Optional[ClientSession] = None,
) -> Optional[Tuple[str, str, str]]:
    if sess is None:
        sess = ClientSession()
    try:
        async with sess.get(url) as res:
            content = await res.read()
    except ClientConnectorError:
        logger.warning(f"[cos]{name}下载失败")
        return url, resource_type, name
    async with aiofiles.open(
        PATHDICT[res_type] / resource_type / name, "wb"
    ) as f:
        await f.write(content)
