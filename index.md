
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
