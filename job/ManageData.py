from sqlalchemy import text, select, inspect
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from job.models import engine, Vacancy, Status


class ManageData:
    STATUSES = {
        'f': 'FAV',
        'r': 'RES',
        'j': 'REJ',
        'd': 'DEL'
    }

    session = None

    @classmethod
    def __set_db(cls):
        if cls.session is None:
            _session = sessionmaker(bind=engine)
            cls.session = _session()

    @classmethod
    def get_regions(cls):
        cls.__set_db()
        return [x.area
                for x in
                cls.session.query(Vacancy.area).order_by(Vacancy.area).distinct()]

    @classmethod
    def get_vacancies(cls, keyword: str, status: str = None, region: str = None, page: int = 1, per_page: int = 10):
        cls.__set_db()
        field_names = cls.get_field_names('vacancies')
        function = text('SELECT *'
                        'FROM list_vacancies('
                        'p_keyword=>:keyword,'
                        'p_region=>:region,'
                        'p_page=>:page,'
                        'p_per_page=>:per_page'
                        ')'
                        )
        params = {
            'keyword': keyword,
            'region': region,
            'page': page,
            'per_page': per_page,
        }
        rows = cls.session.execute(function, params)
        if rows is not None:
            result = [dict(zip(field_names, row)) for row in rows]
            for item in result:
                created_at_value = item.get('published_at')
                if isinstance(created_at_value, datetime):
                    item['published_at'] = created_at_value.strftime('%Y-%m-%d %H:%M:%S')
                print(f'Row: {item}')
            return result
        else:
            return None

    @classmethod
    def add_action(cls, action_type, vacancy_id, comment: str):
        cls.__set_db()
        user_id = 0
        value_status = cls.STATUSES[action_type]
        fld_status = value_status.lower()
        function = text(f'SELECT * FROM get_statuses(p_user=>:user_id, p_vacancy=>:vacancy_id);')
        params = {
            'user_id': user_id,
            'vacancy_id': vacancy_id,
        }
        rows = cls.session.execute(function, params)
        columns = rows.keys()
        print(f'Keys: ', columns)
        row = rows.fetchone()
        row = dict(zip(columns, row))
        print(f'Row: ', row)
        new_value = 1 if row[fld_status] is None or row[fld_status] == 0 else 0
        values = {
            'user_id': user_id,
            'vacancy_id': vacancy_id,
            'status': value_status,
            'value': new_value,
            'comment': comment
        }
        status = Status(**values)
        cls.session.add(status)
        cls.session.commit()

    @classmethod
    def get_field_names(cls, table_name: str):
        inspector = inspect(engine)
        fields = inspector.get_columns(table_name)
        return [x['name'] for x in fields]
