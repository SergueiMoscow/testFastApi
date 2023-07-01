import unittest

from job.ManageData import ManageData


class MyTestCase(unittest.TestCase):

    def test_get_regions(self):
        result = ManageData.get_regions()
        print(result)
        self.assertEqual(True, isinstance(result, list))

    def test_get_vacancies(self):
        result = ManageData.get_vacancies('python', None, 'Москва')
        print(result)
        self.assertEqual(True, result is not None)

    def test_get_table_structure(self):
        result = ManageData.get_field_names('vacancies')
        self.assertEqual(True, isinstance(result, list))


if __name__ == '__main__':
    unittest.main()
