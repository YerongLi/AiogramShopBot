# main.py
import asyncio
from fastapi import FastAPI, Request
from aiogram import Bot, types
from aiogram import Bot, Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

API_TOKEN = "8006406437:AAHvVIKDh_U5SpBjcIpPsPuoYlE1DDq6bfs"
WEBHOOK_URL = "https://9e5e-76-191-22-22.ngrok-free.app/webhook"

bot = Bot(token=API_TOKEN)
dispatcher = Dispatcher()

app = FastAPI()
# uvicorn main:app --host 0.0.0.0 --port 8080
@app.post("/webhook")
async def telegram_webhook(request: Request):
    update_data = await request.json()
    update = types.Update(**update_data)  # Parse update properly

    if update.message:
        chat_id = update.message.chat.id

        # Create a button
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Click Me!", callback_data="button_clicked")]
        ])

        # Send message with button
        await bot.send_message(chat_id, "✅ Webhook received! Press the button below!", reply_markup=keyboard)

    if update.callback_query:
        chat_id = update.callback_query.from_user.id

        # Print when button clicked
        print(f"Button clicked by user {chat_id}")

        # Reply to button click
        await bot.send_message(chat_id, "🎉 You clicked the button!")

        # Optionally you can answer the callback query (to remove the loading spinner)
        await bot.answer_callback_query(update.callback_query.id, text="Button pressed!")

    return {"ok": True}


@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL, allowed_updates=["message", "callback_query"])

    print(f"Webhook set to {WEBHOOK_URL}")

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    await bot.session.close()
    print("Bot shutdown completed")
