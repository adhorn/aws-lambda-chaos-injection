from chaos_lambda import inject_exception
from . import TestBase, ignore_warnings
import unittest
import sys


@inject_exception
def handler_with_exception(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }


@inject_exception(exception_type=ValueError)
def handler_with_exception_arg(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }


@inject_exception(exception_type=TypeError, exception_msg='foobar')
def handler_with_exception_arg_2(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }


class TestExceptionMethods(TestBase):

    @ignore_warnings
    def _setTestUp(self, subfolder):
        self._setUp(subfolder)
        config = "{ \"delay\": 400, \"isEnabled\": true, \"error_code\": 404, \"exception_msg\": \"I FAILED\", \"rate\": 1 }"
        self._create_params(name='test.config', value=config)

    @ignore_warnings
    def test_get_exception(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        with self.assertRaises(Exception):
            handler_with_exception('foo', 'bar')

    @ignore_warnings
    def test_get_exception_arg(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        with self.assertRaises(ValueError):
            handler_with_exception_arg('foo', 'bar')

    @ignore_warnings
    def test_handler_with_exception_arg_2(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        with self.assertRaises(TypeError):
            handler_with_exception_arg_2('foo', 'bar')


class TestExceptionMethodslowrate(TestBase):

    @ignore_warnings
    def _setTestUp(self, subfolder):
        self._setUp(subfolder)
        config = "{ \"delay\": 400, \"isEnabled\": true, \"error_code\": 404, \"exception_msg\": \"I FAILED\", \"rate\": 0.0000001 }"
        self._create_params(name='test.config', value=config)

    @ignore_warnings
    def test_get_statuscode(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        handler_with_exception('foo', 'bar')
        self.assert_(True)


class TestExceptionMethodsnotenabled(TestBase):

    @ignore_warnings
    def _setTestUp(self, subfolder):
        self._setUp(subfolder)
        config = "{ \"delay\": 400, \"isEnabled\": false, \"error_code\": 404, \"exception_msg\": \"I FAILED\", \"rate\": 1 }"
        self._create_params(name='test.config', value=config)

    @ignore_warnings
    def test_get_statuscode(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        handler_with_exception('foo', 'bar')
        self.assert_(True)

    @ignore_warnings
    def test_handler_with_exception_arg_2(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        handler_with_exception_arg_2('foo', 'bar')
        self.assert_(True)


if __name__ == '__main__':
    unittest.main()
