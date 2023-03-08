from datetime import datetime, timedelta

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Command

from tg_bot.handlers.portfolio import generate_edit_portfolio_text
from tg_bot.keyboards.reply.main_menu import main_menu
from tg_bot.models.items import Item, Item2User
from tg_bot.models.status import Status2User, Status
from tg_bot.models.users import User
from tg_bot.models.workers import Worker
from tg_bot.services.broadcast import broadcast


async def stat(message: types.Message):
    session_maker = message.bot['db']
    params = message.text.split(' ')
    reg_users = await User.get_users_by_reg_date(date=params[1], session_maker=session_maker)
    buying_statuses = await Status2User.get_buy_status_by_date(date=params[1], session_maker=session_maker)
    portfolios = await Item2User.get_add_portfolio_by_date(date=params[1], session_maker=session_maker)
    text = [
        f'Статистика за {"все время" if params[1] == "all" else params[1]}',
        f'Новых пользователей: {reg_users}',
        f'Куплено статусов: {buying_statuses}',
        f'Создано портфелей: {portfolios}'
    ]
    await message.answer('\n'.join(text))


async def broadcaster(message: types.Message):
    session_maker = message.bot['db']
    if message.content_type == 'photo':
        text = message.caption[4:]
        photo_id = message.photo[-1].file_id
    else:
        text = message.text[4:]
        photo_id = None
    users = [i[0] for i in await User.get_all_users(session_maker=session_maker)]
    await broadcast(bot=message.bot, users=users, text=text, disable_notifications=True,
                    message_type=message.content_type, photo_id=photo_id)


async def tell(message: types.Message):
    text = message.text.split(' ') if message.content_type == 'text' else message.caption.split(' ')
    text.pop(0)
    user_id = int(text[0])
    text.pop(0)
    message_to_user = ' '.join(text)
    if message.content_type == 'text':
        await message.bot.send_message(user_id, text=f'<b>Администратор отправил вам сообщение:</b> {message_to_user}')
    elif message.content_type == 'photo':
        await message.copy_to(user_id, caption=f'<b>Администратор отправил вам сообщение:</b> {message_to_user}')


async def info(message: types.Message):
    session_maker = message.bot['db']
    params = message.text.split(' ')
    user_id = int(params[1])
    user_reg_date = await User.get_reg_date(user_id=user_id, session_maker=session_maker)
    investments = await Item2User.get_all_user_items(user_id=user_id, session_maker=session_maker)
    now = int(datetime.now().timestamp())
    status_name = 'Отсутствует'
    status_expired = '-'
    status_id = await Status2User.get_user(user_id=user_id, time_now=now, session_maker=session_maker)
    if status_id:
        status_name = (await Status.get_name_by_id(status_id=status_id, session_maker=session_maker)).upper()
        status_end_time = await Status2User.get_end_time(user_id=user_id, session_maker=session_maker,
                                                         time_now=now)
        status_expired = (datetime.fromtimestamp(status_end_time)).strftime('%d.%m.%Y')
    text = f"""
📅 Дата регистрации: {user_reg_date}
🔑 ID: {user_id}
💸 Инвестиции: {len(investments) if investments else 'отсутствуют'}
⏰ Статус: {status_name} Действительный до {status_expired} 
    """
    await message.answer(text)


async def add_worker(message: types.Message):
    session_maker = message.bot['db']
    params = message.text.split(' ')
    params.pop(0)
    user_id = int(params[0])
    password = params[1]

    await Worker.add_worker(user_id=user_id, password=password, session_maker=session_maker)
    await message.answer('Работник успешно добавлен')
    await message.bot.send_message(chat_id=user_id, text='Вас назначили работником')


async def delete_worker(message: types.Message):
    session_maker = message.bot['db']
    params = message.text.split(' ')
    params.pop(0)
    user_id = int(params[0])
    await Worker.delete_worker(user_id=user_id, session_maker=session_maker)
    await message.answer('Работник успешно удален')
    await message.bot.send_message(chat_id=user_id, text='Вас сняли с должности работника', reply_markup=main_menu)


async def add_item(message: types.Message):
    session_maker = message.bot['db']
    params = message.text.split(' ')
    params.pop(0)
    item_type = int(params[0])
    category = int(params[1])
    quality = int(params[2])
    name = params[3]

    await Item.add_item(type=item_type, category=category, quality=quality, name=name, session_maker=session_maker)
    await message.answer(f'Предмет {name} успешно добавлен')


async def delete_item(message: types.Message):
    session_maker = message.bot['db']
    params = message.text.split(' ')
    params.pop(0)
    item_type = int(params[0])
    category = int(params[1])
    name = params[2]

    await Item.delete_item(item_type=item_type, name=name, category=category, session_maker=session_maker)
    await message.answer(f'Предмет {name} успешно удален')


async def add_status(message: types.Message):
    session_maker = message.bot['db']
    params = message.text.split(' ')
    status_name = params[0][1:]
    params.pop(0)
    user_id = int(params[0])
    period = int(params[1]) * 30
    status_id = await Status.get_id_by_name(status_name=status_name, session_maker=session_maker)
    now = int(datetime.now().timestamp())
    end_time = int((datetime.now() + timedelta(days=period)).timestamp())

    await Status2User.add_status_to_user(user_id=user_id, status_id=status_id, now_date=now, end_time=end_time,
                                         session_maker=session_maker)
    await message.answer(f'Статус {status_name} успешно выдан')
    await message.bot.send_message(chat_id=user_id, text=f'Вам выдан статус {status_name} на {params[1]} месяц(ев)')


async def delete_status(message: types.Message):
    session_maker = message.bot['db']
    params = message.text.split(' ')
    status_name = params[0][2:]
    params.pop(0)
    user_id = int(params[0])

    await Status2User.delete_user_status(user_id=user_id, session_maker=session_maker)
    await message.answer(f'Статус {status_name} у пользователя {user_id} успешно удален')
    await message.bot.send_message(chat_id=user_id, text=f'Ваш статус {status_name} был отобран администратором')


async def check_portfel(message: types.Message):
    session_maker = message.bot['db']
    params = message.text.split(' ')
    params.pop(0)
    user_id = int(params[0])
    text = [
        f'Портфель пользователя {user_id}:\n',
        f'Пусто'
    ]
    user_items_id = await Item2User.get_all_user_items(user_id=user_id, session_maker=session_maker)
    if len(user_items_id) > 0:
        user_items_name = [await Item.get_item_name(item_id[1], session_maker) for item_id in user_items_id]
        text = [f'Портфель пользователя {user_id}:\n']
        text += await generate_edit_portfolio_text(user_items_name)

    await message.answer('\n'.join(text))


async def give_balance(message: types.Message):
    session_maker = message.bot['db']
    params = message.text.split(' ')
    params.pop(0)
    user_id = int(params[0])
    value = int(params[1])

    await User.give_balance(user_id=user_id, count=value, session_maker=session_maker)
    await message.answer(f'Выдано {value} пользователю {user_id}')
    await message.bot.send_message(user_id, f'Вам выдано {value} р.')


def register_admin(dp: Dispatcher):
    dp.register_message_handler(stat, Command(['stat']), is_admin=True)
    dp.register_message_handler(broadcaster, text_startswith='/ads', content_types=['text', 'photo'], is_admin=True)
    dp.register_message_handler(tell, text_startswith='/tell', content_types=['text', 'photo'], is_admin=True)
    dp.register_message_handler(add_worker, Command(['ajob']), is_admin=True)
    dp.register_message_handler(delete_worker, Command(['djob']), is_admin=True)
    dp.register_message_handler(add_item, Command(['additem']), is_admin=True)
    dp.register_message_handler(delete_item, Command(['ditem']), is_admin=True)
    dp.register_message_handler(info, Command(['info']), is_admin=True)
    dp.register_message_handler(add_status, Command(['vip', 'premium']), is_admin=True)
    dp.register_message_handler(delete_status, Command(['dvip', 'dpremium']), is_admin=True)
    dp.register_message_handler(check_portfel, Command(['portfel']), is_admin=True)
    dp.register_message_handler(give_balance, Command(['givem']), is_admin=True)
