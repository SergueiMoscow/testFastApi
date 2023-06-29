import unittest

from job.ManageData import GetData
from job.DB import DB


class MyTestCase(unittest.TestCase):
    def test_get_vacancies(self):
        result = GetData.get_vacancies('python', None, 'Москва')
        print(result)
        self.assertEqual(True, result is not None)

    def test_select_list(self):
        db = DB()
        result = db.select_list(
            'information_schema.columns',
            where="table_schema = 'public' AND table_name = 'vacancies'",
            field='column_name',
            order=['ordinal_position ASC']
        )
        self.assertEqual(True, isinstance(result, list))


if __name__ == '__main__':
    unittest.main()
