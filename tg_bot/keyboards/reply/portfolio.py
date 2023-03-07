from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

portfolio_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text='Создать'),
            KeyboardButton(text='Редактировать'),
            KeyboardButton(text='Инвестиции'),
        ],
        [
            KeyboardButton(text='⏪Назад'),
        ]
    ]
)