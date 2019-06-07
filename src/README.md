This repository contains work related to the collection, processing, and analysis of food knowledge.

Make sure to clone the submodules in this repo, by using:

`git clone --recursive [repository-url]`

Or else, clone normally and then update the submodules using:

`git submodule update --init --recursive`.

## Workflow

You'll need `make`, as well as a Python installation (with Python 3.7 available). Python's virtualenv module is used, but is installed automatically.

There are three steps to produce the data and findings from the ISWC paper. Enter each folder and follow the instructions in its README:

1. /src/prep-scripts
2. /src/recipe-handler
3. /src/verify
