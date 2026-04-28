import os
import logging
from aiogram import Bot, Dispatcher, types
from handlers import command_router, callback_router, message_router

import json

logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv("API_TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

dp.include_routers(
    command_router,
    callback_router,
    message_router
)

async def process_event(event):

    update = types.Update.model_validate(json.loads(event['body']), context={"bot": bot})
    await dp.feed_update(bot, update)

async def webhook(event, context):
    if event['httpMethod'] == 'POST':
        # Bot and dispatcher initialization 
        # Объект бота 

        await process_event(event)
        return {'statusCode': 200, 'body': 'ok'}

    return {'statusCode': 405}
