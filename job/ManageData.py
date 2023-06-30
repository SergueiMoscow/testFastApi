from sqlalchemy.orm import sessionmaker

from job.models import engine


class ManageData:

    STATUSES = {
        'f': 'FAV',
        'r': 'RES',
        'j': 'REJ',
        'd': 'DEL'
    }

    @classmethod
    def __set_db(cls):
        if cls.session is None:
            _session = sessionmaker(bind=engine)
            cls.session = _session()

    @classmethod
    def get_regions(cls):
        results = cls.session.query(Region.area).order_by(Region.area).all()

        result = db.select('regions', 'TRUE', fields=['area'])
        return result

    @staticmethod
    def get_vacancies(keyword: str, status: str = None, region: str = None):
        where = f"(name LIKE '%{keyword}%' OR " \
                f"requirement like '%{keyword}%' OR " \
                f"responsibility like '%{keyword}%')"
        if status is not None and status != '0':
            where += f" AND id in (SELECT vacancy_id FROM statuses WHERE status = '{status}')"
        if region is not None and region != 'ALL':
            where += f" AND (area LIKE '%{region}' OR address_city LIKE '%{region}')"

        db = DB()
        struct = db.select_list(
            'information_schema.columns',
            where="table_schema = 'public' AND table_name = 'vacancies'",
            field='column_name',
            order=['ordinal_position ASC']
        )
        print(f'Struct: {struct}')
        rows = db.select('vacancies', where, order=['published_at DESC'], limit='FETCH FIRST 10 ROWS ONLY')
        # OFFSET x ROWS FETCH NEXT y ROWS
        result = []
        dict()
        if rows is not None:
            for row in rows:
                dict_to_append = dict(zip(struct, row))
                dict_to_append['published_at'] = f"{dict_to_append['published_at']}"
                result.append(dict_to_append)
            return result
        else:
            return None

    @classmethod
    def add_action(cls, action_type, vacancy_id, text):
        user_id = 0
        db = DB()
        value_status = cls.STATUSES[action_type]
        fld_status = value_status.lower()
        print(f'query: SELECT * FROM get_statuses({user_id}, {vacancy_id})')
        result = db.cursor_to_dict(db.query(f'SELECT * FROM get_statuses({user_id}, {vacancy_id})'))
        new_value = 1
        for row in result:
            print(f'Row: {row}')
            new_value = 1 if row[fld_status] is None or row[fld_status] == 0 else 0
            break
        fields = ['user_id', 'vacancy_id', 'status', 'value']
        values = (0, vacancy_id, value_status, new_value)
        db.insert('statuses', fields, values)
