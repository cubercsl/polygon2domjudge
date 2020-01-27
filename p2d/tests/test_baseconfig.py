import pytest

from p2d import checkers
from p2d import problems
from p2d import results
from p2d import misc


def test_checkers():
    checkers.load_checker_config()


def test_problems():
    problems.load_problem_config('')


def test_results():
    results.load_result_config()


def test_misc():
    misc.load_misc_config()
