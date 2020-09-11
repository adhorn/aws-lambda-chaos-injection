from chaos_lambda import inject_delay
from test_abstract import client, ignore_warnings
import unittest
import os
import warnings
import boto3
import logging
import pytest


@inject_delay
def handler(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }


@inject_delay(delay=1000)
def handler_with_delay_arg(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }


@inject_delay(delay=0)
def handler_with_delay_zero(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }


class TestDelayMethods(unittest.TestCase):

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    @ignore_warnings
    def setUp(self):
        os.environ['CHAOS_PARAM'] = 'test.config'
        client.put_parameter(
            Value="{ \"delay\": 400, \"isEnabled\": true, \"error_code\": 404, \"exception_msg\": \"I FAILED\", \"rate\": 1 }",
            Name='test.config',
            Type='String',
            Overwrite=True
        )

    @ignore_warnings
    def tearDown(self):
        client.delete_parameters(Names=['test.config'])

    @ignore_warnings
    def test_get_delay(self):
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

    @ignore_warnings
    def test_get_delay_arg(self):
        with self._caplog.at_level(logging.DEBUG, logger="chaos_lambda"):
            response = handler_with_delay_arg('foo', 'bar')
            assert (
                'Injecting 1000 ms of delay with a rate of 1' in self._caplog.text
            )
            assert (
                'sleeping now' in self._caplog.text
            )
        self.assertEqual(
            str(response), "{'statusCode': 200, 'body': 'Hello from Lambda!'}")

    @ignore_warnings
    def test_get_delay_zero(self):
        with self._caplog.at_level(logging.DEBUG, logger="chaos_lambda"):
            response = handler_with_delay_zero('foo', 'bar')
            assert (
                'Injecting 0 ms of delay with a rate of 1' in self._caplog.text
            )
            assert (
                'sleeping now' not in self._caplog.text
            )
        self.assertEqual(
            str(response), "{'statusCode': 200, 'body': 'Hello from Lambda!'}")


class TestDelayMethodsnotEnabled(unittest.TestCase):

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    @ignore_warnings
    def setUp(self):
        os.environ['CHAOS_PARAM'] = 'test.config'
        client.put_parameter(
            Value="{ \"delay\": 0, \"isEnabled\": false, \"error_code\": 404, \"exception_msg\": \"I FAILED\", \"rate\": 1 }",
            Name='test.config',
            Type='String',
            Overwrite=True
        )

    @ignore_warnings
    def tearDown(self):
        client.delete_parameters(Names=['test.config'])

    @ignore_warnings
    def test_get_delay(self):
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

    @ignore_warnings
    def test_get_delay_arg(self):
        with self._caplog.at_level(logging.DEBUG, logger="chaos_lambda"):
            response = handler_with_delay_arg('foo', 'bar')
            assert (
                len(self._caplog.text) == 0
            )
            assert (
                'sleeping now' not in self._caplog.text
            )
        self.assertEqual(
            str(response), "{'statusCode': 200, 'body': 'Hello from Lambda!'}")

    @ignore_warnings
    def test_get_delay_zero(self):
        with self._caplog.at_level(logging.DEBUG, logger="chaos_lambda"):
            response = handler_with_delay_zero('foo', 'bar')
            assert (
                len(self._caplog.text) == 0
            )
            assert (
                'sleeping now' not in self._caplog.text
            )
        self.assertEqual(
            str(response), "{'statusCode': 200, 'body': 'Hello from Lambda!'}")


class TestDelayMethodslowrate(unittest.TestCase):

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    @ignore_warnings
    def setUp(self):
        os.environ['CHAOS_PARAM'] = 'test.config'
        client.put_parameter(
            Value="{ \"delay\": 500, \"isEnabled\": true, \"error_code\": 404, \"exception_msg\": \"I FAILED\", \"rate\": 0.000001 }",
            Name='test.config',
            Type='String',
            Overwrite=True
        )

    @ignore_warnings
    def tearDown(self):
        client.delete_parameters(Names=['test.config'])

    @ignore_warnings
    def test_get_delay(self):
        with self._caplog.at_level(logging.DEBUG, logger="chaos_lambda"):
            response = handler('foo', 'bar')
            assert (
                'sleeping now' not in self._caplog.text
            )
        self.assertEqual(
            str(response), "{'statusCode': 200, 'body': 'Hello from Lambda!'}")


class TestDelayEnabledNoDelay(unittest.TestCase):
    
    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    @ignore_warnings
    def setUp(self):
        os.environ['CHAOS_PARAM'] = 'test.config'
        client.put_parameter(
            Value="{ \"delay\": 0, \"isEnabled\": true, \"error_code\": 404, \"exception_msg\": \"I FAILED\", \"rate\": 0.000001 }",
            Name='test.config',
            Type='String',
            Overwrite=True
        )

    @ignore_warnings
    def tearDown(self):
        client.delete_parameters(Names=['test.config'])

    @ignore_warnings
    def test_get_delay(self):
        with self._caplog.at_level(logging.DEBUG, logger="chaos_lambda"):
            response = handler('foo', 'bar')
            assert (
                'sleeping now' not in self._caplog.text
            )
        self.assertEqual(
            str(response), "{'statusCode': 200, 'body': 'Hello from Lambda!'}")



if __name__ == '__main__':
    unittest.main()
