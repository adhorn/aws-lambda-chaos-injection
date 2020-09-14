from chaos_lambda import get_config
from ssm_cache import InvalidParameterError
from . import TestBase, ignore_warnings
import unittest
import os
import sys


class TestConfigMethods(TestBase):

    @ignore_warnings
    def _setTestUp(self, subfolder):
        self._setUp(subfolder)
        config = "{ \"delay\": 200, \"isEnabled\": true, \"error_code\": 404, \"exception_msg\": \"I FAILED\", \"rate\": 0.5 }"
        self._create_params(name='test.config', value=config)

    @ignore_warnings
    def test_get_config(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        isEnabled, rate = get_config('isEnabled')
        self.assertEqual(isEnabled, True or False)
        self.assertEqual(rate, 0.5)

    @ignore_warnings
    def test_get_config_delay(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        delay, rate = get_config('delay')
        self.assertEqual(delay, 200)
        self.assertEqual(rate, 0.5)

    @ignore_warnings
    def test_get_config_error_code(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        error_code, rate = get_config('error_code')
        self.assertEqual(error_code, 404)
        self.assertEqual(rate, 0.5)

    @ignore_warnings
    def test_get_config_rate(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        rate, rate = get_config('rate')
        self.assertEqual(rate, 0.5)
        self.assertEqual(rate, 0.5)

    @ignore_warnings
    def test_get_config_bad_key(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        with self.assertRaises(KeyError):
            get_config('dela')


class TestWrongConfigMethods(TestBase):

    @ignore_warnings
    def _setTestUp(self, subfolder):
        self._setUp(subfolder)
        config = "{ \"delay\": 200, \"isEnabled\": true, \"error_code\": 404, \"exception_msg\": \"I FAILED\", \"rate\": 0.5 }"
        self._create_params(name='test.config', value=config)

    @ignore_warnings
    def test_get_config_bad_config(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        os.environ['CHAOS_PARAM'] = 'test.conf'
        with self.assertRaises(InvalidParameterError):
            get_config('delay')


class TestConfigErrorMethods(TestBase):

    @ignore_warnings
    def _setTestUp(self, subfolder):
        self._setUp(subfolder)
        config = "{ \"delay\": 200, \"isEnabled\": true, \"exception_msg\": \"I FAILED\", \"rate\": 0.5 }"
        self._create_params(name='test.config', value=config)

    @ignore_warnings
    def test_get_config(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        with self.assertRaises(KeyError):
            get_config('error_code')


class TestConfigisEnabled(TestBase):

    @ignore_warnings
    def _setTestUp(self, subfolder):
        self._setUp(subfolder)
        config = "{ \"delay\": 200, \"isEnabled\": false, \"exception_msg\": \"I FAILED\", \"rate\": 0.5 }"
        self._create_params(name='test.config', value=config)

    @ignore_warnings
    def test_get_config(self):
        method_name = sys._getframe().f_code.co_name
        self._setTestUp(method_name)
        delay, rate = get_config('error_code')
        self.assertEqual(delay, 0)
        self.assertEqual(rate, 0)


if __name__ == '__main__':
    unittest.main()
