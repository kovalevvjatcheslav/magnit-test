# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from hashlib import sha256
from context_managers import get_cursor, connection


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
        if self._id is None:
            with get_cursor(self._db_conn) as cursor:
                self._id = cursor.execute(f'select id from {self._table_name} where name=?;',
                                          (self.name,)).fetchone()[0]
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
            result = cursor.execute(f'select name from {cls.__name__} where id=?;', (id, )).fetchone()
            return cls(name=result[0], db_conn=db_conn)

    @classmethod
    def get_all(cls, db_conn):
        with get_cursor(db_conn) as cursor:
            for each in cursor.execute(f'select name from {cls.__name__};').fetchall():
                yield cls(name=each[0], db_conn=db_conn)

    def save(self):
        with get_cursor(self._db_conn) as cursor:
            cursor.execute(f'insert into {self._table_name} (name) values (?);', (self.name,))
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
        return self

    @classmethod
    def get_by_id(cls, id, db_conn):
        with get_cursor(db_conn) as cursor:
            result = cursor.execute(f'select name, region_id from {cls.__name__} where id=?;', (id, )).fetchone()
            region = Region.get_by_id(result[1], db_conn)
            return cls(name=result[0], region=region, db_conn=db_conn)

    @classmethod
    def get_by_region_id(cls, region_id, db_conn):
        with get_cursor(db_conn) as cursor:
            for each in cursor.execute(f'select name from {cls.__name__} where region_id=?;', (region_id, )).fetchall():
                region = Region.get_by_id(id=region_id, db_conn=db_conn)
                yield cls(name=each[0], region=region, db_conn=db_conn)


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

    def __hash__(self):
        hash_value = sha256()
        hash_value.update(''.join((self.name, self.surname, self.comment, str(self.patronymic),
                                   str(self.city), str(self.phone), str(self.email))).encode('utf-8'))
        return hash_value.hexdigest()

    def save(self):
        with get_cursor(self._db_conn) as cursor:
            cursor.execute(
                f'''insert into {self._table_name} (name, surname, patronymic, city_id, phone, email, comment, hash) 
                                            values (?,    ?,       ?,          ?,       ?,     ?,     ?,       ?);''',
                (self.name, self.surname, self.patronymic, self.city.id if self.city else None, self.phone, self.email,
                 self.comment, self.__hash__())
            )
            self._id = cursor.execute('select last_insert_rowid();').fetchone()[0]
        return self

    @classmethod
    def get_all(cls, db_conn):
        with get_cursor(db_conn) as cursor:
            for each in cursor.execute(f'select name, surname, comment, patronymic, city_id, phone, email '
                                       f'from {cls.__name__};').fetchall():
                if each[4] is not None:
                    city = City.get_by_id(each[4], db_conn)
                else:
                    city = None
                yield cls(name=each[0], surname=each[1], comment=each[2], db_conn=db_conn, patronymic=each[3],
                          city=city, phone=each[5], email=each[6])

    @property
    def id(self):
        if self._id is None:
            with get_cursor(self._db_conn) as cursor:
                self._id = cursor.execute(f'select id from {self._table_name} where hash=?',
                                          (self.__hash__(), )).fetchone()[0]
        return self._id

    @classmethod
    def remove_by_id(cls, id, db_conn):
        with get_cursor(db_conn) as cursor:
            cursor.execute(f'delete from {cls.__name__} where id=?;', (id, ))


if __name__ == '__main__':
    from itertools import product
    names = ['Бздышек', 'Гадь', 'Герваська']
    surnames = ['Западловский', 'Помидоров', 'Черепопенковский']
    comments = ['Хороший тамада и конкурсы интересные', 'Но очень плохая музыка', 'Дверь мне запили']
    with connection('test_db.sqlite') as conn:
        for each in product(names, surnames, comments):
            Comment(name=each[0], surname=each[1], comment=each[2], db_conn=conn).save()
