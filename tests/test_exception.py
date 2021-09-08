from chaos_lambda import inject_fault
from . import TestBase, ignore_warnings
import unittest
import sys
import logging
import pytest


@inject_fault
def handler_with_exception(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }


class TestExceptionMethods(TestBase):

    @ignore_warnings
    def _setTestUp(self, subfolder):
        class_name = self.__class__.__name__
        self._setUp(class_name, subfolder)
        config = "{ \"delay\": 400, \"is_enabled\": true, \"error_code\": 404, \"exception_msg\": \"This is chaos\", \"rate\": 1, \"fault_type\": \"exception\"}"
        self._create_params(name='test.config', value=config)

    @ignore_warnings
    def test_get_exception(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        with self.assertRaises(Exception):
            handler_with_exception('foo', 'bar')


class TestExceptionMethodslowrate(TestBase):

    @ignore_warnings
    def _setTestUp(self, subfolder):
        class_name = self.__class__.__name__
        self._setUp(class_name, subfolder)
        config = "{ \"delay\": 400, \"is_enabled\": true, \"error_code\": 404, \"exception_msg\": \"This is chaos\", \"rate\": 0.0000001, \"fault_type\": \"exception\"}"
        self._create_params(name='test.config', value=config)

    @ignore_warnings
    def test_exception_low_rate(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        handler_with_exception('foo', 'bar')
        self.assert_(True)


class TestExceptionMethodsnotenabled(TestBase):

    @ignore_warnings
    def _setTestUp(self, subfolder):
        class_name = self.__class__.__name__
        self._setUp(class_name, subfolder)
        config = "{ \"delay\": 400, \"is_enabled\": false, \"error_code\": 404, \"exception_msg\": \"This is chaos\", \"rate\": 1, \"fault_type\": \"exception\"}"
        self._create_params(name='test.config', value=config)

    @ignore_warnings
    def test_exception_not_enabled(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        handler_with_exception('foo', 'bar')
        self.assert_(True)


class TestExceptionMethodsNoMSG(TestBase):

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    @ignore_warnings
    def _setTestUp(self, subfolder):
        class_name = self.__class__.__name__
        self._setUp(class_name, subfolder)
        config = "{ \"delay\": 400, \"is_enabled\": true, \"error_code\": 404, \"rate\": 1, \"fault_type\": \"exception\"}"
        self._create_params(name='test.config', value=config)

    @ignore_warnings
    def test_no_exception_msg(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        with self._caplog.at_level(logging.DEBUG, logger="chaos_lambda"):
            response = handler_with_exception('foo', 'bar')
            assert (
                'sleeping now' not in self._caplog.text
            )
            assert (
                'Parameter exception_msg is no valid string' in self._caplog.text
            )
        self.assertEqual(
            str(response), "{'statusCode': 200, 'body': 'Hello from Lambda!'}")


if __name__ == '__main__':
    unittest.main()
