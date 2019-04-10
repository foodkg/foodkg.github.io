import argparse
import sys
import os
import subprocess

def run(args):
    procs = args.procs
    start = args.start
    end = args.end

    directory = os.path.split(__file__)[0]

    span = end - start

    step = span // procs

    proc_list = []

    for i in range(procs):
        proc_start = start + step * i
        proc_end = start + step * (i + 1)
        if i == procs - 1:
            proc_end = end
        print(i, proc_start, proc_end)
        proc_args = ["python", directory + "/scrape-sites.py", args.urls, args.cache, str(proc_start), str(proc_end)]
        proc = subprocess.Popen(proc_args)
        proc_list.append(proc)

    for process in proc_list:
        process.wait()

    f = open(args.done_file, "w")
    f.close()

parser = argparse.ArgumentParser(description="Runs many scraper jobs simultaneously.")

parser.add_argument("urls", help="File containing url-id pairs")
parser.add_argument("cache", help="Where to store the pages")
parser.add_argument("procs", type=int, help="How many processes to start")
parser.add_argument("done_file", help="Name of file to create to signal scraping is done")
parser.add_argument("start", type=int, help="Which index to start at")
parser.add_argument("end", type=int, help="Which index to end at")

run(parser.parse_args())
