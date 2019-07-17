import os
from chaos_lambda import (
    inject_delay, inject_exception, inject_statuscode, SessionWithDelay)

os.environ['CHAOS_PARAM'] = 'chaoslambda.config'


def session_request_with_delay():
    session = SessionWithDelay(delay=300)
    session.get('https://stackoverflow.com/')
    pass


@inject_exception
def lambda_handler_with_exception(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }


@inject_delay
def lambda_handler_with_delay(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }


@inject_statuscode
def lambda_handler_with_statuscode(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }
