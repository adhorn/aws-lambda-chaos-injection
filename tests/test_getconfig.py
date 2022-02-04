from chaos_lambda import get_config, inject_fault
from . import TestBaseSSM, TestBaseAppConfig, TestBaseEmpty, ignore_warnings
import unittest
import os
import sys
import logging
import pytest


@inject_fault
def handler(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }


class TestConfigMethods(TestBaseSSM):

    @ignore_warnings
    def _setTestUp(self, subfolder):
        class_name = self.__class__.__name__
        self._setUp(class_name, subfolder)
        config = "{ \"delay\": 200, \"is_enabled\": true, \"error_code\": 404, \"exception_msg\": \"This is chaos\", \"rate\": 0.5, \"fault_type\": \"latency\"}"
        self._create_params(name=os.environ['CHAOS_PARAM'], value=config)

    @ignore_warnings
    def test_get_config(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        _config = get_config()
        self.assertEqual(_config.get("is_enabled"), True or False)
        self.assertEqual(_config.get("rate"), 0.5)
        self.assertEqual(_config.get("delay"), 200)
        self.assertEqual(_config.get("error_code"), 404)
        self.assertEqual(_config.get("exception_msg"), "This is chaos")
        self.assertEqual(_config.get("fault_type"), "latency")


class TestWrongConfigMethods(TestBaseSSM):

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    @ignore_warnings
    def _setTestUp(self, subfolder):
        class_name = self.__class__.__name__
        self._setUp(class_name, subfolder)
        # is_enable instead of is_enabled
        config = "{ \"is_enable\": true, \"error_code\": 404, \"exception_msg\": \"This is chaos\", \"rate\": 0.5, \"fault_type\": \"latency\"}"
        self._create_params(name=os.environ['CHAOS_PARAM'], value=config)

    @ignore_warnings
    def test_bad_config(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        # os.environ['CHAOS_PARAM'] = 'test.conf'
        with self._caplog.at_level(logging.DEBUG, logger="chaos_lambda"):
            response = handler('foo', 'bar')
            self.assert_(True)
            assert (
                'Injection configuration error - check the configuration is correct' in self._caplog.text
            )
            assert (
                'sleeping now' not in self._caplog.text
            )
            self.assertEqual(
                str(response), "{'statusCode': 200, 'body': 'Hello from Lambda!'}")


class TestConfigNotEnabled(TestBaseSSM):

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    @ignore_warnings
    def _setTestUp(self, subfolder):
        class_name = self.__class__.__name__
        self._setUp(class_name, subfolder)
        config = "{ \"delay\": 200, \"is_enabled\": false, \"error_code\": 404, \"exception_msg\": \"This is chaos\", \"rate\": 0.5, \"fault_type\": \"latency\"}"
        self._create_params(name=os.environ['CHAOS_PARAM'], value=config)

    @ignore_warnings
    def test_config_not_enabled(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        _config = get_config()
        self.assertEqual(_config, 0)
        with self._caplog.at_level(logging.DEBUG, logger="chaos_lambda"):
            response = handler('foo', 'bar')
            self.assert_(True)
            assert (
                'sleeping now' not in self._caplog.text
            )
            self.assertEqual(
                str(response), "{'statusCode': 200, 'body': 'Hello from Lambda!'}")


class TestConfigMissinEnabled(TestBaseSSM):

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    @ignore_warnings
    def _setTestUp(self, subfolder):
        class_name = self.__class__.__name__
        self._setUp(class_name, subfolder)
        # missing is_enabled
        config = "{ \"delay\": 200, \"error_code\": 404, \"exception_msg\": \"This is chaos\", \"rate\": 0.5, \"fault_type\": \"latency\"}"
        self._create_params(name=os.environ['CHAOS_PARAM'], value=config)

    @ignore_warnings
    def test_config_not_enabled(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        _config = get_config()
        self.assertEqual(_config, 0)
        with self._caplog.at_level(logging.DEBUG, logger="chaos_lambda"):
            response = handler('foo', 'bar')
            self.assert_(True)
            assert (
                'Injection configuration error - check the configuration is correct' in self._caplog.text
            )
            assert (
                'sleeping now' not in self._caplog.text
            )
            self.assertEqual(
                str(response), "{'statusCode': 200, 'body': 'Hello from Lambda!'}")


##
TestBaseAppConfig
##


class TestConfigMethodsAC(TestBaseAppConfig):

    @ignore_warnings
    def _setTestUp(self, subfolder):
        class_name = self.__class__.__name__
        self._setUp(class_name, subfolder)
        config = "{\"delay\": 200, \"is_enabled\": true, \"error_code\": 404, \"exception_msg\": \"This is chaos\", \"rate\": 0.5, \"fault_type\": \"latency\"}"
        self._create_params(value=config)

    @ignore_warnings
    def test_get_config(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        _config = get_config()
        self.assertEqual(_config.get("is_enabled"), True or False)
        self.assertEqual(_config.get("rate"), 0.5)
        self.assertEqual(_config.get("delay"), 200)
        self.assertEqual(_config.get("error_code"), 404)
        self.assertEqual(_config.get("exception_msg"), "This is chaos")
        self.assertEqual(_config.get("fault_type"), "latency")


class TestConfigNotEnabledAC(TestBaseAppConfig):

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    @ignore_warnings
    def _setTestUp(self, subfolder):
        class_name = self.__class__.__name__
        self._setUp(class_name, subfolder)
        config = "{ \"delay\": 200, \"is_enabled\": false, \"error_code\": 404, \"exception_msg\": \"This is chaos\", \"rate\": 0.5, \"fault_type\": \"latency\"}"
        self._create_params(value=config)

    @ignore_warnings
    def test_config_not_enabled(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        _config = get_config()
        self.assertEqual(_config, 0)
        with self._caplog.at_level(logging.DEBUG, logger="chaos_lambda"):
            response = handler('foo', 'bar')
            self.assert_(True)
            assert (
                'sleeping now' not in self._caplog.text
            )
            self.assertEqual(
                str(response), "{'statusCode': 200, 'body': 'Hello from Lambda!'}")


class TestConfigMissinEnabledAC(TestBaseAppConfig):

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    @ignore_warnings
    def _setTestUp(self, subfolder):
        class_name = self.__class__.__name__
        self._setUp(class_name, subfolder)
        # mssing is_enabled
        config = "{ \"delay\": 200, \"error_code\": 404, \"exception_msg\": \"This is chaos\", \"rate\": 0.5, \"fault_type\": \"latency\"}"
        self._create_params(value=config)

    @ignore_warnings
    def test_config_not_enabled(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        with self._caplog.at_level(logging.DEBUG, logger="chaos_lambda"):
            response = handler('foo', 'bar')
            self.assert_(True)
            assert (
                'Injection configuration error - check the configuration is correct' in self._caplog.text
            )
            assert (
                'sleeping now' not in self._caplog.text
            )
            self.assertEqual(
                str(response), "{'statusCode': 200, 'body': 'Hello from Lambda!'}")


class TestWrongNoConfigAC(TestBaseEmpty):

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    @ignore_warnings
    def _setTestUp(self, subfolder):
        class_name = self.__class__.__name__
        self._setUp(class_name, subfolder)

    @ignore_warnings
    def test_config_not_enabled(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        self.assertEqual(get_config(), 0)
        with self._caplog.at_level(logging.DEBUG, logger="chaos_lambda"):
            response = handler('foo', 'bar')
            self.assert_(True)
            self.assertEqual(
                str(response), "{'statusCode': 200, 'body': 'Hello from Lambda!'}")


if __name__ == '__main__':
    unittest.main()
