from datetime import datetime

from sqlalchemy import BigInteger, Column, String, Integer, select, insert, update, func
from sqlalchemy.orm import sessionmaker

from tg_bot.services.db_base import Base


class User(Base):
    __tablename__ = 'users'
    telegram_id = Column(BigInteger, primary_key=True)
    username = Column(String(length=100))
    fullname = Column(String(length=100))
    balance = Column(Integer, default=0)
    role = Column(String(length=100), default='user')
    reg_date = Column(String)

    @classmethod
    async def get_user(cls, session_maker: sessionmaker, telegram_id: int) -> 'User':
        async with session_maker() as db_session:
            sql = select(cls).where(cls.telegram_id == telegram_id)
            request = await db_session.execute(sql)
            user: cls = request.scalar()
        return user

    @classmethod
    async def add_user(cls,
                       session_maker: sessionmaker,
                       telegram_id: int,
                       fullname: str,
                       date: datetime,
                       username: str = None,
                       ) -> 'User':
        async with session_maker() as db_session:
            admin_date = date.strftime('%d.%m.%Y')
            sql = insert(cls).values(
                telegram_id=telegram_id,
                fullname=fullname,
                username=username,
                reg_date=admin_date
            ).returning('*')
            result = await db_session.execute(sql)
            await db_session.commit()
            return result.first()

    @classmethod
    async def update_username_fullname(cls, telegram_id: int, session_maker: sessionmaker, username: str,
                                       fullname: str) -> 'User':
        async with session_maker() as db_session:
            extra_context = {'username': username, 'fullname': fullname}
            sql = update(cls).where(cls.telegram_id == telegram_id).values(extra_context)
            result = await db_session.execute(sql)
            await db_session.commit()
            return result

    @classmethod
    async def get_admins(cls, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = select(cls.telegram_id).where(cls.role == 'admin')
            result = await db_session.execute(sql)
            return result.all()

    @classmethod
    async def get_workers(cls, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = select(cls.telegram_id).where(cls.role == 'worker')
            result = await db_session.execute(sql)
            return result.all()

    @classmethod
    async def get_balance(cls, user_id: int, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = select(cls.balance).where(cls.telegram_id == user_id)
            result = await db_session.execute(sql)
            return result.scalar()

    @classmethod
    async def take_balance(cls, user_id: int, count: int, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = update(cls).where(cls.telegram_id == user_id).values({'balance': cls.balance - count})
            result = await db_session.execute(sql)
            await db_session.commit()
            return result

    @classmethod
    async def give_balance(cls, user_id: int, count: int, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = update(cls).where(cls.telegram_id == user_id).values({'balance': cls.balance + count})
            result = await db_session.execute(sql)
            await db_session.commit()
            return result

    @classmethod
    async def set_role(cls, user_id: int, role: str, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = update(cls).where(user_id == cls.telegram_id).values({'role': role})
            result = await db_session.execute(sql)
            await db_session.commit()
            return result

    @classmethod
    async def get_users_by_reg_date(cls, date: str, session_maker: sessionmaker):
        async with session_maker() as db_session:
            if date == 'all':
                sql = select(func.count(cls.telegram_id))
            else:
                sql = select(func.count(cls.telegram_id)).where(cls.reg_date == date)
            result = await db_session.execute(sql)
            return result.scalar()

    @classmethod
    async def get_reg_date(cls, user_id: int, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = select(cls.reg_date).where(user_id == cls.telegram_id)
            result = await db_session.execute(sql)
            return result.scalar()

    @classmethod
    async def get_all_users(cls, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = select(cls.telegram_id)
            request = await db_session.execute(sql)
            return request.all()
