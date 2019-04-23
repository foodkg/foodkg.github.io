USE_ENDPOINT_URL = "http://localhost:9999/bigdata/namespace/kb/sparql"


SIMPLE_QAS_TEMPLATES = ['How much {p} does {s} have?',
                        'How much {p} does {s} contain?',
                        'How much {p} does {s} consist of?',
                        'How much {p} is in {s}?',
                        'What is {p} value in {s}?',
                        'How much {p} is there in {s}?']

COMPARISION_QAS_TEMPLATES = [(True, '{s1} or {s2}, which has more {p}?'),
                            (False, '{s1} or {s2}, which has less {p}?'),
                            (True, 'Which has more {p}, {s1} or {s2}?'),
                            (False, 'Between {s1} and {s2}, which one has less {p}?'),
                            (True, '{s1} or {s2}, which one has higher amount of {p}?'),
                            (False, '{s1} or {s2}, which one has lower amount of {p}?'),
                            (True, 'Which contains more {p}, {s1} or {s2}?'),
                            (True, '{s1} or {s2}, which contains more {p}?'),
                            (False, '{s1} or {s2}, which contains less {p}?'),
                            (False, 'Between {s1} and {s2}, which contains less {p}?'),
                            (True, 'Between {s1} and {s2}, which one consists of larger amount of {p}?'),
                            (True, '{s1} or {s2}, which one consists of higher amount of {p}?'),
                            (False, '{s1} or {s2}, which one consists of lower amount of {p}?'),
                            (False, 'Which consists of lower amount of {p}, {s1} or {s2}?'),
                            ]

CONSTRAINT_QAS_TEMPLATES = ['What are {tag} recipes that contain {in_list}?',
                            'What are {tag} dishes that have ingredients {in_list}?',
                            'What are {tag} dishes that consist of {in_list}?',
                            'What are {tag} recipes that consist of ingredients {in_list}?',
                            'What {tag} dishes have {in_list}?',
                            'What {tag} dishes can I cook with {in_list}?',
                            'What {tag} dishes can I make with {in_list}?',
                            ]


USDA_SPARQL_QUERY = '''prefix np: <http://www.nanopub.org/nschema#>
prefix owl: <http://www.w3.org/2002/07/owl#>
prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix prov: <http://www.w3.org/ns/prov#>
prefix xsd: <http://www.w3.org/2001/XMLSchema#>
prefix uo: <http://purl.obolibrary.org/obo/UO_>
prefix hasco: <http://hadatac.org/ont/hasco#>
prefix heals: <http://idea.rpi.edu/heals/ont/heals#>
prefix heals-kb: <http://idea.rpi.edu/heals/kb/heals#>
prefix nhanes-kb: <http://idea.rpi.edu/heals/kb/nhanes#>
prefix gdc-kb: <http://idea.rpi.edu/heals/kb/gdc#>
prefix seer-kb: <http://idea.rpi.edu/heals/kb/seer#>
prefix chear: <http://hadatac.org/ont/chear#>
prefix chear-kb: <http://hadatac.org/kb/chear#>
prefix uberon: <http://purl.obolibrary.org/obo/UBERON_>
prefix sio: <http://semanticscience.org/resource/>
prefix envo: <http://purl.obolibrary.org/obo/ENVO_>
prefix chebi: <http://purl.obolibrary.org/obo/CHEBI_>
prefix hp: <http://purl.obolibrary.org/obo/HP_>
prefix oae: <http://purl.obolibrary.org/obo/OAE_>
prefix ncit: <http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#>
prefix obo: <http://purl.obolibrary.org/obo/>
prefix pubchem: <http://rdf.ncbi.nlm.nih.gov/pubchem/compound/>
prefix doid: <http://purl.obolibrary.org/obo/DOID_>
prefix pr: <http://purl.obolibrary.org/obo/PR_>
prefix ogg: <http://purl.obolibrary.org/obo/OGG_>
prefix go: <http://purl.obolibrary.org/obo/GO_>
prefix stato: <http://purl.obolibrary.org/obo/STATO_>
prefix snomed-ct: <http://purl.bioontology.org/ontology/SNOMEDCT/>
prefix loinc: <http://purl.bioontology.org/ontology/LNC/>
prefix rxnorm: <http://purl.bioontology.org/ontology/RXNORM/>
prefix efo: <http://www.ebi.ac.uk/efo/EFO_>
prefix synthea: <http://idea.rpi.edu/ont/synthea#>
prefix synthea-kb: <http://idea.rpi.edu/kb/synthea#>
prefix dbr: <http://dbpedia.org/resource/>
prefix usda-kb: <http://idea.rpi.edu/heals/kb/usda#>
prefix foodon: <http://purl.obolibrary.org/obo/foodon.owl>
prefix schema: <http://schema.org/>

SELECT * WHERE {
  ?id_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> sio:Identifier  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasValue> ?id .
  ?description_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> sio:StatusDescriptor  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasValue> ?description ;
    rdfs:label "Long Desc"^^xsd:string .
  ?water_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> envo:00002006 , chebi:15377 , dbr:Water  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    dbr:Gram, uo:0000021 ;
    <http://semanticscience.org/resource/hasValue> ?water .
  ?energy_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> foodon:03510045  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    dbr:Kcal ;
    <http://semanticscience.org/resource/hasValue> ?energy .
  ?protein_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> dbr:Protein  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    dbr:Gram,uo:0000021 ;
    <http://semanticscience.org/resource/hasValue> ?protein .
  ?lipid_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> dbr:Lipid  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    dbr:Gram,uo:0000021 ;
    <http://semanticscience.org/resource/hasValue> ?lipid .
  ?ash_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> chebi:33104  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    dbr:Gram,uo:0000021 ;
    <http://semanticscience.org/resource/hasValue> ?ash .
  ?carbohydrate_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> dbr:Carbohydrate , schema:carbohydrateContent  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    dbr:Gram,uo:0000021 ;
    <http://semanticscience.org/resource/hasValue> ?carbohydrate .
  ?fiber_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> dbr:Dietary_fiber  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    dbr:Gram, uo:0000021 ;
    <http://semanticscience.org/resource/hasValue> ?fiber .
  ?sugar_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> dbr:Sugar  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    dbr:Gram,uo:0000021 ;
    <http://semanticscience.org/resource/hasValue> ?sugar .
  ?calcium_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> dbr:Calcium  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    uo:0000022 ;
    <http://semanticscience.org/resource/hasValue> ?calcium .
  ?iron_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> chebi:18248  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    uo:0000022 ;
    <http://semanticscience.org/resource/hasValue> ?iron .
  ?magnesium_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> chebi:25107  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    uo:0000022 ;
    <http://semanticscience.org/resource/hasValue> ?magnesium .
  ?phosphorus_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> chebi:28659  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    uo:0000022 ;
    <http://semanticscience.org/resource/hasValue> ?phosphorus .
  ?potassium_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> chebi:26216  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    uo:0000022 ;
    <http://semanticscience.org/resource/hasValue> ?potassium .
  ?sodium_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> chebi:26708  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    uo:0000022 ;
    <http://semanticscience.org/resource/hasValue> ?sodium .
  ?zinc_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> chebi:27363  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    uo:0000022 ;
    <http://semanticscience.org/resource/hasValue> ?zinc .
  ?copper_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> chebi:28694  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    uo:0000022 ;
    <http://semanticscience.org/resource/hasValue> ?copper .
  ?manganese_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> chebi:18291  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    uo:0000022 ;
    <http://semanticscience.org/resource/hasValue> ?manganese .
  ?selenium_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> chebi:27568  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    uo:0000023 ;
    <http://semanticscience.org/resource/hasValue> ?selenium .
  ?vitamin_c_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> chebi:21241  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    uo:0000022 ;
    <http://semanticscience.org/resource/hasValue> ?vitamin_c .
  ?thiamin_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> chebi:18385  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    uo:0000022 ;
    <http://semanticscience.org/resource/hasValue> ?thiamin .
  ?riboflavin_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> chebi:17015  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    uo:0000022 ;
    <http://semanticscience.org/resource/hasValue> ?riboflavin .
  ?niacin_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> chebi:15940  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    uo:0000022 ;
    <http://semanticscience.org/resource/hasValue> ?niacin .
  ?panto_acid_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> chebi:25848  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    uo:0000022 ;
    <http://semanticscience.org/resource/hasValue> ?panto_acid .
  ?vitamin_b6_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> chebi:27306  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    uo:0000022 ;
    <http://semanticscience.org/resource/hasValue> ?vitamin_b6 .
  ?food_folate_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> chebi:27470  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    uo:0000023 ;
    <http://semanticscience.org/resource/hasValue> ?food_folate .
  ?choline_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> chebi:15354  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    uo:0000022 ;
    <http://semanticscience.org/resource/hasValue> ?choline .
  ?vit_b12_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> chebi:49100  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    uo:0000023 ;
    <http://semanticscience.org/resource/hasValue> ?vit_b12 .
  ?vit_a_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> dbr:Vitamin_A  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    uo:0000279 ;
    <http://semanticscience.org/resource/hasValue> ?vit_a .
  ?vit_a_rae_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> chebi:12777  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasValue> ?vit_a_rae .
  ?retinol_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> chebi:50211  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    uo:0000023 ;
    <http://semanticscience.org/resource/hasValue> ?retinol .
  ?alpha_carot_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> chebi:23042  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    uo:0000023 ;
    <http://semanticscience.org/resource/hasValue> ?alpha_carot .
  ?beta_carot_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> chebi:17579  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    uo:0000023 ;
    <http://semanticscience.org/resource/hasValue> ?beta_carot .
  ?beta_crypt_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> chebi:3930  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    uo:0000023 ;
    <http://semanticscience.org/resource/hasValue> ?beta_crypt .
  ?lycopene_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> chebi:15948  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    uo:0000023 ;
    <http://semanticscience.org/resource/hasValue> ?lycopene .
  ?vitamin_e_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> chebi:33234  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    uo:0000022 ;
    <http://semanticscience.org/resource/hasValue> ?vitamin_e .
  ?vit_d_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> chebi:27300  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    uo:0000023 ;
    <http://semanticscience.org/resource/hasValue> ?vit_d .
  ?vit_k_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> chebi:28384  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    uo:0000023 ;
    <http://semanticscience.org/resource/hasValue> ?vit_k .
  ?fat_sat_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> chebi:26607  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    uo:0000021 ;
    <http://semanticscience.org/resource/hasValue> ?fat_sat .
  ?fat_mono_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> chebi:25413  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    uo:0000021 ;
    <http://semanticscience.org/resource/hasValue> ?fat_mono .
  ?fat_poly_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> chebi:76567  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    uo:0000021 ;
    <http://semanticscience.org/resource/hasValue> ?fat_poly .
  ?cholestrl_E <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> chebi:16113  ;
    <http://semanticscience.org/resource/isAttributeOf>    ?food_V  ;
    <http://semanticscience.org/resource/hasUnit>    uo:0000022 ;
    <http://semanticscience.org/resource/hasValue> ?cholestrl .
  ?food_V <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> chebi:33290 , dbr:Food .
}'''
