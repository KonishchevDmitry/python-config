"""Python configuration file parser."""

from __future__ import unicode_literals

import imp
import sys

_PY2 = sys.version_info < (3,)
if _PY2:
    str = unicode


_BASIC_TYPES = (bool, int, float, bytes, str)
"""Python basic types."""

if _PY2:
    _BASIC_TYPES += (long,)

_COMPLEX_TYPES = (tuple, list, set, dict)
"""Python complex types."""

_VALID_TYPES = _BASIC_TYPES + _COMPLEX_TYPES
"""Option value must be one of these types."""



class Error(Exception):
    """The base class for all exceptions that the module raises."""

    def __init__(self, error, *args, **kwargs):
        super(Error, self).__init__(error.format(*args, **kwargs) if args or kwargs else error)


class FileReadingError(Error):
    """Error while reading a configuration file."""

    def __init__(self, path, error):
        super(FileReadingError, self).__init__(
            "Error while reading '{0}' configuration file: {1}.", path, error.strerror)
        self.errno = error.errno


class ParsingError(Error):
    """Error while parsing a configuration file."""

    def __init__(self, path, error):
        super(ParsingError, self).__init__(
            "Error while parsing '{0}' configuration file: {1}.", path, error)


class ValidationError(Error):
    """Error during validation of a configuration file."""

    def __init__(self, path, error):
        super(ValidationError, self).__init__(
            "Error while parsing '{0}' configuration file: {1}.", path, error)
        self.option_name = error.option_name


class _ValidationError(Error):
    """Same as ValidationError, but for internal usage."""

    def __init__(self, option_name, *args, **kwargs):
        super(_ValidationError, self).__init__(*args, **kwargs)
        self.option_name = option_name



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

    for option, value in config_module.__dict__.items():
        if not option.startswith("_") and option.isupper():
            try:
                config[option.lower()] = _validate_value(option, value)
            except _ValidationError as e:
                raise ValidationError(path, e)

    return config


def _validate_value(option, value, valid_types=_VALID_TYPES):
    """Validates an option value."""

    value_type = type(value)

    if value_type not in valid_types:
        raise _ValidationError(option,
            "{option} has an invalid value type ({type}). Allowed types: {valid_types}.",
            option=option, type=value_type.__name__,
            valid_types=", ".join(t.__name__ for t in valid_types))

    if value_type is dict:
        value = _validate_dict(option, value)
    elif value_type is list:
        value = _validate_list(option, value)
    elif value_type is tuple:
        value = _validate_tuple(option, value)
    elif value_type is set:
        value = _validate_set(option, value)
    elif value_type is bytes:
        try:
            value = value.decode()
        except UnicodeDecodeError as e:
            raise _ValidationError(option, "{0} has an invalid value: {1}.", option, e)

    return value


def _validate_dict(option, dictionary):
    """Validates a dictionary."""

    for key, value in tuple(dictionary.items()):
        valid_key = _validate_value("A {0}'s key".format(option),
            key, valid_types=_BASIC_TYPES)

        valid_value = _validate_value("{0}[{1}]".format(option, repr(key)), value)

        if valid_key is not key:
            del dictionary[key]
            dictionary[valid_key] = valid_value
        elif valid_value is not value:
            dictionary[valid_key] = valid_value

    return dictionary


def _validate_list(option, sequence):
    """Validates a list."""

    for index, value in enumerate(sequence):
        valid_value = _validate_value("{0}[{1}]".format(option, index), value)
        if valid_value is not value:
            sequence[index] = valid_value

    return sequence


def _validate_tuple(option, sequence):
    """Validates a tuple."""

    return [
        _validate_value("{0}[{1}]".format(option, index), value)
        for index, value in enumerate(sequence)
    ]


def _validate_set(option, sequence):
    """Validates a set."""

    return [
        _validate_value("A {0}'s key".format(option), value)
        for value in sequence
    ]
