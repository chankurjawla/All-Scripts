from telethon import TelegramClient
import asyncio
import os

API_ID = 28379308
API_HASH = '17633bad58479bb4bb1f25d264f5832b'

# --- SET YOUR PATH HERE ---
# For OMV, this usually looks like /srv/dev-disk-by-uuid...
SAVE_PATH = '/srv/dev-disk-by-uuid-9e1c6e06-04c9-4670-9c99-98aaab1929e2/MediaStorage/Movies' 

async def main():
    # Ensure the directory exists so the script doesn't crash
    if not os.path.exists(SAVE_PATH):
        os.makedirs(SAVE_PATH)

    async with TelegramClient('raspi_session', API_ID, API_HASH) as client:
        async for message in client.iter_messages('me', limit=10):
            if message.document:
                print(f"File found. Downloading to {SAVE_PATH}...")
                
                # The 'file' parameter defines the destination
                path = await client.download_media(message, file=SAVE_PATH)
                
                print(f"Success! Saved to: {path}")
                return
        print("No file found in Saved Messages.")

if __name__ == '__main__':
    asyncio.run(main())

