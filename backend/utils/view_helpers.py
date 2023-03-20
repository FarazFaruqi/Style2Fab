"""
view helpers 
"""
import os
import errno
import signal
import functools
from rest_framework import status
from django.core.exceptions import ValidationError

### Global COnstants ###
report = lambda error: f"\033[31m----------------------------\n{error}\n----------------------------\033[0m\n"

### Functions ###
def _is_subset(required_fields, request_fields) -> status:
    """
    Checks that the required fields are a subset of the request fields

    Definitions
        subset
            a sequence of objects contained within another sequence 

            A = {1, 2, 3} is a subset of B = {1, 2, 3, 4, 5}

    Inputs
        :param required_fields: <list> of strings representing fields required
        :param request_fields: <view> of strings representing fields sent by the request 

    Outputs
        :returns: Status ...
                         ... HTTP_200_OK if the required fields are a subset of the request fields
                         ... HTTP_400_BAD_REQUEST if the required fields are not a subset of the request fields
    """
    for field in required_fields:
        if field not in request_fields: 
            return status.HTTP_400_BAD_REQUEST
    return status.HTTP_200_OK


class TimeoutError(Exception):
    pass

def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    """ Handles timeout for single thread """
    def decorator(func):
        def _handle_timeout(signum, frame, silent = False):
            if not silent: raise TimeoutError(error_message)
            else:
                print(error_message)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wrapper

    return decorator