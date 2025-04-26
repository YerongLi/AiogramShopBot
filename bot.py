import logging
import traceback

from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BufferedInputFile
from redis.asyncio import Redis
import config
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from fastapi import FastAPI, Request, status, HTTPException
from config import TOKEN, WEBHOOK_URL, ADMIN_ID_LIST, WEBHOOK_SECRET_TOKEN
from db import create_db_and_tables
import uvicorn
from fastapi.responses import JSONResponse
from services.notification import NotificationService

redis = Redis(password=config.REDIS_PASSWORD)
bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=RedisStorage(redis))
app = FastAPI()


@app.post(config.WEBHOOK_PATH)
async def webhook(request: Request):
    secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    
    data = await request.json()
    print("📨 Raw update:", data)

    # Log the chat id for debugging purposes
    chat_id = data.get("message", {}).get("chat", {}).get("id")
    if chat_id:
        print(f"📱 Found chat ID: {chat_id}")
    else:
        print("❌ No chat ID in the update data")

    print(secret_token != WEBHOOK_SECRET_TOKEN)
    if secret_token != WEBHOOK_SECRET_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    try:
        update_data = await request.json()
        print('Finish updating')
        try:
            # This assumes you're accessing some field inside update_data
            await dp.feed_webhook_update(bot, update_data)

        except KeyError as e:
            # Log the missing field and its value
            missing_field = e.args[0]  # The key that was not found
            print(f"Field '{missing_field}' not found in update_data.")
            print(f"Update data: {update_data}")

        # await dp.feed_webhook_update(bot, update_data)
        print('Finish updating')
        return {"status": "ok"}
    except Exception as e:
        logging.error(f"Error processing webhook: {e}")
        return {"status": "error"}, status.HTTP_500_INTERNAL_SERVER_ERROR


@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()
    await bot.set_webhook(
        url=WEBHOOK_URL,
        secret_token=WEBHOOK_SECRET_TOKEN
    )
    for admin in ADMIN_ID_LIST:
        try:
            await bot.send_message(admin, 'Bot is working')
        except Exception as e:
            logging.warning(e)


@app.on_event("shutdown")
async def on_shutdown():
    logging.warning('Shutting down..')
    await bot.delete_webhook()
    await dp.storage.close()
    logging.warning('Bye!')


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    traceback_str = traceback.format_exc()
    admin_notification = (
        f"Critical error caused by {exc}\n\n"
        f"Stack trace:\n{traceback_str}"
    )
    if len(admin_notification) > 4096:
        byte_array = bytearray(admin_notification, 'utf-8')
        admin_notification = BufferedInputFile(byte_array, "exception.txt")
    await NotificationService.send_to_admins(admin_notification, None)
    return JSONResponse(
        status_code=500,
        content={"message": f"An error occurred: {str(exc)}"},
    )


def main() -> None:
    uvicorn.run(app, host=config.WEBAPP_HOST, port=config.WEBAPP_PORT)
