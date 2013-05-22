__version__ = '1.1'

import sys
import traceback


class UserError(Exception):
    pass


def wrap_script_entry_point(function, logger,
                            exceptions_no_traceback=(UserError,),
                            args=None, sys_exit=True):
    """
        Wraps the main() of a script.
        For Exception: we exit with value 2.
        
        :param exceptions_no_traceback: list of exceptions for which we 
         just print the error, and return 1.
        
    """

    ret = wrap_script_entry_point_noexit(function, logger, exceptions_no_traceback, args)
    if sys_exit:
        sys.exit(ret)
    else:
        return ret

def wrap_script_entry_point_noexit(function, logger,
                            exceptions_no_traceback=(UserError,),
                            args=None):
    """
        Wraps the main() of a script.
         
        :param exceptions_no_traceback: list of exceptions for which we 
         just print the error, and return 1.
        
    """
    if args is None:
        args = sys.argv[1:]
    try:
        ret = function(args)
        if ret is None:
            ret = 0
        return ret
    except exceptions_no_traceback as e:
        logger.error(str(e))
        return 1
    except Exception as e:
        logger.error(traceback.format_exc())
        return 2
