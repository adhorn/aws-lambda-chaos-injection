from chaos_lambda import get_config
from ssm_cache import InvalidParameterError
from . import TestBase, ignore_warnings
import unittest
import os
import sys


class TestConfigMethods(TestBase):

    @ignore_warnings
    def _setTestUp(self, subfolder):
        class_name = self.__class__.__name__
        self._setUp(class_name, subfolder)
        config = "{ \"delay\": 200, \"is_enabled\": true, \"error_code\": 404, \"exception_msg\": \"This is chaos\", \"rate\": 0.5, \"fault_type\": \"latency\"}"
        self._create_params(name='test.config', value=config)

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


class TestWrongConfigMethods(TestBase):

    @ignore_warnings
    def _setTestUp(self, subfolder):
        class_name = self.__class__.__name__
        self._setUp(class_name, subfolder)
        config = "{ \"is_enabled\": true, \"error_code\": 404, \"exception_msg\": \"This is chaos\", \"rate\": 0.5, \"fault_type\": \"latency\"}"
        self._create_params(name='test.config', value=config)

    @ignore_warnings
    def test_bad_config(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        os.environ['CHAOS_PARAM'] = 'test.conf'
        with self.assertRaises(InvalidParameterError):
            _config = get_config()
            self.assertNotEqual(_config.get("is_enabled"), True or False)


class TestConfigNotEnabled(TestBase):

    @ignore_warnings
    def _setTestUp(self, subfolder):
        class_name = self.__class__.__name__
        self._setUp(class_name, subfolder)
        config = "{ \"delay\": 200, \"is_enabled\": false, \"error_code\": 404, \"exception_msg\": \"This is chaos\", \"rate\": 0.5, \"fault_type\": \"latency\"}"
        self._create_params(name='test.config', value=config)

    @ignore_warnings
    def test_config_not_enabled(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        _config = get_config()
        self.assertEqual(_config, 0)


if __name__ == '__main__':
    unittest.main()
