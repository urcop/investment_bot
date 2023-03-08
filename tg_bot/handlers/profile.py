import datetime
import logging

from aiogram import Dispatcher, types
from aiogram.types import CallbackQuery
from sqlalchemy.orm import sessionmaker

from tg_bot.keyboards.inline.profile import status_keyboard, status_callback
from tg_bot.keyboards.inline.status import status_choice_keyboard, status_choice_callback, selection_selected_status, \
    select_selected_status, status_period, status_period_callback, edit_status_keyboard, change_status
from tg_bot.models.items import Item2User
from tg_bot.models.status import Status, Status2User
from tg_bot.models.users import User


async def generate_profile_text(user_id: int, username: str, session_maker: sessionmaker):
    status_name = 'Отсутствует'
    balance = await User.get_balance(user_id=user_id, session_maker=session_maker)
    now = int(datetime.datetime.now().timestamp())
    status_id = await Status2User.get_user(user_id=user_id, time_now=now, session_maker=session_maker)
    if status_id:
        status_name = (await Status.get_name_by_id(status_id=status_id, session_maker=session_maker)).upper()
    investments = await Item2User.get_all_user_items(user_id=user_id, session_maker=session_maker)
    text = f"""
🔑 ID: {user_id}
👤 Никнейм: {f'@{username}' if username else 'Отсутствует'}
💵 Баланс: {balance}
💸 Инвестиции: {len(investments) if investments else 'Отсутствуют'}
⏰ Статус: <strong>{status_name}</strong>
        """
    return text


async def generate_status_text(status_name: str):
    text = []
    if status_name == 'vip':
        text = ['Позволяет вам создавать 3 слота в портфеле.',
                'Месяц <strong>100 руб / 50 грн</strong>',
                '3 месяца <strong>250 руб / 125 грн.</strong>']
    elif status_name == 'premium':
        text = ['Позволяет вам создавать 15 слота в портфеле.',
                'Месяц <strong>500 руб / 250 грн</strong>',
                '3 месяца <strong>1200 руб / 600 грн.</strong>']
    return '\n'.join(text)


async def profile(message: types.Message):
    session_maker = message.bot['db']
    user_id = message.from_user.id
    username = message.from_user.username
    text = await generate_profile_text(user_id=user_id, username=username, session_maker=session_maker)
    await message.answer(text, reply_markup=status_keyboard)


async def status(call: CallbackQuery):
    session_maker = call.bot['db']
    now = int(datetime.datetime.now().timestamp())
    status_id = await Status2User.get_user(user_id=call.from_user.id, time_now=now, session_maker=session_maker)
    if status_id:
        status_name = await Status.get_name_by_id(status_id=status_id, session_maker=session_maker)
        status_end_time = await Status2User.get_end_time(user_id=call.from_user.id, session_maker=session_maker,
                                                         time_now=now)
        datetime_end_time = datetime.datetime.fromtimestamp(status_end_time)
        datetime_now_time = datetime.datetime.fromtimestamp(now)
        timer = str(datetime_end_time - datetime_now_time).replace('days', 'дней').replace('day', 'день')
        text = [
            f'✅ У вас приобретен статус <strong>{status_name.upper()}</strong>',
            '🕑 Подписка заканчивается через',
            f'\t\t\t\t\t\t{timer}'
        ]
        await call.message.edit_text('\n'.join(text), reply_markup=edit_status_keyboard)
    else:
        text = 'Выберите статус: '
        await call.message.edit_text(text, reply_markup=status_choice_keyboard)


async def status_choice(call: CallbackQuery, callback_data: dict):
    session_maker = call.bot['db']
    user_id = call.from_user.id
    username = call.from_user.username
    choice = callback_data['status']
    if choice == 'back':
        text = await generate_profile_text(user_id=user_id, username=username, session_maker=session_maker)
        keyboard = status_keyboard
    else:
        text = await generate_status_text(choice)
        keyboard = await selection_selected_status(choice)
    await call.message.edit_text(text, reply_markup=keyboard)


async def selected_status_choice(call: CallbackQuery, callback_data: dict):
    choice = callback_data['action']
    if choice == 'back':
        text = 'Выберите статус'
        keyboard = status_choice_keyboard
        await call.message.edit_text(text, reply_markup=keyboard)
    else:
        status_name = callback_data['status']
        await call.message.edit_text('Выберите период подписки', reply_markup=await status_period(status_name))


async def buy_status(call: CallbackQuery, callback_data: dict):
    status_name = callback_data['status']
    period = int(callback_data['period'])
    price = int(callback_data['price'])
    session_maker = call.bot['db']
    now = int(datetime.datetime.now().timestamp())
    time = {
        1: (datetime.datetime.now() + datetime.timedelta(days=30)).timestamp(),
        3: (datetime.datetime.now() + datetime.timedelta(days=90)).timestamp(),
    }

    user_balance = await User.get_balance(call.from_user.id, session_maker=session_maker)
    user_status_id = await Status2User.get_user(user_id=call.from_user.id, time_now=now, session_maker=session_maker)
    if user_status_id:
        await Status2User.delete_user_status(user_id=call.from_user.id, session_maker=session_maker)
    status_id = await Status.get_id_by_name(status_name=status_name, session_maker=session_maker)
    if user_balance >= price:
        await Status2User.add_status_to_user(user_id=call.from_user.id, status_id=status_id, end_time=int(time[period]),
                                             session_maker=session_maker, now_date=now)
        await User.take_balance(user_id=call.from_user.id, count=price, session_maker=session_maker)
        await call.message.edit_text(f'Вы успешно приобрели статус {status_name}')
        for admin in await User.get_admins(session_maker=session_maker):
            await call.bot.send_message(chat_id=int(admin[0]),
                                        text=f'Пользователь {call.from_user.id} купил {status_name} на {period} месяц(а)')
    else:
        await call.message.answer('У вас недостаточно средств')
        return


async def edit_status(call: types.CallbackQuery):
    await call.message.edit_text('Выберите статус:', reply_markup=status_choice_keyboard)


def register_profile(dp: Dispatcher):
    dp.register_message_handler(profile, text='Профиль 📝')
    dp.register_callback_query_handler(status, status_callback.filter())
    dp.register_callback_query_handler(status_choice, status_choice_callback.filter())
    dp.register_callback_query_handler(selected_status_choice, select_selected_status.filter())
    dp.register_callback_query_handler(buy_status, status_period_callback.filter())
    dp.register_callback_query_handler(edit_status, change_status.filter())
