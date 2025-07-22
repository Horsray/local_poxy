# main_payload.py
import os, base64, zipfile, io, requests, shutil, atexit
from Crypto.Cipher import AES

REMOTE_PAYLOAD_URL = "https://pub-35bf041400df49f594c852a1ca8489db.r2.dev/hueying-workflows-update/payload.b64"
LOCAL_PAYLOAD_PATH = "payload.b64"
KEY = b"1234567890abcdef"  

def download_payload():
    try:
        print("📡 下载更新文件 payload.b64 ...")
        r = requests.get(REMOTE_PAYLOAD_URL, timeout=10)
        if r.status_code == 200:
            with open(LOCAL_PAYLOAD_PATH, "wb") as f:
                f.write(r.content)
            print("✅ 下载完成")
            return True
        else:
            print(f"❌ 下载失败: 状态码 {r.status_code}")
    except Exception as e:
        print(f"❌ 下载异常: {e}")
    return False

def decrypt(data: bytes, key: bytes) -> bytes:
    nonce, tag, ciphertext = data[:16], data[16:32], data[32:]
    cipher = AES.new(key, AES.MODE_EAX, nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)

def extract_payload(temp_dir):
    with open(LOCAL_PAYLOAD_PATH, "rb") as f:
        decrypted = decrypt(base64.b64decode(f.read()), KEY)
        with zipfile.ZipFile(io.BytesIO(decrypted)) as zf:
            print("📦 解压内容如下：", zf.namelist())
            tmp_extract_dir = os.path.join(temp_dir, ".payload_tmp")
            if os.path.exists(tmp_extract_dir):
                shutil.rmtree(tmp_extract_dir, ignore_errors=True)
            os.makedirs(tmp_extract_dir, exist_ok=True)
            zf.extractall(tmp_extract_dir)

            # ✅ 自动判断 payload 根目录（新版逻辑）
            possible_items = os.listdir(tmp_extract_dir)
            if "payload" in possible_items:
                payload_root = os.path.join(tmp_extract_dir, "payload")
            else:
                payload_root = tmp_extract_dir
                print("📦 未检测到 payload 文件夹，尝试使用根目录作为 payload 目录")
                            # 最终强校验：必须包含 workflows 或 workflow_mappings.json，否则报错
            if not any(name in possible_items for name in ["workflows", "workflow_mappings.json"]):
                raise RuntimeError("❌ 无法识别有效 payload 内容：缺少 workflows 或 workflow_mappings.json")
            # ✅ 将 payload 内容复制到 temp_dir

            for item in os.listdir(payload_root):
                s = os.path.join(payload_root, item)
                d = os.path.join(temp_dir, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)

            print(f"✅ 文件提取完成，提取到：{temp_dir}")
            atexit.register(lambda: shutil.rmtree(tmp_extract_dir, ignore_errors=True))




def init_payload():
    temp_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp", "HueyingAI_temp_root")
    if not os.path.exists(temp_dir) or not os.listdir(temp_dir):
        print("📦 当前为首次加载，开始检查本地 payload 文件...")
        if os.path.exists(LOCAL_PAYLOAD_PATH):
            print("✅ 本地 payload.b64 已存在，准备解压...")
            extract_payload(temp_dir)
        else:
            print("📡 未检测到本地 payload，尝试从远程下载...")
            if not download_payload():
                raise RuntimeError("❌ 无法下载热更新文件")
            extract_payload(temp_dir)