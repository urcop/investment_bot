from datetime import datetime

from sqlalchemy import Column, Integer, String, insert, select, and_, Float, func, BigInteger, delete, update
from sqlalchemy.orm import sessionmaker

from tg_bot.services.db_base import Base


class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    type = Column(Integer)
    category = Column(Integer)
    quality = Column(Integer)
    price = Column(Float)

    @classmethod
    async def _get_last_id(cls, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = select(func.max(cls.id))
            result = await db_session.execute(sql)
            return result.scalar()

    @classmethod
    async def add_item(cls, name: str, type: int,
                       category: int, quality: int,
                       session_maker: sessionmaker):
        async with session_maker() as db_session:
            last_id = await cls._get_last_id(session_maker)
            sql = insert(cls).values(id=last_id + 1 if last_id else 1, name=name, type=type, category=category,
                                     quality=quality, price=0)
            result = await db_session.execute(sql)
            await db_session.commit()
            return result

    @classmethod
    async def get_all_id(cls, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = select(cls.id)
            result = await db_session.execute(sql)
            return result.all()

    @classmethod
    async def delete_item(cls, item_type: int, category: int, name: str, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = delete(cls).where(and_(cls.type == item_type, cls.category == category, cls.name == name))
            result = await db_session.execute(sql)
            await db_session.commit()
            return result

    @classmethod
    async def update_price(cls, item_id: int, value: float, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = update(cls).where(cls.id == item_id).values({'price': value})
            result = await db_session.execute(sql)
            await db_session.commit()
            return result

    @classmethod
    async def find_all_items(cls, type: int, category: int, quality: int, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = select(cls.name).where(and_(cls.type == type, cls.category == category, cls.quality == quality))
            result = await db_session.execute(sql)
            return result.all()

    @classmethod
    async def get_item_id(cls, name: str, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = select(cls.id).where(cls.name == name)
            result = await db_session.execute(sql)
            return result.scalar()

    @classmethod
    async def get_item_name(cls, item_id: int, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = select(cls.name).where(cls.id == item_id)
            result = await db_session.execute(sql)
            return result.scalar()

    @classmethod
    async def get_item_price(cls, item_id: int, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = select(cls.price).where(cls.id == item_id)
            result = await db_session.execute(sql)
            return result.scalar()


class Item2User(Base):
    __tablename__ = 'item2user'
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer)
    user_id = Column(BigInteger)
    price = Column(Float)
    count = Column(Integer)
    date_unix = Column(Integer)
    admin_date = Column(String)

    @classmethod
    async def _get_last_id(cls, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = select(func.max(cls.id))
            result = await db_session.execute(sql)
            return result.scalar()

    @classmethod
    async def add_item_to_user(cls, item_id: int, user_id: int, price: float, count: int, now_date: int,
                               session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = insert(cls).values(item_id=item_id, user_id=user_id, price=price, count=count,
                                     date_unix=int(now_date),
                                     admin_date=(datetime.fromtimestamp(now_date)).strftime('%d.%m.%Y'))
            result = await db_session.execute(sql)
            await db_session.commit()
            return result

    @classmethod
    async def get_all_user_items(cls, user_id: int, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = select(cls.id, cls.item_id).where(cls.user_id == user_id)
            result = await db_session.execute(sql)
            return result.all()

    @classmethod
    async def delete_user_item(cls, invest_id: int, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = delete(cls).where(cls.id == invest_id)
            result = await db_session.execute(sql)
            await db_session.commit()
            return result

    @classmethod
    async def update_invest(cls, invest_id: int, value: float, action: str, session_maker: sessionmaker):
        async with session_maker() as db_session:
            if action == 'price':
                sql = update(cls).where(cls.id == invest_id).values({cls.price: value})
            else:
                sql = update(cls).where(cls.id == invest_id).values({cls.count: int(value)})
            result = await db_session.execute(sql)
            await db_session.commit()
            return result

    @classmethod
    async def get_item_id(cls, invest_id: int, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = select(cls.item_id).where(cls.id == invest_id)
            result = await db_session.execute(sql)
            return result.scalar()

    @classmethod
    async def get_item_count(cls, invest_id: int, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = select(cls.count).where(cls.id == invest_id)
            result = await db_session.execute(sql)
            return result.scalar()

    @classmethod
    async def get_item_price(cls, invest_id: int, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = select(cls.price).where(cls.id == invest_id)
            result = await db_session.execute(sql)
            return result.scalar()

    @classmethod
    async def is_exist(cls, user_id: int, item_id: int, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = select(cls.id).where(and_(cls.item_id == item_id, cls.user_id == user_id))
            result = await db_session.execute(sql)
            return result.scalar()

    @classmethod
    async def get_add_portfolio_by_date(cls, date: str, session_maker: sessionmaker):
        async with session_maker() as db_session:
            if date == 'all':
                sql = select(func.count(cls.id))
            else:
                sql = select(func.count(cls.id)).where(cls.admin_date == date)
            result = await db_session.execute(sql)
            return result.scalar()
