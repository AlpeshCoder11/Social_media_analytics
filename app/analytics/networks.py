import os
import sys
import logging
from pathlib import Path
import pandas as pd
import networkx as nx

# Automatically resolve project root
sys.path.append(str(Path(__file__).resolve().parents[2]))

try:
    from app.database.postgres import get_db_connection
except ImportError:
    get_db_connection = None

logger = logging.getLogger("network_engine")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def build_network_and_compute_metrics():
    """
    Builds a bipartite projection graph (User-to-User) based on shared channel activity,
    calculates SIH blueprint network metrics, and persists them to PostgreSQL and CSV.
    """
    if not get_db_connection:
        logger.error("PostgreSQL connection module not found. Exiting.")
        return

    # Fetch user participation per channel to infer implicit community networks
    query = """
        SELECT 
            user_id, 
            channel_id, 
            COUNT(message_id) as activity_weight
        FROM messages
        WHERE user_id IS NOT NULL AND channel_id IS NOT NULL
        GROUP BY user_id, channel_id;
    """

    with get_db_connection() as conn:
        df = pd.read_sql_query(query, conn)

    if df.empty:
        logger.warning("No interaction data found to build the network graph.")
        return

    logger.info(f"Loaded {len(df)} user-channel interaction edges.")

    # 1. Build Bipartite Graph & Project to User-User Network
    B = nx.Graph()
    users = df['user_id'].unique()
    channels = df['channel_id'].unique()
    
    B.add_nodes_from(users, bipartite=0)
    B.add_nodes_from(channels, bipartite=1)

    edges = [(row['user_id'], row['channel_id'], row['activity_weight']) for _, row in df.iterrows()]
    B.add_weighted_edges_from(edges)

    # Project to a weighted User-to-User graph (Users are connected if they active in the same channels)
    logger.info("Projecting bipartite graph into User-to-User interaction network...")
    user_nodes = {n for n, d in B.nodes(data=True) if d['bipartite'] == 0}
    G = nx.bipartite.projected_graph(B, user_nodes)

    if len(G.nodes) == 0:
        logger.warning("Graph projection failed. Not enough overlapping user activity.")
        return

    # 2. Compute Blueprint Network Metrics
    logger.info("Calculating PageRank (KOL / Authority)...")
    pagerank = nx.pagerank(G, weight='weight')

    logger.info("Calculating Degree Centrality (Broadcast/Reach)...")
    degree = nx.degree_centrality(G)

    logger.info("Calculating Betweenness Centrality (Bridge Accounts)...")
    # Limit calculation on very large graphs for hackathon speed constraints
    k_samples = min(len(G.nodes), 500) 
    betweenness = nx.betweenness_centrality(G, k=k_samples, weight='weight')

    logger.info("Running Louvain Community Detection (Echo-chamber clustering)...")
    try:
        communities = nx.community.louvain_communities(G, weight='weight')
        community_map = {}
        for idx, comm in enumerate(communities):
            for node in comm:
                community_map[node] = idx
    except AttributeError:
        # Fallback if using older NetworkX version
        community_map = {node: 0 for node in G.nodes}
        logger.warning("Louvain requires NetworkX >= 2.7. Defaulting to community 0.")

    # 3. Aggregate Results
    results = []
    for node in G.nodes:
        results.append({
            "user_id": node,
            "pagerank": round(pagerank.get(node, 0.0), 6),
            "betweenness": round(betweenness.get(node, 0.0), 6),
            "degree": round(degree.get(node, 0.0), 6),
            "community_id": community_map.get(node, -1)
        })

    metrics_df = pd.DataFrame(results)
    
    # 4. Persist to CSV and PostgreSQL
    os.makedirs("data", exist_ok=True)
    csv_path = "data/network_metrics.csv"
    metrics_df.sort_values(by="pagerank", ascending=False).to_csv(csv_path, index=False)
    logger.info(f"Exported top KOLs and network metrics to {csv_path}")

    upsert_query = """
        INSERT INTO network_metrics (user_id, pagerank, betweenness, degree, community_id, last_updated)
        VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        ON CONFLICT (user_id)
        DO UPDATE SET 
            pagerank = EXCLUDED.pagerank,
            betweenness = EXCLUDED.betweenness,
            degree = EXCLUDED.degree,
            community_id = EXCLUDED.community_id,
            last_updated = CURRENT_TIMESTAMP;
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            records = [
                (r["user_id"], float(r["pagerank"]), float(r["betweenness"]), float(r["degree"]), int(r["community_id"]))
                for _, r in metrics_df.iterrows()
            ]
            cur.executemany(upsert_query, records)
            conn.commit()

    logger.info(f"Persisted {len(records)} node metrics to PostgreSQL.")

    # Console Summary
    print("\n" + "=" * 80)
    print("      SIH NETWORK INTELLIGENCE — KEY OPINION LEADERS (KOLs)")
    print("=" * 80)
    print(metrics_df.sort_values(by="pagerank", ascending=False).head(15).to_string(index=False))
    print("=" * 80 + "\n")

if __name__ == "__main__":
    build_network_and_compute_metrics()