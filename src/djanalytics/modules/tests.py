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
        response = client.get("/httpevent?"+params)
        return response

    def test_db_works(self):
        ''' Test that events and queries work. 
        '''
        c = Client()

        response = c.get('/query/clear_database')
        self.assertEqual(response.content, '"Database clear"')
        response = c.get('/query/event_count')
        response = c.get('/query/event_count')
        self.assertEqual(response.content, "0")
        self.assertEqual(self.send_event(c, {'event':'hello'}).content, "Success")
        response = c.get('/query/event_count')
        self.assertEqual(response.content, "1")
        self.assertEqual(self.send_event(c, {'event':'hello'}).content, "Success")
        response = c.get('/query/event_count')
        self.assertEqual(response.content, "2")
        self.assertEqual(self.send_event(c, {'event':'hello'}).content, "Success")
        response = c.get('/query/event_count')
        self.assertEqual(response.content, "3")
        print "After 3 events: ", response.content
        response = c.get('/query/clear_database')
        self.assertEqual(response.content, '"Database clear"')
    
    def test_per_user_works(self):
        ''' Test that we can have per-user events and queries
        ''' 
        c = Client()
        response = c.get('/query/clear_database')
        self.assertEqual(response.content, '"Database clear"')
        response = c.get('/query/user_event_count?user=alice')
        self.assertEqual(response.content, "0")
        self.assertEqual(self.send_event(c, {'user':'alice'}).content, "Success")
        self.assertEqual(self.send_event(c, {'user':'eve'}).content, "Success")
        self.assertEqual(self.send_event(c, {'user':'alice'}).content, "Success")
        response = c.get('/query/user_event_count?user=alice')
        self.assertEqual(response.content, "2")
        response = c.get('/query/user_event_count?user=eve')
        self.assertEqual(response.content, "1")

    def test_osfs_works(self):
        ''' Make sure there is no file. Create a file. Read it. Erase it. Confirm it is gone. 
        '''
        c = Client()
        self.assertEqual(self.send_event(c, {'event':'pyfstest', 'delete' : 'foo.txt'}).content, "Success")
        response = c.get('/query/readfile?filename=foo.txt')
        self.assertEqual(self.send_event(c, {'event':'pyfstest', 'create' : 'foo.txt', 'contents':'hello'}).content, "Success")
        response = c.get('/query/readfile?filename=foo.txt')
        self.assertEqual(self.send_event(c, {'event':'pyfstest', 'delete' : 'foo.txt'}).content, "Success")
        response = c.get('/query/readfile?filename=foo.txt')

    def test_osfs_forgets(self):
        c = Client()
        def verify(d):
            for key in d:
                r = json.loads(c.get('/query/readfile?filename='+key).content)
                if d[key]:
                    self.assertEqual(r, "hello world!")
                else: 
                    self.assertEqual(r, "File not found")
        self.send_event(c, { 'fs_forgets_contents' : "hello world!", 'filename' : "foo1.txt", 'fs_forgets_expiry' : -5})
        self.send_event(c, { 'fs_forgets_contents' : "hello world!", 'filename' : "foo2.txt", 'fs_forgets_expiry' : -5})
        self.send_event(c, { 'fs_forgets_contents' : "hello world!", 'filename' : "foo3.txt", 'fs_forgets_expiry' : 15})
        self.send_event(c, { 'fs_forgets_contents' : "hello world!", 'filename' : "foo4.txt", 'fs_forgets_expiry' : 15})
        verify({"foo1.txt":True, "foo2.txt":True, "foo3.txt":True, "foo4.txt":True})
        from modulefs.modulefs import expire_objects
        expire_objects()
        verify({"foo1.txt":False, "foo2.txt":False, "foo3.txt":True, "foo4.txt":True})
        self.send_event(c, { 'filename' : "foo3.txt", 'fs_forgets_expiry' : -15})
        self.send_event(c, { 'filename' : "foo4.txt", 'fs_forgets_expiry' : -15})
        expire_objects()
        verify({"foo1.txt":False, "foo2.txt":False, "foo3.txt":False, "foo4.txt":False})

    def test_render(self):
        c = Client()
        self.assertEqual(c.get('/view/hello_template').content, open('modules/testmodule/templates/hello.html').read())

    def test_storage(self):
        from django.contrib.staticfiles import finders
        import os.path

        absolute_path = finders.find('djmodules/testmodule/hello.html')
        assert os.path.exists(absolute_path)

    def test_cache(self):
        c = Client()
        ## Tests fail. In progress
        print "Testing cache..."
        self.assertEqual(self.send_event(c, {'event':'cachetest', 
                                             'key' : 'key1', 
                                             'value': 'value1',
                                             'timeout':30}).content, "Success")
        self.assertEqual(self.send_event(c, {'event':'cachetest', 
                                             'key' : 'key2', 
                                             'value': 'value2',
                                             'timeout':30}).content, "Success")

        response = json.loads(c.get('/query/cache_get?key=key1').content)
        self.assertEqual(response, 'value1')
        response = json.loads(c.get('/query/cache_get?key=key2').content)
        self.assertEqual(response, 'value2')
        self.assertEqual(self.send_event(c, {'event':'cachetest', 
                                             'key' : 'key1', 
                                             'value': 'valuea',
                                             'timeout':30}).content, "Success")
        response = json.loads(c.get('/query/cache_get?key=key1').content)
        self.assertEqual(response, 'valuea')

    def test_event_property(self):
        c = Client()
        self.assertEqual(self.send_event(c, {'event_property_check':True, 
                                             'user' : 'bob'}).content, "Success")
        response = json.loads(c.get('/query/cache_get?key=last_seen_user').content)
        self.assertEqual(response, "bob")
        self.assertEqual(self.send_event(c, {'event_property_check':True, 
                                             'user' : 'joe'}).content, "Success")
        response = json.loads(c.get('/query/cache_get?key=last_seen_user').content)
        self.assertEqual(response, "joe")
        
