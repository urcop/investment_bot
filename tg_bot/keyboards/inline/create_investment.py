from typing import List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

item_type_callback = CallbackData('item_type', 'type')
item_category_callback = CallbackData('item_category', 'category')
item_quality_callback = CallbackData('item_quality', 'quality')
item_callback = CallbackData('item', 'name')

types_keyboard = InlineKeyboardMarkup(
    row_width=1,
    inline_keyboard=[
        [
            InlineKeyboardButton('Оружие', callback_data=item_type_callback.new(1)),
        ],
        [
            InlineKeyboardButton('Наклейка', callback_data=item_type_callback.new(2)),
        ],
        [
            InlineKeyboardButton('Брелок', callback_data=item_type_callback.new(3)),
        ],
        [
            InlineKeyboardButton('Графиты', callback_data=item_type_callback.new(4)),
        ]
    ]
)

category_keyboard = InlineKeyboardMarkup(
    row_width=1,
    inline_keyboard=[
        [
            InlineKeyboardButton('Regular', callback_data=item_category_callback.new(1))
        ],
        [
            InlineKeyboardButton('StatTrack', callback_data=item_category_callback.new(2))
        ],
        [
            InlineKeyboardButton('Назад', callback_data=item_category_callback.new('back'))
        ]
    ]
)

quality_keyboard = InlineKeyboardMarkup(
    row_width=1,
    inline_keyboard=[
        [
            InlineKeyboardButton('Arcane', callback_data=item_quality_callback.new(4))
        ],
        [
            InlineKeyboardButton('Legendary', callback_data=item_quality_callback.new(3))
        ],
        [
            InlineKeyboardButton('Epic', callback_data=item_quality_callback.new(2))
        ],
        [
            InlineKeyboardButton('Rare', callback_data=item_quality_callback.new(1))
        ],
        [
            InlineKeyboardButton('Назад', callback_data=item_quality_callback.new('back'))
        ]
    ]
)


async def generate_output_keyboard(_items: List[str]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=2)

    for item in _items:
        keyboard.insert(InlineKeyboardButton(item, callback_data=item_callback.new(item)))

    keyboard.add(InlineKeyboardButton('Назад', callback_data=item_callback.new('back')))

    return keyboard

