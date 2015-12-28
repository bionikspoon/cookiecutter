# -*- coding: utf-8 -*-

import pytest

from cookiecutter import generate, exceptions
from tests.utils import dir_tests


def test_pre_gen_hook(tmpdir):
    context = {
        'cookiecutter': {
            "repo_dir": "foobar",
            "abort_pre_gen": "yes",
            "abort_post_gen": "no"
        }
    }

    with pytest.raises(exceptions.FailedHookException):
        generate.generate_files(
            repo_dir=dir_tests('hooks-abort-render'),
            context=context,
            output_dir=str(tmpdir)
        )

    assert not tmpdir.join('foobar').isdir()


def test_post_gen_hook(tmpdir):
    context = {
        'cookiecutter': {
            "repo_dir": "foobar",
            "abort_pre_gen": "no",
            "abort_post_gen": "yes"
        }
    }

    with pytest.raises(exceptions.FailedHookException):
        generate.generate_files(
            repo_dir=dir_tests('hooks-abort-render'),
            context=context,
            output_dir=str(tmpdir)
        )

    assert not tmpdir.join('foobar').isdir()
