from . import (DecentParamFlag, DecentParam, DecentParamMultiple,
    DecentParamChoice, DecentParamsUserError, DecentParamsResults)
from contracts import contract
from argparse import ArgumentParser
from quickapp.library.variations.variations import Choice

__all__ = ['DecentParams']


class DecentParams():
    
    def __init__(self, usage=None, prog=None):
        self.usage = usage
        self.prog = prog
        self.params = {}
      
    def _add(self, p):
        if p.name in self.params:
            msg = "I already know param %r." % p.name
            raise ValueError(msg)
        p.order = len(self.params)
        self.params[p.name] = p
        
          
    def add_flag(self, name, **args):
        self._add(DecentParamFlag(ptype=bool, name=name, **args))

    def add_string(self, name, **args):
        self._add(DecentParam(ptype=str, name=name, **args))
        
    def add_float(self, name, **args):
        self._add(DecentParam(ptype=float, name=name, **args))

    def add_int(self, name, **args):
        self._add(DecentParam(ptype=int, name=name, **args))

    def add_string_list(self, name, **args):
        self._add(DecentParamMultiple(ptype=str, name=name, **args))
        
    def add_float_list(self, name, **args):
        self._add(DecentParamMultiple(ptype=float, name=name, **args))

    def add_int_list(self, name, **args):
        self._add(DecentParamMultiple(ptype=int, name=name, **args))
    
    def add_int_choice(self, name, choices, **args):
        self._add(DecentParamChoice(name=name, choices=choices, ptype=int, **args))

    def add_float_choice(self, name, choices, **args):
        self._add(DecentParamChoice(name=name, choices=choices, ptype=float, **args))

    def add_string_choice(self, name, choices, **args):
        self._add(DecentParamChoice(name=name, choices=choices, ptype=str, **args))
    
    def parse_args(self, args, allow_choice=True):
        parser = self.create_parser()
        values, given = self.parse_using_parser(parser, args)
        # TODO: check no Choice()
        res = DecentParamsResults(values, given, self.params) 
        return res

    @contract(args='list(str)', returns='tuple(dict, list(str))')    
    def parse_using_parser(self, parser, args):
        """ Returns a dictionary with all values of parameters,
            but possibly some values are Choice() instances,
            and an """
        try:
            res = parser.parse_args(args)
        except SystemExit as e:
            raise
            # raise Exception(e)  # XXX

        parsed = vars(res)
        values = dict()
        given = set()
        for k, v in self.params.items():
            if v.compulsory and parsed[k] is None:
                msg = 'Compulsory option %r not given.' % k
                raise DecentParamsUserError(msg)
            
            if parsed[k] is not None:
                if parsed[k] != self.params[k].default:
                    given.add(k)
                    if isinstance(self.params[k], DecentParamMultiple):
                        if isinstance(parsed[k], list):
                            values[k] = parsed[k]
                        else:
                            values[k] = [parsed[k]]
                    else:
                        if isinstance(parsed[k], list):
                            if len(parsed[k]) > 1:
                                values[k] = Choice(parsed[k])
                            else:
                                values[k] = parsed[k][0]
                        else:
                            values[k] = parsed[k]
                    # values[k] = self.params[k].value_from_string(parsed[k])
                else:
                    values[k] = self.params[k].default
            else:
                values[k] = self.params[k].default
        return values, list(given) 
        
    def populate_parser(self, option_container):
        params = sorted(self.params.values(), key=lambda x: x.order)
        for p in params:
            p.populate(option_container)
        
    def create_parser(self):
        parser = ArgumentParser(usage=self.usage, prog=self.prog)
        # parser.disable_interspersed_args()
        self.populate_parser(parser)
        return parser
            
