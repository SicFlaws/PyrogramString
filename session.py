#!/usr/bin/env python3
# secure_pyrogram_session_gen.py
# Pyrogram v2 session-string generator (non-interactive login flow)

import asyncio
import sys
from getpass import getpass
from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeExpired, PhoneNumberInvalid, FloodWait

async def main():
    print("\nPyrogram v2 — Secure Session String Generator\n")

    # Gather credentials
    try:
        api_id_raw = input("Enter API_ID: ").strip()
        api_id = int(api_id_raw)
    except Exception:
        print("Invalid API_ID. It must be an integer.")
        return

    api_hash = input("Enter API_HASH: ").strip()
    if not api_hash:
        print("API_HASH cannot be empty.")
        return

    phone = input("Enter Phone Number (with country code, or leave empty for bot token): ").strip()
    if not phone:
        print("Phone number empty. This script currently requires a phone number login (not bot token).")
        return

    # Create client but DO NOT use 'async with' or start() — those trigger Pyrogram's interactive prompts.
    app = Client(
        name="gen_session",
        api_id=api_id,
        api_hash=api_hash,
        in_memory=True,
        no_updates=True,   # safer on VPS
    )

    try:
        await app.connect()
    except Exception as e:
        print("Failed to connect to Telegram (network/credential issue):", e)
        return

    try:
        # Send the code. This returns an object with phone_code_hash we must pass to sign_in.
        try:
            sent = await app.send_code(phone)
        except PhoneNumberInvalid:
            print("The phone number appears invalid. Check country code and format.")
            return
        except FloodWait as fw:
            print(f"FloodWait: must wait {fw.x} seconds before retrying.")
            return
        except Exception as e:
            print("Failed to send confirmation code:", e)
            return

        code = input("Enter confirmation code: ").strip()
        if not code:
            print("No code entered — aborting.")
            return

        # Attempt sign-in using phone_code_hash from send_code result
        try:
            await app.sign_in(phone_number=phone, phone_code_hash=sent.phone_code_hash, phone_code=code)
        except SessionPasswordNeeded:
            # Two-step verification enabled: ask for password securely.
            pw = getpass("Two-step verification is enabled. Enter password (input hidden): ")
            if pw == "":
                print("Empty password provided. If you don't remember it you must recover via Telegram client. Aborting.")
                return
            try:
                await app.check_password(pw)
            except Exception as e:
                print("Failed to verify password:", e)
                return
        except PhoneCodeExpired:
            print("The confirmation code has expired. Please run the script again to request a new code.")
            return
        except Exception as e:
            # Generic sign-in failure
            print("Sign-in failed:", e)
            return

        # At this point we're logged in in-memory — export the string
        try:
            session_string = await app.export_session_string()
        except Exception as e:
            print("Failed to export session string:", e)
            return

        print("\n--- SESSION STRING (copy and store safely) ---\n")
        print(session_string)
        print("\n---------------------------------------------")
        print("IMPORTANT: Do not share this string. Treat it like your password.")
    finally:
        # Ensure clean disconnect
        try:
            await app.disconnect()
        except Exception:
            pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting.")
        try:
            # Best-effort: nothing to disconnect here (async loop closed), just exit.
            pass
        finally:
            sys.exit(1)
