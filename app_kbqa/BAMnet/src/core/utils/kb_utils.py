
USDA_FOOD_ATTRIBUTES = ['water','energy','protein','lipid','ash','carbohydrate','fiber','sugar','calcium','iron','magnesium','phosphorus','potassium','sodium','zinc','copper','manganese','selenium','vitamin_C','thiamin','riboflavin','niacin','panto_acid','vitamin_B6','folate','folic_acid','food_folate','folate_DFE','choline','vit_B12','vit_A','vit_A_RAE','retinol','alpha_carot','beta_carot','beta_crypt','lycopene','lut_zea','vitamin_E','vit_D','vit_K','fat_sat','fat_mono','fat_poly','cholestrl','GmWt_1','GmWt_Desc1','GmWt_2','GmWt_Desc2','Refuse_Pct']


def query_remote_kb(sparql, topic_entity, kb_name):
    if kb_name == 'usda':
        graph = fetch_usda_subgraph_one_hop(sparql, topic_entity, USDA_FOOD_ATTRIBUTES)
    elif kb_name == 'recipe':
        graph = fetch_recipe_subgraph_two_hop(sparql, topic_entity)
    else:
        graph = None
    return graph

def fetch_usda_subgraph_one_hop(sparql, ingredient_entity, attributes):
    return_vars = ' '.join(['?{}Val'.format(x) for x in attributes])
    match_attrs = '\n'.join(['?{attr} a usda:{attr} ;\n sio:hasValue ?{attr}Val .'.format(attr=x) for x in attributes])
    query = '''
    PREFIX sio: <http://semanticscience.org/resource/>
    PREFIX usda: <http://idea.rpi.edu/heals/kb/usda#>
    SELECT {return_vars}
                WHERE {{
                  GRAPH ?assertion {{
                            ?desc sio:hasValue ?name;
                                  a usda:description.
                            {match_attrs}
                            FILTER (?name="{name}"^^xsd:string) }}
                }}'''.format(return_vars=return_vars, match_attrs=match_attrs, name=ingredient_entity)
    sparql.setQuery(query)
    sparql.setReturnFormat('json')
    results = sparql.query().convert()
    results = results['results']['bindings']
    results = results[0] if len(results) > 0 else {}

    if len(results) > 0:
        graph = {'id': '', 'name': [ingredient_entity], 'alias': [], 'type': ['ingredient'], 'neighbors':{}}
        for attr, ret_val in results.items():
            datatype = ret_val['datatype'].split('#')[-1]
            if datatype == 'integer':
                val = int(ret_val['value'])
            elif datatype == 'float':
                val = float(ret_val['value'])
            graph['neighbors'][attr] = [val]
        return {ingredient_entity: graph}
    else:
        return None

def fetch_recipe_subgraph_two_hop(sparql, tag_entity):
    tag_name = ' '.join(tag_entity.split('/')[-1].split('%20'))
    graph = {'id': tag_entity, 'name': [tag_name], 'alias': [], 'type': ['tag'], 'neighbors': {}}
    dishes = fetch_all_dishes(sparql, '<{}>'.format(tag_entity))
    graph['neighbors']['tagged_dishes'] = []
    for dish in dishes:
        dish_name = ' '.join(dish.split('/')[-1].split('%20'))
        dish_graph = {dish: {'name': [dish_name], 'alias': [], 'type': ['dish_recipe'], 'neighbors': {}}}
        dish_graph[dish]['neighbors']['contains_ingredients'] = []
        ingredients = fetch_all_ingredients(sparql, '<{}>'.format(dish))
        for ingredient in ingredients:
            ingredient_name = ' '.join(ingredient.split('/')[-1].split('%20'))
            ingredient_graph = {ingredient: {'name': [ingredient_name], 'alias': [], 'type': ['ingredient']}}
            dish_graph[dish]['neighbors']['contains_ingredients'].append(ingredient_graph)
        graph['neighbors']['tagged_dishes'].append(dish_graph)
    return {tag_entity: graph}

def fetch_all_dishes(sparql, tag):
    query = '''
        PREFIX recipe-kb: <http://idea.rpi.edu/heals/kb/>
        SELECT DISTINCT ?r {{
            ?r recipe-kb:tagged {} .
        }}'''.format(tag)

    sparql.setQuery(query)
    sparql.setReturnFormat('json')
    results = sparql.query().convert()
    dishes = [x['r']['value'] for x in results['results']['bindings']]
    return dishes

def fetch_all_ingredients(sparql, dish):
    query = '''PREFIX recipe-kb: <http://idea.rpi.edu/heals/kb/>
        SELECT ?in {{
            {} recipe-kb:uses ?ii .
            ?ii recipe-kb:ing_name ?in
        }}
    '''.format(dish)

    sparql.setQuery(query)
    sparql.setReturnFormat('json')
    results = sparql.query().convert()
    ingredients = [x['in']['value'] for x in results['results']['bindings']]
    return ingredients
