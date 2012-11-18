from nose.tools import raises
from quickapp import DecentParams
import unittest


class ParamsTest(unittest.TestCase):
        
    def decent_params_test1(self):
        
        p = DecentParams()
        p.add_string('vehicle', default='x')
        p.add_float('float1')
        p.add_float_list('floats')
        p.add_int('int1')
        p.add_int_list('ints')
        p.add_string_choice('ciao', ['2', '1'], default='1')
        p.add_int_choice('ciao2', [2, 1], default=1)
        
        args = ['--vehicle', 'y',
                '--float1', '1.2',
                '--floats', '1.2,2.3',
                '--ints', '1,2,3']
        
        try:    
            res = p.parse_args(args)
        except SystemExit as e:
            print e
            raise Exception(str(e))
        
        assert res.given('floats') == True
        assert res.given('int1') == False
        assert res['ciao'] == '1'
        assert res['ciao2'] == 1
        assert res.ciao == '1'
        assert res.ciao2 == 1
        assert res.floats == [1.2, 2.3]
        assert res.ints == [1, 2, 3]
        
    @raises(ValueError)
    def decent_params_test2(self):
        """ Test compulsory """
        p = DecentParams()
        p.add_string('a', compulsory=True)
        p.add_string('b')
        p.parse_args(['--b', '1'])
        
        
