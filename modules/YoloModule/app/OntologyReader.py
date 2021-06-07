from owlready2 import *

onto2 = get_ontology("file:///Users/janickspirig/school2.owl").load()

print(list(default_world.sparql("""
           SELECT (COUNT(?x) AS ?nb)
           { ?x a owl:Class . }
    """)))