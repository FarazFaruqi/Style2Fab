import os
import errno
import signal
import functools

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