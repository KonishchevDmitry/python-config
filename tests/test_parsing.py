"""Test configuration file parsing."""

from __future__ import unicode_literals

import sys

import pytest

import python_config

PY2 = sys.version_info < (3,)
if PY2:
    str = unicode


def test_parsing():
    config = python_config.load("test", """
import sys

some_variable = 0
_UNDERSCORE_VALUE = 0

INT_VALUE = 1
FLOAT_VALUE = 3.3

if sys.version_info < (3,):
    BYTES_VALUE = "bytes value"
    STRING_VALUE = unicode("string value")
    LONG_VALUE = long(0)
else:
    BYTES_VALUE = "bytes value".encode("utf-8")
    STRING_VALUE = "string value"

TUPLE_VALUE = ( "a", 1 )

LIST_VALUE = ( "b", 2 )

SET_VALUE = set(( "a", "b", "c" ))

DICT_VALUE = {
    1:   "number",
    "s": "string",
    "d": {
        "l": [ "one", 2 ],
        "t": [ 1, "two" ],
    },
}
    """)

    assert type(config["INT_VALUE"]) == int
    assert type(config["FLOAT_VALUE"]) == float

    assert type(config["BYTES_VALUE"]) == str
    assert type(config["STRING_VALUE"]) == str

    if PY2:
        assert type(config["LONG_VALUE"]) == long

    assert type(config["SET_VALUE"]) == list
    config["SET_VALUE"] = sorted(config["SET_VALUE"])

    valid_config = {
        "INT_VALUE": 1,
        "FLOAT_VALUE": 3.3,

        "BYTES_VALUE": "bytes value",
        "STRING_VALUE": "string value",

        "TUPLE_VALUE": [ "a", 1 ],

        "LIST_VALUE": [ "b", 2 ],

        "SET_VALUE": sorted(( "a", "b", "c" )),

        "DICT_VALUE": {
            1:   "number",
            "s": "string",
            "d": {
                "l": [ "one", 2 ],
                "t": [ 1, "two" ],
            },
        },
    }

    if PY2:
        valid_config["LONG_VALUE"] = 0

    assert config == valid_config


def test_invalid_type():
    assert pytest.raises(python_config.ValidationError, lambda:
        python_config.load("test", "OS = object()")
    ).value.option_name == "OS"


def test_invalid_dict_key():
    assert pytest.raises(python_config.ValidationError, lambda:
        python_config.load("test", "A = {}; B = { (0, 1): 2 }")
    ).value.option_name == "A B's key"


def test_invalid_syntax():
    with pytest.raises(python_config.ParsingError):
        python_config.load("test", contents="a=")
