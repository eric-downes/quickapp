from . import QuickAppInterface
from .. import (Choice, logger as l, DecentParams, DecentParamsResults,
    all_combinations)
from ...utils import UserError, wrap_script_entry_point_noexit
from compmake import (batch_command, compmake_console, read_rc_files,
    use_filesystem, comp_prefix)
from reprep.report_utils import ReportManager
import contracts
import os
import sys
import argparse
import hashlib


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
            
    def main2(self, script_name=None, args=None):
        if script_name is not None:
            script_name = os.path.basename(sys.argv[0])
        
        default_output_dir = 'out-%s/' % script_name
        
        if args is None:
            args = sys.argv[1:]
            
        main_params = DecentParams()
        main_params.add_flag('contracts', help='Activate PyContracts')
        main_params.add_flag('profile', help='Use Python Profiler')
        main_params.add_string('output', short='o', help='Output directory',
                               default=default_output_dir)
    
        main_params.add_flag('console', help='Use Compmake console')

        main_params.add_string('command', short='c',
                      help="Command to pass to compmake for batch mode",
                      default='make')

        app_params = DecentParams()
        self.define_options(app_params)    

        parser = argparse.ArgumentParser(prog=script_name)

        group_quickapp = parser.add_argument_group('QuickApp arguments')
        main_params.populate_parser(group_quickapp)
        group_app = parser.add_argument_group('Application arguments')
        app_params.populate_parser(group_app)
        
        x = main_params.parse_using_parser(parser, args)
        options = DecentParamsResults(x[0], x[1], main_params.params)
        
        if not options['contracts']:
            msg = 'PyContracts disabled for speed. Use --contracts to activate.'
            self.logger.warning(msg)
            contracts.disable_all()

        values, given = app_params.parse_using_parser(parser, args)

        run_name = create_conf_name_digest(values, length=12)
        self.logger.info('Configuration name: %r' % run_name)
        outdir = os.path.join(options.output, run_name)
        
        # Compmake storage for results        
        storage = os.path.join(outdir, 'compmake')
        reports = os.path.join(outdir, 'reports')
        reports_index = os.path.join(outdir, 'reports.html')

        self._report_manager = ReportManager(reports, reports_index)
        use_filesystem(storage)
        read_rc_files()
        
        combs = {}
        for params, choices in all_combinations(values, give_choices=True):
            i = len(combs)
            name = 'C%03d' % i
            combs[name] = dict(params=params, choices=choices, given=given)         
        self.add_combs(outdir, combs, app_params)
        
        self._report_manager.create_index_job()
        
        if not options.console:
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

def create_conf_name_digest(values, length=12):
    """ Create an hash for the given values """
    s = "-".join([str(values[x]) for x in sorted(values.keys())])
    h = hashlib.sha224(s).hexdigest()
    if len(h) > length:
        h = h[:length]
    return h


#
# def create_conf_name(values, given, limit=32):
#    cn = create_conf_name_values(values, given)
#    if len(cn) > limit:
#        cn = cn[:limit]  # TODO XXX
#    return cn
#    
    
#    
# def create_conf_name_values(values, given):
#    def make_short(a):
#        if isinstance(a, Choice):
#            s = ','.join([make_short(x) for x in a])
#        else:
#            s = str(a)
#        if '/' in s:
#            s = os.path.basename(s)
#            s = os.path.splitext(s)[0]
#            s = s.replace('.', '_')
#        s = s.replace(',', '_')
#        return s
#    return "-".join([make_short(values[x]) for x in sorted(given)])
#    
#    
    
