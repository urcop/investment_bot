from aiogram import Bot

from tg_bot.models.items import Item
from tg_bot.models.queue import ChangeQueue
from tg_bot.models.users import User


async def update_queue(bot: Bot):
    session_maker = bot['db']
    workers = await User.get_workers(session_maker)
    for worker in workers:
        await bot.send_message(chat_id=worker[0], text='❗️Обновились тикеты на изменение цен')
    all_items_id = await Item.get_all_id(session_maker=session_maker)
    all_items_id_clear = [item_id[0] for item_id in all_items_id]

    for item_id in all_items_id_clear:
        is_exists = await ChangeQueue.get_item(item_id=int(item_id), session_maker=session_maker)
        if not is_exists:
            await ChangeQueue.add_to_queue(item_id=item_id, session_maker=session_maker)


async def check_sub(bot: Bot):
    ...
