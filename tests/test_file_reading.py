"""Test configuration file reading."""

from __future__ import unicode_literals

import errno
import os
import tempfile

import pytest

import python_config
from python_config import FileReadingError


def test_reading():
    assert python_config.load("tests/test.conf") == { "KEY": "VALUE" }


def test_missing_file():
    assert pytest.raises(FileReadingError, lambda:
        python_config.load("missing.conf")
    ).value.errno == errno.ENOENT


def test_no_access():
    with tempfile.NamedTemporaryFile() as config:
        os.chmod(config.name, 0)

        assert pytest.raises(FileReadingError, lambda:
            python_config.load(config.name)
        ).value.errno == errno.EACCES
