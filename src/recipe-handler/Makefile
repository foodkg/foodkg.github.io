.PHONY: clean all mini copy

env = env/bin/activate
python = . $(env); LC_CTYPE=C.UTF-8 python

all: out/iswc/

mini: out/mini/

out/iswc/: $(env) recipe.py data/recipe1m-ex-limited.json data/usda-pairs.csv data/foodon-pairs.csv | out
	mkdir -p out/iswc/
	$(python) recipe.py job iswc data/recipe1m-ex-limited.json data/usda-pairs.csv data/foodon-pairs.csv out/iswc/ --cutoff 99999999999999
	touch out/iswc/

out/mini/: $(env) recipe.py data/1k.json data/usda-pairs.csv data/foodon-pairs.csv | out
	mkdir -p out/mini/
	$(python) recipe.py job iswc data/1k.json data/usda-pairs.csv data/foodon-pairs.csv out/mini/ --cutoff 99999999999999
	touch out/mini/

data/1k.json: $(env) data/recipe1m-ex-limited.json
	$(python) -c "import json; json.dump(json.load(open('data/recipe1m-ex-limited.json'))[0:1000], open('data/1k.json', 'w'))"

$(env): requirements.txt
	rm -rf env/
	python -m pip install --user virtualenv
	python -m virtualenv -p python3 env
	$(python) -m pip install -r requirements.txt

copy_mini: /out/mini/
	mkdir -p ../verify/data/
	cp out/mini/foodon-links.trig ../verify/data/
	cp out/mini/usda-links.trig ../verify/data/

copy: out/iswc/
	mkdir -p ../verify/data/
	cp out/iswc/foodon-links.trig ../verify/data/
	cp out/iswc/usda-links.trig ../verify/data/

out:
	mkdir -p out/
	touch out/

clean:
	rm -rf out/
