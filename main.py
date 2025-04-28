# main.py
import asyncio
from fastapi import FastAPI, Request
from aiogram import Bot
from aiogram import Bot, Dispatcher

API_TOKEN = "8006406437:AAHvVIKDh_U5SpBjcIpPsPuoYlE1DDq6bfs"
WEBHOOK_URL = "https://4237-76-191-22-22.ngrok-free.app/webhook"

bot = Bot(token=API_TOKEN)
dispatcher = Dispatcher()

app = FastAPI()

@app.post("/webhook")
async def telegram_webhook(request: Request):
    update_data = await request.json()
    # INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
    # {'update_id': 662924880, 'message': {'message_id': 77, 'from': {'id': 8189842766, 'is_bot': False, 'first_name': '景', 'last_name': '歌', 'username': 'renren627', 'language_code': 'en'}, 'chat': {'id': 8189842766, 'first_name': '景', 'last_name': '歌', 'username': 'renren627', 'type': 'private'}, 'date': 1745798156, 'text': '/start', 'entities': [{'offset': 0, 'length': 6, 'type': 'bot_command'}]}}
    # 399 finsiehd
    # 4350`

    # Process incoming update
    print(update_data)
    response = await dispatcher.feed_webhook_update(bot=bot, update=update_data)

    # Send a message to yourself (user who sent something)
    if "message" in update_data:
        chat_id = update_data["message"]["chat"]["id"]
        await bot.send_message(chat_id, "✅ Webhook received! I got your message!")

    if response:
        return response.model_dump()
    return {"ok": True}


@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)
    print(f"Webhook set to {WEBHOOK_URL}")

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    await bot.session.close()
    print("Bot shutdown completed")
