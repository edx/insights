"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client

import urllib, json

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

    def send_event(self, client, event):
        ''' Send a JSON event to the server
        '''
        params = urllib.urlencode({'msg':json.dumps(event)})
        response = client.get("/event?"+params)
        return response

    def test_db_works(self):
        ''' Test that events and queries work
        '''
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
        ''' Test that we can have per-user events and queries
        ''' 
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

    def test_osfs_works(self):
        ''' Make sure there is no file. Create a file. Read it. Erase it. Confirm it is gone. 
        '''
        c = Client()
        self.assertEqual(self.send_event(c, {'event':'pyfstest', 'delete' : 'foo.txt'}).content, "Success")
        response = c.get('/query/filename/readfile?filename=foo.txt')
        self.assertEqual(self.send_event(c, {'event':'pyfstest', 'create' : 'foo.txt', 'contents':'hello'}).content, "Success")
        response = c.get('/query/filename/readfile?filename=foo.txt')
        self.assertEqual(self.send_event(c, {'event':'pyfstest', 'delete' : 'foo.txt'}).content, "Success")
        response = c.get('/query/filename/readfile?filename=foo.txt')
