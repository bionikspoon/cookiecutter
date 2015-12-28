#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_generate_files
-------------------

Tests formerly known from a unittest residing in test_generate.py named
TestGenerateFiles.test_generate_files_nontemplated_exception
TestGenerateFiles.test_generate_files
TestGenerateFiles.test_generate_files_with_trailing_newline
TestGenerateFiles.test_generate_files_binaries
TestGenerateFiles.test_generate_files_absolute_path
TestGenerateFiles.test_generate_files_output_dir
TestGenerateFiles.test_generate_files_permissions

Use the global global_setup fixture.

For a better understanding - order of fixture calls:
global_setup setup code
"""

from __future__ import unicode_literals

import io

import os
import pytest
from builtins import str

from cookiecutter import generate, exceptions
from tests.utils import dir_tests


@pytest.mark.parametrize('invalid_dirname', ['', '{foo}', '{{foo', 'bar}}'])
def test_ensure_dir_is_templated_raises(invalid_dirname):
    with pytest.raises(exceptions.NonTemplatedInputDirException):
        generate.ensure_dir_is_templated(invalid_dirname)


def test_generate_files_nontemplated_exception():
    with pytest.raises(exceptions.NonTemplatedInputDirException):
        generate.generate_files(
            context={
                'cookiecutter': {'food': 'pizza'}
            },
            repo_dir=dir_tests('test-generate-files-nontemplated')
        )


def test_generate_files():
    generate.generate_files(
        context={
            'cookiecutter': {'food': 'pizzä'}
        },
        repo_dir=dir_tests('test-generate-files')
    )

    simple_file = 'inputpizzä/simple.txt'
    assert os.path.isfile(simple_file)

    simple_text = io.open(simple_file, 'rt', encoding='utf-8').read()
    assert simple_text == u'I eat pizzä'


def test_generate_files_with_trailing_newline():
    generate.generate_files(
        context={
            'cookiecutter': {'food': 'pizzä'}
        },
        repo_dir=dir_tests('test-generate-files')
    )

    newline_file = 'inputpizzä/simple-with-newline.txt'
    assert os.path.isfile(newline_file)

    with io.open(newline_file, 'r', encoding='utf-8') as f:
        simple_text = f.read()
    assert simple_text == u'I eat pizzä\n'


def test_generate_files_binaries():
    generate.generate_files(
        context={
            'cookiecutter': {'binary_test': 'binary_files'}
        },
        repo_dir=dir_tests('test-generate-binaries')
    )

    assert os.path.isfile('inputbinary_files/logo.png')
    assert os.path.isfile('inputbinary_files/.DS_Store')
    assert os.path.isfile('inputbinary_files/readme.txt')
    assert os.path.isfile('inputbinary_files/some_font.otf')
    assert os.path.isfile('inputbinary_files/binary_files/logo.png')
    assert os.path.isfile('inputbinary_files/binary_files/.DS_Store')
    assert os.path.isfile('inputbinary_files/binary_files/readme.txt')
    assert os.path.isfile('inputbinary_files/binary_files/some_font.otf')
    assert os.path.isfile(
        'inputbinary_files/binary_files/binary_files/logo.png'
    )


def test_generate_files_absolute_path():
    generate.generate_files(
        context={
            'cookiecutter': {'food': 'pizzä'}
        },
        repo_dir=os.path.abspath(dir_tests('test-generate-files'))
    )
    assert os.path.isfile('inputpizzä/simple.txt')


def test_generate_files_output_dir(tmpdir):
    tmpdir.mkdir('custom_output_dir')
    generate.generate_files(
        context={
            'cookiecutter': {'food': 'pizzä'}
        },
        repo_dir=os.path.abspath(dir_tests('test-generate-files')),
        output_dir=str(tmpdir.join('custom_output_dir'))
    )
    unicode_file_name = str(tmpdir.join(
        u'custom_output_dir/inputpizzä/simple.txt'
    ))
    assert os.path.isfile(unicode_file_name)


def test_return_rendered_project_dir(tmpdir):
    tmpdir.mkdir('custom_output_dir')
    project_dir = generate.generate_files(
        context={
            'cookiecutter': {'food': 'pizzä'}
        },
        repo_dir=os.path.abspath(dir_tests('test-generate-files')),
        output_dir=str(tmpdir.join('custom_output_dir'))
    )
    assert project_dir == tmpdir.join('custom_output_dir', 'inputpizzä')


def test_generate_files_permissions():
    """
    simple.txt and script.sh should retain their respective 0o644 and
    0o755 permissions
    """
    generate.generate_files(
        context={
            'cookiecutter': {'permissions': 'permissions'}
        },
        repo_dir=dir_tests('test-generate-files-permissions')
    )

    assert os.path.isfile('inputpermissions/simple.txt')

    # simple.txt should still be 0o644
    tests_simple_file = dir_tests(
        'test-generate-files-permissions',
        'input{{cookiecutter.permissions}}',
        'simple.txt'
    )
    tests_simple_file_mode = os.stat(tests_simple_file).st_mode & 0o777

    input_simple_file = os.path.join(
        'inputpermissions',
        'simple.txt'
    )
    input_simple_file_mode = os.stat(input_simple_file).st_mode & 0o777
    assert tests_simple_file_mode == input_simple_file_mode

    assert os.path.isfile('inputpermissions/script.sh')

    # script.sh should still be 0o755
    tests_script_file = dir_tests(
        'test-generate-files-permissions',
        'input{{cookiecutter.permissions}}',
        'script.sh'
    )
    tests_script_file_mode = os.stat(tests_script_file).st_mode & 0o777

    input_script_file = os.path.join(
        'inputpermissions',
        'script.sh'
    )
    input_script_file_mode = os.stat(input_script_file).st_mode & 0o777
    assert tests_script_file_mode == input_script_file_mode


@pytest.fixture
def undefined_context():
    return {
        'cookiecutter': {
            'project_slug': 'testproject',
            'github_username': 'hackebrot'
        }
    }


def test_raise_undefined_variable_file_name(tmpdir, undefined_context):
    output_dir = tmpdir.mkdir('output')

    with pytest.raises(exceptions.UndefinedVariableInTemplate) as err:
        generate.generate_files(
            repo_dir=dir_tests('undefined-variable/file-name/'),
            output_dir=str(output_dir),
            context=undefined_context
        )
    error = err.value
    assert "Unable to create file '{{cookiecutter.foobar}}'" == error.message
    assert error.context == undefined_context

    assert not output_dir.join('testproject').exists()


def test_raise_undefined_variable_file_content(tmpdir, undefined_context):
    output_dir = tmpdir.mkdir('output')

    with pytest.raises(exceptions.UndefinedVariableInTemplate) as err:
        generate.generate_files(
            repo_dir=dir_tests('undefined-variable/file-content/'),
            output_dir=str(output_dir),
            context=undefined_context
        )
    error = err.value
    assert "Unable to create file 'README.rst'" == error.message
    assert error.context == undefined_context

    assert not output_dir.join('testproject').exists()


def test_raise_undefined_variable_dir_name(tmpdir, undefined_context):
    output_dir = tmpdir.mkdir('output')

    with pytest.raises(exceptions.UndefinedVariableInTemplate) as err:
        generate.generate_files(
            repo_dir=dir_tests('undefined-variable/dir-name/'),
            output_dir=str(output_dir),
            context=undefined_context
        )
    error = err.value

    directory = os.path.join('testproject', '{{cookiecutter.foobar}}')
    msg = "Unable to create directory '{}'".format(directory)
    assert msg == error.message

    assert error.context == undefined_context

    assert not output_dir.join('testproject').exists()


def test_raise_undefined_variable_project_dir(tmpdir):
    output_dir = tmpdir.mkdir('output')

    with pytest.raises(exceptions.UndefinedVariableInTemplate) as err:
        generate.generate_files(
            repo_dir=dir_tests('undefined-variable/dir-name/'),
            output_dir=str(output_dir),
            context={}
        )
    error = err.value
    msg = "Unable to create project directory '{{cookiecutter.project_slug}}'"
    assert msg == error.message
    assert error.context == {}

    assert not output_dir.join('testproject').exists()
