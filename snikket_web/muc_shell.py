"""
MUC Shell - 直接透過 docker exec prosodyctl shell 執行 MUC 操作

取代原本的 Node.js MUC API Server (snikket_muc_api_server.js)
"""

import asyncio
import re
import typing

# Docker container name
DOCKER_CONTAINER = "snikket"

# 有效的 affiliation 值
VALID_AFFILIATIONS = ["owner", "admin", "member", "none", "outcast"]


def validate_room_jid(room: str, muc_domain: str) -> bool:
    """驗證 MUC 房間 JID 格式。

    Args:
        room: 完整房間 JID (e.g., room@groups.example.com)
        muc_domain: MUC 域名 (e.g., groups.example.com)

    Returns:
        True if valid
    """
    # 轉義 domain 中的點
    escaped_domain = re.escape(muc_domain)
    pattern = rf"^[a-zA-Z0-9._-]+@{escaped_domain}$"
    return bool(re.match(pattern, room))


def validate_user_jid(user: str, domain: str) -> bool:
    """驗證用戶 JID 格式。

    Args:
        user: 完整用戶 JID (e.g., user@example.com)
        domain: 伺服器域名 (e.g., example.com)

    Returns:
        True if valid
    """
    escaped_domain = re.escape(domain)
    pattern = rf"^[a-zA-Z0-9._-]+@{escaped_domain}$"
    return bool(re.match(pattern, user))


def validate_affiliation(affiliation: str) -> bool:
    """驗證 affiliation 值是否有效。"""
    return affiliation in VALID_AFFILIATIONS


async def run_prosody_shell(lua_code: str) -> str:
    """執行 prosodyctl shell 指令。

    Args:
        lua_code: 要執行的 Lua 程式碼

    Returns:
        stdout 輸出

    Raises:
        RuntimeError: 如果執行失敗
    """
    proc = await asyncio.create_subprocess_exec(
        "docker",
        "exec",
        DOCKER_CONTAINER,
        "prosodyctl",
        "shell",
        lua_code,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        raise RuntimeError(f"prosody error: {stderr.decode()}")

    return stdout.decode()


def parse_muc_list_output(stdout: str) -> typing.List[str]:
    """解析 prosodyctl shell muc:list() 輸出。

    Args:
        stdout: prosodyctl shell 的輸出

    Returns:
        房間 JID 列表
    """
    rooms: typing.List[str] = []
    for line in stdout.strip().split("\n"):
        line = line.strip()
        if line and not line.startswith("|") and "@" in line:
            rooms.append(line)
    return rooms


def parse_affiliation_output(stdout: str) -> typing.Optional[str]:
    """解析 prosodyctl shell get_affiliation() 輸出。

    Args:
        stdout: prosodyctl shell 的輸出

    Returns:
        affiliation 值或 None
    """
    stdout = stdout.strip().lower()
    for aff in VALID_AFFILIATIONS:
        if aff in stdout:
            return aff
    return None


async def muc_list_rooms(muc_domain: str) -> typing.List[str]:
    """列出指定域名的所有 MUC 房間。

    Args:
        muc_domain: MUC 域名 (e.g., groups.example.com)

    Returns:
        房間 JID 列表
    """
    # 轉義單引號以避免 injection
    safe_domain = muc_domain.replace("'", "\\'")
    lua_code = f"muc:list('{safe_domain}')"

    stdout = await run_prosody_shell(lua_code)
    return parse_muc_list_output(stdout)


async def muc_get_affiliation(
    room_jid: str,
    user_jid: str,
) -> typing.Optional[str]:
    """取得用戶在 MUC 房間中的身份。

    Args:
        room_jid: 完整房間 JID (e.g., room@groups.example.com)
        user_jid: 完整用戶 JID (e.g., user@example.com)

    Returns:
        affiliation (owner/admin/member/none/outcast) 或 None
    """
    # 轉義單引號
    safe_room = room_jid.replace("'", "\\'")
    safe_user = user_jid.replace("'", "\\'")
    lua_code = f"muc:room('{safe_room}'):get_affiliation('{safe_user}')"

    stdout = await run_prosody_shell(lua_code)
    return parse_affiliation_output(stdout)


async def muc_set_affiliation(
    room_jid: str,
    user_jid: str,
    affiliation: str,
) -> bool:
    """設定用戶在 MUC 房間中的身份。

    Args:
        room_jid: 完整房間 JID (e.g., room@groups.example.com)
        user_jid: 完整用戶 JID (e.g., user@example.com)
        affiliation: owner/admin/member/none/outcast

    Returns:
        True if successful

    Raises:
        ValueError: 如果 affiliation 無效
    """
    if not validate_affiliation(affiliation):
        raise ValueError(f"Invalid affiliation: {affiliation}")

    # 轉義單引號
    safe_room = room_jid.replace("'", "\\'")
    safe_user = user_jid.replace("'", "\\'")
    lua_code = (
        f"muc:room('{safe_room}'):set_affiliation(true, '{safe_user}', '{affiliation}')"
    )

    await run_prosody_shell(lua_code)
    return True
