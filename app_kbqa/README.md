# Application: Answering Natural Language Questions over FoodKG

## Prerequisites

This code was written in python 3. To use it you will need to install:

* pytorch 0.4
* Numpy
* NLTK
* gensim
* fuzzywuzzy
* SPARQLWrapper
* argparse
* yaml


## Create a synthetic Q&A dataset

### Fetch KG subgraphs from a remote KG stored in Blazegraph

* Go to the data_builder/src folder, run the following cmd:

	```
    python usda.py -o [qas_dir]
    python recipe.py -o [qas_dir]
	```
	In the [qas\_dir] folder, you will see two JSON files: *usda\_subgraphs.json* which is 	for the USDA data and *recipe\_kg.json* which is for the Recipe1M data.

* Note that in the recipe data, a few tags contain more than 5000 recipes which might cause Out of Memory issue when running the KBQA system. So you may want to create a smaller recipe dataset by randomly keeping at most 2000 recipes under each recipe tag. In order to do that, run the following cmd:

	```
	python filterout_recipe.py -recipe [qas_dir/recipe_kg.json] -o [qas_dir/sampled_recipe_kg.json] -max_dish_count_per_tag 2000
	```

* Now, you can merge the above two files into a single file using the following cmd:

	```
	cat [qas_dir/usda_subgraphs.json] [qas_dir/sampled_recipe_kg.json] > [qas_dir/foodkg.json]
	```
	This is the local KG file which will be accessed by a KBQA system.


### Generate synthetic questions

* Run the following cmd:

	```
	python generate_qa.py -usda [qas_dir/usda_subgraphs.json] -recipe [qas_dir/sampled_recipe_kg.json] -o [qas_dir] -sampling_prob 0.05 -num_qas_per_tag 20
	```
	Note that if your machine does not have large RAM (e.g., > 16GB), you can set smaller sampling ratios (i.e., sampling_prob and num_qas_per_tag) when creating the dataset.




## Run a KBQA system

### Preprocess the Q&A dataset

* Go to the BAMnet/src folder, run the following cmd:

	```
	python build_all_data.py -data_dir [qas_dir] -kb_path [qas_dir/foodkg.json] -out_dir [qas_dir]
	```

### Load pretrained word embeddings

* Download the pretrained Glove word ebeddings [glove.840B.300d.zip](http://nlp.stanford.edu/data/wordvecs/glove.840B.300d.zip).

* Unzip the file and convert glove format to word2vec format using the following cmd:

	```
	python -m gensim.scripts.glove2word2vec --input glove.840B.300d.txt --output glove.840B.300d.w2v
	```

* Fetch the pretrained Glove vectors for our vocabulary.

	```
	python build_pretrained_w2v.py -emb glove.840B.300d.w2v -data_dir [qas_dir] -out [qas_dir/glove_pretrained_300d_w2v.npy] -emb_size 300
	```

### Tran/test a KBQA system

* Modify the config file config/kbqa.yml (e.g., file paths, vocab_size, num_ent_types, num_relations).


* Train the KBQA model.

	```
	python train.py -config config/kbqa.yml
	```

* Test the KBQA model:

	```
	python run_online.py -config config/kbqa.yml
	```

Note that we use the BAMnet model as our KBQA system in this application. For more details about the BAMnet model, please refer to the [original paper](https://arxiv.org/abs/1903.02188).



