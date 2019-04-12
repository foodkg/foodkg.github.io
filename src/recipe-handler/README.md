# Using the Makefile

The Makefile will install virtualenv, create an environment, install dependencies, and run the processing jobs.

You will need to run `make` in `/prep-scripts` to generate the data files, then run `make copy` in `/prep-scripts` to move them into `/recipe-handler/data`

No other action needs to be taken. Run `make` to run all of the processing jobs. This will take several hours, depending on storage and processor speed.

You can also run `make mini` to run the processor on 1,000 recipes. This is significantly faster.

## Post-processing

After the job terminates, you'll have data in /out/iswc or /out/mini.

Run `make copy` or `make copy_mini` to copy this data into `/verify`.
