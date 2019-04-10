.PHONY: clean copy move auto

env = env/bin/activate
python = . $(env); LC_CTYPE=C.UTF-8 python
usda_sr_files = in/usda-sr/FOOD_DES.txt

# tools 

wget = $(python) tools/wget.py
unzip = $(python) tools/unzip.py
mkdir = $(python) tools/mkdir.py
# since clean needs this, and the env might not exist, we ignore the env here
rm = python tools/rm.py

# groups

auto_download = in/usda-sr/ in/USDA_SR.zip in/ontofox/

iswc: auto out/recipe1m-ex-limited.json

auto: out/usda-pairs.csv out/foodon-pairs.csv

out/foodon-pairs.csv: $(env) rdf/extract-labels.py in/ontofox/foodon.owl | out
	$(python) rdf/extract-labels.py in/ontofox/foodon.owl out/foodon-pairs.csv

out/usda-pairs.csv: $(env) usda/extract-names.py in/usda-sr/FOOD_DES.txt | out
	$(python) usda/extract-names.py in/usda-sr/FOOD_DES.txt "http://idea.rpi.edu/heals/kb/usda#" out/usda-pairs.csv

out/recipe1m-ex.json: $(env) recipe1m-ex/join-recipe1m.py int/tags.json in/layer1.json in/det_ingrs.json | out
	$(python) recipe1m-ex/join-recipe1m.py in/layer1.json in/det_ingrs.json int/tags.json out/recipe1m-ex.json

out/recipe1m-ex-limited.json: $(env) recipe1m-ex/join-recipe1m-limited.py in/layer1.json in/det_ingrs.json | out
	$(python) recipe1m-ex/join-recipe1m-limited.py in/layer1.json in/det_ingrs.json out/recipe1m-ex-limited.json

$(usda_sr_files): $(env) | in/usda-sr
	$(wget) "https://www.ars.usda.gov/ARSUserFiles/80400525/Data/SR-Legacy/SR-Leg_ASC.zip" "in/USDA_SR.zip"
	$(unzip) "in/USDA_SR.zip" "in/usda-sr"

in/ontofox/foodon.owl: $(env) ontofox/configs/foodon.txt | in/ontofox
	$(python) ontofox/query-ontofox.py ontofox/configs/foodon.txt in/ontofox/foodon.owl

$(env): requirements.txt
	$(rm) env/
	python -m pip install --user virtualenv
	python -m virtualenv -p python3 env
	$(python) -m pip install -r requirements.txt

copy: iswc
	$(mkdir) ../recipe-handler/data/
	cp out/* ../recipe-handler/data/
	$(mkdir) ../verify/data/
	cp out/* ../verify/data/
	cp in/det_ingrs.json ../verify/data/
	cp in/layer1.json ../verify/data/
	cp in/usda-sr/FOOD_DES.txt ../verify/data/
	cp in/usda-sr/NUTR_DEF.txt ../verify/data/

in/usda-sr: $(env) | in
	$(mkdir) in/usda-sr/

in/ontofox: $(env) | in
	$(mkdir) in/ontofox/

in: $(env)
	$(mkdir) in/

int: $(env)
	$(mkdir) int/

out: $(env)
	$(mkdir) out/

clean:
	$(rm) out/
	$(rm) int/

clean_autoin: clean
	$(rm) $(auto_download)

clean_all: clean clean_autoin
	$(rm) in/
	$(rm) env/
