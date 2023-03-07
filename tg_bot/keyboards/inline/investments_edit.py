from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

invest_edit_callback = CallbackData('invest', 'invest_id')
invest_view_callback = CallbackData('invest_view', 'invest_id')
portfolio_edit_choice_callback = CallbackData('invest_edit', 'action', 'invest_id')
delete_confirm_callback = CallbackData('delete_confirm', 'answer', 'invest_id')


async def generate_invest_edit_items_keyboard(_items):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for item in _items:
        invest_id = item[0]
        keyboard.insert(InlineKeyboardButton(text=_items.index(item) + 1,
                                             callback_data=invest_edit_callback.new(invest_id=invest_id)))
    return keyboard


async def generate_invest_view_items_keyboard(_items):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for item in _items:
        invest_id = item[0]
        keyboard.insert(InlineKeyboardButton(text=_items.index(item) + 1,
                                             callback_data=invest_view_callback.new(invest_id=invest_id)))
    return keyboard


async def portfolio_edit_choice_keyboard(invest_id):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Количество',
                                     callback_data=portfolio_edit_choice_callback.new('count', invest_id))
            ],
            [
                InlineKeyboardButton(text='Изначальную стоимость',
                                     callback_data=portfolio_edit_choice_callback.new('price', invest_id))
            ],
            [
                InlineKeyboardButton(text='Удалить инвестицию',
                                     callback_data=portfolio_edit_choice_callback.new('delete', invest_id))
            ]
        ]
    )
    return keyboard


async def delete_confirm(invest_id):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Да', callback_data=delete_confirm_callback.new('yes', invest_id))
            ],
            [
                InlineKeyboardButton(text='Нет', callback_data=delete_confirm_callback.new('no', 'None'))
            ]
        ]
    )
    return keyboard
