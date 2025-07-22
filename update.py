import os
import requests
import base64
from Crypto.Cipher import AES
import io, zipfile

BASE_URL = "https://pub-35bf041400df49f594c852a1ca8489db.r2.dev/hueying-workflows-update"
PAYLOAD_URL = f"{BASE_URL}/payload.b64"
VERSION_URL = f"{BASE_URL}/version.txt"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VERSION_FILE = os.path.join(SCRIPT_DIR, 'version.txt')
PAYLOAD_FILE = os.path.join(SCRIPT_DIR, 'payload.b64')
KEY = b"1234567890abcdef"


def decrypt(data: bytes, key: bytes) -> bytes:
    nonce, tag, ciphertext = data[:16], data[16:32], data[32:]
    cipher = AES.new(key, AES.MODE_EAX, nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)


def get_local_version():
    if os.path.exists(VERSION_FILE):
        try:
            with open(VERSION_FILE, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            print(f"❌ 读取本地版本失败: {e}")
    return ''


def write_local_version(version: str):
    try:
        with open(VERSION_FILE, 'w', encoding='utf-8') as f:
            f.write(version)
        return True
    except Exception as e:
        print(f"❌ 写入本地版本失败: {e}")
        return False


def fetch_remote_version():
    try:
        r = requests.get(VERSION_URL, timeout=10)
        if r.status_code == 200:
            return r.text.strip()
        print(f"❌ 获取远程版本失败: 状态码 {r.status_code}")
    except Exception as e:
        print(f"❌ 获取远程版本异常: {e}")
    return None


def verify_payload(data: bytes, expected_version: str) -> bool:
    try:
        decrypted = decrypt(base64.b64decode(data), KEY)
        with zipfile.ZipFile(io.BytesIO(decrypted)) as zf:
            for name in zf.namelist():
                if name.endswith('version.txt'):
                    with zf.open(name) as f:
                        found = f.read().decode('utf-8').strip()
                    return found == expected_version
    except Exception as e:
        print(f"❌ 校验更新包失败: {e}")
    return False


def download_payload(version: str) -> bool:
    """Download payload.b64 and update local version file."""
    try:
        r = requests.get(PAYLOAD_URL, timeout=10)
        if r.status_code == 200:
            if verify_payload(r.content, version):
                with open(PAYLOAD_FILE, 'wb') as f:
                    f.write(r.content)
                write_local_version(version)
                print('✅ 已完成更新，重启程序后生效')
                return True
            print('❌ 更新包校验失败')
        else:
            print(f"❌ 下载更新包失败: 状态码 {r.status_code}")
    except Exception as e:
        print(f"❌ 下载更新包异常: {e}")
    return False


def auto_update_if_needed() -> bool:
    """Check remote version and update payload if needed.

    Returns True if the payload file is ready for use, otherwise False."""
    local_version = get_local_version()
    remote_version = fetch_remote_version()
    print(f"📦 当前本地版本: {local_version}")
    if not remote_version:
        return os.path.exists(PAYLOAD_FILE)
    if not local_version or local_version < remote_version:
        print(f"📡 检测到新版本: {remote_version}, 开始下载...")
        if not download_payload(remote_version):
            print('❌ 更新失败，继续使用本地版本')
    else:
        print('✅ 当前已是最新版本')
    return os.path.exists(PAYLOAD_FILE)
