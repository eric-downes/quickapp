__version__ = "1.1dev1"

import reprep
import compmake
import contracts

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)



# return values

# error in computation
QUICKAPP_COMPUTATION_ERROR = 2

# error in passing parameters
QUICKAPP_USER_ERROR = 1


from .utils import col_logging

from .library import *

from .library.app_commands.app_with_commands import QuickMultiCmdApp, add_subcommand
from .library.context.resource_manager import ResourceManager


symbols = [QuickMultiCmdApp, QuickApp, add_subcommand, ResourceManager]
for s in symbols: 
    s.__module__ = 'quickapp'
