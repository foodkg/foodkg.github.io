
# HEALS Food Knowledge Graph

## USDA Food Mappings 

This dataset includes mappings to some of the concepts found in:
- DBpedia
- schema.org
- FoodOn
- Units Ontology
- ChEBI 

[USDA Knowledge Graph in nanopublications (trig) format](https://drive.google.com/open?id=1hkitCcxnM_7R6OYuvC5zakWojlN2Xuog)

## Reproduction

To reproduce the knowledge graph described in the paper, you will require the following:

* `make` (available on most Linux distributions; can be obtained with some effort for Windows)
* Python 3, along with the virtualenv module
* This repository, https://github.com/foodkg/foodkg.github.io/
* im2recipe's Recipe1M dataset. Sign up to acquire it here: http://im2recipe.csail.mit.edu/dataset/login/

Specific instructions for creating and transforming the data are found in `/src/README.md`. A high level overview:

1. Download the data required by `/src/prep-scripts/README.md`
2. Build the source data with `make`
3. Move to `/src/recipe-handler`
4. Create the linked data with `make` (placed into the `out` directory)
5. Move to `/src/verify`
6. Create statistics with `make`

## Usage

You will need the following:

* Blazegraph or any equivalent knowledge graph database software

The `.trig` data can be imported into a database of your choice. This may take some time, due to the volume of data involved.   

If you are using Blazegraph, then you can load the data with the following procedure:

1. Start the Blazegraph server and navigate to the web interface (typically `localhost:9999`)
2. Switch to the UPDATE tab
3. In the dropdown menu below the input field, change from "SPARQL Update" to "File path or URL"
4. In the input field, enter the absolute path to the generated `.trig` file, prefixed by `file://`. For example, you might load the USDA links with a path of `fiel:///home/alice/foodkg.github.io/src/recipe-handler/out/iswc/usda-links.trig`, replacing `usda-links.trig` with the other file names in the output directory to load everything

