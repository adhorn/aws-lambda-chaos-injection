""" Define a test base class for all tests """
import unittest
import os
import logging
import warnings
import boto3
import placebo
import sys
import time
import random
import string
from ssm_cache import SSMParameter
from aws_lambda_powertools.utilities import parameters


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def randomword(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


logging.getLogger('boto3').setLevel(logging.CRITICAL)

PLACEBO_MODE = os.environ.get('PLACEBO', 'play')


def ignore_warnings(test_func):
    def do_test(self, *args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            warnings.simplefilter("ignore", DeprecationWarning)
            test_func(self, *args, **kwargs)
    return do_test


class TestBaseSSM(unittest.TestCase):
    """ Base class with boto3 client """
    PLACEBO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'placebo'))

    def tearDown(self):
        self.ssm_client.delete_parameters(Names=[os.environ['CHAOS_PARAM']])
        SSMParameter._ssm_client = None
        os.environ.pop('CHAOS_PARAM')

    def _create_params(self, name, value):
        arguments = dict(
            Name=name,
            Value=value,
            Type="String",
            Overwrite=True,
        )
        self.ssm_client.put_parameter(**arguments)

    def _setUp(self, class_name, test_name):
        if os.environ.get('APPCONFIG_APPLICATION'):
            os.environ.pop('APPCONFIG_APPLICATION')
        if os.environ.get('APPCONFIG_CONFIGURATION'):
            os.environ.pop('APPCONFIG_CONFIGURATION')
        if os.environ.get('APPCONFIG_ENVIRONMENT'):
            os.environ.pop('APPCONFIG_ENVIRONMENT')

        SSM_CONFIG_FILE = 'test.config' + randomword(5)
        os.environ['CHAOS_PARAM'] = SSM_CONFIG_FILE
        session = boto3.Session()
        dir_name = os.path.join(self.PLACEBO_PATH, class_name, test_name)
        pill = placebo.attach(session, data_path=os.path.join(self.PLACEBO_PATH, class_name, test_name))

        if PLACEBO_MODE == "record":
            try:
                os.makedirs(dir_name)
            except FileExistsError:
                print("Directory already exists")
            print("Recording")
            pill.record()
        else:
            pill.playback()

        self.ssm_client = session.client('ssm')
        SSMParameter.set_ssm_client(self.ssm_client)


class TestBaseAppConfig(unittest.TestCase):
    """ Base class with boto3 client """
    PLACEBO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'placebo'))

    def tearDown(self):
        # parameters.AppConfigProvider(boto3_session=None)

        self.appconfig_client.delete_hosted_configuration_version(
            ApplicationId=self.appconfig_application_id,
            ConfigurationProfileId=self.appconfig_configprofile_id,
            VersionNumber=int(self.appconfig_configprofile_version)
        )
        self.appconfig_client.delete_configuration_profile(
            ApplicationId=self.appconfig_application_id,
            ConfigurationProfileId=self.appconfig_configprofile_id
        )
        self.appconfig_client.delete_environment(
            ApplicationId=self.appconfig_application_id,
            EnvironmentId=self.appconfig_environment_id
        )
        self.appconfig_client.delete_application(
            ApplicationId=self.appconfig_application_id,
        )
        self.appconfig_client.delete_deployment_strategy(
            DeploymentStrategyId=self.appconfig_deployment_strategy_id
        )
        os.environ.pop('APPCONFIG_APPLICATION')
        os.environ.pop('APPCONFIG_CONFIGURATION')
        os.environ.pop('APPCONFIG_ENVIRONMENT')

    def _create_params(self, value):

        rsp = self.appconfig_client.create_hosted_configuration_version(
            ApplicationId=self.appconfig_application_id,
            ConfigurationProfileId=self.appconfig_configprofile_id,
            Content=bytes(value, 'utf-8'),
            ContentType='application/json'
        )
        self.appconfig_configprofile_version = rsp['VersionNumber']

        rsp = self.appconfig_client.create_deployment_strategy(
            Name='string',
            Description='string',
            DeploymentDurationInMinutes=0,
            FinalBakeTimeInMinutes=0,
            GrowthFactor=100,
            GrowthType='EXPONENTIAL',
            ReplicateTo='NONE',
        )

        self.appconfig_deployment_strategy_id = rsp['Id']

        rsp = self.appconfig_client.start_deployment(
            ApplicationId=self.appconfig_application_id,
            EnvironmentId=self.appconfig_environment_id,
            DeploymentStrategyId=self.appconfig_deployment_strategy_id,
            ConfigurationProfileId=self.appconfig_configprofile_id,
            ConfigurationVersion=self.appconfig_configprofile_version
        )
        self.appconfig_depoyment_number = rsp['DeploymentNumber']

        self.appconfig_depoyment_state = rsp['State']

        while self.appconfig_depoyment_state != 'COMPLETE':
            rsp = self.appconfig_client.get_deployment(
                ApplicationId=self.appconfig_application_id,
                EnvironmentId=self.appconfig_environment_id,
                DeploymentNumber=self.appconfig_depoyment_number
            )
            self.appconfig_depoyment_state = rsp['State']
            time.sleep(5)

    def _setUp(self, class_name, test_name):
        if os.environ.get('CHAOS_PARAM'):
            os.environ.pop('CHAOS_PARAM')

        APPCONFIG_CONFIGURATION = "TestChaosConfig" + randomword(5)
        APPCONFIG_ENVIRONMENT = "Test" + randomword(5)
        APPCONFIG_APPLICATION = "Test-Chaos-Config" + randomword(5)

        os.environ['APPCONFIG_APPLICATION'] = APPCONFIG_APPLICATION
        os.environ['APPCONFIG_CONFIGURATION'] = APPCONFIG_CONFIGURATION
        os.environ['APPCONFIG_ENVIRONMENT'] = APPCONFIG_ENVIRONMENT

        session = boto3.Session()
        dir_name = os.path.join(self.PLACEBO_PATH, class_name, test_name)
        pill = placebo.attach(session, data_path=os.path.join(self.PLACEBO_PATH, class_name, test_name))

        if PLACEBO_MODE == "record":
            try:
                os.makedirs(dir_name)
            except FileExistsError:
                print("Directory already exists")
            print("Recording")
            pill.record()
        else:
            pill.playback()

        self.appconfig_client = session.client('appconfig')
        parameters.AppConfigProvider(boto3_session=session)

        rsp = self.appconfig_client.create_application(
            Name=APPCONFIG_APPLICATION
        )
        self.appconfig_application_id = rsp['Id']

        rsp = self.appconfig_client.create_configuration_profile(
            ApplicationId=self.appconfig_application_id,
            Name=APPCONFIG_CONFIGURATION,
            LocationUri='hosted'
        )
        self.appconfig_configprofile_id = rsp['Id']

        rsp = self.appconfig_client.create_environment(
            ApplicationId=self.appconfig_application_id,
            Name=APPCONFIG_ENVIRONMENT,
        )
        self.appconfig_environment_id = rsp['Id']


class TestBaseEmpty(unittest.TestCase):
    """ Base class with boto3 client """
    PLACEBO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'placebo'))

    def tearDown(self):
        pass

    def _create_params(self, name, value):
        pass

    def _setUp(self, class_name, test_name):
        pass
