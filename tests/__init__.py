""" Define a test base class for all tests """
import unittest
import os
import sys
import logging
import warnings
import boto3
from ssm_cache import SSMParameter

SSM_CONFIG_FILE = 'test.config'

# directly from here: https://github.com/boto/boto3/issues/521
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)

# pylint: disable=wrong-import-order,wrong-import-position
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def ignore_warnings(test_func):
    def do_test(self, *args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            warnings.simplefilter("ignore", DeprecationWarning)
            test_func(self, *args, **kwargs)
    return do_test


class TestBase(unittest.TestCase):
    """ Base class with mock values and boto3 client """
    os.environ['CHAOS_PARAM'] = SSM_CONFIG_FILE

    ssm_client = boto3.client('ssm')

    @classmethod
    def tearDownClass(cls):
        # pylint: disable=protected-access
        # reset class-level client for other tests
        cls.ssm_client.delete_parameters(Names=[SSM_CONFIG_FILE])
        SSMParameter._ssm_client = None
