# -*- coding: utf-8 -*-
import base64
import json
import secrets
from typing import Any, Dict

import requests
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# 请求超时（秒）。代理不强制指定：默认跟随系统/环境代理
# （本地访问 workers.dev 通常需要代理，GitHub Actions 无代理时自动直连）
TIMEOUT = 30


class CloudflareApi:
    """Cloudflare API 客户端。

    :param shared_key: 共享秘钥（64 位 hex 字符串，即 32 字节 AES-GCM 密钥），
                      与后端 backend/src/crypto/index.js 中的 SHARED_KEY 一致
    :param base_url: 接口根地址，如
    """

    def __init__(self, shared_key: str, base_url: str):
        if not shared_key:
            raise ValueError("shared_key 不能为空，请通过环境变量 CLOUDFLARE_SHARED_KEY 配置")
        if not base_url:
            raise ValueError("base_url 不能为空，请通过环境变量 API_BASE 配置")
        self.shared_key = bytes.fromhex(shared_key)
        self.base_url = base_url.rstrip("/")

    # ---- 加解密 ----
    @staticmethod
    def _b64url_encode(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

    @staticmethod
    def _b64url_decode(text: str) -> bytes:
        return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))

    def encrypt_text(self, plaintext: str) -> str:
        """加密明文字符串，返回 base64url(iv).base64url(ciphertext)"""
        iv = secrets.token_bytes(12)
        ciphertext = AESGCM(self.shared_key).encrypt(iv, plaintext.encode("utf-8"), None)
        return "{}.{}".format(self._b64url_encode(iv), self._b64url_encode(ciphertext))

    def decrypt_text(self, payload: str) -> str:
        """解密 base64url(iv).base64url(ciphertext)，返回明文字符串"""
        iv_b64, ciphertext_b64 = payload.split(".", 1)
        plaintext = AESGCM(self.shared_key).decrypt(
            self._b64url_decode(iv_b64), self._b64url_decode(ciphertext_b64), None
        )
        return plaintext.decode("utf-8")

    # ---- 接口 ----
    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送加密 POST 请求，返回解密后响应中的 data 部分。
        HTTP 非 200 或业务 code 非 0 时抛出 RuntimeError。
        """
        plaintext = json.dumps(payload, ensure_ascii=False)
        response = requests.post(
            "{}{}".format(self.base_url, path),
            json={"data": self.encrypt_text(plaintext)},
            # 显式禁用压缩：部分网络环境会返回 zstd 编码，旧版 requests 无法解码
            headers={"Accept-Encoding": "identity"},
            timeout=TIMEOUT,
        )

        try:
            encrypted = response.json()
        except ValueError:
            raise RuntimeError("请求失败（HTTP {}）：响应不是 JSON".format(response.status_code))

        # 响应为 {"data": "<密文>"}，解密后为 {"code", "message", "data"}；个别场景可能直接返回明文
        body = (
            json.loads(self.decrypt_text(encrypted["data"]))
            if isinstance(encrypted.get("data"), str)
            else encrypted
        )

        if response.status_code != 200 or body.get("code") != 0:
            raise RuntimeError("请求失败（HTTP {}）：{}".format(response.status_code, body.get("message", "未知错误")))
        return body.get("data") or {}

    def fetch_unsigned_accounts(self) -> Dict[str, Any]:
        """
        查询今日未签到账号。
        返回：{ serverTime, total, list: [{ account, password }] }
        """
        return self._post("/accounts/unsigned", {})

    def update_account(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        上传单个账号的签到结果（upsert：账号存在则只更新传入字段，不存在则新增）。
        record 字段：account、token、coin_gain、total_coin、change_bind_num、sign_in_time
        """
        return self._post("/accounts/update", record)
