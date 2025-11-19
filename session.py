#!/usr/bin/env python3
import asyncio
import sys
from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded

async def main():
    print("\nPyrogram v2 — Stable Session Generator (No Hidden Input)\n")

    api_id = int(input("API_ID: ").strip())
    api_hash = input("API_HASH: ").strip()
    phone = input("Phone Number (with country code): ").strip()

    app = Client(
        name="session_gen",
        api_id=api_id,
        api_hash=api_hash,
        in_memory=True,
        no_updates=True,
    )

    await app.connect()

    sent = await app.send_code(phone)
    code = input("Enter OTP: ").strip()

    try:
        await app.sign_in(phone, sent.phone_code_hash, code)
    except SessionPasswordNeeded:
        pw = input("Enter your 2-Step Verification password (visible input, no lag): ")
        await app.check_password(pw)

    session = await app.export_session_string()
    print("\n--- SESSION STRING ---\n")
    print(session)
    print("\n-----------------------\n")

    await app.disconnect()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(1)
