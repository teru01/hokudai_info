import unittest
from borrowed_books.borrowed_book import is_due_back_soon
import datetime


class TestIsDueBackSoon(unittest.TestCase):
    def setUp(self):
        self.today = datetime.datetime.today()

    def test_is_due_back_soon(self):
        self.assertTrue(is_due_back_soon(self.today))
