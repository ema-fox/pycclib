import unittest
import pycclib.cclib
from mock import patch, Mock, call, sentinel, DEFAULT
from datetime import datetime
from time import mktime
from decimal import Decimal
from calendar import timegm

@patch.multiple('pycclib.cclib', Request=DEFAULT, json=DEFAULT)
class Test(unittest.TestCase):
    def setUp (self):
        self.api = pycclib.cclib.API(token=sentinel.token, api_url=sentinel.api_url)
        self.api.requires_token = Mock()

    def assert_requires_token(self):
        self.assertEqual([call()], self.api.requires_token.mock_calls)

    def assert_post(self, json, Request, result, resource, data):
        self.assert_requires_token()
        self.assertEqual([call(token=sentinel.token, api_url=sentinel.api_url),
                          call().post(resource, data)],
                         Request.mock_calls)
        self.assertEqual([call.loads(Request.return_value.post.return_value)],
                         json.mock_calls)
        self.assertEqual(json.loads.return_value, result)

    def assert_get(self, json, Request, result, resource):
        self.assert_requires_token()
        self.assertEqual([call(token=sentinel.token, api_url=sentinel.api_url),
                          call().get(resource)], Request.mock_calls)
        self.assertEqual([call.loads(Request.return_value.get.return_value)], json.mock_calls)
        self.assertEqual(json.loads.return_value, result)

    def assert_put(self, json, Request, result, resource, data):
        self.assert_requires_token()
        self.assertEqual([call(token=sentinel.token, api_url=sentinel.api_url),
                          call().put(resource, data)],
                         Request.mock_calls)
        self.assertEqual([call.loads(Request.return_value.put.return_value)],
                         json.mock_calls)
        self.assertEqual(json.loads.return_value, result)

    def assert_delete(self, Request, resource):
        self.assert_requires_token()
        self.assertEqual([call(token=sentinel.token, api_url=sentinel.api_url), call().delete(resource)], Request.mock_calls)

    def test_create_app1(self, json, Request):
        result = self.api.create_app('foo', sentinel.type, sentinel.repo_type)
        self.assert_post(json, Request, result, '/app/', {'name': 'foo',
                                                          'type': sentinel.type,
                                                          'repository_type': sentinel.repo_type})

    def test_create_app2(self, json, Request):
        result = self.api.create_app('foo', sentinel.type, sentinel.repo_type,
                                     sentinel.buildpack_url)
        self.assert_post(json, Request, result, '/app/',
                         {'name': 'foo',
                          'type': sentinel.type,
                          'repository_type': sentinel.repo_type,
                          'buildpack_url': sentinel.buildpack_url})

    def test_read_apps(self, json, Request):
        result = self.api.read_apps()
        self.assert_get(json, Request, result, '/app/')

    def test_read_app1(self, json, Request):
        result = self.api.read_app('foo')
        self.assert_get(json, Request, result, '/app/foo/')

    def test_read_app2(self, json, Request):
        with self.assertRaisesRegexp(TypeError, 'read_app\(\) takes exactly 2 arguments \(1 given\)'):
            self.api.read_app()

    def test_read_app3(self, json, Request):
        with self.assertRaisesRegexp(TypeError, 'read_app\(\) takes exactly 2 arguments \(3 given\)'):
            self.api.read_app('foo', True)

    def test_delete_app(self, json, Request):
        self.assertEqual(self.api.delete_app('foo'), True)
        self.assert_delete(Request, '/app/foo/')

    def test_create_deployment1(self, json, Request):
        result = self.api.create_deployment('foo')
        self.assert_post(json, Request, result, '/app/foo/deployment/', {})


    def test_create_deployment2(self, json, Request):
        result = self.api.create_deployment('foo', sentinel.depl_name, sentinel.stack)
        self.assert_post(json, Request, result, '/app/foo/deployment/',
                         {'name': sentinel.depl_name, 'stack': sentinel.stack})

    def test_read_deployment(self, json, Request):
        result = self.api.read_deployment('foo', 'bar')
        self.assert_get(json, Request, result, '/app/foo/deployment/bar/')

    def test_read_deployment_users(self, json, Request):
        result = self.api.read_deployment_users('foo', 'bar')
        self.assert_get(json, Request, result, '/app/foo/deployment/bar/user/')

    def test_update_deployment1(self, json, Request):
        result = self.api.update_deployment('foo')
        self.assert_put(json, Request, result, '/app/foo/deployment/default/',
                        {'version': -1})

    def test_update_deployment2(self, json, Request):
        result = self.api.update_deployment('foo', sentinel.version, 'bar',
                                            sentinel.min_boxes, sentinel.max_boxes,
                                            sentinel.bill_account, sentinel.stack)
        self.assert_put(json, Request, result, '/app/foo/deployment/bar/',
                        {'version': sentinel.version,
                         'min_boxes': sentinel.min_boxes, 'max_boxes': sentinel.max_boxes,
                         'billing_account': sentinel.bill_account,
                         'stack': sentinel.stack})

    def test_delete_deployment(self, json, Request):
        self.assertEqual(self.api.delete_deployment('foo', 'bar'), True)
        self.assert_delete(Request, '/app/foo/deployment/bar/')

    def test_create_alias(self, json, Request):
        result = self.api.create_alias('foo', sentinel.alias_name, 'bar')
        self.assert_post(json, Request, result, '/app/foo/deployment/bar/alias/',
                         {'name': sentinel.alias_name})

    def test_read_aliases(self, json, Request):
        result = self.api.read_aliases('foo', 'bar')
        self.assert_get(json, Request, result, '/app/foo/deployment/bar/alias/')

    def test_read_alias(self, json, Request):
        result = self.api.read_alias('foo', 'quux', 'bar')
        self.assert_get(json, Request, result, '/app/foo/deployment/bar/alias/quux/')

    def test_delete_alias(self, json, Request):
        self.assertEqual(self.api.delete_alias('foo', 'quux', 'bar'), True)
        self.assert_delete(Request, '/app/foo/deployment/bar/alias/quux/')

    def test_create_worker1(self, json, Request):
        result = self.api.create_worker('foo', 'bar', sentinel.command)
        self.assert_post(json, Request, result, '/app/foo/deployment/bar/worker/',
                         {'command': sentinel.command})

    def test_create_worker2(self, json, Request):
        result = self.api.create_worker('foo', 'bar', sentinel.command, sentinel.params, sentinel.size)
        self.assert_post(json, Request, result, '/app/foo/deployment/bar/worker/',
                         {'command': sentinel.command, 'params': sentinel.params, 'size': sentinel.size})

    def test_create_worker3(self, json, Request):
        result = self.api.create_worker('foo', 'bar', sentinel.command, size=sentinel.size, params=sentinel.params)
        self.assert_post(json, Request, result, '/app/foo/deployment/bar/worker/',
                         {'command': sentinel.command, 'params': sentinel.params, 'size': sentinel.size})

    def test_create_worker4(self, json, Request):
        result = self.api.create_worker('foo', 'bar', sentinel.command, sentinel.params, size=sentinel.size)
        self.assert_post(json, Request, result, '/app/foo/deployment/bar/worker/',
                         {'command': sentinel.command, 'params': sentinel.params, 'size': sentinel.size})

    def test_create_worker5(self, json, Request):
        result = self.api.create_worker(app_name='foo', deployment_name='bar',
                                        command=sentinel.command, params=sentinel.params, size=sentinel.size)
        self.assert_post(json, Request, result, '/app/foo/deployment/bar/worker/',
                         {'command': sentinel.command, 'params': sentinel.params, 'size': sentinel.size})

    def test_create_worker6(self, json, Request):
        with self.assertRaisesRegexp(TypeError, "create_worker\(\) got an unexpected keyword argument 'not_there'"):
            self.api.create_worker('foo', 'bar', sentinel.command, not_there=sentinel.not_there)

    def test_create_worker7(self, json, Request):
        with self.assertRaisesRegexp(TypeError, "create_worker\(\) got multiple values for keyword argument 'params'"):
            self.api.create_worker('foo', 'bar', sentinel.command, sentinel.params, params=sentinel.params2)
    def test_read_workers(self, json, Request):
        result = self.api.read_workers('foo', 'bar')
        self.assert_get(json, Request, result, '/app/foo/deployment/bar/worker/')

    def test_read_worker(self, json, Request):
        result = self.api.read_worker('foo', 'bar', 'quux')
        self.assert_get(json, Request, result, '/app/foo/deployment/bar/worker/quux/')

    def test_delete_worker(self, json, Request):
        self.assertTrue(self.api.delete_worker('foo', 'bar', 'quux'))
        self.assert_delete(Request, '/app/foo/deployment/bar/worker/quux/')

    def test_create_cronjob(self, json, Request):
        result = self.api.create_cronjob('foo', 'bar', sentinel.url)
        self.assert_post(json, Request, result, '/app/foo/deployment/bar/cron/',
                         {'url': sentinel.url})

    def test_read_cronjobs(self, json, Request):
        result = self.api.read_cronjobs('foo', 'bar')
        self.assert_get(json, Request, result, '/app/foo/deployment/bar/cron/')

    def test_read_cronjob(self, json, Request):
        result = self.api.read_cronjob('foo', 'bar', 'quux')
        self.assert_get(json, Request, result, '/app/foo/deployment/bar/cron/quux/')

    def test_delete_cronjob(self, json, Request):
        self.assertTrue(self.api.delete_cronjob('foo', 'bar', 'quux'))
        self.assert_delete(Request, '/app/foo/deployment/bar/cron/quux/')

    def test_create_addon1(self, json, Request):
        result = self.api.create_addon('foo', 'bar', sentinel.addon_name)
        self.assert_post(json, Request, result, '/app/foo/deployment/bar/addon/',
                         {'addon': sentinel.addon_name})

    def test_create_addon2(self, json, Request):
        result = self.api.create_addon('foo', 'bar', sentinel.addon_name, sentinel.options)
        self.assert_post(json, Request, result, '/app/foo/deployment/bar/addon/',
                         {'addon': sentinel.addon_name, 'options': sentinel.options})

    def test_read_addons1(self, json, Request):
        result = self.api.read_addons()
        self.assertEqual([], self.api.requires_token.mock_calls)
        self.assertEqual([call(token=sentinel.token, api_url=sentinel.api_url),
                          call().get('/addon/')], Request.mock_calls)
        self.assertEqual([call.loads(Request.return_value.get.return_value)], json.mock_calls)
        self.assertEqual(json.loads.return_value, result)

    def test_read_addons2(self, json, Request):
        result = self.api.read_addons('foo', 'bar')
        self.assert_get(json, Request, result, '/app/foo/deployment/bar/addon/')

    def test_read_addon(self, json, Request):
        result = self.api.read_addon('foo', 'bar', 'quux')
        self.assert_get(json, Request, result, '/app/foo/deployment/bar/addon/quux/')

    def test_update_addon(self, json, Request):
        result = self.api.update_addon('foo', 'bar', 'quux', sentinel.new_addon)
        self.assert_put(json, Request, result, '/app/foo/deployment/bar/addon/quux/',
                        {'addon': sentinel.new_addon})

    def test_delete_addon(self, json, Request):
        self.assertTrue(self.api.delete_addon('foo', 'bar', 'quux'))
        self.assert_delete(Request, '/app/foo/deployment/bar/addon/quux/')

    def test_read_app_users(self, json, Request):
        result = self.api.read_app_users('foo')
        self.assert_get(json, Request, result, '/app/foo/user/')

    def test_create_app_user1(self, json, Request):
        result = self.api.create_app_user('foo', sentinel.email)
        self.assert_post(json, Request, result, '/app/foo/user/',
                         {'email': sentinel.email})

    def test_create_app_user2(self, json, Request):
        result = self.api.create_app_user('foo', sentinel.email, sentinel.role)
        self.assert_post(json, Request, result, '/app/foo/user/',
                         {'email': sentinel.email,
                          'role': sentinel.role})

    def test_delete_app_user(self, json, Request):
        self.assertTrue(self.api.delete_app_user('foo', 'masterFoo'))
        self.assert_delete(Request, '/app/foo/user/masterFoo/')

    def test_create_deployment_user1(self, json, Request):
        result = self.api.create_deployment_user('foo', 'bar', sentinel.email)
        self.assert_post(json, Request, result, '/app/foo/deployment/bar/user/',
                         {'email': sentinel.email})

    def test_create_deployment_user2(self, json, Request):
        result = self.api.create_deployment_user('foo', 'bar', sentinel.email,
                                                 sentinel.role)
        self.assert_post(json, Request, result, '/app/foo/deployment/bar/user/',
                         {'email': sentinel.email,
                          'role': sentinel.role})

    def test_delete_deployment_user(self, json, Request):
        self.assertTrue(self.api.delete_deployment_user('foo', 'bar', 'masterFoo'))
        self.assert_delete(Request, '/app/foo/deployment/bar/user/masterFoo/')

    def test_read_users(self, json, Request):
        result = self.api.read_users()
        self.assert_get(json, Request, result, '/user/')

    def test_create_user(self, json, Request):
        result = self.api.create_user(sentinel.name, sentinel.email, sentinel.password)
        self.assertEqual([], self.api.requires_token.mock_calls)
        self.assertEqual([call(api_url=sentinel.api_url),
                          call().post('/user/', {'username': sentinel.name,
                                                 'email': sentinel.email,
                                                 'password': sentinel.password})],
                         Request.mock_calls)

    def test_read_user(self, json, Request):
        result = self.api.read_user('masterFoo')
        self.assert_get(json, Request, result, '/user/masterFoo/')

    def test_update_user1(self, json, Request):
        self.assertFalse(self.api.update_user(sentinel.name))

    def test_update_user2(self, json, Request):
        self.assertTrue(self.api.update_user('masterFoo', sentinel.activation_code))
        self.assertEqual([], self.api.requires_token.mock_calls)
        self.assertEqual([call(api_url=sentinel.api_url),
                          call().put('/user/masterFoo/', {'activation_code': sentinel.activation_code})],
                         Request.mock_calls)

    def test_delete_user(self, json, Request):
        self.assertTrue(self.api.delete_user('masterFoo'))
        self.assert_delete(Request, '/user/masterFoo/')

    def test_read_user_keys(self, json, Request):
        result = self.api.read_user_keys('masterFoo')
        self.assert_get(json, Request, result, '/user/masterFoo/key/')

    def test_read_user_key(self, json, Request):
        result = self.api.read_user_key('masterFoo', 'quux')
        self.assert_get(json, Request, result, '/user/masterFoo/key/quux/')

    def test_create_user_key(self, json, Request):
        result = self.api.create_user_key('masterFoo', sentinel.key)
        self.assert_post(json, Request, result, '/user/masterFoo/key/',
                         {'key': sentinel.key})

    def test_delete_user_key(self, json, Request):
        self.assertTrue(self.api.delete_user_key('masterFoo', 'quux'))
        self.assert_delete(Request, '/user/masterFoo/key/quux/')

    def test_read_log1(self, json, Request):
        result = self.api.read_log('foo', 'bar', 'quux')
        self.assert_get(json, Request, result, '/app/foo/deployment/bar/log/quux/')

    def test_read_log2(self, json, Request):
        test_date = datetime(2013, 3, 12, 2, 11, 1, 99)
        result = self.api.read_log('foo', 'bar', 'quux', test_date)
        self.assert_get(json, Request, result, '/app/foo/deployment/bar/log/quux/?timestamp=%s' % Decimal('{}.{}'.format(int(mktime(test_date.timetuple())), test_date.microsecond)))

    def test_read_log3(self, json, Request):
        test_date = (2013, 3, 12, 2, 11, 1)
        result = self.api.read_log('foo', 'bar', 'quux', test_date)
        self.assert_get(json, Request, result, '/app/foo/deployment/bar/log/quux/?timestamp=%s' % timegm(test_date))

    def test_create_billing_account(self, json, Request):
        result = self.api.create_billing_account('masterFoo', 'quux', sentinel.data)
        self.assert_post(json, Request, result, '/user/masterFoo/billing/quux/',
                         sentinel.data)

    def test_update_billing_account(self, json, Request):
        result = self.api.update_billing_account('masterFoo', 'quux', sentinel.data)
        self.assert_put(json, Request, result, '/user/masterFoo/billing/quux/',
                        sentinel.data)

    def test_get_billing_account(self, json, Request):
        result = self.api.get_billing_accounts('masterFoo')
        self.assert_get(json, Request, result, '/user/masterFoo/billing/')

if __name__ == '__main__':
    unittest.main()
