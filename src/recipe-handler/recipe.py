import argparse
import sys

import sources
import processors
import sinks
import jobs


class GrabParams(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(GrabParams, self).__init__(option_strings, dest, nargs=nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        name = values[0]
        params = values[1:]

        if not getattr(namespace, self.dest):
            setattr(namespace, self.dest, [])

        getattr(namespace, self.dest).append({"name": name, "params": params})


class ExtendedHelp(argparse._HelpAction):
    def __call__(self, parser, namespace, values, option_string=None):
        parser.epilog = "\n".join(epilog_lines_extended)
        super().__call__(parser, namespace, values, option_string)


def gather_help(items):
    result = []
    for item in items:
        desc = item.__doc__
        desc = "\n".join(map(lambda x: x.strip(), desc.split("\n")))
        desc += "\n"
        text = item._parser.format_help().strip()
        updated_text = []

        for line in text.split("\n"):
            updated_text.append("\t" + line)

        text = "\n".join(updated_text)
        if len(text.split(item.name)[1]) == 0:
            text += " <no arguments>"
        result.append(item.name + ": " + desc + "\n" + text + "\n")
    return "\n".join(result)


def bold(string):
    return "\033[1m" + string + "\033[0;0m"


epilog_lines = [
    "Sources produce named data streams.",
    "Processors read these streams, and can modify them or create new ones.",
    "Sinks read streams.",
    "Each command is executed in sequence, from left to right.",
    "Use --help for more details",
]
epilog_lines.append(bold("Sources:"))
epilog_lines.append(", ".join(sources.sources.keys()))
epilog_lines.append(bold("Processors:"))
epilog_lines.append(", ".join(processors.processors.keys()))
epilog_lines.append(bold("Sinks:"))
epilog_lines.append(", ".join(sinks.sinks.keys()))
epilog_lines.append("")
epilog_lines.append("For more detailed help, use --help")
epilog_lines.append("")

epilog_lines_extended = []

epilog_lines_extended.append(" ")
epilog_lines_extended.append(bold("Sources:"))
epilog_lines_extended.append(gather_help(sources.sources.values()))
epilog_lines_extended.append(" ")
epilog_lines_extended.append(bold("Processors:"))
epilog_lines_extended.append(gather_help(processors.processors.values()))
epilog_lines_extended.append(" ")
epilog_lines_extended.append(bold("Sinks:"))
epilog_lines_extended.append(gather_help(sinks.sinks.values()))
epilog_lines_extended.append(" ")


def construct(choices, nameparam):
    return choices[nameparam["name"]].parse(nameparam["params"])


def execute(module, streams):
    try:
        progress = module.run(streams)
        if progress:
            for update in progress:
                print("==> " + update)
    except:
        print("Error during " + module.name)
        raise


def evaluate(jobSources, jobProcs, jobSinks):
    streams = {}

    for source in jobSources:
        execute(source, streams)
    for processor in jobProcs:
        execute(processor, streams)
    for sink in jobSinks:
        execute(sink, streams)

    print("Job's done")


def process(args):
    streams = {}
    sourceModules = []
    processorModules = []
    sinkModules = []

    for source in args.source:
        sourceModules.append(construct(sources.sources, source))
    for process in args.process:
        processorModules.append(construct(processors.processors, process))
    for sink in args.sink:
        sinkModules.append(construct(sinks.sinks, sink))

    evaluate(sourceModules, processorModules, sinkModules)


def do_job(job, args):
    sou, pro, sin = job.execute(args)
    evaluate(sou, pro, sin)


def run():
    parser = argparse.ArgumentParser("recipe.py")

    subparsers = parser.add_subparsers(help="mode", dest="mode")
    subparsers.required = True

    config = subparsers.add_parser(
        "config",
        help="Manually construct a pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,
        epilog="\n".join(epilog_lines),
    )

    config.set_defaults(func=process)

    config.add_argument(
        "--source",
        metavar=("name", "param"),
        action=GrabParams,
        nargs="+",
        required=True,
    )

    config.add_argument(
        "--process",
        metavar=("name", "param"),
        action=GrabParams,
        nargs="+",
        required=True,
    )

    config.add_argument(
        "--sink", metavar=("name", "param"), action=GrabParams, nargs="+", required=True
    )

    config.add_argument(
        "-h", action="help", default=argparse.SUPPRESS, help="Show this help and exit"
    )

    config.add_argument(
        "--help",
        action=ExtendedHelp,
        default=argparse.SUPPRESS,
        help="Show extended help and exit",
    )

    job = subparsers.add_parser("job", help="Run a preconfigured job")

    job_parsers = job.add_subparsers(help="Which job to run", dest="job")

    job.set_defaults(func=None)

    for jobname in jobs.jobs:
        job_choice = jobs.jobs[jobname]
        job_parser = job_parsers.add_parser(job_choice.name, help=job_choice.__doc__)
        job_choice.setup_parser(job_parser)
        job_parser.set_defaults(
            func=lambda args, job_choice=job_choice: do_job(job_choice, args)
        )

    # argparse does not work quite right
    # it doesn't give help help for a subparser if there are no further args
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    if len(sys.argv) == 2:
        if sys.argv[1] == "config":
            config.print_help(sys.stderr)
            sys.exit(1)
        elif sys.argv[1] == "job":
            job.print_help(sys.stderr)
            sys.exit(1)

    args = parser.parse_args()

    if args.func:
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    run()
