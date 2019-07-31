import boto3
import random
import time
import json

def get_config(key):
    return json.loads(
        '{"isEnabled": true, \
        "delay": 400, \
        "error_code": 404, \
        "exception_msg": "I really failed seriously", \
        "rate": 1 \
    }').get(key)


class BotoFailureInjector(object):

    def __init__(self):
        self._regid = None
        self.delay = get_config('delay')
        self.rate = get_config('rate')
        self.exception = get_config('exception_msg')
        self.error_code = get_config('error_code')
        self.enabled = get_config('isEnabled')
        

    def attach(self, s):
        self._regid = s.register('after-call.*.*', self.invoke)
        
    def invoke(self, http_response, parsed, model, **kwargs):
        print("content: {}".format(http_response.content))

        print('Model name: {}'.format(model.name))
        print('Http response: {}'.format(dir(http_response)))
        http_response = {
            'headers': http_response.headers,
            'text': "hello worlds!",
            'status_code': 500
        }
        http_response['body'] = 'breaking things'
        # print('Http response_dict: {}'.format(response_dict))

        # http_response = response_dict
        print('Http http_response: {}'.format(http_response))


        # print('**kwargs: {}'.format(kwargs))

        # return http_response



if __name__ == '__main__':
    boto3.client('ec2')
    fault_injector = BotoFailureInjector()
    fault_injector.attach(boto3.DEFAULT_SESSION._session)
    client = boto3.client('ec2')

