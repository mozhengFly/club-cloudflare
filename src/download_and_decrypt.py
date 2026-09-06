"""下载加密的 login.enc 并使用 AES 解密为 login.py。"""
import os
import sys
import urllib.request
from pathlib import Path

import requests

SRC_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC_DIR))

from aes_cipher import AESCipher

REQUIRED_ENV = {
    "LOGIN_ENC_URL": "加密 login 文件的下载地址",
    "AES_PASSWORD": "解密 login.enc 所用的 AES 密码",
}
ENC_FILE = SRC_DIR / "login.enc"
OUTPUT_FILE = SRC_DIR / "login.py"


def _require_env():
    missing = [name for name in REQUIRED_ENV if not os.environ.get(name)]
    if missing:
        print("错误: 以下环境变量未配置:")
        for name in missing:
            print(f"  - {name}: {REQUIRED_ENV[name]}")
        print()
        print("本地运行示例 (PowerShell):")
        print('  $env:LOGIN_ENC_URL = "https://example.com/login.enc"')
        print('  $env:AES_PASSWORD = "your-aes-password"')
        print()
        print("GitHub Actions 请在 Settings → Secrets and variables → Actions 中配置对应 Secret。")
        sys.exit(1)

    return os.environ["LOGIN_ENC_URL"], os.environ["AES_PASSWORD"]


def _download_with_urllib(url: str) -> bytes:
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(url, timeout=60) as response:
        return response.read()


def download_encrypted_file(url: str, dest: Path) -> None:
    print(f"正在下载 {url} ...")
    content = None

    try:
        session = requests.Session()
        session.trust_env = False
        response = session.get(
            url,
            timeout=60,
            proxies={"http": None, "https": None},
        )
        response.raise_for_status()
        content = response.content
    except requests.RequestException as exc:
        print(f"requests 下载失败 ({exc})，尝试使用 urllib ...")
        try:
            content = _download_with_urllib(url)
        except Exception as urllib_exc:
            raise requests.RequestException(
                f"requests 与 urllib 均下载失败: {urllib_exc}"
            ) from urllib_exc

    dest.write_bytes(content)
    print(f"下载完成，共 {len(content)} 字节")


def decrypt_login_file(password: str, enc_file: Path, output_file: Path) -> None:
    print(f"正在解密 {enc_file.name} -> {output_file.name} ...")
    cipher = AESCipher(password)
    cipher.decrypt_file(str(enc_file), str(output_file))
    print("解密完成")


def cleanup_old_login() -> None:
    if OUTPUT_FILE.exists():
        OUTPUT_FILE.unlink()
        print(f"已删除旧的 {OUTPUT_FILE}")


def main() -> None:
    login_enc_url, aes_password = _require_env()

    cleanup_old_login()

    try:
        download_encrypted_file(login_enc_url, ENC_FILE)
        decrypt_login_file(aes_password, ENC_FILE, OUTPUT_FILE)
    except requests.RequestException as exc:
        print(f"下载失败: {exc}")
        sys.exit(1)
    except Exception as exc:
        print(f"解密失败: {exc}")
        sys.exit(1)
    finally:
        if ENC_FILE.exists():
            ENC_FILE.unlink()


if __name__ == "__main__":
    main()
