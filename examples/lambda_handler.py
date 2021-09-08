import os
from chaos_lambda import (
    inject_fault)

os.environ['CHAOS_PARAM'] = 'chaoslambda.config'


@inject_fault
def handler(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }
