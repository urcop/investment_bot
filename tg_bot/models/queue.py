from sqlalchemy import Column, Integer, String, select, insert, func, delete, update, BigInteger
from sqlalchemy.orm import sessionmaker

from tg_bot.services.db_base import Base


class ChangeQueue(Base):
    __tablename__ = 'change_queue'
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer)
    active_worker = Column(BigInteger)

    @classmethod
    async def _get_last_id(cls, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = select(func.max(cls.id))
            result = await db_session.execute(sql)
            return result.scalar()

    @classmethod
    async def add_to_queue(cls, item_id: int, session_maker: sessionmaker):
        async with session_maker() as db_session:
            queue_id = await cls._get_last_id(session_maker)
            sql = insert(cls).values(id=queue_id + 1 if queue_id else 1, item_id=item_id, active_worker=0)
            result = await db_session.execute(sql)
            await db_session.commit()
            return result

    @classmethod
    async def get_item_id(cls, queue_id, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = select(cls.item_id).where(cls.id == queue_id)
            result = await db_session.execute(sql)
            return result.scalar()

    @classmethod
    async def get_all_queue(cls, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = select(cls.id).where(cls.active_worker == 0)
            result = await db_session.execute(sql)
            return result.all()

    @classmethod
    async def delete_from_queue(cls, queue_id: int, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = delete(cls).where(cls.id == queue_id)
            result = await db_session.execute(sql)
            await db_session.commit()
            return result

    @classmethod
    async def get_item(cls, item_id: int, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = select(cls.id).where(cls.item_id == item_id)
            result = await db_session.execute(sql)
            return result.scalar()

    @classmethod
    async def set_worker(cls, queue_id: int, worker_id: int, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = update(cls).where(cls.id == queue_id).values({'active_worker': worker_id})
            result = await db_session.execute(sql)
            await db_session.commit()
            return result
