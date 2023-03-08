import random

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from tg_bot.keyboards.inline.worker import generate_item_keyboard, queue_item_callback, accept_set_price_keyboard, \
    accept_set_price_callback
from tg_bot.keyboards.reply.main_menu import main_menu
from tg_bot.keyboards.reply.worker import worker_keyboard
from tg_bot.models.items import Item
from tg_bot.models.queue import ChangeQueue
from tg_bot.models.workers import Worker


async def job(message: types.Message, state: FSMContext):
    session_maker = message.bot['db']
    params = message.text.split(' ')
    if params[1] == 'off':
        await Worker.set_active(user_id=message.from_user.id, active=False, session_maker=session_maker)
        await message.answer('Вы закончили работу', reply_markup=main_menu)
        await state.finish()
    else:
        auth_worker = await Worker.auth_worker(user_id=message.from_user.id, password=params[1],
                                               session_maker=session_maker)
        if auth_worker:
            await Worker.set_active(user_id=message.from_user.id, active=True, session_maker=session_maker)
            await state.set_state('worker_in_job')
            await message.answer('Успешная авторизация', reply_markup=worker_keyboard)
            return
        else:
            await message.answer('Неверный пароль')
            return


async def take(message: types.Message):
    session_maker = message.bot['db']
    all_in_queue = await ChangeQueue.get_all_queue(session_maker=session_maker)
    if len(all_in_queue) == 0:
        await message.answer('Нет предметов в очереди')
        return

    random_num = random.randint(0, len(all_in_queue) - 1)
    queue_id = all_in_queue[random_num][0]
    item_id = await ChangeQueue.get_item_id(queue_id=int(queue_id), session_maker=session_maker)
    item_name = await Item.get_item_name(item_id=int(item_id), session_maker=session_maker)
    item_price = await Item.get_item_price(item_id=int(item_id), session_maker=session_maker)

    await ChangeQueue.set_worker(queue_id=int(queue_id), worker_id=message.from_user.id, session_maker=session_maker)

    text = f"""
🔑 Предмет: <code>{item_name}</code>
💵 Текущая цена: <strong>{item_price}</strong>

Нажмите на кнопку принять и введите новую цену предмета.
    """
    await message.answer(text, reply_markup=await generate_item_keyboard(int(item_id), queue_id))


async def accept_work(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    item_id = callback_data['item_id']
    queue_id = callback_data['queue_id']
    await call.message.edit_text('Введите новую стоимость')
    async with state.proxy() as data:
        await state.set_state('worker_set_price')
        data['item_id'] = item_id
        data['queue_id'] = queue_id


async def set_price(message: types.Message, state: FSMContext):
    try:
        new_price = float(message.text)
    except ValueError:
        await message.answer('Введите число')
        return
    async with state.proxy() as data:
        session_maker = message.bot['db']
        data['new_price'] = new_price
        item_id = int(data['item_id'])
        old_price = await Item.get_item_price(item_id=item_id, session_maker=session_maker)
        await message.answer(
            f'Вы хотите изменить стоимость <strong>{old_price}</strong> на <strong>{new_price}</strong>?',
            reply_markup=accept_set_price_keyboard)


async def set_price_accept(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    session_maker = call.bot['db']
    answer = callback_data['answer']
    async with state.proxy() as data:
        item_id = int(data['item_id'])
        queue_id = int(data['queue_id'])

    if answer == 'yes':
        new_price = float(data['new_price'])
        await ChangeQueue.delete_from_queue(queue_id=queue_id, session_maker=session_maker)
        await Item.update_price(item_id=item_id, value=new_price, session_maker=session_maker)
        await call.message.edit_text('Цена успешно изменена, напишите /take, чтобы взять следующий товар')
        await state.set_state('worker_in_job')
    else:
        await ChangeQueue.set_worker(queue_id=queue_id, worker_id=0, session_maker=session_maker)
        await call.message.edit_text('Отменено, напишите /take, чтобы взять другой товар')


def register_worker(dp: Dispatcher):
    dp.register_message_handler(job, Command(['job']), is_worker=True, state=['worker_in_job', None])
    dp.register_message_handler(take, Command(['take']), is_worker=True, state='worker_in_job')
    dp.register_callback_query_handler(accept_work, queue_item_callback.filter(), is_worker=True, state='worker_in_job')
    dp.register_message_handler(set_price, is_worker=True, state='worker_set_price')
    dp.register_callback_query_handler(set_price_accept, accept_set_price_callback.filter(), is_worker=True,
                                       state='worker_set_price')
