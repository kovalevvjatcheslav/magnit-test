# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from context_managers import get_cursor


class BaseModel(metaclass=ABCMeta):
    __slots__ = ('name', '_table_name', '_id', '_db_conn')

    @abstractmethod
    def __init__(self, name, db_conn):
        self.name = name
        self._table_name = type(self).__name__
        self._id = None
        self._db_conn = db_conn

    @property
    def id(self):
        return self._id


class Region(BaseModel):
    __slots__ = ()

    def __init__(self, name, db_conn):
        super().__init__(name, db_conn)

    def __str__(self):
        return f'{self.name} {self.id}'

    @classmethod
    def get_by_id(cls, id, db_conn):
        with get_cursor(db_conn) as cursor:
            row = cursor.execute(f'select name, id from {cls.__name__} where id=?;', (id, )).fetchone()
            region = cls(name=row[0], db_conn=db_conn)
            region._id = row[1]
            return region

    @classmethod
    def get_all(cls, db_conn):
        with get_cursor(db_conn) as cursor:
            for row in cursor.execute(f'select name, id from {cls.__name__};').fetchall():
                region = cls(name=row[0], db_conn=db_conn)
                region._id = row[1]
                yield region

    def save(self):
        with get_cursor(self._db_conn) as cursor:
            cursor.execute(f'insert into {self._table_name} (name) values (?);', (self.name,))
            self._id = cursor.execute('select last_insert_rowid();').fetchone()[0]
        return self


class City(BaseModel):
    __slots__ = ('region', )

    def __init__(self, name, region, db_conn):
        super().__init__(name, db_conn)
        self.region = region

    def __str__(self):
        return f'{self.name} {self.id}'

    def save(self):
        with get_cursor(self._db_conn) as cursor:
            cursor.execute(
                f'insert into {self._table_name} (name, region_id) values (?, ?);',
                (self.name, self.region.id)
            )
            self._id = cursor.execute('select last_insert_rowid();').fetchone()[0]
        return self

    @classmethod
    def get_by_id(cls, id, db_conn):
        with get_cursor(db_conn) as cursor:
            row = cursor.execute(f'select name, region_id, id from {cls.__name__} where id=?;', (id, )).fetchone()
            region = Region.get_by_id(row[1], db_conn)
            city = cls(name=row[0], region=region, db_conn=db_conn)
            city._id = row[2]
        return city

    @classmethod
    def get_all(cls, db_conn):
        with get_cursor(db_conn) as cursor:
            for row in cursor.execute(f'select name, region_id, id from {cls.__name__};').fetchall():
                region = Region.get_by_id(id=row[1], db_conn=db_conn)
                city = cls(name=row[0], region=region, db_conn=db_conn)
                city._id = row[2]
                yield city

    @classmethod
    def get_by_region_id(cls, region_id, db_conn):
        with get_cursor(db_conn) as cursor:
            for row in cursor.execute(f'select name, id from {cls.__name__} where region_id=?;', (region_id, )).fetchall():
                region = Region.get_by_id(id=region_id, db_conn=db_conn)
                city = cls(name=row[0], region=region, db_conn=db_conn)
                city._id = row[1]
                yield city


class Comment(BaseModel):
    __slots__ = ('surname', 'comment', 'patronymic', 'city', 'phone', 'email')

    def __init__(self, name, surname, comment, db_conn, patronymic=None, city=None, phone=None, email=None):
        super().__init__(name, db_conn)
        self.surname = surname
        self.comment = comment
        self.patronymic = patronymic
        self.city = city
        self.phone = phone
        self.email = email

    def save(self):
        with get_cursor(self._db_conn) as cursor:
            cursor.execute(
                f'''insert into {self._table_name} (name, surname, patronymic, city_id, phone, email, comment) 
                                            values (?,    ?,       ?,          ?,       ?,     ?,     ?);''',
                (self.name, self.surname, self.patronymic, self.city.id if self.city else None, self.phone, self.email,
                 self.comment)
            )
            self._id = cursor.execute('select last_insert_rowid();').fetchone()[0]
        return self

    @classmethod
    def get_all(cls, db_conn):
        with get_cursor(db_conn) as cursor:
            for row in cursor.execute(f'select name, surname, comment, patronymic, city_id, phone, email, id '
                                      f'from {cls.__name__};').fetchall():
                if row[4] is not None:
                    city = City.get_by_id(row[4], db_conn)
                else:
                    city = None
                comment = cls(name=row[0], surname=row[1], comment=row[2], db_conn=db_conn, patronymic=row[3],
                              city=city, phone=row[5], email=row[6])
                comment._id = row[7]
                yield comment

    @classmethod
    def get_by_region_id(cls, region_id, db_conn):
        with get_cursor(db_conn) as cursor:
            for row in cursor.execute('''select Comment.name, Comment.surname, Comment.comment, Comment.patronymic,
                                                City.id, Comment.phone, Comment.email, Comment.id from Comment 
                                                inner join City on Comment.city_id=City.id and City.region_id=?;''',
                                      (region_id, )).fetchall():
                city = City.get_by_id(row[4], db_conn)
                comment = cls(name=row[0], surname=row[1], comment=row[2], db_conn=db_conn, patronymic=row[3],
                              city=city, phone=row[5], email=row[6])
                comment._id = row[7]
                yield comment

    @classmethod
    def remove_by_id(cls, id, db_conn):
        with get_cursor(db_conn) as cursor:
            cursor.execute(f'delete from {cls.__name__} where id=?;', (id, ))
