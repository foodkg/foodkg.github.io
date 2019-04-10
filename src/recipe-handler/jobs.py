"""Prepared workflows."""

import inspect
import sys
import os
import sources
import processors
import sinks


class _Job:
    @classmethod
    def setup_parser(cls, parser):
        parser.set_defaults(func=cls.execute)

class PrepareISWC(_Job):
    """Prepares recipe data for the ISWC paper."""

    name = "iswc"

    @classmethod
    def setup_parser(cls, parser):
        parser.add_argument(
            "recipes", help="An json file containing extended recipe1m data"
        )
        parser.add_argument("usda", help="A csv file containing USDA pairs.")
        parser.add_argument("foodon", help="A csv file containing foodon pairs.")
        parser.add_argument("output", help="Where to write the output data.")
        parser.add_argument("--cutoff", help="How many quads to write into each trig file", default=None, action="store", type=int)

    @classmethod
    def execute(cls, args):
        jobSources, jobProcs, jobSinks = [], [], []

        jobSources.append(sources.Recipe1MExtended(args.recipes, "recipes"))
        jobSources.append(sources.TypedCSV(args.usda, "usda-pairs"))
        jobSources.append(sources.TypedCSV(args.foodon, "foodon-pairs"))

        jobProcs.append(
            processors.Extract("recipes", "ing-names", ["ingredients[]", "name"], True)
        )
        jobProcs.append(
            processors.ResolveNames("ing-names", "usda-pairs", "usda-links", ", ")
        )
        jobProcs.append(
            processors.BundleNanopub("usda-links", "usda-links-bundled")
        )
        jobProcs.append(
            processors.ResolveNames("ing-names", "foodon-pairs", "foodon-links", ", ")
        )
        jobProcs.append(
            processors.BundleNanopub("foodon-links", "foodon-links-bundled")
        )

        jobSinks.append(sinks.RDFNanopubs(args.output + "foodkg-core.trig", ["recipes"], args.cutoff))
        jobSinks.append(sinks.RDFNanopubs(args.output + "foodon-links.trig", ["foodon-links"], args.cutoff))
        jobSinks.append(sinks.RDFNanopubs(args.output + "usda-links.trig", ["usda-links"], args.cutoff))
        
        return jobSources, jobProcs, jobSinks


__all__ = []
_locals = dict(locals())  # pylint: disable=invalid-name
jobs = {}  # pylint: disable=invalid-name


def _setup():
    classes = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    for _, obj in classes:
        if issubclass(obj, _Job) and obj != _Job:
            __all__.append(obj.__name__)
            jobs[obj.name] = obj


_setup()
