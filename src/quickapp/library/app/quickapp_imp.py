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
from .. import DecentParamsResults
from .. import all_combinations
from compmake.ui.ui import comp_prefix


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
        
        x = main_params.parse_using_parser(parser, args)
        options = DecentParamsResults(x[0], x[1], main_params.params)
        
        if not options['contracts']:
            msg = 'PyContracts disabled for speed. Use --contracts to activate.'
            self.logger.warning(msg)
            contracts.disable_all()

        # Compmake storage for results
        outdir = os.path.join(options.output)
        storage = os.path.join(outdir, 'compmake')
        reports = os.path.join(outdir, 'reports')
        self._report_manager = ReportManager(reports)
        use_filesystem(storage)
        read_rc_files()
        
        values, given = app_params.parse_using_parser(parser, args)

        combs = {}
        for params, choices in all_combinations(values, give_choices=True):
            i = len(combs)
            name = 'C%d' % i
            combs[name] = dict(params=params, choices=choices, given=given)         
        self.add_combs(outdir, combs, app_params)
        
        self._report_manager.create_index_job()
        
        if options.given('command'):
            return batch_command(options.command)
        else:
            compmake_console()
            return 0

    def add_combs(self, outdir, combs, app_params):
        multiple = len(combs) > 1
        for name, x in combs.items():
            params = x['params']
            choices = x['choices']
            given = x['given']
            if multiple:
                self.logger.info('Config %s: %s' % (name, choices))
                comp_prefix(name) 
            self._options = DecentParamsResults(params, given, app_params.params)
            self._current_params = params
            
            self._output_dir = os.path.join(outdir, 'output', name)
            if not os.path.exists(self._output_dir):
                os.makedirs(self._output_dir)

            self.define_jobs()
        if multiple:
            comp_prefix()
    
    @staticmethod
    def choice(it):
        return Choice(it)
