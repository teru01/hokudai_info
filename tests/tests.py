import unittest
from borrowed_books.borrowed_book import decide_loan_period_state, LoanPeriodState
import datetime


class TestBorrowedBook(unittest.TestCase):
    def setUp(self):
        self.today = datetime.date.today()
        self.yesterday = self.today - datetime.timedelta(days=1)
        self.reminder_days = 3
        self.soon_border_day = self.today + datetime.timedelta(days=self.reminder_days)
        self.format_str = "%Y.%m.%d"

    def test_decide_loan_period_state(self):
        self.assertEqual(decide_loan_period_state(self.yesterday.strftime(self.format_str)),
                         LoanPeriodState.OVERDUE)
        self.assertEqual(decide_loan_period_state(self.today.strftime(self.format_str)),
                         LoanPeriodState.SOON)
        self.assertEqual(decide_loan_period_state(self.soon_border_day.strftime(self.format_str)),
                         LoanPeriodState.SOON)

if __name__ == '__main__':
    unittest.main()
