""" Define a test base class for all tests """
import unittest
import os
import logging
import warnings
import boto3
from ssm_cache import SSMParameter
import placebo
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

SSM_CONFIG_FILE = 'test.config'

logging.getLogger('boto3').setLevel(logging.CRITICAL)


def ignore_warnings(test_func):
    def do_test(self, *args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            warnings.simplefilter("ignore", DeprecationWarning)
            test_func(self, *args, **kwargs)
    return do_test


class TestBase(unittest.TestCase):
    """ Base class with boto3 client """
    PLACEBO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'placebo'))

    def tearDown(self):
        self.ssm_client.delete_parameters(Names=[SSM_CONFIG_FILE])
        SSMParameter._ssm_client = None

    def _create_params(self, name, value):
        arguments = dict(
            Name=name,
            Value=value,
            Type="String",
            Overwrite=True,
        )
        self.ssm_client.put_parameter(**arguments)

    def _setUp(self, subfolder):
        os.environ['CHAOS_PARAM'] = SSM_CONFIG_FILE
        session = boto3.Session()
        # pill = placebo.attach(session, data_path=self.PLACEBO_PATH)
        # pill = placebo.attach(session, data_path=os.path.join(self.PLACEBO_PATH, subfolder))
        # pill.playback()
        # pill.record(services='ssm')
        self.ssm_client = session.client('ssm')
        SSMParameter.set_ssm_client(self.ssm_client)
