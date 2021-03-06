# -*- coding: utf8 -*-
"""
    This is part of shot detector.
    Produced by w495 at 2017.05.04 04:18:27
"""

from __future__ import absolute_import, division, print_function

import argparse
import os
import re
import sys
import types

if sys.version_info >= (3, 0):
    from io import StringIO
else:
    # noinspection PyUnresolvedReferences,PyUnresolvedReferences
    from StringIO import StringIO

if sys.version_info < (2, 7):
    # noinspection PyUnresolvedReferences
    from ordereddict import OrderedDict
else:
    from collections import OrderedDict

# noinspection PyProtectedMember
ACTION_TYPES_THAT_DONT_NEED_A_VALUE = {
    argparse._StoreTrueAction,
    argparse._StoreFalseAction,
    argparse._CountAction,
    argparse._StoreConstAction,
    argparse._AppendConstAction
}

# global ConfigArgParser instances
_parsers = {}


def init_argument_parser(name=None, **kwargs):
    """
        Creates a global ConfigArgParser instance 
        with the given name, passing any args other than "name" 
        to the ConfigArgParser constructor. This instance 
        can then be retrieved using get_argument_parser(..)
    """

    if name is None:
        name = "default"

    if name in _parsers:
        # noinspection PyPep8
        raise ValueError(
            ("kwargs besides 'name' can only be passed in the"
             " first time. '%s' ConfigArgParser already exists: %s") % (
                name, _parsers[name]))

    # noinspection PyPep8
    kwargs.setdefault('formatter_class',
                      argparse.ArgumentDefaultsHelpFormatter)
    kwargs.setdefault('conflict_handler', 'resolve')
    _parsers[name] = ConfigArgParser(**kwargs)


def get_argument_parser(name=None, **kwargs):
    # noinspection PyPep8
    """Returns the global ConfigArgParser instance with the given name. The 1st
        time this function is called, a new ConfigArgParser instance will be created
        for the given name, and any args other than "name" will be passed on to the
        ConfigArgParser constructor.
        """
    if name is None:
        name = "default"

    if len(kwargs) > 0 or name not in _parsers:
        init_argument_parser(name, **kwargs)

    return _parsers[name]


# noinspection PyPep8
class ArgumentDefaultsRawHelpFormatter(
    argparse.ArgumentDefaultsHelpFormatter,
    argparse.RawTextHelpFormatter,
    argparse.RawDescriptionHelpFormatter):
    # noinspection PyPep8
    """HelpFormatter that adds default values AND doesn't do line-wrapping"""
    pass


# used while parsing args to keep track of where they came from
_COMMAND_LINE_SOURCE_KEY = "command_line"
_ENV_VAR_SOURCE_KEY = "environment_variables"
_CONFIG_FILE_SOURCE_KEY = "config_file"
_DEFAULTS_SOURCE_KEY = "defaults"


# noinspection PyPep8
class ConfigArgParser(argparse.ArgumentParser):
    """Drop-in replacement for argparse.ConfigArgParser that adds support for
    environment variables and .ini or .yaml-style config files.
    """

    def __init__(self,
                 prog=None,
                 usage=None,
                 description=None,
                 epilog=None,
                 version=None,
                 parents=None,
                 formatter_class=argparse.HelpFormatter,
                 prefix_chars='-',
                 fromfile_prefix_chars=None,
                 argument_default=None,
                 conflict_handler='error',
                 add_help=True,

                 add_config_file_help=True,
                 add_env_var_help=True,

                 auto_env_var_prefix=None,

                 config_file_parser=None,
                 default_config_files=None,
                 ignore_unknown_config_file_keys=False,
                 allow_unknown_config_file_keys=False,  # deprecated

                 args_for_setting_config_path=None,
                 config_arg_is_required=False,
                 config_arg_help_message="config file path",

                 args_for_writing_out_config_file=None,
                 write_out_config_file_arg_help_message="takes the current command line "
                                                        "args and writes them out to a config file at the given path, then "
                                                        "exits"
                 ):

        # noinspection PyPep8
        """Supports all the same args as the argparse.ConfigArgParser
                constructor, as well as the following additional args.
        
                Additional Args:
                    add_config_file_help: Whether to add a description of config file
                        syntax to the help message.
                    add_env_var_help: Whether to add something to the help message for
                        args that can be set through environment variables.
                    auto_env_var_prefix: If set to a string instead of None, all config-
                        file-settable options will become also settable via environment
                        variables whose names are this prefix followed by the config
                        file key, all in upper case. (eg. setting this to "foo_" will
                        allow an arg like "--my-arg" to also be set via the FOO_MY_ARG
                        environment variable)
                    config_file_parser: An instance of a parser to be used for parsing
                        config files. Default: ConfigFileParser()
                    default_config_files: When specified, this list of config files will
                        be parsed in order, with the values from each config file
                        taking precedence over previous ones. This allows an application
                        to look for config files in multiple standard locations such as
                        the install directory, home directory, and current directory:
                        ["<install dir>/app_config.ini",
                        "~/.my_app_config.ini",
                        "./app_config.txt"]
                    ignore_unknown_config_file_keys: If true, settings that are found
                        in a config file but don't correspond to any defined
                        configargparse args will be ignored. If false, they will be
                        processed and appended to the commandline like other args, and
                        can be retrieved using parse_known_args() instead of parse_args()
                    allow_unknown_config_file_keys:
                        @deprecated
                        Use ignore_unknown_config_file_keys instead.
        
                        If true, settings that are found in a config file but don't
                        correspond to any defined configargparse args, will still be
                        processed and appended to the command line (eg. for
                        parsing with parse_known_args()). If false, they will be ignored.
        
                    args_for_setting_config_path: A list of one or more command line
                        args to be used for specifying the config file path
                        (eg. ["-c", "--config-file"]). Default: []
                    config_arg_is_required: When args_for_setting_config_path is set,
                        set this to True to always require users to provide a config path.
                    config_arg_help_message: the help message to use for the
                        args listed in args_for_setting_config_path.
                    args_for_writing_out_config_file: A list of one or more command line
                        args to use for specifying a config file output path. If
                        provided, these args cause configargparse to write out a config
                        file with settings based on the other provided commandline args,
                        environment variants and defaults, and then to exit.
                        (eg. ["-w", "--write-out-config-file"]). Default: []
                    write_out_config_file_arg_help_message: The help message to use for
                        the args in args_for_writing_out_config_file.
                """

        if not parents:
            # noinspection PyPep8
            parents = list()

        if not default_config_files:
            default_config_files = list()

        if not args_for_setting_config_path:
            args_for_setting_config_path = list()

        if not args_for_writing_out_config_file:
            args_for_writing_out_config_file = list()

        self._source_to_settings = None

        self._add_config_file_help = add_config_file_help
        self._add_env_var_help = add_env_var_help
        self._auto_env_var_prefix = auto_env_var_prefix

        # extract kwargs that can be passed to the super constructor
        # noinspection PyPep8
        kwargs_for_super = dict(
            (k, v) for k, v in locals().items() if k in [
                "prog", "usage", "description", "epilog", "version",
                "parents",
                "formatter_class", "prefix_chars",
                "fromfile_prefix_chars",
                "argument_default", "conflict_handler", "add_help"])
        if sys.version_info >= (3, 3) and "version" in kwargs_for_super:
            # noinspection PyPep8
            del kwargs_for_super[
                "version"]  # version arg deprecated in v3.3

        argparse.ArgumentParser.__init__(self, **kwargs_for_super)

        # parse the additional args
        if config_file_parser is None:
            self._config_file_parser = ConfigFileParser()
        else:
            self._config_file_parser = config_file_parser
        self._default_config_files = default_config_files
        # noinspection PyPep8
        self._ignore_unknown_config_file_keys = ignore_unknown_config_file_keys \
                                                or allow_unknown_config_file_keys
        if args_for_setting_config_path:
            # noinspection PyPep8
            self.add_argument(*args_for_setting_config_path,
                              dest="config_file",
                              required=config_arg_is_required,
                              help=config_arg_help_message,
                              is_config_file_arg=True)

        if args_for_writing_out_config_file:
            # noinspection PyPep8
            self.add_argument(*args_for_writing_out_config_file,
                              dest="write_out_config_file_to_this_path",
                              metavar="CONFIG_OUTPUT_PATH",
                              help=write_out_config_file_arg_help_message,
                              is_write_out_config_file_arg=True)

    def parse_args(self, args=None, namespace=None,
                   config_file_contents=None, env_vars=os.environ):
        # noinspection PyPep8
        """Supports all the same args as the ConfigArgParser.parse_args(..),
                as well as the following additional args.
        
                Additional Args:
                    args: a list of args as in argparse, or a string (eg. "-x -y bla")
                    config_file_contents: String. Used for testing.
                    env_vars: Dictionary. Used for testing.
                """
        # noinspection PyPep8
        args, argv = self.parse_known_args(args=args,
                                           namespace=namespace,
                                           config_file_contents=config_file_contents,
                                           env_vars=env_vars)
        if argv:
            self.error('unrecognized arguments: %s' % ' '.join(argv))
        return args

    # noinspection PyPep8
    def parse_known_args(self, args=None, namespace=None,
                         config_file_contents=None,
                         env_vars=os.environ):
        # noinspection PyPep8
        """Supports all the same args as the ConfigArgParser.parse_args(..),
                as well as the following additional args.
        
                Additional Args:
                    args: a list of args as in argparse, or a string (eg. "-x -y bla")
                    config_file_contents: String. Used for testing.
                    env_vars: Dictionary. Used for testing.
                """
        if args is None:
            args = sys.argv[1:]
        elif type(args) == str:
            args = args.split()
        else:
            args = list(args)

        for a in self._actions:
            a.is_positional_arg = not a.option_strings

        # maps string describing the source (eg. env var) to a settings dict
        # to keep track of where values came from (used by print_values())
        self._source_to_settings = OrderedDict()
        if args:
            # noinspection PyPep8
            a_v_pair = (
                None, list(args))  # copy args list to isolate changes
            # noinspection PyPep8
            self._source_to_settings[_COMMAND_LINE_SOURCE_KEY] = {
                '': a_v_pair}

        # handle auto_env_var_prefix __init__ arg by setting a.env_var as needed
        if self._auto_env_var_prefix is not None:
            for a in self._actions:
                config_file_keys = self.get_possible_config_keys(a)
                # noinspection PyPep8
                if config_file_keys and not (
                                    a.env_var or a.is_positional_arg
                            or a.is_config_file_arg or a.is_write_out_config_file_arg):
                    # noinspection PyPep8
                    stripped_config_file_key = config_file_keys[
                        0].strip(
                        self.prefix_chars)
                    # noinspection PyPep8
                    a.env_var = (self._auto_env_var_prefix +
                                 stripped_config_file_key).replace('-',
                                                                   '_').upper()

        # add env var settings to the commandline that aren't there already
        env_var_args = []
        # noinspection PyPep8
        actions_with_env_var_values = [a for a in self._actions
                                       if
                                       not a.is_positional_arg and a.env_var and a.env_var in env_vars
                                       and not already_on_command_line(
                                           args, a.option_strings)]
        for action in actions_with_env_var_values:
            key = action.env_var
            value = env_vars[key]
            env_var_args += self.convert_setting_to_command_line_arg(
                action, key, value)

        args += env_var_args

        if env_var_args:
            self._source_to_settings[_ENV_VAR_SOURCE_KEY] = OrderedDict(
                [(a.env_var, (a, env_vars[a.env_var]))
                 for a in actions_with_env_var_values])

        # prepare for reading config file(s)
        # noinspection PyPep8
        known_config_keys = dict(
            (config_key, action) for action in self._actions
            for config_key in self.get_possible_config_keys(action))

        # open the config file(s)
        if config_file_contents:
            stream = StringIO(config_file_contents)
            stream.name = "method arg"
            config_streams = [stream]
        else:
            config_streams = self._open_config_files(args)

        config_settings = OrderedDict()
        # parse each config file
        # noinspection PyPep8
        for stream in config_streams[::-1]:
            try:
                config_settings = self._config_file_parser.parse(stream)
            except ConfigFileParserException as e:
                self.error(e)
            finally:
                if hasattr(stream, "close"):
                    stream.close()

            # add each config setting to the commandline unless it's there already
            config_args = []
            for key, value in config_settings.items():
                if key in known_config_keys:
                    action = known_config_keys[key]
                    discard_this_key = already_on_command_line(
                        args, action.option_strings)
                else:
                    action = None
                    # noinspection PyPep8
                    discard_this_key = self._ignore_unknown_config_file_keys or \
                                       already_on_command_line(
                                           args,
                                           self.get_command_line_key_for_unknown_config_file_setting(
                                               key))

                if not discard_this_key:
                    # noinspection PyPep8
                    config_args += self.convert_setting_to_command_line_arg(
                        action, key, value)
                    # noinspection PyPep8
                    source_key = "%s|%s" % (
                        _CONFIG_FILE_SOURCE_KEY, stream.name)
                    if source_key not in self._source_to_settings:
                        # noinspection PyPep8
                        self._source_to_settings[
                            source_key] = OrderedDict()
                    # noinspection PyPep8
                    self._source_to_settings[source_key][key] = (
                        action, value)

            args += config_args

        # save default settings for use by print_values()
        default_settings = OrderedDict()
        for action in self._actions:
            # noinspection PyPep8
            cares_about_default_value = (not action.is_positional_arg or
                                         action.nargs in [OPTIONAL,
                                                          ZERO_OR_MORE])
            # noinspection PyPep8
            if (already_on_command_line(args, action.option_strings) or
                    not cares_about_default_value or
                        action.default is None or
                        action.default == SUPPRESS or
                        type(
                            action) in ACTION_TYPES_THAT_DONT_NEED_A_VALUE):
                continue
            else:
                if action.option_strings:
                    key = action.option_strings[-1]
                else:
                    key = action.dest
                default_settings[key] = (action, str(action.default))

        if default_settings:
            # noinspection PyPep8
            self._source_to_settings[
                _DEFAULTS_SOURCE_KEY] = default_settings

        # parse all args (including commandline, config file, and env var)
        # noinspection PyPep8
        namespace, unknown_args = argparse.ArgumentParser.parse_known_args(
            self, args=args, namespace=namespace)

        # handle any args that have is_write_out_config_file_arg set to true
        # noinspection PyPep8
        user_write_out_config_file_arg_actions = [a for a in
                                                  self._actions
                                                  if getattr(a,
                                                             "is_write_out_config_file_arg",
                                                             False)]
        if user_write_out_config_file_arg_actions:
            output_file_paths = []
            # noinspection PyPep8
            for action in user_write_out_config_file_arg_actions:
                # check if the user specified this arg on the commandline
                output_file_path = getattr(namespace, action.dest, None)
                if output_file_path:
                    # validate the output file path
                    try:
                        # noinspection PyUnusedLocal
                        with open(output_file_path, "w") as output_file:
                            output_file_paths.append(output_file_path)
                    except IOError as e:
                        # noinspection PyPep8
                        raise ValueError(
                            "Couldn't open %s for writing: %s" % (
                                output_file_path, e))

            if output_file_paths:
                # generate the config file contents
                config_items = self.get_items_for_config_file_output(
                    self._source_to_settings, namespace)
                # noinspection PyPep8
                contents = self._config_file_parser.serialize(
                    config_items)
                for output_file_path in output_file_paths:
                    with open(output_file_path, "w") as output_file:
                        output_file.write(contents)
                if len(output_file_paths) == 1:
                    output_file_paths = output_file_paths[0]
                # noinspection PyPep8
                self.exit(message="Wrote config file to " + str(
                    output_file_paths))
        return namespace, unknown_args

    def get_command_line_key_for_unknown_config_file_setting(self, key):
        # noinspection PyPep8
        """Compute a commandline arg key to be used for a config file setting
                that doesn't correspond to any defined configargparse arg (and so
                doesn't have a user-specified commandline arg key).
        
                Args:
                    key: The config file key that was being set.
                """
        key_without_prefix_chars = key.strip(self.prefix_chars)
        # noinspection PyPep8
        command_line_key = self.prefix_chars[
                               0] * 2 + key_without_prefix_chars

        return command_line_key

    def get_items_for_config_file_output(self, source_to_settings,
                                         parsed_namespace):
        # noinspection PyPep8
        """Does the inverse of config parsing by taking parsed values and
                converting them back to a string representing config file contents.
        
                Args:
                    source_to_settings: the dictionary created within parse_known_args()
                    parsed_namespace: namespace object created within parse_known_args()
                Returns:
                    an OrderedDict with the items to be written to the config file
                """
        config_file_items = OrderedDict()
        for source, settings in source_to_settings.items():
            if source == _COMMAND_LINE_SOURCE_KEY:
                _, existing_command_line_args = settings['']
                for action in self._actions:
                    # noinspection PyPep8
                    config_file_keys = self.get_possible_config_keys(
                        action)
                    # noinspection PyPep8
                    if config_file_keys and not action.is_positional_arg and \
                            already_on_command_line(
                                existing_command_line_args,
                                action.option_strings):
                        # noinspection PyPep8
                        value = getattr(parsed_namespace, action.dest,
                                        None)
                        if value is not None:
                            if type(value) is bool:
                                value = str(value).lower()
                            elif type(value) is list:
                                # noinspection PyPep8
                                value = "[" + ", ".join(
                                    map(str, value)) + "]"
                            # noinspection PyPep8
                            config_file_items[
                                config_file_keys[0]] = value

            elif source == _ENV_VAR_SOURCE_KEY:
                for key, (action, value) in settings.items():
                    # noinspection PyPep8
                    config_file_keys = self.get_possible_config_keys(
                        action)
                    if config_file_keys:
                        # noinspection PyPep8
                        value = getattr(parsed_namespace, action.dest,
                                        None)
                        if value is not None:
                            # noinspection PyPep8
                            config_file_items[
                                config_file_keys[0]] = value
            elif source.startswith(_CONFIG_FILE_SOURCE_KEY):
                for key, (action, value) in settings.items():
                    config_file_items[key] = value
            elif source == _DEFAULTS_SOURCE_KEY:
                for key, (action, value) in settings.items():
                    # noinspection PyPep8
                    config_file_keys = self.get_possible_config_keys(
                        action)
                    if config_file_keys:
                        # noinspection PyPep8
                        value = getattr(parsed_namespace, action.dest,
                                        None)
                        if value is not None:
                            # noinspection PyPep8
                            config_file_items[
                                config_file_keys[0]] = value
        return config_file_items

    def convert_setting_to_command_line_arg(self, action, key, value):
        # noinspection PyPep8
        """Converts a config file or env var key/value to a list of
                commandline args to append to the commandline.
        
                Args:
                    action: The action corresponding to this setting, or None if this
                        is a config file setting that doesn't correspond to any
                        defined configargparse arg.
                    key: The config file key or env var name
                    value: The raw value string from the config file or env var
                """
        if type(value) != str:
            raise ValueError("type(value) != str: %s" % str(value))

        args = []
        if action is None:
            # noinspection PyPep8
            command_line_key = \
                self.get_command_line_key_for_unknown_config_file_setting(
                    key)
        else:
            command_line_key = action.option_strings[-1]

        if value.lower() == "true":
            if action is not None:
                # noinspection PyPep8
                if type(
                        action) not in ACTION_TYPES_THAT_DONT_NEED_A_VALUE:
                    # noinspection PyPep8
                    self.error(
                        "%s set to 'True' rather than a value" % key)
            # noinspection PyPep8
            args.append(command_line_key)
        elif value.startswith("[") and value.endswith("]"):
            if action is not None:
                # noinspection PyProtectedMember
                if type(action) != argparse._AppendAction:
                    # noinspection PyPep8
                    self.error(
                        ("%s can't be set to a list '%s' unless its "
                         "action type is changed to 'append'") % (
                            key, value))
            for list_elem in value[1:-1].split(","):
                # noinspection PyPep8
                args.append(command_line_key)
                # noinspection PyPep8
                args.append(list_elem.strip())
        else:
            if action is not None:
                if type(action) in ACTION_TYPES_THAT_DONT_NEED_A_VALUE:
                    # noinspection PyPep8
                    self.error(
                        "%s is a flag but is being set to '%s'" % (
                            key, value))
            # noinspection PyPep8
            args.append(command_line_key)
            # noinspection PyPep8
            args.append(value)
        return args

    def get_possible_config_keys(self, action):
        # noinspection PyPep8
        """This method decides which actions can be set in a config file and
                what their keys will be. It returns a list of 0 or more config keys that
                can be used to set the given action's value in a config file.
                """
        keys = []
        for arg in action.option_strings:
            if any([arg.startswith(2 * c) for c in self.prefix_chars]):
                # noinspection PyPep8
                keys += [arg[2:],
                         arg]  # eg. for '--bla' return ['bla', '--bla']

        return keys

    # noinspection PyPep8
    def _open_config_files(self, command_line_args):
        # noinspection PyPep8
        """Tries to parse config file path(s) from within command_line_args. 
                Returns a list of opened config files, including files specified on the 
                commandline as well as any default_config_files specified in the
                constructor that are present on disk.
        
                Args:
                    command_line_args: List of all args (already split on spaces)
                """
        # open any default config files
        # noinspection PyPep8
        config_files = [open(f) for f in map(
            os.path.expanduser, self._default_config_files) if
                        os.path.isfile(f)]

        if not command_line_args:
            return config_files

        # list actions with is_config_file_arg=True. Its possible there is more
        # than one such arg.
        # noinspection PyPep8
        user_config_file_arg_actions = [
            a for a in self._actions if
            getattr(a, "is_config_file_arg", False)]

        if not user_config_file_arg_actions:
            return config_files

        # noinspection PyPep8
        for action in user_config_file_arg_actions:
            # try to parse out the config file path by using a clean new
            # ConfigArgParser that only knows this one arg/action.
            arg_parser = argparse.ArgumentParser(
                prefix_chars=self.prefix_chars,
                add_help=False)

            arg_parser._add_action(action)

            # make parser not exit on error by replacing its error method.
            # Otherwise it sys.exits(..) if, for example, config file 
            # is_required=True and user doesn't provide it.
            # noinspection PyUnusedLocal
            def error_method(message):
                """
                
                :param message: 
                :return: 
                """
                pass

            # noinspection PyArgumentList,PyPep8
            arg_parser.error = types.MethodType(error_method,
                                                arg_parser)

            # check whether the user provided a value 
            # noinspection PyPep8
            parsed_arg = arg_parser.parse_known_args(
                args=command_line_args)
            if not parsed_arg:
                continue
            namespace, _ = parsed_arg
            user_config_file = getattr(namespace, action.dest, None)
            if not user_config_file:
                continue
            # validate the user-provided config file path
            user_config_file = os.path.expanduser(user_config_file)
            if not os.path.isfile(user_config_file):
                self.error('File not found: %s' % user_config_file)

            config_files += [open(user_config_file)]

        return config_files

    def format_values(self):
        """Returns a string with all args and settings and where they came from
        (eg. commandline, config file, environment variable or default)
        """
        source_key_to_display_value_map = {
            _COMMAND_LINE_SOURCE_KEY: "Command Line Args: ",
            _ENV_VAR_SOURCE_KEY: "Environment Variables:\n",
            _CONFIG_FILE_SOURCE_KEY: "Config File (%s):\n",
            _DEFAULTS_SOURCE_KEY: "Defaults:\n"
        }

        r = StringIO()
        for source, settings in self._source_to_settings.items():
            source = source.split("|")
            # noinspection PyPep8
            source = source_key_to_display_value_map[source[0]] % tuple(
                source[1:])
            r.write(source)
            for key, (action, value) in settings.items():
                if key:
                    r.write("  %-19s%s\n" % (key + ":", value))
                else:
                    if type(value) is str:
                        r.write("  %s\n" % value)
                    elif type(value) is list:
                        r.write("  %s\n" % ' '.join(value))

        return r.getvalue()

    def print_values(self, file=sys.stdout):
        # noinspection PyPep8
        """Prints the format_values() string (to sys.stdout or another file)."""
        file.write(self.format_values())

    def format_help(self):
        """
        
        :return: 
        """
        msg = ""
        added_config_file_help = False
        added_env_var_help = False
        if self._add_config_file_help:
            default_config_files = self._default_config_files
            cc = 2 * self.prefix_chars[0]  # eg. --
            # noinspection PyPep8
            config_settable_args = [(arg, a) for a in self._actions for
                                    arg in
                                    a.option_strings if
                                    self.get_possible_config_keys(
                                        a) and not
                                    (
                                        a.dest == "help" or a.is_config_file_arg or
                                        a.is_write_out_config_file_arg)]
            # noinspection PyPep8
            config_path_actions = [a for a in
                                   self._actions if
                                   getattr(a, "is_config_file_arg",
                                           False)]

            if config_settable_args and (default_config_files or
                                             config_path_actions):
                # noinspection PyPep8
                self._add_config_file_help = False  # prevent duplication
                added_config_file_help = True

                # noinspection PyPep8
                msg += (
                           "Args that start with '%s' (eg. %s) can also be set in "
                           "a config file") % (
                           cc, config_settable_args[0][0])
                # noinspection PyPep8
                config_arg_string = " or ".join(a.option_strings[0]
                                                for a in
                                                config_path_actions if
                                                a.option_strings)
                if config_arg_string:
                    # noinspection PyPep8
                    config_arg_string = "specified via " + config_arg_string
                if default_config_files or config_arg_string:
                    # noinspection PyPep8
                    msg += " (%s)." % " or ".join(default_config_files +
                                                  [config_arg_string])
                # noinspection PyPep8
                msg += " " + self._config_file_parser.get_syntax_description()

        if self._add_env_var_help:
            env_var_actions = [(a.env_var, a) for a in self._actions
                               if getattr(a, "env_var", None)]
            for env_var, a in env_var_actions:
                env_var_help_string = "   [env var: %s]" % env_var
                if not a.help:
                    a.help = ""
                if env_var_help_string not in a.help:
                    a.help += env_var_help_string
                    added_env_var_help = True
                    # noinspection PyPep8
                    self._add_env_var_help = False  # prevent duplication

        if added_env_var_help or added_config_file_help:
            value_sources = ["defaults"]
            if added_config_file_help:
                value_sources = ["config file values"] + value_sources
            if added_env_var_help:
                # noinspection PyPep8
                value_sources = [
                                    "environment variables"] + value_sources
            # noinspection PyPep8
            msg += (
                       " If an arg is specified in more than one place, then "
                       "commandline values override %s.") % (
                       " which override ".join(value_sources))
        if msg:
            self.description = (self.description or "") + " " + msg

        return argparse.ArgumentParser.format_help(self)


# noinspection PyPep8
class ConfigFileParser(object):
    """
        ...
    """

    @staticmethod
    def parse(stream):
        """Parses a config file and return a dictionary of settings"""

        settings = OrderedDict()
        for i, line in enumerate(stream):
            line = line.strip()
            # noinspection PyPep8
            if not line or line[0] in ["#", ";",
                                       "["] or line.startswith("---"):
                continue
            white_space = "\\s*"
            key = "(?P<key>[^:=;#\s]+?)"
            value1 = white_space + "[:=]" + white_space + "(?P<value>[^;#]+?)"
            # noinspection PyPep8
            value2 = white_space + "[\s]" + white_space + "(?P<value>[^;#\s]+?)"
            comment = white_space + "(?P<comment>\\s[;#].*)?"

            key_only_match = re.match("^" + key + comment + "$", line)
            if key_only_match:
                key = key_only_match.group("key")
                settings[key] = "true"
                continue

            # noinspection PyPep8
            key_value_match = re.match(
                "^" + key + value1 + comment + "$", line) or \
                              re.match(
                                  "^" + key + value2 + comment + "$",
                                  line)
            if key_value_match:
                key = key_value_match.group("key")
                value = key_value_match.group("value")
                settings[key] = value
                continue

            # noinspection PyPep8
            raise ConfigFileParserException(
                "Unexpected line %s in %s: %s" % \
                (i, stream.name, line))
        return settings

    @staticmethod
    def serialize(items):
        # noinspection PyPep8
        """Does the inverse of config parsing by taking parsed values and
                converting them back to a string representing config file contents.
        
                Args:
                    items: an OrderedDict with items to be written to the config file
                Returns:
                    contents of config file as a string
                """
        r = StringIO()
        for key, value in items.items():
            r.write("%s = %s\n" % (key, value))
        return r.getvalue()

    @staticmethod
    def get_syntax_description():
        """
        
        :return: 
        """
        # noinspection PyPep8
        msg = (
            "The recognized syntax for setting (key, value) pairs is based "
            "on the INI and YAML formats (e.g. key=value or foo=TRUE). "
            "For full documentation of the differences from the standards "
            "please refer to the ConfigArgParse documentation.")
        return msg


class ConfigFileParserException(Exception):
    """Raised when config file parsing failed.
    """
    pass


def add_argument(self, *args, **kwargs):
    # noinspection PyPep8
    """
        This method supports the same args as ConfigArgParser.add_argument(..)
        as well as the additional args below.
    
        Additional Args:
            env_var: If set, the value of this environment variable will override
                any config file or default values for this arg (but can itself
                be overridden on the commandline). Also, if auto_env_var_prefix is
                set in the constructor, this env var name will be used instead of
                the automatic name.
            is_config_file_arg: If True, this arg is treated as a config file path
                This provides an alternative way to specify config files in place of
                the ConfigArgParser(fromfile_prefix_chars=..) mechanism.
                Default: False
            is_write_out_config_file_arg: If True, this arg will be treated as a
                config file path, and, when it is specified, will cause
                configargparse to write all current commandline args to this file
                as config options and then exit.
                Default: False
        """

    env_var = kwargs.pop("env_var", None)

    is_config_file_arg = kwargs.pop(
        "is_config_file_arg", None) or kwargs.pop(
        "is_config_file", None)  # for backward compatibility.

    is_write_out_config_file_arg = kwargs.pop(
        "is_write_out_config_file_arg", None)

    action = self.original_add_argument_method(*args, **kwargs)

    action.is_positional_arg = not action.option_strings
    action.env_var = env_var
    action.is_config_file_arg = is_config_file_arg
    action.is_write_out_config_file_arg = is_write_out_config_file_arg

    if action.is_positional_arg and env_var:
        raise ValueError("env_var can't be set for a positional arg.")
    # noinspection PyProtectedMember,PyPep8
    if action.is_config_file_arg and type(
            action) != argparse._StoreAction:
        raise ValueError("arg with is_config_file_arg=True must have "
                         "action='store'")
    if action.is_write_out_config_file_arg:
        error_prefix = "arg with is_write_out_config_file_arg=True "
        # noinspection PyProtectedMember
        if type(action) != argparse._StoreAction:
            raise ValueError(error_prefix + "must have action='store'")
        if is_config_file_arg:
            # noinspection PyPep8
            raise ValueError(error_prefix + "can't also have "
                                            "is_config_file_arg=True")

    return action


def already_on_command_line(existing_args, potential_command_line_args):
    """Utility method for checking if any of the existing_args is
    already present in existing_args
    """
    return any(potential_arg in existing_args
               for potential_arg in potential_command_line_args)


# wrap ConfigArgParser's add_argument(..) method with the one above
# noinspection PyProtectedMember,PyPep8
argparse._ActionsContainer.original_add_argument_method = argparse._ActionsContainer.add_argument
# noinspection PyProtectedMember
argparse._ActionsContainer.add_argument = add_argument

# add all public classes
# and constants from argparse module's namespace to this
# module's namespace so that the 2 modules are truly interchangeable
HelpFormatter = argparse.HelpFormatter
RawDescriptionHelpFormatter = argparse.RawDescriptionHelpFormatter
RawTextHelpFormatter = argparse.RawTextHelpFormatter
ArgumentDefaultsHelpFormatter = argparse.ArgumentDefaultsHelpFormatter
ArgumentError = argparse.ArgumentError
ArgumentTypeError = argparse.ArgumentTypeError
Action = argparse.Action
FileType = argparse.FileType
Namespace = argparse.Namespace
ONE_OR_MORE = argparse.ONE_OR_MORE
OPTIONAL = argparse.OPTIONAL
REMAINDER = argparse.REMAINDER
SUPPRESS = argparse.SUPPRESS
ZERO_OR_MORE = argparse.ZERO_OR_MORE

# create shorter aliases for the key methods and class names
getArgParser = get_argument_parser
getParser = get_argument_parser

ArgParser = ConfigArgParser
Parser = ConfigArgParser

# noinspection PyProtectedMember,PyProtectedMember,PyPep8
argparse._ActionsContainer.add_arg = argparse._ActionsContainer.add_argument
# noinspection PyProtectedMember,PyProtectedMember
argparse._ActionsContainer.add = argparse._ActionsContainer.add_argument

ConfigArgParser.parse = ConfigArgParser.parse_args
ConfigArgParser.parse_known = ConfigArgParser.parse_known_args

RawFormatter = RawDescriptionHelpFormatter
DefaultsFormatter = ArgumentDefaultsHelpFormatter
DefaultsRawFormatter = ArgumentDefaultsRawHelpFormatter
