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

    def test_auth(self):
        ''' Inject a dummy settings.DJA_AUTH into auth. 
        '''
        import auth
        temp = auth.settings

        def plus1dec(f):
            def p1(x):
                return f(x)+1
            return p1

        def minus1dec(f):
            def p1(x):
                return f(x)-1
            return p1

        class S(object):
            DJA_AUTH = {'f1' : plus1dec, 
                        'g.*' : minus1dec}
        
        auth.settings = S
        
        @auth.auth
        def f1(x):
            return x**2
        
        @auth.auth
        def f2(x):
            return x**2

        @auth.auth
        def g2(x):
            return x**2

        self.assertEqual(f1(7), 50)
        self.assertEqual(f2(7), 49)
        self.assertEqual(g2(7), 48)

        auth.settings = temp
    
    def test_urls(self):
        from django.test.client import Client
        c = Client()
        urls = ["/event_properties", "/schema"]
        for url in urls: 
            response = c.get(url)
            self.assertEqual(response.status_code, 200)
