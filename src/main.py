# -*- coding: utf-8 -*-
"""每日签到主流程（GitHub Action 定时触发，也可手动运行）。

流程：
  1. 调用 Cloudflare 接口 /api/v1/accounts/unsigned 拉取今日未签到账号与密码
  2. 按 login.py 的逻辑，把账号列表 AES 加密后写入环境变量 ACCOUNT_PASSWORD
  3. 复用 login.py 的签到逻辑逐账号签到（随机顺序、随机间隔）
  4. 签到完成的账号立即调用 /api/v1/accounts/update 回传：
     token / 本次获取金币 / 签到时间（北京时间）/ 总金币 / 换绑次数
  5. 保存 sign_result.json 并打印汇总（Action 中随后用 print_sign_result.py 打印表格）

签到失败（未取到 token）的账号不上传，保持“今日未签到”状态，明天自动重试。

环境变量：
  API_BASE               Cloudflare 接口根地址（必填，敏感信息只在环境变量中配置）
  CLOUDFLARE_SHARED_KEY  Cloudflare API 共享秘钥，64 位 hex（必填）
  ACCOUNT_AES_KEY        账号配置加密密钥（可选，默认 login.py 内置密钥）
"""
import json
import os
import random
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Tuple

from aes_cipher import AESCipher
from cloudflare_api import CloudflareApi

try:
    import login
except ImportError:
    print("[-] 缺少 src/login.py，请先运行 python src/download_and_decrypt.py 下载并解密 login")
    sys.exit(1)

# Cloudflare API 客户端：秘钥与地址属于敏感信息，只从环境变量读取（必填）
#   CLOUDFLARE_SHARED_KEY  API 共享秘钥（64 位 hex）
#   API_BASE               API 根地址
SHARED_KEY = os.environ.get("CLOUDFLARE_SHARED_KEY", "").strip()
API_BASE = os.environ.get("API_BASE", "").strip()
if not SHARED_KEY or not API_BASE:
    print("[-] 缺少环境变量 CLOUDFLARE_SHARED_KEY 或 API_BASE（敏感信息只在环境变量中配置）")
    print("    本地运行示例 (PowerShell):")
    print('      $env:CLOUDFLARE_SHARED_KEY = ""')
    print('      $env:API_BASE = ""')
    print("    GitHub Actions 请在 Settings → Secrets and variables → Actions 中配置对应 Secret。")
    sys.exit(1)

cloudflare = CloudflareApi(shared_key=SHARED_KEY, base_url=API_BASE)

# 相邻账号之间的随机等待秒数，与 login.py 的 do_club_sign_in_for_current_hour 保持一致
# 可用环境变量覆盖（本地测试时可设为 0 加速）
ACCOUNT_WAIT_MIN_SECONDS = int(os.environ.get("ACCOUNT_WAIT_MIN_SECONDS", "10"))
ACCOUNT_WAIT_MAX_SECONDS = int(os.environ.get("ACCOUNT_WAIT_MAX_SECONDS", "20"))

BEIJING_TZ = timezone(timedelta(hours=8))


def beijing_now() -> str:
    """当前北京时间，格式 yyyy-MM-dd HH:mm:ss（与服务器端 sign_in_time 格式一致）"""
    return datetime.now(BEIJING_TZ).strftime("%Y-%m-%d %H:%M:%S")


def load_unsigned_accounts() -> List[Dict[str, str]]:
    """从 Cloudflare 拉取今日未签到账号，校验后返回 [{account, password}]"""
    data = cloudflare.fetch_unsigned_accounts()
    print("[CLOUDFLARE] 服务器时间: {}，今日未签到账号: {} 个".format(data.get("serverTime"), data.get("total", 0)))

    accounts: List[Dict[str, str]] = []
    for item in data.get("list") or []:
        account = str(item.get("account") or "").strip()
        password = str(item.get("password") or "").strip()
        if account and password:
            accounts.append({"account": account, "password": password})
    return accounts


def setup_account_env(accounts: List[Dict[str, str]]) -> None:
    """
    按 login.py 的逻辑设置环境变量 ACCOUNT_PASSWORD：
    账号列表 JSON 序列化后，用 ACCOUNT_AES_KEY（默认 login.DEFAULT_ACCOUNT_AES_KEY）AES 加密
    """
    key = os.environ.get("ACCOUNT_AES_KEY") or login.DEFAULT_ACCOUNT_AES_KEY
    cipher = AESCipher(key)
    os.environ["ACCOUNT_PASSWORD"] = cipher.encrypt(json.dumps(accounts, ensure_ascii=False))


def load_account_pairs() -> List[Tuple[str, str]]:
    """复用 login.py 的 _load_accounts_config 从环境变量解密加载账号，校验成 (账号, 密码) 列表"""
    pairs: List[Tuple[str, str]] = []
    for index, entry in enumerate(login._load_accounts_config()):
        if not isinstance(entry, dict):
            print("[-] 下标 {} 的配置项格式错误，应为对象".format(index))
            continue
        username = entry.get("account")
        password = entry.get("password")
        if not username or not password:
            print("[-] 下标 {} 的配置缺少 account 或 password".format(index))
            continue
        pairs.append((username, password))
    return pairs


def upload_sign_result(result: Dict[str, Any]) -> None:
    """把单个账号的签到结果回传 Cloudflare；未取到 token 的失败账号跳过（明天自动重试）"""
    token = result.get("token")
    if not token:
        print("[SKIP] 账号 {} 签到失败（未获取 token），不上传，明日重试".format(result.get("account")))
        return

    record = {
        "account": result.get("account"),
        "token": token,
        "coin_gain": result.get("coin_gain", 0),
        "total_coin": result.get("total_coin", 0),
        "change_bind_num": result.get("change_bind_num"),
        "sign_in_time": beijing_now(),
    }

    try:
        cloudflare.update_account(record)
        print(
            "[CLOUDFLARE] 账号 {} 签到结果已上传：本次 +{} 金币，总金币 {}".format(
                record["account"], record["coin_gain"], record["total_coin"]
            )
        )
    except Exception as exc:
        print("[-] 账号 {} 上传签到结果失败: {}".format(record["account"], exc))


def run_sign_in(pairs: List[Tuple[str, str]]) -> List[Dict[str, Any]]:
    """
    随机打乱顺序后逐账号签到，签到一个上传一个；
    token 失败次数达到上限（login.TokenFailureExit）时终止剩余账号。
    """
    random.shuffle(pairs)
    total = len(pairs)
    print("[LIST] 共 {} 个账号，已随机打乱顺序".format(total))

    results: List[Dict[str, Any]] = []

    for index, (username, password) in enumerate(pairs, start=1):
        print("\n[SIGN] 第 {}/{} 个账号 {}".format(index, total, username))
        try:
            result = login.do_club_sign_in_for_day(username, password)
        except login.TokenFailureExit:
            print("[X] token 失败次数已达上限，终止剩余账号签到")
            break

        if result:
            results.append(result)
            upload_sign_result(result)

        if index < total:
            wait_seconds = random.uniform(ACCOUNT_WAIT_MIN_SECONDS, ACCOUNT_WAIT_MAX_SECONDS)
            print("[WAIT] 等待 {:.1f} 秒后执行下一个...".format(wait_seconds))
            time.sleep(wait_seconds)

    return results


def print_summary(results: List[Dict[str, Any]]) -> None:
    total = len(results)
    success_results = [r for r in results if (r.get("coin_gain") or 0) > 0]
    failed_results = [r for r in results if (r.get("coin_gain") or 0) <= 0]
    print(
        "\n[SUMMARY] 签到汇总：共 {} 个，成功 {} 个，失败 {} 个".format(total, len(success_results), len(failed_results)))
    if failed_results:
        print("  失败账号：{}".format([r.get("account") for r in failed_results]))


def main() -> None:
    accounts = load_unsigned_accounts()
    if not accounts:
        print("\n[OK] 今日没有待签到账号")
        login.save_sign_results([])
        return

    setup_account_env(accounts)
    pairs = load_account_pairs()
    if not pairs:
        print("[-] 账号配置为空，跳过签到")
        login.save_sign_results([])
        return

    results = run_sign_in(pairs)
    login.save_sign_results(results)
    print_summary(results)


if __name__ == "__main__":
    main()
