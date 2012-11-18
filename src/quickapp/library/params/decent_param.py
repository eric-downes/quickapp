from contracts import contract, describe_type, describe_value
from .. import Choice
from ...utils.script_utils import UserError


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
        """ Possibly returns Choice(options) """
        sep = ','
        if sep in s:
            return Choice([self.value_from_string(x) 
                           for x in s.split(sep)])
        
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
    
