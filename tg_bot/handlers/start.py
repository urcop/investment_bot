from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Command

from tg_bot.keyboards.reply.main_menu import main_menu


async def start(message: types.Message):
    text = [
        "Спасибо что выбрали нас!",
        "Выберите в меню, что хотите сделать."
    ]
    await message.answer('\n'.join(text), reply_markup=main_menu)


def register_start(dp: Dispatcher):
    dp.register_message_handler(start, Command(['start']))
