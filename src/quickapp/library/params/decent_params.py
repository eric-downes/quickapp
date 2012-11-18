from optparse import OptionParser
from contracts import contract, describe_type, describe_value
from .. import Choice
from ...utils.script_utils import UserError

__all__ = ['DecentParams']

class DecentParamsUserError(UserError):
    pass

class DecentParam():
    
    def __init__(self, ptype, name, default=None, help=None,  # @ReservedAssignment
                 compulsory=False, short=None):
        self.ptype = ptype
        self.name = name
        self.default = default  
        self.desc = help
        self.compulsory = compulsory
        self.short = short
        self.order = None
        if self.default is not None:
            self.validate(self.default)
        
    def validate(self, value):
        self.check_type(value)
 
    def set_from_string(self, s):
        self._value = self.value_from_string(s)
                 
    def value_from_string(self, s):
        if self.ptype == str:
            return str(s)
        if self.ptype == float:
            return float(s)
        if self.ptype == int:
            return int(s)  # TODO: check
        if self.ptype == bool:
            return bool(s)  # TODO: check
        msg = 'Unknown type %r' % self.ptype
        raise ValueError(msg)
    
    def check_type(self, x):
        expected = self.ptype
        if self.ptype == float:
            expected = (float, int)
            
        if not isinstance(x, expected):
            msg = ("For param %r, expected %s, got %s.\n%s" % 
                    (self.name, self.ptype, describe_type(x),
                     describe_value(x)))
            raise DecentParamsUserError(msg)
    
    def get_desc(self):
        desc = self.desc
        if self.compulsory:
            desc = '*required* %s' % desc
        elif self.default is not None:
            desc = '[default: %%default] %s' % desc 
        return desc
    
    def populate(self, parser):
        option = '--%s' % self.name
        other = dict(help=self.get_desc(), default=self.default)
        if self.short is not None:
            option1 = '-%s' % self.short
            parser.add_option(option1, option, **other)
        else:
            parser.add_option(option, **other)
         

class DecentParamsResults():
    
    def __init__(self, values, given, params):
        self._values = values
        self._given = given
        self._params = params
    
        for k, v in values.items():
            self.__dict__[k] = v 
    
    def __getitem__(self, name):
        return self._values[name]
        
    def given(self, name):
        return name in self._given
    
#    def as_choices(self, which=None):
#        if which is None:
#            which = self._values.keys()
#            
#        from .. import Choice
#        res = {}
#        for k in which:
#            v = self._values[k]
#            if isinstance(self._params[k], DecentParamMultiple):
#                v = Choice(v) 
#            res[k] = v
#        return res

class DecentParamMultiple(DecentParam):
    """ Allow multiple values """    
    
    
    def __init__(self, ptype, name, default=None, **args):
        if default is not None:
            if not isinstance(default, list):
                default = [default]
        DecentParam.__init__(self, ptype=ptype, name=name, default=default,
                             **args)
        
    @contract(s='str')
    def value_from_string(self, s):
        values = [DecentParam.value_from_string(self, x) for x in s.split(',')]
        return Choice(values)

    def validate(self, value):
        if not isinstance(value, list):
            msg = "Should be a list, not %r" % value
            raise DecentParamsUserError(msg)
        for x in value:
            self.check_type(x)
    

    def populate(self, parser):
        option = '--%s' % self.name
        parser.add_option(option, help=self.get_desc(), default=self.default)
              
class DecentParamFlag(DecentParam):
    def populate(self, parser):
        option = '--%s' % self.name
        parser.add_option(option, help=self.desc, action='store_true')
      
        
class DecentParamChoice(DecentParam):
    def __init__(self, choices, **args):
        self.choices = choices
        DecentParam.__init__(self, **args)
        
    def validate(self, value):
        if not value in self.choices:
            msg = 'Not %r in %r' % (value, self.choices)
            raise DecentParamsUserError(msg)
    
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
    
    def parse_args(self, args):
        parser = self.create_parser()
        return self.parse_using_parser(parser, args)

    @contract(args='list(str)')    
    def parse_using_parser(self, parser, args):
        options, misc = parser.parse_args(args)
        if misc:
            msg = "Spurious arguments: %r" % misc
            raise DecentParamsUserError(msg)
        parsed = vars(options)
        values = dict()
        given = set()
        for k, v in self.params.items():
            if v.compulsory and parsed[k] is None:
                msg = 'Compulsory option %r not given.' % k
                raise DecentParamsUserError(msg)
            
            if parsed[k] is not None:
                given.add(k)
                if parsed[k] != self.params[k].default:
                    values[k] = self.params[k].value_from_string(parsed[k])
                else:
                    values[k] = self.params[k].default
            else:
                values[k] = self.params[k].default
            
        res = DecentParamsResults(values, given, self.params) 
        return res
    
    def populate_parser(self, option_container):
        params = sorted(self.params.values(), key=lambda x: x.order)
        for p in params:
            p.populate(option_container)
        
    def create_parser(self):
        parser = OptionParser(usage=self.usage, prog=self.prog)
        parser.disable_interspersed_args()
        self.populate_parser(parser)
        return parser
            
