from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Channels, Base, Users, Creatives, Buys
from typing import Dict, Tuple, List, Optional
from sqlalchemy import select, update, insert, or_
from sqlalchemy.sql.expression import func


class DBController:
    Base()
    
    def __init__(self, connection: str) -> None:
        self.engine = create_engine(connection, echo=True)
        self.session = sessionmaker(autoflush=False, bind=self.engine)


    def register_user(self, username: str, user_id: str) -> Tuple:
        """ Внесение в БД первичных данных о пользователе """
        with self.session.begin() as session:
            new_user = Users(username=username, telegram_id=user_id)
            session.add(new_user)
            session.commit()

    
    def register_channel(self, channel_name: str, ch_id: str, admin_id: list) -> Tuple:
        with self.session.begin() as session:
            new_user = Channels(username=channel_name, telegram_id=ch_id, admin=admin_id)
            session.add(new_user)
            session.commit()


    def check_user(self, user_id: str) -> list:
        """ Проверка наличия пользователя """
        with self.session.begin() as session:
            result = session.execute(
                select(Users.username).where(Users.telegram_id == user_id)
            ).fetchall()
            session.commit()
            return result
    
    def get_all_users(self, type='user') -> list:
        """ Проверка наличия пользователя """
        if type == 'user':
            with self.session.begin() as session:
                result = session.execute(
                    select(Users.telegram_id)
                ).fetchall()
                session.commit()
            return result
        if type == 'channel':
            with self.session.begin() as session:
                result = session.execute(
                    select(Channels.telegram_id)
                ).fetchall()
                session.commit()
            return result
            
    def get_user_channels(self, id: str) -> list:
        with self.session.begin() as session:
            usernames = session.execute(
                select(Channels.username).where(Channels.admin == id)
            ).fetchall()
            session.commit()
            return usernames
        
    def get_primary_key(self, id: str) -> int:
        with self.session.begin() as session:
            prime_key = session.execute(
                select(Users.id).where(Users.telegram_id == id)
            ).fetchall()
            session.commit()
            return prime_key[0][0]
        
    def get_creatives(self, id: str) -> dict:
        """ Достаем все креативы пользователя """
        with self.session.begin() as session:
            creatives = session.execute(
                select(Creatives.__table__).where(Creatives.telegram_id == id)
            ).fetchall()
            session.commit()
            return creatives
        
    def add_creative(self, id: str, text: str, url='', media='') -> None:
        with self.session.begin() as session:
            new_creative = Creatives(telegram_id=id, text=text, url=url, media=media)
            session.add(new_creative)
            session.commit()

    def add_buy(self, id: str, data) -> None:
        with self.session.begin() as session:
            new_buy = Buys(telegram_id=id, channel=data['place'], datetime=data['date'], price=data['price'], creative=data['creative'], admin=data['admin'], link=data['link'], theme=data['theme'])
            session.add(new_buy)
            session.commit()


    '''def get_user_channels(self, tg_id: str, flag=True) -> list:
        with self.session.begin() as session:
            if flag:
                session.execute(
                    update(Users),
                    [
                        {"telegram_id": 1, "auto_reception": 1}
                    ],
                )
            else:
                session.execute(
                    update(Users),
                    [
                        {"telegram_id": 1, "auto_reception": 0}
                    ],
                )'''
