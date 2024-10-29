import os
import time
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from telegram import Bot
from telegram.constants import ParseMode

TOKEN = 'TOKEN BOT'
CHAT_ID = 'CHAT ID'
FILE_PATH = '/root/masa.txt'

# Initialize the bot
bot = Bot(token=TOKEN)

# Store the last sent logs
last_sent_logs = []

async def send_message(chat_id, text, parse_mode=None):
    await bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)

async def send_latest_logs():
    global last_sent_logs
    if os.path.exists(FILE_PATH):
        output = os.popen(f"grep 'work_completion' {FILE_PATH}").readlines()
        
        if output:
            new_logs = [log for log in output if log not in last_sent_logs]
            if new_logs:
                for log in new_logs:
                    await send_message(chat_id=CHAT_ID, text=log.strip())
                last_sent_logs.extend(new_logs)

class LogFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == FILE_PATH:
            asyncio.run(send_latest_logs())  # Ensure the coroutine is run

if __name__ == "__main__":
    asyncio.run(send_latest_logs())  # Send initial logs
    event_handler = LogFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(FILE_PATH), recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
