import boto3
import time

class  BotoSessionWithDelay(boto3.Session):
    def __init__(self, delay=None, *args, **kwargs):
        super(BotoSessionWithDelay, self).__init__(*args, **kwargs)
        self.delay = delay

    def client(self, service_name, region_name=None, api_version=None,
               use_ssl=True, verify=None, endpoint_url=None,
               aws_access_key_id=None, aws_secret_access_key=None,
               aws_session_token=None, config=None, **kwargs):
        print('Added {1:.2f}ms of delay to {0:s}'.format(
            service_name, self.delay))
        time.sleep(self.delay / 1000.0)
        return super(BotoSessionWithDelay, self).client(service_name, **kwargs)



