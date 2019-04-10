"""Base classes and utility functions for the system."""

import argparse


class ParserCreator(type):
    """Provides each subclass of Module with its own parser."""

    # pylint: disable=unused-argument
    def __new__(mcs, name, bases, nmspc):
        """Attaches a fresh parser instance to each class."""
        if "name" in nmspc:
            nmspc["_parser"] = argparse.ArgumentParser(
                prog=nmspc["name"], prefix_chars="+", add_help=False
            )

        if "run" in nmspc:
            nmspc["run"] = bookend(nmspc["run"])

        return super(ParserCreator, mcs).__new__(mcs, name, bases, nmspc)

    # pylint: disable=super-init-not-called, unused-argument
    def __init__(cls, name, bases, nmspc):
        """Recursively sets up the parser for each class."""
        if "_parser" in nmspc:
            cls._init_parser()


class Module(metaclass=ParserCreator):
    """Provides fundamental features for modules, like parsing."""

    name = None

    @classmethod
    def parse(cls, args):
        """Consumes the list of arguments and instantiates an object."""
        parsed = cls._parser.parse_args(args)
        return cls(**vars(parsed))

    @classmethod
    def _init_parser(cls):
        """Adds any needed arguments to the parser for this class."""
        pass


def bookend(func):
    """As the name suggests, this bookends a module with start/end notices."""

    def wrapped(self, streams):
        yield "Starting " + self.name

        invoke = func(self, streams)
        if invoke:
            for yielded in invoke:
                yield "\t" + yielded

        yield "Completed " + self.name

    return wrapped
