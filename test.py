#   -*- encoding=UTF-8 -*-
import unittest
from nowstagram import  app

class NowstagramTest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        print  'setup'

    def tearDown(self):
        print  'tearDown'
        pass

    def register(self,username,email,password,password_again,next):
        return  self.app.post('/register/',data={'username':username,'email':email,'password':password,'password_again':password_again,'next':next},follow_redirects=True)

    def login(self,username,password,next):
        return  self.app.post('/login/',data={'username':username,'password':password,'next':next},follow_redirects=True)

    def logout(self):
        return  self.app.get('/logout/')

    def test_register_login_logout(self):
        assert self.register('hello','gao_feng_li0@sina.com','123','123','/profile/20/').status_code==200
        assert '首页' in self.app.open('/').data
        r = self.app.open('/profile/20/',follow_redirects=True)
        assert r.status_code == 200
        assert '个人主页' in r.data
        self.logout()
        assert  self.login('hello','123','').status_code == 200
        o = self.app.open('/profile/12/')
        assert '个人主页' in o.data
        self.logout()
        assert  self.login('gao_feng_li0@sina.com','123','').status_code==200
        print  'test_register_login_logout OK'

    def test_profile(self):
        r = self.app.open('/profile/3/', follow_redirects=True)
        assert r.status_code == 200
        assert "password" in r.data
        self.register("hello2", '12344@qq.com',"123",'123','')
        o = self.app.open('/profile/1/', follow_redirects=True)
        assert o.status_code == 200
        # print  o.data o.data就是网页代码
        assert "hello2" in o.data
        print  'test_profile OK'

