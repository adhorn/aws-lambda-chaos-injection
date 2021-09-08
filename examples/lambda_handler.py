import os
from chaos_lambda import (
    inject_fault)

# For SSM e.g.
os.environ['CHAOS_PARAM'] = 'chaoslambda.config'

# For AppConfig e.g.
os.environ['APPCONFIG_APPLICATION'] = "TestChaosConfig"
os.environ['APPCONFIG_ENVIRONMENT'] = "TestEnv"
os.environ['APPCONFIG_CONFIGURATION'] = "TestChaosConfig"


@inject_fault
def handler(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }
