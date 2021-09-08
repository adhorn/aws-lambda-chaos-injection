from chaos_lambda import inject_fault
from . import TestBase, ignore_warnings
import unittest
import logging
import pytest
import sys


@inject_fault
def handler(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }


class TestDelayMethods(TestBase):

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    @ignore_warnings
    def _setTestUp(self, subfolder):
        class_name = self.__class__.__name__
        self._setUp(class_name, subfolder)
        config = "{ \"delay\": 400, \"is_enabled\": true, \"error_code\": 404, \"exception_msg\": \"This is chaos\", \"rate\": 1, \"fault_type\": \"latency\"}"
        self._create_params(name='test.config', value=config)

    @ignore_warnings
    def test_get_delay(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        with self._caplog.at_level(logging.DEBUG, logger="chaos_lambda"):
            response = handler('foo', 'bar')
            assert (
                'Injecting 400 ms of delay with a rate of 1' in self._caplog.text
            )
            assert (
                'sleeping now' in self._caplog.text
            )
        self.assertEqual(
            str(response), "{'statusCode': 200, 'body': 'Hello from Lambda!'}")


class TestDelayMethodsnotEnabled(TestBase):

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    @ignore_warnings
    def _setTestUp(self, subfolder):
        class_name = self.__class__.__name__
        self._setUp(class_name, subfolder)
        config = "{ \"delay\": 400, \"is_enabled\": false, \"error_code\": 404, \"exception_msg\": \"This is chaos\", \"rate\": 1, \"fault_type\": \"latency\"}"
        self._create_params(name='test.config', value=config)

    @ignore_warnings
    def test_delay_not_enabled(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        with self._caplog.at_level(logging.DEBUG, logger="chaos_lambda"):
            response = handler('foo', 'bar')
            assert (
                len(self._caplog.text) == 0
            )
            assert (
                'sleeping now' not in self._caplog.text
            )
        self.assertEqual(
            str(response), "{'statusCode': 200, 'body': 'Hello from Lambda!'}")


class TestDelayMethodslowrate(TestBase):

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    @ignore_warnings
    def _setTestUp(self, subfolder):
        class_name = self.__class__.__name__
        self._setUp(class_name, subfolder)
        config = "{ \"delay\": 400, \"is_enabled\": true, \"error_code\": 404, \"exception_msg\": \"This is chaos\", \"rate\": 0.000001, \"fault_type\": \"latency\"}"
        self._create_params(name='test.config', value=config)

    @ignore_warnings
    def test_delay_low_rate(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        with self._caplog.at_level(logging.DEBUG, logger="chaos_lambda"):
            response = handler('foo', 'bar')
            assert (
                'sleeping now' not in self._caplog.text
            )
        self.assertEqual(
            str(response), "{'statusCode': 200, 'body': 'Hello from Lambda!'}")


class TestDelayEnabledNoDelay(TestBase):

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    @ignore_warnings
    def _setTestUp(self, subfolder):
        class_name = self.__class__.__name__
        self._setUp(class_name, subfolder)
        config = "{ \"delay\": 0, \"is_enabled\": true, \"error_code\": 404, \"exception_msg\": \"This is chaos\", \"rate\": 0.000001, \"fault_type\": \"latency\"}"
        self._create_params(name='test.config', value=config)

    @ignore_warnings
    def test_delay_zero(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        with self._caplog.at_level(logging.DEBUG, logger="chaos_lambda"):
            response = handler('foo', 'bar')
            assert (
                'sleeping now' not in self._caplog.text
            )
        self.assertEqual(
            str(response), "{'statusCode': 200, 'body': 'Hello from Lambda!'}")


class TestDelayEnabledDelayNotInt(TestBase):

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    @ignore_warnings
    def _setTestUp(self, subfolder):
        class_name = self.__class__.__name__
        self._setUp(class_name, subfolder)
        config = "{ \"delay\": \"boo\", \"is_enabled\": true, \"error_code\": 404, \"exception_msg\": \"This is chaos\", \"rate\": 0.000001, \"fault_type\": \"latency\"}"
        self._create_params(name='test.config', value=config)

    @ignore_warnings
    def test_delay_not_int(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        with self._caplog.at_level(logging.DEBUG, logger="chaos_lambda"):
            response = handler('foo', 'bar')
            assert (
                'sleeping now' not in self._caplog.text
            )
            assert (
                'Parameter delay is no valid int' in self._caplog.text
            )   
        self.assertEqual(
            str(response), "{'statusCode': 200, 'body': 'Hello from Lambda!'}")


if __name__ == '__main__':
    unittest.main()
