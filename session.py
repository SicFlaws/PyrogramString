#!/usr/bin/env python3
# Secure Pyrogram v2 Session String Generator

import asyncio
from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded

async def main():
    print("\n--- Pyrogram v2 Session String Generator ---\n")

    api_id = int(input("Enter API_ID: ").strip())
    api_hash = input("Enter API_HASH: ").strip()
    phone_number = input("Enter Phone Number (with country code): ").strip()

    async with Client(
        name="gen_session",
        api_id=api_id,
        api_hash=api_hash,
        in_memory=True  # ensures no session file is written to disk
    ) as app:

        print("\nSending OTP...")
        try:
            sent_code = await app.send_code(phone_number)
        except Exception as e:
            print("Failed to send OTP:", e)
            return

        otp = input("Enter the OTP you received: ").strip()

        try:
            await app.sign_in(phone_number, sent_code.phone_code_hash, otp)
        except SessionPasswordNeeded:
            password = input("Two-Step Verification is enabled.\nEnter your password: ").strip()
            await app.check_password(password)
        except Exception as e:
            print("Login failed:", e)
            return

        print("\nLogin successful!")
        session_string = await app.export_session_string()

        print("\n--- SESSION STRING (COPY SAFELY) ---\n")
        print(session_string)
        print("\n--------------------------------------")
        print("IMPORTANT: Never share this string with anyone.\n")

if __name__ == "__main__":
    asyncio.run(main())
