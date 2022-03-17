"""\
Command line argument processor.

Created on September 16, 2021

@author Eric Mader
"""

import typing

import types
from FontDocTools.ArgumentIterator import ArgumentIterator


ArgProcessor = typing.Callable[[typing.Any, str], typing.Any]
Argument = typing.Union[typing.Callable[[ArgumentIterator], typing.Any], typing.Any]

# useful for creating unique instances
class _no_object(object):
    pass


class CommandLineOption:
    """\
    An object that represents a command line option.
    """

    def __init__(
        self,
        option: str,
        processor: typing.Optional[ArgProcessor],
        arg: Argument,
        prop: typing.Union[str, tuple[str, ...]],
        defaultValue: typing.Union[typing.Any, tuple[typing.Any, ...]],
        required: bool = True,
    ):
        """\
        Initialize a CommandLineOption object.

        :param option: the name of the option
        :param processor: a function to process the option's extra argument, or None if no processing needed
        :param arg: a function to fetch the option's argument from the command line, or the argument directly
        :param prop: the name of the property to be set in the spec object, or a list of names
        :param defaultValue: the value to be set if the option isn't present on the command line
        :param reauired: True if the object must be present on the command line
        """
        self._option = f"--{option}"
        self._processor = processor
        self._arg = arg
        self._prop = prop
        self._defaultValue = defaultValue
        self._required = required

    @staticmethod
    def valueFromDict(
        dict: dict[str, typing.Any], key: str, type: typing.Any
    ) -> typing.Any:
        """\
        Get a value for the given key in dict, or raise ValueError if the key isn't present.

        :param dict: the dictionary
        :param key: the key
        :param type: a string identifying the type of the value, used in ValueError
        """
        try:
            return dict[key]
        except:
            raise ValueError(f"invalid {type}: {key}")

    @staticmethod
    def booleanFromArgument(argument: typing.Any) -> bool:
        """\
        Get the boolean value of an argument. Called with an ArgumentIterator
        if the option is on the command line, or a boolean to set the default value.

        :param argument: a boolean or an ArgumentIterator
        :return: argument if it's a boolean, otherwise True
        """
        return argument if isinstance(argument, bool) else True

    def getArg(self, arguments: ArgumentIterator):
        """\
        Get the option's argument.

        :param arguments: A function to fetch the argument, or the argument itself
        :return: the argument
        """
        return (
            self.arg(arguments)
            if isinstance(self.arg, types.FunctionType)
            else self.arg
        )

    def getProp(self, s: "CommandLineArgs", arg: typing.Any):
        """\
        Get the option's value to set in the spec object.

        :param s: the spec object
        :param arg: the option's argument
        :return: the value
        """
        return self.processor(s, arg) if self.processor else arg

    def setProp(self, s: typing.Any, arg: Argument):
        """\
        Set the option's props in the spec object.

        :param s: the spec object
        :param arg: the argument
        """
        sd = s.__dict__
        value = self.getProp(s, arg)
        if isinstance(self.prop, tuple):
            for p, v in zip(self.prop, value):
                sd[p] = v
        else:
            sd[self.prop] = value

    @property
    def option(self):
        return self._option

    @property
    def processor(self):
        return self._processor

    @property
    def arg(self):
        return self._arg

    @property
    def prop(self):
        return self._prop

    @property
    def defaultValue(self):
        return self._defaultValue

    @property
    def required(self):
        return self._required


class CommandLineArgs:
    """\
    A base class to hold the results of parsing the command line.
    """

    def __init__(self):
        # base class, so no CommandLineOptions
        self._options: list[CommandLineOption] = []

    def processArguments(self, argumentList: list[str]):
        """\
        Process the command line. Look the argument up in the
        list of CommandLineOptions, get its value and set it in the spec object.

        Set the default value for any unseen arguments.

        Raise ValueError for any unknow options or any missing required options.
        """
        arguments = ArgumentIterator(argumentList)
        argumentsSeen: dict[str, bool] = {}

        for argument in arguments:
            if argument in argumentsSeen:
                raise ValueError(f'Duplicate option: "{argument}"')
            argumentsSeen[argument] = True

            for option in self._options:
                if option.option == argument:
                    arg = option.getArg(arguments)
                    option.setProp(self, arg)
                    break
            else:
                raise ValueError(f'Unrecognized option: "{argument}"')

        # check for any required argument that are missing
        missingOptions: list[str] = []
        for option in self._options:
            if option.required and option.option not in argumentsSeen:
                missingOptions.append(f'"{option.option}"')

        if missingOptions:
            raise ValueError(f"Missing options: {', '.join(missingOptions)}")

        self.completeInit(argumentsSeen)

    def completeInit(self, argumentsSeen: dict[str, bool]):
        """\
        Complete initialization of a CommandLineArgs after some values have
        been set from the argument list.
        Fill in defaults for non-required options that weren't seen.
        Raise ValueError if invalid option combinations are detected.

        :param argumentsSeen: a dictionary of all options seen on the command line
        """
        for option in self._options:
            if option.option not in argumentsSeen:
                option.setProp(self, option.defaultValue)

        return  # nothing else to check

    def setProps(self, propsDict: dict[str, typing.Any]):
        """\
        Set properties from a dictionary.
        Keys are property names and values are the values to be set.
        Values are processed using the process member in the corresponding
        CommandLineOption.

        :param propsDict: the dictionary
        """

        #
        # By doing this here, we're guaranteed that _nothing will
        # be a unique instance that can't be a value in propsDict.
        #
        _nothing = _no_object()

        for option in self._options:
            if not isinstance(option.prop, tuple):
                value = propsDict.get(option.prop, _nothing)
                if value is not _nothing:
                    option.setProp(self, value)
