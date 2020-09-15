from chaos_lambda import inject_statuscode
from . import TestBase, ignore_warnings
import unittest
import pytest
import logging
import sys


@inject_statuscode
def handler_with_statuscode(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }


@inject_statuscode(error_code=500)
def handler_with_statuscode_arg(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }


class TestStatusCodeMethods(TestBase):

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    @ignore_warnings
    def _setTestUp(self, subfolder):
        class_name = self.__class__.__name__
        self._setUp(class_name, subfolder)
        config = "{ \"delay\": 400, \"isEnabled\": true, \"error_code\": 404, \"exception_msg\": \"I FAILED\", \"rate\": 1 }"
        self._create_params(name='test.config', value=config)

    @ignore_warnings
    def test_get_statuscode(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        with self._caplog.at_level(logging.DEBUG, logger="chaos_lambda"):
            response = handler_with_statuscode('foo', 'bar')
            assert (
                'Injecting Error 404 at a rate of 1' in self._caplog.text
            )
        self.assertEqual(
            str(response), "{'statusCode': 404, 'body': 'Hello from Lambda!'}")

    @ignore_warnings
    def test_get_statuscode_arg(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        with self._caplog.at_level(logging.DEBUG, logger="chaos_lambda"):
            response = handler_with_statuscode_arg('foo', 'bar')
            assert (
                'Injecting Error 500 at a rate of 1' in self._caplog.text
            )
        self.assertEqual(
            str(response), "{'statusCode': 500, 'body': 'Hello from Lambda!'}")


class TestStatusCodeMethodslowrate(TestBase):

    @ignore_warnings
    def _setTestUp(self, subfolder):
        class_name = self.__class__.__name__
        self._setUp(class_name, subfolder)
        config = "{ \"delay\": 400, \"isEnabled\": true, \"error_code\": 404, \"exception_msg\": \"I FAILED\", \"rate\": 0.0000001 }"
        self._create_params(name='test.config', value=config)

    @ignore_warnings
    def test_get_statuscode(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        response = handler_with_statuscode('foo', 'bar')
        self.assertEqual(
            str(response), "{'statusCode': 200, 'body': 'Hello from Lambda!'}")


class TestStatusCodeMethodsnotenabled(TestBase):

    @ignore_warnings
    def _setTestUp(self, subfolder):
        class_name = self.__class__.__name__
        self._setUp(class_name, subfolder)
        config = "{ \"delay\": 400, \"isEnabled\": false, \"error_code\": 404, \"exception_msg\": \"I FAILED\", \"rate\": 1 }"
        self._create_params(name='test.config', value=config)

    @ignore_warnings
    def test_get_statuscode(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        response = handler_with_statuscode('foo', 'bar')
        self.assertEqual(
            str(response), "{'statusCode': 200, 'body': 'Hello from Lambda!'}")

    @ignore_warnings
    def handler_with_statuscode_arg(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        response = handler_with_statuscode_arg('foo', 'bar')
        self.assertEqual(
            str(response), "{'statusCode': 200, 'body': 'Hello from Lambda!'}")


if __name__ == '__main__':
    unittest.main()
