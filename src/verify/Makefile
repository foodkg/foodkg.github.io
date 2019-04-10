env = env/bin/activate
python = . $(env); LC_CTYPE=C.UTF-8 python

files = data/layer1.json data/det_ingrs.json data/recipe1m-ex-limited.json data/usda-pairs.csv data/foodon-pairs.csv data/NUTR_DEF.txt data/FOOD_DES.txt

report.txt: $(env) $(files) config.json
	$(python) report.py

$(env): requirements.txt
	rm -rf env/
	python -m pip install --user virtualenv
	python -m virtualenv -p python3 env
	$(python) -m pip install -r requirements.txt

clean:
	rm report.txt
