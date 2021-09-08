from chaos_lambda import inject_fault
from . import TestBase, ignore_warnings
import unittest
import pytest
import logging
import sys


@inject_fault
def handler_with_statuscode(event, context):
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
        config = "{ \"delay\": 400, \"is_enabled\": true, \"error_code\": 404, \"exception_msg\": \"This is chaos\", \"rate\": 1, \"fault_type\": \"status_code\"}"
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


class TestStatusCodeMethodslowrate(TestBase):

    @ignore_warnings
    def _setTestUp(self, subfolder):
        class_name = self.__class__.__name__
        self._setUp(class_name, subfolder)
        config = "{ \"delay\": 400, \"is_enabled\": true, \"error_code\": 404, \"exception_msg\": \"This is chaos\", \"rate\": 0.0000001, \"fault_type\": \"status_code\"}"
        self._create_params(name='test.config', value=config)

    @ignore_warnings
    def test_statuscode_low_rate(self):
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
        config = "{ \"delay\": 400, \"is_enabled\": false, \"error_code\": 404, \"exception_msg\": \"This is chaos\", \"rate\": 1, \"fault_type\": \"status_code\"}"
        self._create_params(name='test.config', value=config)

    @ignore_warnings
    def test_statuscode_not_enabled(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        response = handler_with_statuscode('foo', 'bar')
        self.assertEqual(
            str(response), "{'statusCode': 200, 'body': 'Hello from Lambda!'}")


class TestStatusCodeNoError_Code(TestBase):

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    @ignore_warnings
    def _setTestUp(self, subfolder):
        class_name = self.__class__.__name__
        self._setUp(class_name, subfolder)
        config = "{ \"delay\": 400, \"is_enabled\": false, \"exception_msg\": \"This is chaos\", \"rate\": 1, \"fault_type\": \"status_code\"}"
        self._create_params(name='test.config', value=config)

    @ignore_warnings
    def test_statuscode_not_enabled(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        with self._caplog.at_level(logging.DEBUG, logger="chaos_lambda"):
            response = handler_with_statuscode('foo', 'bar')
            assert (
                'sleeping now' not in self._caplog.text
            )
        self.assertEqual(
            str(response), "{'statusCode': 200, 'body': 'Hello from Lambda!'}")


class TestErrorCodeNotValid(TestBase):

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    @ignore_warnings
    def _setTestUp(self, subfolder):
        class_name = self.__class__.__name__
        self._setUp(class_name, subfolder)
        config = "{ \"delay\": 400, \"is_enabled\": true, \"exception_msg\": \"This is chaos\", \"rate\": 1, \"error_code\": \"error\", \"fault_type\": \"status_code\"}"
        self._create_params(name='test.config', value=config)

    @ignore_warnings
    def test_errorcode_not_valid(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        with self._caplog.at_level(logging.DEBUG, logger="chaos_lambda"):
            response = handler_with_statuscode('foo', 'bar')
            assert (
                'sleeping now' not in self._caplog.text
            )
            assert (
                'Parameter error_code is no valid int' in self._caplog.text
            )
        self.assertEqual(
            str(response), "{'statusCode': 200, 'body': 'Hello from Lambda!'}")


if __name__ == '__main__':
    unittest.main()
