__version__ = "6.0.2"

# Flag to control whether to show warnings about missing dependencies
# Set to False to suppress warnings, True to show them
SHOW_DEPENDENCY_WARNINGS = False

# Handle zuper_commons import
try:
    from zuper_commons.logs import ZLogger
except ImportError:
    # Use our patched version when ZLogger is not available
    from .zuper_commons_patch import ZLogger
    if SHOW_DEPENDENCY_WARNINGS:
        import warnings
        warnings.warn("Using patched ZLogger implementation. Original zuper_commons.logs.ZLogger not found.")

# Handle importing zuper_commons.text and zuper_commons.types by setting up sys.modules
import sys
import types

# Create the zuper_commons module structure if it doesn't exist
if 'zuper_commons' not in sys.modules:
    sys.modules['zuper_commons'] = types.ModuleType('zuper_commons')
    sys.modules['zuper_commons'].__path__ = []

# Handle text module
try:
    import zuper_commons.text
except ImportError:
    if 'zuper_commons.text' not in sys.modules:
        # Import our patched version
        from . import zuper_commons_patch
        from .zuper_commons_patch import text as patched_text
        
        # Set it in sys.modules so imports like "from zuper_commons.text import indent" work
        sys.modules['zuper_commons.text'] = patched_text
        
        if SHOW_DEPENDENCY_WARNINGS:
            import warnings
            warnings.warn("Using patched zuper_commons.text module. Original zuper_commons.text not found.")

# Handle types module
try:
    import zuper_commons.types
except ImportError:
    if 'zuper_commons.types' not in sys.modules:
        # Import our patched version
        from . import zuper_commons_patch
        from .zuper_commons_patch import types as patched_types
        
        # Set it in sys.modules so imports like "from zuper_commons.types import X" work
        sys.modules['zuper_commons.types'] = patched_types
        
        if SHOW_DEPENDENCY_WARNINGS:
            import warnings
            warnings.warn("Using patched zuper_commons.types module. Original zuper_commons.types not found.")

logger = ZLogger(__name__)

# error in computation
QUICKAPP_COMPUTATION_ERROR = 2

# error in passing parameters
QUICKAPP_USER_ERROR = 1

from .utils import col_logging

from .quick_app_base import *
from .quick_multi_app import *
from .resource_manager import *
from .report_manager import *
from .quick_app import *
from .compmake_context import *
from .app_utils import *

symbols = [QuickMultiCmdApp, QuickApp,
           QuickAppBase, add_subcommand, ResourceManager]

for s in symbols:
    s.__module__ = 'quickapp'
