'''
Tests for data loading and validation process.
'''


from django_solver.base.utils import (get_data_form_request, strict_validate,
                                      smart_validate, convert,
                                      validate)
                
from django.test import TestCase
import numpy as np 

class strict_validation_TestCase(TestCase):
    '''Tests for strict_validate function'''

    def test_validate_single_value(self):
        test_str_int = '3'
        test_str_float = '3.0' 
        test_inv_float = '3.Osjk.9'
        test_inv_int = 'O'
        test_tiny_float = '1.'
        self.assertTrue(strict_validate(test_str_float,'float'))
        self.assertFalse(strict_validate(test_inv_float,'float'))
        self.assertFalse(strict_validate(test_str_float,'integer'))
        self.assertTrue(strict_validate(test_str_int,'integer'))
        self.assertFalse(strict_validate(test_inv_int,'integer'))
        self.assertTrue(strict_validate(test_tiny_float,'float'))

    def test_validate_1D_array_of_ints(self):
        test_str_ints = '1,2,3,4,5,6'
        test_inv_ints = '1,2,,3,45'
        test_floats = '1.0,2,3,4'
        self.assertTrue(strict_validate(test_str_ints, 'integer'))
        self.assertFalse(strict_validate(test_inv_ints, 'integer'))
        self.assertFalse(strict_validate(test_floats, 'integer'))
    
    def test_validate_1D_array_of_floats(self):
        test_str_floats = '1.0,2,3,4,5'
        test_inv_floats = '1.0,,5.0,6.0'
        test_bad_floats = '1.0,er4,5.0,6.0'
        self.assertTrue(strict_validate(test_str_floats,'float'))
        self.assertFalse(strict_validate(test_inv_floats,'float'))
        self.assertFalse(strict_validate(test_bad_floats,'float'))
    
    def test_validate_string(self):
        sample_str = '1234asdf'
        empty_str = ''
        self.assertTrue(strict_validate(sample_str, 'string'))
        self.assertFalse(strict_validate(sample_str, 'string'))
    
    def test_validate_1D_array_of_strings(self):
        sample_array = "'one', 'two', 'three'"
        sample_inv_array = "'one', 'two', ''"
        self.assertTrue(strict_validate(sample_array, 'string'))
        self.assertFalse(strict_validate(sample_inv_array, 'string'))
        
    def test_validate_2D_array_of_ints(self):
        sample_2d_ints = ''' 1,2,3,4\n
        2,3,4,5
        1,2,3,4'''
        sample_2d_invalid = '''1,2,3,4\n
        1,2,3
        '''
        sample_2d_with_empty = '''1,2,,3\n
        1,2,3'''
        sample_2d_some_floats = '''1.0,2,3\n
        1,2,34
        '''
        self.assertTrue(strict_validate(sample_2d_ints, 'integer')) 
        self.assertFalse(strict_validate(sample_2d_invalid, 'integer'))
        self.assertFalse(strict_validate(sample_2d_with_empty, 'integer'))
        self.assertFalse(strict_validate(sample_2d_some_floats, 'integer'))
        
    def test_validate_2D_array_of_floats(self):
        sample_2d_floats = '''1.0, 2.0, 3.0 \n
        1.23,5.4,3.3
        ''' 
        sample_2d_invalid = '''1.0,2.0\n
        ,2.3
        '''
        tiny_sample_floats = '''1.,2.\n
        3.,4.'''
        self.assertTrue(strict_validate(sample_2d_floats, 'float'))   
        self.assertFalse(strict_validate(sample_2d_invalid, 'float'))
        self.assertTrue(strict_validate(tiny_sample_floats, 'float'))
        
    def test_validate_2D_array_of_strings(self):
        sample_strs = """'guest1','guest2','another'\n
        'right','left', 'middle' """
        sample_inv_strs = """ 'guest1','guest2','another'\n
        'right','left', '' """
        self.assertTrue(strict_validate(sample_strs, 'string'))
        self.assertFalse(strict_validate(sample_inv_strs, 'string'))
        
        
class smart_validation_TestCase(TestCase):
    '''Tests for smart_validate function'''
    
    def test_smart_single_int(self):
        '''It is assumed that smart_validate could treat float-like objects as integers if they could be 
        converted to integers without loss of precision.
        '''
        single_int = '1'
        single_int_as_float = '1.0'
        single_float = '1.5'
        self.assertTrue(smart_validate(single_int, 'integer'))
        self.assertTrue(smart_validate(single_int_as_float, 'integer'))
        self.assertFalse(smart_validate(single_float, 'integer'))
        
    def test_smart_single_float(self):
        '''smart_validate should interpret ints as floats if needed.
        On floats behaviour of smart_validate is the same as strict_validate.
        So no tests needed (yet)...
        '''
        self.assertTrue(True)

    def test_smart_1D_validate_ints(self):
        sample_ints = '1,2,3,4,5' # Just integer, nothing to check
        sample_floats = '1.0,2.0,3.0,4.0,5.0' # convertable floats should be converted... 
        sample_right_ints1 = '1.0,2.0,3.0,4.0,5.5' # One non-convertable should be excluded
        sample_right_ints = '1,,2' # only one empty, this is not a mistake
        sample_empty = '' # empty array, thats might be... 
        sample_bad_ints = 'one, two, 1' # This is bad, we could not decide what should be here: integers or strings?
        sample_many_floats = '1.2, 1.3, 3' # Many floats should cause error, because they could not be truncated to ints and the number of its is 2.
        self.assertTrue(smart_validate(sample_ints, 'integer'))
        self.assertTrue(smart_validate(sample_empty, 'integer'))
        self.assertTrue(smart_validate(sample_right_ints, 'integer'))
        self.assertFalse(smart_validate(sample_bad_ints, 'integer'))
        self.assertTrue(smart_validate(sample_right_ints1, 'integer'))
        self.assertTrue(smart_validate(sample_floats, 'integer'))
        self.assertFalse(smart_validate(sample_many_floats, 'integer'))

    def test_smart_1D_validate_floats(self):
        sample_floats = '1.0,2.0,3.0,4.0,5.0'
        sample_ints = '1,2,3'
        sample_right_floats = '1.0,2.,,3.'
        sample_empty = ''
        sample_bad_floats = 'one, two, 1.0'
        sample_few_floats = 'one, 2.0, 1.0'
        self.assertTrue(smart_validate(sample_floats, 'float'))
        self.assertTrue(smart_validate(sample_ints, 'float'))
        self.assertTrue(smart_validate(sample_right_floats, 'float'))
        self.assertTrue(smart_validate(sample_empty, 'float')) # This should be treated as empty array...
        self.assertTrue(smart_validate(sample_few_floats, 'float')) 
        self.assertFalse(smart_validate(sample_bad_floats, 'float'))
    
    def test_smart_2D_validate_ints(self):
        sample_2D_ints = '1,2,3\n 4,5,6' 
        sample_2D_floats_like_ints = '1.0, 3.0\n 1, 2'
        self.assertTrue(smart_validate(sample_2D_ints, 'integer'))
        self.assertTrue(smart_validate(sample_2D_floats_like_ints, 'integer'))

    def test_smart_2D_validate_floats(self):
        sample_2D_floats = '1.0,2.0,3.4\n 4.4,5,6.0' 
        sample_2D_bad_floats = '1.0,tor, cot\n 1,cot,3'
        self.assertTrue(smart_validate(sample_2D_floats, 'float'))
        self.assertFalse(smart_validate(sample_2D_bad_floats, 'float'))


class smart_conversion_TestCase(TestCase):
    ''' Test for data input conversion process'''
   
    def test_single_int(self):
        sint = '3'
        sint_like_float = '4.0'
        bad_int = 'this is not an int'
        nint = '-9'
        self.assertEqual(convert(sint), 3)
        self.assertEqual(convert(sint_like_float), 4)
        self.assertIsNone(convert(bad_int))
        self.assertEqual(convert(nint), -9)
    
    def test_single_float(self):
        sflt = '3.0'
        sflt1 = '1.2e+3'
        bad_flt = 'This is not a float'
        negative_flt = '-1.2e+5'
        self.assertIsNone(convert(bad_flt))
        self.assertEqual(convert(sflt), 3.0)
        self.assertEqual(convert(sflt1), 1.2e+3)
        self.assertEqual(convert(negative_flt), -1.2e+5)
    
    def test_1D_floats_array(self):
        sample_floats = '1.1,2.2,3,4'
        sample_floats_with_empty = '1,2,,3,4'
        sample_floats_with_error = 'd, 1, 2.5'
        sample_floats_empty = ''

        t1 = np.linalg.norm(np.array(convert(sample_floats)) - np.array([1.1, 2.2, 3, 4]))
        self.assertLess(t1, 1.0e-14)
        
        t2 = np.linalg.norm(np.array(convert(sample_floats_with_empty)) - np.array([1, 2, 3, 4]))
        self.assertLess(t2, 1.0e-14)
        
        t3 = np.linalg.norm(np.array(convert(sample_floats_with_error)) - np.array([1, 2.5]))
        self.assertLess(t3, 1.0e-14)
        
        t4 = convert(sample_floats_empty)
        self.assertEqual(t4, list())
        
    def test_1D_integers_array(self):
        sample_integers = '1,2,3,4'
        sample_integers_empty = ''
        sample_integers_exclude_floats = '1,2.5,3'
        sample_integers_as_floats = '1.0,2.0,3.0'
        self.assertEqual(convert(sample_integers), [1, 2, 3, 4])
        self.assertIsNone(convert(sample_integers_empty))
        self.assertEqual(convert(sample_integers_exclude_floats), [1, 3])
        self.assertEqual(convert(sample_integers_as_floats), [1,2,3])

    def test_2D_integers_array(self):
        sample_integers = '1,2\n 3,4'
        sample_integers_as_floats = '1, 2.0\n 4, 4'
        sample_bad_integers_2D = 'one, two \n three, four'
        self.assertEqual(convert(sample_integers),[[1, 2], [3, 4]])
        self.assertEqual(convert(sample_integers_as_floats), [[1, 2], [4, 4]])
        self.assertIsNone(convert(sample_bad_integers_2D))

    def test_2D_floats_array(self):
        simple_floats = '1.0,2.4,\n 3.3, 5.5'
        floats_with_error = '1.0, this \n 3, 4'
        
        
        t1 = np.linalg.norm(np.array(convert(simple_floats))-np.array([1.0, 2.4, 3.3, 5.5]))
        self.assertLess(t1, 1.0e-14)
        self.assertEqual(convert(floats_with_error), [[1.0, np.nan], [3.0, 4.0]])
        
        
        
        
        
    
        
        
    