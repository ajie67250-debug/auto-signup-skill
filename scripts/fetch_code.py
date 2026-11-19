#!/usr/bin/env python3
"""从 Gmail 收取注册验证码。

需要环境变量 GMAIL_USER 和 GMAIL_APP_PASSWORD（Gmail 应用专用密码）。
用法:
  export GMAIL_USER="you@example.com"
  export GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"
  python3 fetch_code.py --from-hint github --site openai.com
"""
import argparse
import email
import imaplib
import os
import re
import sys
import time
from email.header import decode_header

USER = os.environ.get("GMAIL_USER", "")
CODE_RE = re.compile(r"\b(\d{4,8})\b")


def decode(value):
    parts = []
    for chunk, charset in decode_header(value or ""):
        if isinstance(chunk, bytes):
            parts.append(chunk.decode(charset or "utf-8", "ignore"))
        else:
            parts.append(chunk)
    return "".join(parts)


def bodies(msg):
    yield decode(msg.get("Subject", ""))
    for part in msg.walk() if msg.is_multipart() else [msg]:
        if part.get_content_type() in ("text/plain", "text/html"):
            payload = part.get_payload(decode=True)
            if payload:
                charset = part.get_content_charset() or "utf-8"
                yield payload.decode(charset, "ignore")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-hint", default="", help="发件人/域名关键字，如 github")
    ap.add_argument("--site", default="", help="平台名关键字，用于在正文中匹配")
    ap.add_argument("--wait", type=int, default=60, help="等待新邮件秒数")
    ap.add_argument("--timeout", type=int, default=120, help="总超时秒数")
    args = ap.parse_args()

    if not USER:
        sys.exit("缺少 GMAIL_USER。")
    app_pw = os.environ.get("GMAIL_APP_PASSWORD", "").replace(" ", "")
    if not app_pw:
        sys.exit("缺少 GMAIL_APP_PASSWORD。Google 账号 -> 安全 -> 两步验证 -> 应用专用密码生成。")

    deadline = time.time() + args.timeout
    seen = set()
    while True:
        try:
            imap = imaplib.IMAP4_SSL("imap.gmail.com")
            imap.login(USER, app_pw)
            imap.select("INBOX")
            since = "-1h" if args.wait else "-10m"
            typ, data = imap.search(None, f'(SINCE {since} UNSEEN)')
            for num in data[0].split():
                seen.add(num)
                typ, msg_data = imap.fetch(num, "(RFC822)")
                msg = email.message_from_bytes(msg_data[0][1])
                text = "\n".join(bodies(msg))
                sender = decode(msg.get("From", ""))
                blob = f"{sender}\n{text}".lower()
                if args.from_hint and args.from_hint.lower() not in blob:
                    continue
                if args.site and args.site.lower() not in blob and args.from_hint.lower() not in blob:
                    continue
                nums = [n for n in CODE_RE.findall(text) if len(n) in (4, 5, 6, 8)]
                if nums:
                    print(nums[0])
                    return
        except Exception as exc:  # noqa: BLE001
            print(f"IMAP 错误: {exc}", file=sys.stderr)
        if time.time() > deadline:
            sys.exit("超时：未找到验证码邮件")
        time.sleep(5)


if __name__ == "__main__":
    main()
