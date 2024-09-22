import asyncio
import logging
import sys
from os import getenv
from typing import Any, Dict

from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

TOKEN = getenv("BOT_TOKEN")

form_router = Router()


class Car(StatesGroup):
    car_type = State()


@form_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    await state.set_state(Car.car_type)
    await message.answer(
        "Добро пожаловать в бот GTT delailing!"
        "Бот воздан для улучшения работы с нашими уважаемыми клиентами! (с вами)."
        "Здесь вы можете выбрать необходимые услуги."
        "Для более точной суммы за услуги необходимо обратиться  в наш детейлинг центр."
        "Что бы создать новую заявку воспользуйтесь командой /new_application",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(Command("new_application"))
async def new_application(message: Message, state: FSMContext) -> None:
    await state.set_state(Car.car_type)
    await message.answer("New application!")


async def show_summary(message: Message, data: Dict[str, Any], positive: bool = True) -> None:
    name = data["name"]
    language = data.get("language", "<something unexpected>")
    text = f"I'll keep in mind that, {html.quote(name)}, "
    text += (
        f"you like to write bots with {html.quote(language)}."
        if positive
        else "you don't like to write bots, so sad..."
    )
    await message.answer(text=text, reply_markup=ReplyKeyboardRemove())


async def main():
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp = Dispatcher()

    dp.include_router(form_router)

    # Start event dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())