import asyncio
import logging
import sys
from os import getenv
from typing import Any, List

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import Scene, on, SceneRegistry
from aiogram.fsm.storage.memory import SimpleEventIsolation
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardRemove,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder

TOKEN = getenv("BOT_TOKEN")


car_types = ["легковая", "внедорожник", "минивен", "говновоз"]

services = [
    "полировка", "хим чистка",  "полировка стекла", "тонировка",
    "защитные покрытия", "оклейка кузова полиуретановой пленкой"
]

option_list = {
    "polirovka": {
        "legkaya": {"легковая": 1000, "внедорожник": 2500, "минивен": 1700, "говновоз": 9999},
        "glubokaya": {"легковая": 2000, "внедорожник": 5000, "минивен": 3200, "говновоз": 9999}
    },
    "xim chistka": {
        "all": {"легковая": 10000, "внедорожник": 25000, "минивен": 17000, "говновоз": 99999},
        "1 chair": {"легковая": 1000, "внедорожник": 2500, "минивен": 1700, "говновоз": 9999}
    },
}


class GTTScene(Scene, state="quiz"):
    @on.message.enter()
    async def on_enter(
            self, message: Message, state: FSMContext,
            step: str | None = "car_choosing", path: List | None = None) -> Any:

        if step == "car_choosing":
            text = "Выберите тип машины"
            options = car_types
        elif step == "service_choosing":
            text = "Выберите услугу"
            await state.update_data(path=path)

            if path is None:
                path = []

            options = option_list
            for option in path:
                options = options[option]

            if list(options.keys()) == car_types:
                data = await state.get_data()
                answers = data.get("answers", {})
                answers[path[0]] = options[data["answers"]["car_choosing"]]
                data["path"] = []

                await state.update_data(data=data)
                options = option_list

            options = list(options.keys()) + ["Завершить выбор услуг"]

        markup = ReplyKeyboardBuilder()
        markup.add(*[KeyboardButton(text=option) for option in options])

        await state.update_data(step=step)
        return await message.answer(text=text, reply_markup=markup.adjust(2).as_markup(resize_keyboard=True))

    @on.message.exit()
    async def on_exit(self, message: Message, state: FSMContext) -> None:
        pass

    @on.message(F.text)
    async def answer(self, message: Message, state: FSMContext) -> None:
        data = await state.get_data()
        step = data["step"]
        path = data.get("path")

        if step == "car_choosing":
            if message.text.casefold() in car_types:
                answers = data.get("answers", {})
                answers[step] = message.text

                await state.update_data(answers=answers)
                step = "service_choosing"
            else:
                await message.answer("Не известный тип автомобиля, попробуйте еще раз")
        elif step == "service_choosing":
            if path is None:
                options = option_list.keys()
            else:
                options = option_list
                for option in path:
                    options = options[option]

            if message.text.casefold() in options:
                if path is None:
                    path = []
                path.append(message.text)
        await self.wizard.retake(step=step, path=path)

    @on.message()
    async def unknown_message(self, message: Message) -> None:
        await message.answer("Please select an answer.")


quiz_router = Router(name=__name__)
quiz_router.message.register(GTTScene.as_handler(), Command("new_application"))


@quiz_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    await message.answer(
        "Добро пожаловать в бот GTT delailing!"
        "Бот воздан для улучшения работы с нашими уважаемыми клиентами! (с вами)."
        "Здесь вы можете выбрать необходимые услуги."
        "Для более точной суммы за услуги необходимо обратиться  в наш детейлинг центр."
        "Что бы создать новую заявку воспользуйтесь командой /new_application",
        reply_markup=ReplyKeyboardRemove(),
    )


def create_dispatcher():
    dispatcher = Dispatcher(
        events_isolation=SimpleEventIsolation(),
    )
    dispatcher.include_router(quiz_router)

    scene_registry = SceneRegistry(dispatcher)
    scene_registry.add(GTTScene)

    return dispatcher


async def main():
    dp = create_dispatcher()
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
