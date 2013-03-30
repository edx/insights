"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import time

from django.test import TestCase

from decorators import memoize_query

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

    def __init__(self, arg):
        TestCase.__init__(self, arg)
        self.calls =  0

    def test_memoize(self):
        self.calls = 0
        @memoize_query(0.05)
        def double_trouble(x):
            self.calls = self.calls + 1
            return 2*x

        self.assertEqual(double_trouble(2), 4)
        self.assertEqual(double_trouble(4), 8)
        self.assertEqual(double_trouble(2), 4)
        self.assertEqual(double_trouble(4), 8)
        self.assertEqual(self.calls, 2)
        time.sleep(0.1)
        self.assertEqual(double_trouble(2), 4)
        self.assertEqual(double_trouble(4), 8)
        self.assertEqual(double_trouble(2), 4)
        self.assertEqual(double_trouble(4), 8)
        self.assertEqual(self.calls, 4)
