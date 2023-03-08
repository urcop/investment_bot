import logging
from datetime import datetime

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from tg_bot.keyboards.inline.create_investment import types_keyboard, item_type_callback, category_keyboard, \
    quality_keyboard, item_category_callback, generate_output_keyboard, item_quality_callback, item_callback
from tg_bot.keyboards.inline.investments_edit import invest_edit_callback, \
    portfolio_edit_choice_keyboard, portfolio_edit_choice_callback, delete_confirm, delete_confirm_callback, \
    generate_invest_edit_items_keyboard, generate_invest_view_items_keyboard, invest_view_callback
from tg_bot.keyboards.reply.main_menu import back_main_menu
from tg_bot.keyboards.reply.portfolio import portfolio_keyboard
from tg_bot.models.items import Item, Item2User
from tg_bot.models.status import Status2User
from tg_bot.states.create_investment import CreateInvestment


async def generate_edit_portfolio_text(_items):
    return [f'{index + 1}: <strong>{item}</strong>' for index, item in enumerate(_items)]


async def portfolio(message: types.Message):
    await message.answer('Портфель', reply_markup=portfolio_keyboard)


async def create(message: types.Message):
    statuses = {
        -1: 1,
        2: 5,
        1: 15
    }
    session_maker = message.bot['db']
    user_invests = await Item2User.get_all_user_items(user_id=message.from_user.id, session_maker=session_maker)
    now = int(datetime.now().timestamp())
    status_id = await Status2User.get_user(user_id=message.from_user.id, time_now=now, session_maker=session_maker)
    user_status = status_id if status_id else -1
    if len(user_invests) < statuses[user_status]:
        await message.answer('Выберите предмет:', reply_markup=types_keyboard)
        await CreateInvestment.first()
    else:
        await message.answer('❗️Вы создали максимальное количество портфелей, обновите свой статус.')


async def get_item_type(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    async with state.proxy() as data:
        try:
            if data['category'] == 'back':
                data.pop('category')
            if data['quality'] == 'back':
                data.pop('quality')
        except KeyError:
            pass
        data['type'] = int(callback_data.get('type'))
        if data['type'] == 1:
            await CreateInvestment.category.set()
            await call.message.edit_text('Выберите категорию оружия', reply_markup=category_keyboard)
        else:
            if data['type'] in (2, 3, 4):
                text = {
                    2: 'наклейки',
                    3: 'брелока',
                    4: 'графита'
                }
                await call.message.edit_text(f'Выберите качество {text[data["type"]]}',
                                             reply_markup=quality_keyboard)
                await CreateInvestment.quality.set()


async def choosing_an_item_category(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    async with state.proxy() as data:
        data['category'] = callback_data.get('category')
        if data['category'] == 'back':
            await CreateInvestment.type.set()
            await call.message.edit_text('Выберите предмет для вывода', reply_markup=types_keyboard)
        else:
            if data['type'] == 1:
                await call.message.edit_text(f'Выберите качество оружия',
                                             reply_markup=quality_keyboard)
                await CreateInvestment.quality.set()


async def choosing_an_item_quality(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    async with state.proxy() as data:
        try:
            if data['category'] == 'back':
                data['category'] = 0
        except KeyError:
            data['category'] = 0

        data['quality'] = callback_data.get('quality')
        if data['quality'] == 'back' and data['category'] == 0:
            await CreateInvestment.type.set()
            await call.message.edit_text('Выберите предмет для вывода', reply_markup=types_keyboard)
        elif data['quality'] == 'back' and data['type'] == 1:
            await CreateInvestment.category.set()
            await call.message.edit_text('Выберите категорию оружия', reply_markup=category_keyboard)
        elif data['quality'] != 'back':
            session_maker = call.bot['db']
            await CreateInvestment.item.set()
            items = [item[0] for item in
                     await Item.find_all_items(type=int(data['type']), category=int(data['category']),
                                               quality=int(data['quality']),
                                               session_maker=session_maker)]
            if len(items) > 0:
                await call.message.edit_text('Выберите предмет из списка',
                                             reply_markup=await generate_output_keyboard(items))
            else:
                await call.message.edit_text('Не найдены предметы в этой категории')
                await state.finish()


async def get_item_name(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    session_maker = call.bot['db']
    async with state.proxy() as data:
        data['item'] = callback_data.get('name')
        item_id = await Item.get_item_id(name=data['item'], session_maker=session_maker)
        if data['item'] == 'back':
            await CreateInvestment.quality.set()
            if data['type'] in (1, 2, 3, 4):
                text = {
                    1: 'оружия',
                    2: 'наклейки',
                    3: 'брелока',
                    4: 'графита',
                }
                await call.message.edit_text(f'Выберите качество {text[data["type"]]}',
                                             reply_markup=quality_keyboard)
        else:
            is_exists = await Item2User.is_exist(item_id=item_id, user_id=call.from_user.id,
                                                 session_maker=session_maker)
            if not is_exists:
                await call.message.edit_text('Введите за сколько вы покупали предмет')
                await CreateInvestment.price.set()
            else:
                await state.finish()
                await call.message.edit_text(
                    '❗В вашем портфеле уже есть такой лот, вы можете добавить новый или изменить существующий')



async def get_item_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        try:
            data['price'] = float(message.text)
            await CreateInvestment.count.set()
            await message.answer('Введите количество')
        except ValueError:
            await message.answer('Введите число')
            return


async def get_item_count(message: types.Message, state: FSMContext):
    session_maker = message.bot['db']
    async with state.proxy() as data:
        try:
            data['count'] = float(message.text)
            item_id = await Item.get_item_id(name=data['item'], session_maker=session_maker)

            now = int(datetime.now().timestamp())
            await Item2User.add_item_to_user(item_id=item_id, user_id=message.from_user.id,
                                             price=float(data['price']),
                                             count=int(data['count']), session_maker=session_maker, now_date=now)
            await state.finish()
            await message.answer('🎉 Предмет успешно добавлен в портфель')
        except ValueError:
            await message.answer('Введите число')
            return


async def portfolio_edit(message: types.Message, state: FSMContext):
    is_state = await state.get_state()
    if is_state:
        await state.finish()

    param = message.text
    session_maker = message.bot['db']
    user_items_id = await Item2User.get_all_user_items(user_id=message.from_user.id, session_maker=session_maker)
    if len(user_items_id) > 0:
        user_items_name = [await Item.get_item_name(item_id[1], session_maker) for item_id in user_items_id]
        text = ['Выберите инвестицию:\n']
        text += await generate_edit_portfolio_text(user_items_name)
    else:
        await message.answer(
            'На данный момент у вас нет инвестиций, добавьте ее нажав на кнопку <strong>Создать</strong>')
        return
    if param == 'Редактировать':
        keyboard = await generate_invest_edit_items_keyboard(user_items_id)
    else:
        keyboard = await generate_invest_view_items_keyboard(user_items_id)
    await message.answer('\n'.join(text), reply_markup=keyboard)


async def portfolio_edit_choice(call: types.CallbackQuery, callback_data: dict):
    invest_id = int(callback_data['invest_id'])
    await call.message.edit_text('Выберите что хотите изменить:',
                                 reply_markup=await portfolio_edit_choice_keyboard(invest_id=invest_id))


async def action_with_investment(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    action = callback_data['action']
    invest_id = int(callback_data['invest_id'])

    async with state.proxy() as data:
        if action == 'delete':
            await call.message.edit_text('Вы действительно хотите удалить эту инвестицию?',
                                         reply_markup=await delete_confirm(invest_id=invest_id))
        elif action == 'count':
            await call.message.delete()
            await call.message.answer('Введите новое значение количества', reply_markup=back_main_menu)
            await state.set_state('action_with_invest')
            data['invest_id'] = invest_id
            data['action'] = action
        elif action == 'price':
            await call.message.delete()
            await call.message.answer(
                'Введите новое значение изначальной цены (можно писать через точку или запятую но не более двух цифр)',
                reply_markup=back_main_menu)
            await state.set_state('action_with_invest')
            data['invest_id'] = invest_id
            data['action'] = action


async def delete_confirmation(call: types.CallbackQuery, callback_data: dict):
    answer = callback_data['answer']
    if answer == 'yes':
        session_maker = call.bot['db']
        invest_id = int(callback_data['invest_id'])
        await Item2User.delete_user_item(invest_id=invest_id, session_maker=session_maker)
        await call.message.edit_text('Инвестиция успешно удалена')

    elif answer == 'no':
        await call.message.edit_text('Операция отменена')


async def get_edit_value(message: types.Message, state: FSMContext):
    try:
        value = float(message.text)
    except ValueError:
        await message.answer('Введите число')
        return

    async with state.proxy() as data:
        invest_id = int(data['invest_id'])
        action = data['action']
        session_maker = message.bot['db']
        await Item2User.update_invest(invest_id=invest_id, value=value, action=action, session_maker=session_maker)
        await message.answer('Цена успешно изменена' if action == 'price' else 'Количество успешно изменено')
        await state.finish()


async def portfolio_view_invest(call: types.CallbackQuery, callback_data: dict):
    session_maker = call.bot['db']
    invest_id = int(callback_data['invest_id'])
    item_id = await Item2User.get_item_id(invest_id=invest_id, session_maker=session_maker)
    item_name = await Item.get_item_name(item_id=item_id, session_maker=session_maker)
    item_price = await Item.get_item_price(item_id=item_id, session_maker=session_maker)
    user_price = await Item2User.get_item_price(invest_id=invest_id, session_maker=session_maker)
    count = await Item2User.get_item_count(invest_id=invest_id, session_maker=session_maker)
    income = (item_price - user_price - ((item_price - user_price) * 0.2)) * count

    text = [
        f'Название: <strong>{item_name}</strong>',
        f'Количество: <strong>{count}</strong>',
        f'Стоимость на данный момент: <strong>{item_price}</strong>',
        f'Потрачено денег: <strong>{user_price * count}</strong>',
        f'Заработано: <strong>{"вы в плюсе" if income > 0 else "вы в минусе"} на {abs(income)}</strong>'
    ]
    await call.message.edit_text('\n'.join(text))


def register_portfolio(dp: Dispatcher):
    dp.register_message_handler(portfolio, text='Портфель 💼')
    dp.register_message_handler(create, text='Создать')
    dp.register_callback_query_handler(get_item_type, item_type_callback.filter(), state=CreateInvestment.type)
    dp.register_callback_query_handler(choosing_an_item_category, item_category_callback.filter(),
                                       state=CreateInvestment.category)
    dp.register_callback_query_handler(choosing_an_item_quality, item_quality_callback.filter(),
                                       state=CreateInvestment.quality)
    dp.register_callback_query_handler(get_item_name, item_callback.filter(), state=CreateInvestment.item)
    dp.register_message_handler(get_item_price, state=CreateInvestment.price)
    dp.register_message_handler(get_item_count, state=CreateInvestment.count)
    dp.register_message_handler(portfolio_edit, text=['Редактировать', 'Инвестиции'], state='*')
    dp.register_callback_query_handler(portfolio_edit_choice, invest_edit_callback.filter())
    dp.register_callback_query_handler(action_with_investment, portfolio_edit_choice_callback.filter())
    dp.register_callback_query_handler(delete_confirmation, delete_confirm_callback.filter())
    dp.register_message_handler(get_edit_value, state='action_with_invest')
    dp.register_callback_query_handler(portfolio_view_invest, invest_view_callback.filter())
