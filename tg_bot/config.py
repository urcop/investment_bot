from dataclasses import dataclass
from environs import Env



@dataclass
class TgBot:
    token: str
    use_redis: bool


@dataclass
class Db:
    host: str
    password: str
    user: str
    database: str
    port: str


@dataclass
class Misc:
    ua_card: int
    phone: str
    ru_card: int
    other_params: str = None


@dataclass
class Qiwi:
    token: str
    qiwi_pub_key: str
    qiwi_sec_key: str
    qiwi_phone: str


@dataclass
class Config:
    bot: TgBot
    db: Db
    misc: Misc
    qiwi: Qiwi


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        bot=TgBot(
            token=env.str("BOT_TOKEN"),
            use_redis=env.bool("USE_REDIS"),
        ),
        db=Db(
            host=env.str("DATABASE_HOST"),
            password=env.str("DATABASE_PASSWORD"),
            user=env.str("DATABASE_USER"),
            database=env.str("DATABASE_NAME"),
            port=env.str("DATABASE_PORT"),
        ),
        misc=Misc(
            ua_card=env.int("UA_CARD"),
            phone=env.str("PHONE"),
            ru_card=env.int("RU_CARD")
        ),
        qiwi=Qiwi(
            token=env.str("QIWI_TOKEN"),
            qiwi_pub_key=env.str("QIWI_PUB_KEY"),
            qiwi_sec_key=env.str("QIWI_SEC_KEY"),
            qiwi_phone=env.str("QIWI_WALLET"),
        ),
    )
