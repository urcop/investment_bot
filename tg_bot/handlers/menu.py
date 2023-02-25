from aiogram import Dispatcher, types
from aiogram.types import CallbackQuery

from tg_bot.keyboards.inline.profile import status_keyboard, status_callback
from tg_bot.keyboards.inline.status import status_choice_keyboard, status_choice_callback, selection_selected_status, \
    select_selected_status


async def generate_profile_text(id: int, username: str):
    text = f"""
🔑 ID: {id}
👤 Никнейм: {f'@{username}' if username else 'Отсутствует'}
💸 Инвестиции: Отсутствуют
⏰ Статус: Отсутствует
        """
    return text


async def generate_status_text(status: str):
    text = []
    if status == 'vip':
        text = ['Позволяет вам создавать 3 слота в портфеле.',
                'Месяц <strong>100 руб / 50 грн</strong>',
                '3 месяца <strong>250 руб / 125 грн.</strong>']
    elif status == 'premium':
        text = ['Позволяет вам создавать 15 слота в портфеле.',
                'Месяц <strong>500 руб / 250 грн</strong>',
                '3 месяца <strong>1200 руб / 600 грн.</strong>']
    return '\n'.join(text)


async def bag(message: types.Message):
    ...


async def support(message: types.Message):
    text = [
        'Сообщите о вашей проблеме - @karpevg'
    ]
    await message.answer('\n'.join(text))


async def profile(message: types.Message):
    id = message.from_user.id
    username = message.from_user.username
    text = await generate_profile_text(id=id, username=username)
    await message.answer(text, reply_markup=status_keyboard)


async def status(call: CallbackQuery):
    text = 'Выберите статус: '
    await call.message.edit_text(text, reply_markup=status_choice_keyboard)


async def status_choice(call: CallbackQuery, callback_data: dict):
    id = call.from_user.id
    username = call.from_user.username
    choice = callback_data['status']
    if choice == 'back':
        text = await generate_profile_text(id=id, username=username)
        keyboard = status_keyboard
    else:
        text = await generate_status_text(choice)
        keyboard = await selection_selected_status(choice)
    await call.message.edit_text(text, reply_markup=keyboard)


async def selected_status_choice(call: CallbackQuery, callback_data: dict):
    choice = callback_data['action']
    if choice == 'back':
        text = 'Выберите статус: '
        keyboard = status_choice_keyboard
        await call.message.edit_text(text, reply_markup=keyboard)
    else:
        status = callback_data['status']
        await call.message.answer(status)


def register_menu(dp: Dispatcher):
    dp.register_message_handler(bag, text='Портфель 💼')
    dp.register_message_handler(support, text='Тех.Поддержка 👤')
    dp.register_message_handler(profile, text='Профиль 📝')
    dp.register_callback_query_handler(status, status_callback.filter())
    dp.register_callback_query_handler(status_choice, status_choice_callback.filter())
    dp.register_callback_query_handler(selected_status_choice, select_selected_status.filter())
