
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
* (TODO: link to the repository here)
* im2recipe's Recipe1M dataset. Sign up to acquire it here: http://im2recipe.csail.mit.edu/dataset/login/

1. Enter the cloned repository
2. cd into `/prep-scripts`
3. Create a directory called `in`.
4. Place `det_ingrs.json` and `layer1.json` from the Recipe1M data in `in/`
5. Run `make iswc`
6. Run `make copy` to copy the resulting data into place for the next step
7. cd into `/recipe-handler`
8. Run `make`

The `.trig` data will be found in `out/`. By default, it will be broken into groups of 1,000,000 triples to ease loading. You can change this behavior by adjusting the `--cutoff` parameter in the Makefile

## Usage

You will need the following:

* Blazegraph or any equivalent knowledge graph database software

The `.trig` data can be imported into a database of your choice. This may take some time, due to the volume of data involved.   
