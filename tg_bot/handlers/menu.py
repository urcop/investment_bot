from aiogram import Dispatcher, types


async def bag(message: types.Message):
    ...


async def support(message: types.Message):
    text = [
        'Сообщите о вашей проблеме - @karpevg'
    ]
    await message.answer('\n'.join(text))


async def profile(message: types.Message):
    ...


def register_menu(dp: Dispatcher):
    dp.register_message_handler(bag, text='Портфель 💼')
    dp.register_message_handler(support, text='Тех.Поддержка 👤')
    dp.register_message_handler(profile, text='Профиль 📝')
