"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

    def test_db_works(self):
        c = Client()

        response = c.get('/query/global/clear_database')
        self.assertEqual(response.content, '"Database clear"')
        response = c.get('/query/global/event_count')
        response = c.get('/query/global/event_count')
        self.assertEqual(response.content, "0")
        response = c.get('/event?msg="Hello"')
        response = c.get('/query/global/event_count')
        self.assertEqual(response.content, "1")
        response = c.get('/event?msg="Hello"')
        response = c.get('/query/global/event_count')
        self.assertEqual(response.content, "2")
        response = c.get('/event?msg="Hello"')
        response = c.get('/query/global/event_count')
        self.assertEqual(response.content, "3")
        print "After 3 events: ", response.content
        response = c.get('/query/global/clear_database')
        self.assertEqual(response.content, '"Database clear"')
    
    def test_per_user_works(self):
        c = Client()
        response = c.get('/query/global/clear_database')
        self.assertEqual(response.content, '"Database clear"')
        response = c.get('/query/user/user_event_count?user=alice')
        self.assertEqual(response.content, "0")
        response = c.get('/event?msg=%7B%22user%22:%22alice%22%7D')
        response = c.get('/event?msg=%7B%22user%22:%22eve%22%7D')
        response = c.get('/event?msg=%7B%22user%22:%22alice%22%7D')
        response = c.get('/query/user/user_event_count?user=alice')
        self.assertEqual(response.content, "2")
        print response
