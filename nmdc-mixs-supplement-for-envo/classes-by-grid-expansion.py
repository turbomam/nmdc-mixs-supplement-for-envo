import csv
import pprint
import re
from itertools import product
from typing import Dict, List
from rdflib import Graph, RDFS, URIRef, Namespace, Literal, RDF, OWL

nmsfe = Namespace("http://example.org/nmsfe/")
BFO = Namespace("http://purl.obolibrary.org/obo/BFO_")

triad_slots = ["env_broad_scale", "env_local_scale", "env_medium"]

statuses = ['proposed', 'accepted', 'rejected']

g = Graph()
g.parse("nmsfe_static.ttl")
g.add((URIRef(nmsfe.mixs_environmental_triad), RDFS.subClassOf, URIRef(BFO['0000004'])))
g.add((URIRef(BFO['0000004']), RDF.type, OWL.Class))

with open('target/mixs_packages.tsv') as f:
    packages_content = [{k: v for k, v in row.items()} for row in
                        csv.DictReader(f, skipinitialspace=True, delimiter="\t")]

packages = [i["Environmental package"] for i in packages_content]

unique_packages = list(set(packages))
unique_packages.sort()
simplified_packages = [i for i in unique_packages if " " not in i and "/" not in i]

with open('target/mixs_core.tsv') as f:
    core_content_lod = [{k: v for k, v in row.items() if k} for row in
                        csv.DictReader(f, skipinitialspace=True, delimiter="\t")]

core_content = {item['Structured comment name']: item for item in core_content_lod}

with open('mixs_cols_translations.txt') as f:
    mixs_cols_translations_lod = [{k: v for k, v in row.items()} for row in
                                  csv.DictReader(f, skipinitialspace=True, delimiter="\t")]

mixs_cols_translations = {item['MIxS']: {'RDF': item['RDF'], 'LinkML': item['LinkML']} for item in
                          mixs_cols_translations_lod}

for k, v in core_content.items():
    if k in triad_slots:
        g.add((URIRef(nmsfe[k]), RDFS.subClassOf, URIRef(nmsfe.mixs_environmental_triad)))
        for vk, vv in v.items():
            g.add((URIRef(nmsfe[k]), URIRef(mixs_cols_translations[vk]['RDF']), Literal(vv)))
            g.add((URIRef(mixs_cols_translations[vk]['RDF']), RDF.type, OWL.AnnotationProperty))


def expand_grid(grid_dict_in: Dict):
    temp = product(*grid_dict_in.values())
    expanded_tuple_list = [expanded_tuple for expanded_tuple in temp]
    return expanded_tuple_list


outer_dictionary = {'context': triad_slots,
                    'status': statuses}

outer_expanded = expand_grid(outer_dictionary)

for i in outer_expanded:
    concatenated_name = "_".join(i)
    g.add((nmsfe[concatenated_name], RDFS.subClassOf, nmsfe[i[0]]))


def load_graph_from_remote_construct(graph: Graph, construct_file_path: str):
    # todo parse construct_statement_node out of construct_statement
    with open(construct_file_path, "r") as f:
        construct_statement = f.readlines()

    construct_statement = "".join(construct_statement)

    see_also_extractor = 'rdfs:seeAlso\s*<(.*?)>'
    see_alsos = re.compile(see_also_extractor, re.MULTILINE).findall(construct_statement)
    print(see_alsos)

    construct_results = graph.query(construct_statement)

    for row in construct_results:
        graph.add(row)

    if len(see_alsos) == 1:
        graph.add((URIRef(see_alsos[0]), RDF.type, OWL.NamedIndividual))
        g.add(
            (URIRef(see_alsos[0]), RDFS.comment,
             Literal(construct_statement)))


load_graph_from_remote_construct(g, "ubergraph_biome_SC_construct.sparql")

load_graph_from_remote_construct(g, "ubergraph_biome_label_construct.sparql")

load_graph_from_remote_construct(g, "ubergraph_env_mat_SC_construct.sparql")

# with open("exhaustive_subclasses.sparql", "r") as f:
#     exhaustive_query = f.readlines()
#
# exhaustive_query = "".join(exhaustive_query)
#
# print(exhaustive_query)
#
# exhaustive_results = g.query(exhaustive_query)
#
# print(exhaustive_results)
#
# for row in exhaustive_results:
#     print("hello")

# print(g.serialize(format='turtle'))
g.serialize(destination="target/nmdc-mixs-supplement-for-envo.ttl")
