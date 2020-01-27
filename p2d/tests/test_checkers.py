import pytest
import os

from unittest import TestCase

from p2d import checkers


class Checker_test(TestCase):

    @staticmethod
    def __checker_dict():
        return {
            'md5sum': 'b70e0031f1596501f33844ef512bd35e',
            'validator_flags': 'case_sensitive space_change_sensitive'
        }

    def test_create(self):
        checkers.Checker('casewcmp', self.__checker_dict())

    def test_update(self):
        check = checkers.Checker('casewcmp', self.__checker_dict())

        with pytest.raises(checkers.CheckerConfigError):
            # md5sum invalid
            check.update({'md5sum': 'b70e'})

        check.update({'md5sum': '00000000000000000000000000000000'})
        assert check.md5sum == '00000000000000000000000000000000'

        check.update({'validator_flags': 'space_change_sensitive'})
        assert check.validator_flags == 'space_change_sensitive'

    def test_invalid_name(self):
        vals = self.__checker_dict()
        with pytest.raises(TypeError):
            checkers.Checker(None, vals)
        with pytest.raises(TypeError):
            checkers.Checker(12, vals)
        with pytest.raises(checkers.CheckerConfigError):
            checkers.Checker('åäö', vals)
        with pytest.raises(checkers.CheckerConfigError):
            checkers.Checker('_java_', vals)
        with pytest.raises(checkers.CheckerConfigError):
            checkers.Checker('Capital_', vals)

    def test_missing_md5(self):
        vals = self.__checker_dict()
        del vals['md5sum']
        with pytest.raises(checkers.CheckerConfigError):
            checkers.Checker('id', vals)

    def test_invalid_md5(self):
        vals = self.__checker_dict()
        vals['md5sum'] = ['A List']
        with pytest.raises(checkers.CheckerConfigError):
            checkers.Checker('id', vals)

    def test_without_validator_flags(self):
        vals = self.__checker_dict()
        del vals['validator_flags']
        checkers.Checker('id', vals)

    def test_invalid_validator_flags(self):
        vals = self.__checker_dict()
        vals['validator_flags'] = ['case_sensitive', 'space_change_sensitive']
        with pytest.raises(checkers.CheckerConfigError):
            checkers.Checker('id', vals)


__EXAMPLES_PATH = os.path.join(os.path.dirname(__file__), 'checkers_examples')


def examples_path(test_file):
    return os.path.join(__EXAMPLES_PATH, test_file)


class Checkers_test(TestCase):

    def test_empty_checkers(self):
        checks = checkers.Checkers()
        assert checks.checkers == {}
        assert checks.detect_checker(examples_path('src1.zoo')) is None

    def test_deplicate_md5(self):
        checks = checkers.Checkers()
        config = {
            'src1': {
                'md5sum': '9b39f964848064045988688880149e7c'
            },
            'src2': {
                'md5sum': '5d99b2d2051125a62f2086c9dcb2c558'
            },
            'src3': {
                'md5sum': '78e6620c1bd5cca6d818ba60310a4d8c'
            }
        }
        config['src3']['md5sum'] = '9b39f964848064045988688880149e7c'
        with pytest.raises(checkers.CheckerConfigError):
            checks.update(config)

    def test_invalid_format(self):
        checks = checkers.Checkers()
        conf1 = {'src1': '9b39f964848064045988688880149e7c'}
        conf2 = [{'src1': '9b39f964848064045988688880149e7c'},
                 {'src2': '5d99b2d2051125a62f2086c9dcb2c558'},
                 {'src3': '78e6620c1bd5cca6d818ba60310a4d8c'}]
        conf3 = None
        with pytest.raises(checkers.CheckerConfigError):
            checks.update(conf1)
        with pytest.raises(checkers.CheckerConfigError):
            checks.update(conf2)
        with pytest.raises(checkers.CheckerConfigError):
            checks.update(conf3)

    def test_empty(self):
        checks = checkers.Checkers()
        checks.update({})
        assert checks.checkers == {}

    def test_src(self):
        checks = checkers.Checkers()

        config = {
            'src1': {
                'md5sum': '9b39f964848064045988688880149e7c'
            },
            'src2': {
                'md5sum': '5d99b2d2051125a62f2086c9dcb2c558'
            },
            'src3': {
                'md5sum': '78e6620c1bd5cca6d818ba60310a4d8c'
            }
        }

        checks.update(config)

        check = checks.detect_checker(examples_path('src1.zoo'))
        assert check == 'src1'
        check = checks.detect_checker(examples_path('src2.zoo'))
        assert check == 'src2'
        check = checks.detect_checker(examples_path('src3.zpp'))
        assert check == 'src3'
