# -*- coding: utf-8 -*-

import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy

from modules import common_handlers, guild_stock, triggers, bottles_giveout

from config_data.config import load_config, Config


# Загружаем конфиг в переменную config
config: Config = load_config()
bot_token: str = config.tg_bot.token


async def main() -> None:
    storage: MemoryStorage = MemoryStorage()
    dp: Dispatcher = Dispatcher(storage=storage, fsm_strategy=FSMStrategy.CHAT)
    # бот не работает в личных переписках
    dp.message.filter(F.chat.type != "private")
    dp.include_router(common_handlers.router)
    dp.include_router(guild_stock.router)
    dp.include_router(bottles_giveout.router)
    dp.include_router(triggers.router)
    bot: Bot = Bot(bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.send_message(391639940, "Поехали!")
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
