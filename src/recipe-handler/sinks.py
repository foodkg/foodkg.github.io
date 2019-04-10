from module import Module
import inspect
import sys
import os
import rdflib
import jsonpickle
import data
import csv
import tqdm


class _Sink(Module):
    """Receives and stores objects."""


class Null(_Sink):
    """Doesn't do anything."""

    name = "null"

    def run(self, streams):
        pass


class Stdout(_Sink):
    """Writes out objects to stdout (mostly for debugging)."""

    name = "stdout"

    def __init__(self, streams):
        super().__init__()
        self.streams = streams

    @classmethod
    def _init_parser(cls):
        cls._parser.add_argument(
            "streams",
            metavar="stream",
            help="Which datastreams to write out",
            nargs="+",
        )

    def run(self, streams):
        for id in self.streams:
            stream = streams[id]
            for object in stream:
                print(object)


class File(_Sink):
    """Writes out objects as JSON."""

    name = "file"

    def __init__(self, file, streams):
        super().__init__()
        self.file = file
        self.streams = streams

    @classmethod
    def _init_parser(cls):
        cls._parser.add_argument("file", help="The filename to write out to")
        cls._parser.add_argument(
            "streams",
            metavar="stream",
            help="Which datastreams to write out",
            nargs="+",
        )

    def run(self, streams):
        with open(self.file, "w") as file:
            for id in self.streams:
                stream = streams[id]
                for object in tqdm.tqdm(stream):
                    file.write(jsonpickle.dumps(object))


class CSV(_Sink):
    """Writes out objects as CSV."""

    name = "csv"

    def __init__(self, file, streams):
        super().__init__()
        self.file = file
        self.streams = streams

    @classmethod
    def _init_parser(cls):
        cls._parser.add_argument("file", help="The filename to write out to")
        cls._parser.add_argument(
            "streams",
            metavar="stream",
            help="Which datastreams to write out",
            nargs="+",
        )

    def run(self, streams):
        with open(self.file, "w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            for id in self.streams:
                yield "Starting stream: " + id

                stream = streams[id]
                for object in tqdm.tqdm(stream):
                    if type(object) == list:
                        writer.writerow(flatten(object))
                    elif issubclass(object.__class__, data._Data):
                        writer.writerow(object.__array__())
                    else:
                        writer.writerow([object])


def flatten(object):
    if type(object) == list:
        result = []
        for item in object:
            result += flatten(item)
        return result
    else:
        return [object]


class RDFFile(_Sink):
    """Writes out objects as RDF data."""

    name = "rdf"

    def __init__(self, file, format, streams):
        super().__init__()
        self.file = file
        self.format = format
        self.streams = streams

    @classmethod
    def _init_parser(cls):
        super()._init_parser()
        cls._parser.add_argument("file", help="The filename to write out to")
        cls._parser.add_argument("format", help="The format to serialize the data to")
        cls._parser.add_argument(
            "streams",
            metavar="stream",
            help="Which datastreams to write out",
            nargs="+",
        )

    def run(self, streams):

        g = rdflib.Graph()
        g.namespace_manager.bind("recipe-kb", "http://idea.rpi.edu/heals/kb/", True)

        for id in self.streams:
            stream = streams[id]
            for object in tqdm.tqdm(stream):
                for triple in object.__rdf__(None):
                    g.add(triple[0:3])

        with open(self.file, "wb") as file:
            file.write(g.serialize(format=self.format))


class RDFNanopubs(_Sink):
    """Writes out objects as trig nanopublications."""

    name = "nanopub"

    def __init__(self, file, streams, cutoff):
        super().__init__()
        self.file = file
        self.streams = streams
        self.cutoff = cutoff

    @classmethod
    def _init_parser(cls):
        super()._init_parser()
        cls._parser.add_argument("file", help="The filename to write out to")
        cls._parser.add_argument(
            "streams",
            metavar="stream",
            help="Which datastreams to write out",
            nargs="+",
        )
        cls._parser.add_argument(
            "++cutoff",
            help="If set, starts a new .trig file after adding this many quads",
            default=None,
            type=int,
            action="store",
            nargs="?"
        )

    def run(self, streams):

        counter = 1

        base_name, ext = os.path.splitext(self.file)

        d = rdflib.Dataset()
        d.namespace_manager.bind("np", data.NP, True)
        d.namespace_manager.bind("recipe-kb", data.BASE, True)
        d.namespace_manager.bind("prov", data.PROV, True)
        d.namespace_manager.bind("owl", data.OWL, True)


        for id in self.streams:
            yield "Starting stream: " + id
            stream = streams[id]

            for object in tqdm.tqdm(stream):
                for quad in object.__publish__():
                    if self.cutoff and len(d) > self.cutoff:
                        with open(base_name + "-" + str(counter) + ext, "wb") as file:
                            yield "Beginning serialization"
                            file.write(d.serialize(format="trig"))
                        counter += 1

                        yield("Beginning new split")
                        d = rdflib.Dataset()
                        d.namespace_manager.bind("np", data.NP, True)
                        d.namespace_manager.bind("recipe-kb", data.BASE, True)
                        d.namespace_manager.bind("prov", data.PROV, True)

                    d.add(quad)

        yield "All done, serializing what's left"
    
        suffix = "-" + str(counter) if counter > 1 else ""

        with open(base_name + suffix + ext, "wb") as file:
            yield "Beginning serialization"
            file.write(d.serialize(format="trig"))


__all__ = []
_locals = dict(locals())  # pylint: disable=invalid-name
sinks = {}  # pylint: disable=invalid-name


def _setup():
    classes = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    for _, obj in classes:
        if issubclass(obj, _Sink) and obj != _Sink:
            __all__.append(obj.__name__)
            sinks[obj.name] = obj


_setup()
