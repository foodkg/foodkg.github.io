This directory contains a script to produce many of the statistics cited in the ISWC paper.

Just run `make` to generate them. This will take a few minutes if you enable everything. The results are saved into report.txt

If you only want to see one category of data, you can turn off other categories in `config.json`.

To get figures for the resulting knowledge graphs, you will need to load them into Blazegraph (or an equivalent datastore) and query them there - rdflib is far too slow to efficiently query such large graphs.
