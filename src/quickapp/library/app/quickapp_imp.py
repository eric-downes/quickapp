from . import QuickAppInterface
from .. import Choice, logger as l, DecentParams
from ...utils import CmdOptionParser, UserError, wrap_script_entry_point_noexit
from compmake import (batch_command, compmake_console, read_rc_files,
    use_filesystem)
from optparse import OptionGroup
from reprep.report_utils import ReportManager
import contracts
import os
import sys


class QuickApp(QuickAppInterface):
    
    def __init__(self, logger=None):
        if logger is None:
            logger = l
        self.logger = logger
        

    def main(self, args=None):
        return wrap_script_entry_point_noexit(self.main2,
                                self.logger,
                                exceptions_no_traceback=(UserError,),
                                args=args)
            
    def main2(self, args=None):
        if args is None:
            args = sys.argv[1:]
            
        main_params = DecentParams()
        main_params.add_flag('contracts', help='Activate PyContracts')
        main_params.add_flag('profile', help='Use Python Profiler')
        main_params.add_string('output', short='o', help='Output directory',
                               compulsory=True)
    
        main_params.add_string('command', short='c',
                      help="Command to pass to compmake for batch mode")

        app_params = DecentParams()
        self.define_options(app_params)    

        parser = CmdOptionParser(prog='prog', usage=None, args=None)
        parser.disable_interspersed_args()
        group = OptionGroup(parser, "General QuickApp options", "")
        main_params.populate_parser(group)
        parser.add_option_group(group)
        
        group = OptionGroup(parser, "Application options",
                    "Options for this applications")
        app_params.populate_parser(group)
        parser.add_option_group(group)
        
        options = main_params.parse_using_parser(parser, args)
    
        if not options.contracts:
            msg = 'PyContracts disabled for speed. Use --contracts to activate.'
            self.logger.warning(msg)
            contracts.disable_all()

        app_options = app_params.parse_using_parser(parser, args)    
        
        outdir = os.path.join(options.output)
    
        # Compmake storage for results
        storage = os.path.join(outdir, 'compmake')
        use_filesystem(storage)
        read_rc_files()
        
        reports = os.path.join(outdir, 'reports')
        self._output_dir = os.path.join(outdir, 'output')
        self._report_manager = ReportManager(reports)
        self._options = app_options 
        self.define_jobs()
        
        self._report_manager.create_index_job()
        
        if options.given('command'):
            return batch_command(options.command)
        else:
            compmake_console()
            return 0
    
    @staticmethod
    def choice(it):
        return Choice(it)
