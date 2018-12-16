try:
    from .stat import *
except SystemError:
    from stat import *

import unittest

class TestStat(unittest.TestCase):

    def test_year_to_century(self):
        self.assertEqual(year_to_century(1000), 10)
        self.assertEqual(year_to_century(1001), 10)
        self.assertEqual(year_to_century(1099), 10)
        self.assertEqual(year_to_century(1100), 11)

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    unittest.main()


