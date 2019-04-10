# Preparation Scripts

This directory contains scripts for generating data used elsewhere.

## Requirements

* Python 3

Almost all operations are executed via Python. The virtualenv package will be installed, if it is missing.

You may need to install `python3-distutils` with your system's package manager.

## Setup

Publicly available data is automatically downloaded by the Makefile

You'll need to acquire the following files and place them under a directory called `in/`:

### Recipe1M Dataset

http://im2recipe.csail.mit.edu/dataset/login/

* `layer1.json`
* `det_ingrs.json`

## Execution

Everything's in the Makefile, so you can just use:

`make`

This includes the creation of the Python virtual environment - it's done automatically.

The process is quite memory-heavy, due to the size of the files involved.

The useful output is placed under `out/`. Other intermediate files are stored in `int/`

To make everything that can be done *without* manually acquiring data, run:

`make auto`

## Cleaning Up

To delete the intermediate and generated data, run:

`make clean`

To additionally delete autodownloaded files, run:

`make clean_autoin`

To additionally delete the virtualenv **all input data**, run:

`make clean_all`
