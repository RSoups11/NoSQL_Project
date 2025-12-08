from neo4j import GraphDatabase
import os

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

_driver = None

def get_driver():
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    return _driver

def close_driver():
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None

def init_constraints():
    """
    Crée les contraintes / index nécessaires dans Neo4j.
    On suppose que chaque protéine est identifiée par 'entry' (colonne 'Entry').
    """
    driver = get_driver()
    cypher = """
    CREATE CONSTRAINT protein_entry_unique IF NOT EXISTS
    FOR (p:Protein)
    REQUIRE p.entry IS UNIQUE
    """
    with driver.session() as session:
        session.run(cypher)
