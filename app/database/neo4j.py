import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

from app.models import Interaction, InteractionType

load_dotenv()

URI = os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "neo4jpassword")

class Neo4jClient:
    def __init__(self):
        self._driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

    def close(self):
        self._driver.close()

    def init_schema(self):
        """Applies uniqueness constraints and indexes for rapid node traversal."""
        constraints = [
            "CREATE CONSTRAINT user_id_unique IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE;",
            "CREATE CONSTRAINT channel_id_unique IF NOT EXISTS FOR (c:Channel) REQUIRE c.id IS UNIQUE;"
        ]
        with self._driver.session() as session:
            for constraint in constraints:
                session.run(constraint)

    def upsert_user_node(self, user_id: str, platform: str, username: str = None):
        """Creates or updates a User node."""
        query = """
        MERGE (u:User {id: $user_id})
        ON CREATE SET u.platform = $platform, u.username = $username
        ON MATCH SET u.username = coalesce($username, u.username)
        """
        with self._driver.session() as session:
            session.run(query, user_id=user_id, platform=platform, username=username)

    def upsert_channel_node(self, channel_id: str, platform: str):
        """Creates or matches a Channel node."""
        query = """
        MERGE (c:Channel {id: $channel_id})
        ON CREATE SET c.platform = $platform
        """
        with self._driver.session() as session:
            session.run(query, channel_id=channel_id, platform=platform)

    def add_interaction(self, interaction: Interaction):
        """
        Creates a timestamped directed edge between entities.
        Dynamically handles User->User or User->Channel connections.
        """
        type_str = interaction.interaction_type.value
        iso_timestamp = interaction.timestamp.isoformat()

        # Build dynamic relationship Cypher based on the interaction type
        query = f"""
        MERGE (s:User {{id: $source_id}})
        MERGE (t:User {{id: $target_id}})
        CREATE (s)-[r:{type_str} {{
            channel_id: $channel_id,
            timestamp: datetime($timestamp),
            weight: $weight
        }}]->(t)
        """
        with self._driver.session() as session:
            session.run(
                query,
                source_id=interaction.source_id,
                target_id=interaction.target_id,
                channel_id=interaction.channel_id,
                timestamp=iso_timestamp,
                weight=interaction.weight
            )

# Shared singleton instance
neo4j_client = Neo4jClient()