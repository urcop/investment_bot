from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

status_choice_callback = CallbackData('status_choice', 'status')
select_selected_status = CallbackData('select_selected', 'action', 'status')

status_choice_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='VIP', callback_data=status_choice_callback.new('vip'))
        ],
        [
            InlineKeyboardButton(text='Premium', callback_data=status_choice_callback.new('premium'))
        ],
        [
            InlineKeyboardButton(text='Назад', callback_data=status_choice_callback.new('back'))
        ],
    ]
)


async def selection_selected_status(status):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Купить', callback_data=select_selected_status.new('buy', status))
            ],
            [
                InlineKeyboardButton(text='Назад', callback_data=select_selected_status.new('back', 'None'))
            ]
        ]
    )
    return keyboard
