import unittest

from job.ManageData import ManageData
from job.DB import DB


class MyTestCase(unittest.TestCase):

    def test_get_regions(self):
        result = ManageData.get_regions()
        print(result)
        self.assertEqual(True, isinstance(result, list))

    def test_get_vacancies(self):
        result = ManageData.get_vacancies('python', None, 'Москва')
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

    def test_get_table_structure(self):
        result = ManageData.get_field_names('vacancies')
        self.assertEqual(True, isinstance(result, list))


if __name__ == '__main__':
    unittest.main()
