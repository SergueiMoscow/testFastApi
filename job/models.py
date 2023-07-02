from contextlib import contextmanager

from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, func, DateTime, Boolean, Text, Index, Date, TIMESTAMP, \
    text, inspect, Inspector, Table
import os
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()
str_engine = f"postgresql://{os.getenv('pgsql_user')}:{os.getenv('pgsql_password')}@" \
             f"{os.getenv('pgsql_host')}/{os.getenv('pgsql_db')}"
engine = create_engine(str_engine)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False)
    first_name = Column(String, nullable=True, default=None)
    last_name = Column(String, nullable=True, default=None)
    phone = Column(String, nullable=True, default=None)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), index=True)
    deleted_at = Column(DateTime, index=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    last_login = Column(DateTime, index=True, nullable=True, default=None)
    reset_password_token = Column(String, unique=True, default=None, nullable=True)
    email_confirmed = Column(Boolean, default=False)
    need_refresh_token = Column(Boolean, default=False)


class Vacancy(Base):
    __tablename__ = 'vacancies'

    id = Column(Integer, primary_key=True)
    source = Column(String, nullable=False)
    source_id = Column(String(40), nullable=False, default='')
    name = Column(String(100), nullable=False)
    area = Column(String(50))
    salary_from = Column(Integer, default=0)
    salary_to = Column(Integer, default=0)
    salary_currency = Column(String(3), default='RUR')
    status = Column(String(20))
    address_city = Column(String(50))
    address_street = Column(String(255))
    address_metro = Column(String(30))
    published_at = Column(DateTime(timezone=True))
    url = Column(String(255))
    url_api = Column(String(255))
    employer_id = Column(String(40))
    requirement = Column(Text)
    responsibility = Column(Text)
    experience = Column(String(50))
    employment = Column(String(50))

    __table_args__ = (
        Index('ix_vacancy_soucre_id', 'source', 'source_id'),
        Index('ix_vacancy_area', 'area'),
        Index('ix_salary_from', 'salary_from'),
        {'schema': 'public'}
    )

    Index('ix_vacancy_soucre_id', 'source', 'source_id')
    Index('ix_vacancy_area', 'area')
    Index('ix_salary_from', 'salary_from')


class Status(Base):
    __tablename__ = 'statuses'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    vacancy_id = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False)
    value = Column(String(1), nullable=False, default='')
    comment = Column(Text, nullable=True, default='')
    created_at = Column(DateTime, server_default=func.now(), index=True)

    Index('statuses_id', 'id', postgresql_using='btree'),
    Index('statuses_user', 'user_id', postgresql_using='btree')


class RegionView:
    @staticmethod
    def create_view(engine):
        with engine.connect() as connection:
            query = text(
                '''
                CREATE OR REPLACE VIEW regions AS
                SELECT area, cnt
                FROM your_table_name;
                '''
            )
            connection.execute(query)


def get_db_objects_names(object_type: str) -> list:
    """Возвращает список объектов (функций или представлений), описанных SQL кодом в папке db

    Args:
        object_type: 'f' - для функций, 'v' - для представлений.
    """
    db_directory = os.path.join(os.path.dirname(os.getcwd()), 'db')
    filtered_files = [
        file.replace(f"{object_type}_", "").replace(".sql", "")
        for file in os.listdir(db_directory)
        if file.startswith(f'{object_type}_') and file.endswith('.sql')
    ]
    return filtered_files


@contextmanager
def session_scope():
    _session = sessionmaker(bind=engine)
    session = _session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def check_views():
    """Проверка существования представлений.
    Если не существует, создаёт его, как описано в файле db/v_*.sql.
    """
    views = get_db_objects_names('v')
    inspector = inspect(engine)
    for view in views:
        if not inspector.has_table(view, schema='public', type='view'):
            file_name = os.path.join(os.path.dirname(os.getcwd()), 'db', f'v_{view}.sql')
            if os.path.exists(file_name):
                with open(file_name) as file:
                    sql_query = file.read()
                try:
                    with session_scope() as session:
                        session.execute(text(sql_query))
                except Exception as e:
                    print(f"Ошибка выполнения SQL-запроса для представления {view}: {str(e)}")
            else:
                print(f"Файл {file_name} не существует.")


def check_functions():
    """Проверка существования функций в БД, если функция не существует, создает её
    как описано в файле db/f_*.sql.
    """
    functions = get_db_objects_names('f')
    for func_name in functions:
        _session = sessionmaker(bind=engine)
        session = _session()
        query = f"""
                SELECT routine_name
                FROM information_schema.routines
                WHERE routine_name = '{func_name}'
                """
        result = session.execute(text(query)).fetchone()
        if result is None:
            with open(f'../db/f_{func_name}.sql', 'r') as f:
                sql_create_function = f.read()
                created = session.execute(text(sql_create_function))
                session.commit()


if __name__ == '__main__':
    """В случае запуска непосредственно этого файла создаются все таблицы, представления и функции.
    """
    Base.metadata.create_all(engine)
    check_functions()
    check_views()
