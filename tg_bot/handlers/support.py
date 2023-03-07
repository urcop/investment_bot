from aiogram import Dispatcher, types


async def support(message: types.Message):
    text = [
        'Сообщите о вашей проблеме - @karpevg'
    ]
    await message.answer('\n'.join(text))


def register_menu(dp: Dispatcher):
    dp.register_message_handler(support, text='Тех.Поддержка 👤')
