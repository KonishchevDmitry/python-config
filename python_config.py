"""Python configuration file parser."""

from __future__ import unicode_literals

import imp
import sys

PY2 = sys.version_info < (3,)
if PY2:
    str = unicode


class Error(Exception):
    """The base class for exceptions that our code throws."""

    def __init__(self, error, *args):
        super(Error, self).__init__(error.format(*args) if args else error)


class FileReadingError(Error):
    """Error while reading a configuration file."""

    def __init__(self, path, error):
        super(FileReadingError, self).__init__(
            "Error while reading configuration file '{0}': {1}.", path, error.strerror)
        self.errno = error.errno


class ParsingError(Error):
    """Error while parsing a configuration file."""

    def __init__(self, path, error):
        super(ParsingError, self).__init__(
            "Error while parsing configuration file '{0}': {1}.", path, error)


class ValidationError(Error):

    def __init__(self, path, option, error):
        super(ValidationError, self).__init__(
            "Error while parsing configuration file '{0}': {1}.", path, error)
        self.option = option


class _ValidationError(Error):
    def __init__(self, option, *args):
        super(_ValidationError, self).__init__(*args)
        self.option = option




def load(path, contents=None):
    """Loads a configuration file."""

    config_module = imp.new_module("config")
    config_module.__file__ = path

    if contents is None:
        try:
            with open(path) as config_file:
                contents = config_file.read()
        except EnvironmentError as e:
            raise FileReadingError(path, e)

    try:
        exec(compile(contents, path, "exec"), config_module.__dict__)
    except Exception as e:
        raise ParsingError(path, e)

    config = {}

    for key, value in config_module.__dict__.items():
        if not key.startswith("_") and key.isupper():
            try:
                config[key] = _validate_value(key, value)
            except _ValidationError as e:
                raise ValidationError(path, e.option, e)

    return config


def _validate_value(key, value):
    """Validates a configuration file value."""

    valid_types = ( dict, set, list, tuple, str, bytes, int, float )
    if PY2:
        valid_types += ( long, )

    value_type = type(value)

    if value_type not in valid_types:
        raise _ValidationError(key, "{0} has an invalid value type ({1}). Allowed types: {2}.",
            key, value_type.__name__, ", ".join(t.__name__ for t in valid_types))

    if value_type is bytes:
        try:
            value = value.decode()
        except UnicodeDecodeError as e:
            raise _ValidationError(key, "{0} has an invalid value: {1}.", key, e)
    elif value_type is dict:
        value = _validate_dict_value(key, value)
    elif value_type in (list, tuple, set):
        value = _validate_list_like_value(key, value)

    return value


def _validate_dict_value(key, value):
    """Validates a dict value."""

    new_value = {}

    for subkey, subvalue in value.items():
        subkey = _validate_value("A {0}'s key".format(key), subkey)
        subvalue = _validate_value("{0}[{1}]".format(key, repr(subkey)), subvalue)
        new_value[subkey] = subvalue

    return new_value


def _validate_list_like_value(key, value):
    """Validates a list-like value."""

    if type(value) is set:
        return [
            _validate_value("A {0}'s key".format(key), subvalue)
            for subvalue in value
        ]
    else:
        return [
            _validate_value("{0}[{1}]".format(key, repr(index)), subvalue)
            for index, subvalue in enumerate(value)
        ]
