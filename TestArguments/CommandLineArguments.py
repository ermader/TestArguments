"""\
Command line argument processor.

Created on September 16, 2021

@author Eric Mader
"""

from FontDocTools.ArgumentIterator import ArgumentIterator

functionType = type(lambda a: a)
tupleType = type((1,1))

class CommandLineOption:
    def __init__(self, option, processor, arg, prop, defaultValue, required=True):
        self._option = f"--{option}"
        self._processor = processor
        self._arg = arg
        self._prop = prop
        self._defaultValue = defaultValue
        self._required = required

    @staticmethod
    def valueFromDict(dict, key, type):
        try:
            return dict[key]
        except:
            raise ValueError(f"invalid {type}: {key}")

    @staticmethod
    def booleanFromArgument(argument):
        return argument if type(argument) == type(True) else True

    def getArg(self, arguments):
        return self.arg(arguments) if type(self.arg) == functionType else self.arg

    def getProp(self, s, value):
        return self.processor(s, value) if self.processor else value

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
    def __init__(self):
        self._options = []

    def processArguments(self, argumentList):
        arguments = ArgumentIterator(argumentList)
        argumentsSeen = {}
        dict = self.__dict__

        for argument in arguments:
            if argument in argumentsSeen:
                raise ValueError(f"Duplicate option: \"{argument}\"")
            argumentsSeen[argument] = True

            for option in self._options:
                if option.option == argument:
                    arg = option.getArg(arguments)
                    value = option.getProp(self, arg)
                    if type(option.prop) == tupleType:
                        for p, v in zip(option.prop, value):
                            dict[p] = v
                    else:
                        dict[option.prop] = value
                    break
            else:
                raise ValueError(f"Unrecognized option: \"{argument}\"")

        missingOptions = []
        for option in self._options:
            if option.required and option.option not in argumentsSeen:
                missingOptions.append(f"\"{option.option}\"")

        if missingOptions:
            raise ValueError(f"Missing options: {', '.join(missingOptions)}")

        self.completeInit(argumentsSeen)

    def completeInit(self, argumentsSeen):
        """\
        Complete initialization of a CommandLineArgs after some values have
        been set from the argument list.
        Fill in defaults for non-required options.
        Raise ValueError if invalid option combinations are detected.
        """
        dict = self.__dict__
        for option in self._options:
            if option.option not in argumentsSeen:
                dict[option.prop] = option.getProp(self, option.defaultValue)

        return  # nothing else to check

    def setProps(self, propsDict):
        """\
        Set properties from propsDict.
        Keys are property names and values are the values to be set.
        Values are processed using the process member in the corresponding
        CommandLineOption.
        This won't work for options where the prop is a tuple.
        """
        dict = self.__dict__
        for option in self._options:
            prop = option.prop
            if prop in propsDict:
                dict[prop] = option.getProp(self, propsDict[prop])