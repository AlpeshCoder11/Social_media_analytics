from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
from app.database.postgres import get_db_connection

router = APIRouter()

@router.get("/api/network/kols")
def get_key_opinion_leaders(limit: int = 10):
    """Returns the top influencers ranked by PageRank for the Leaderboard."""
    query = """
        SELECT user_id, pagerank, betweenness, degree, community_id 
        FROM network_metrics 
        ORDER BY pagerank DESC 
        LIMIT %s;
    """
    try:
        with get_db_connection() as conn:
            df = pd.read_sql_query(query, conn, params=(limit,))
        return {"kols": df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/network/bridges")
def get_bridge_accounts(limit: int = 3):
    """Returns users with the highest Betweenness Centrality for Highlight Cards."""
    query = """
        SELECT user_id, betweenness, community_id 
        FROM network_metrics 
        ORDER BY betweenness DESC 
        LIMIT %s;
    """
    try:
        with get_db_connection() as conn:
            df = pd.read_sql_query(query, conn, params=(limit,))
        return {"bridges": df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/network/communities")
def get_community_distribution():
    """Returns the size of each Louvain cluster for a Donut Chart."""
    query = """
        SELECT community_id, COUNT(user_id) as user_count 
        FROM network_metrics 
        GROUP BY community_id 
        ORDER BY user_count DESC;
    """
    try:
        with get_db_connection() as conn:
            df = pd.read_sql_query(query, conn)
        return {"communities": df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/api/sentiment/distribution")
def get_sentiment_distribution():
    """Pillar 1: Sentiment & Emotion Breakdown"""
    query = """
        SELECT label as emotion, COUNT(*) as count 
        FROM sentiment_results 
        GROUP BY label 
        ORDER BY count DESC;
    """
    try:
        with get_db_connection() as conn:
            df = pd.read_sql_query(query, conn)
        return {"sentiment": df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/demographics/summary")
def get_demographic_summary():
    """Pillar 2: Aggregate Audience Profiling"""
    query = """
        SELECT segment_type, segment_name, SUM(user_count) as total_users
        FROM demographic_aggregates 
        GROUP BY segment_type, segment_name
        ORDER BY total_users DESC;
    """
    try:
        with get_db_connection() as conn:
            df = pd.read_sql_query(query, conn)
        return {"demographics": df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/trends/top")
def get_top_trends(limit: int = 8):
    """Pillar 3: Emerging Topics and Velocity"""
    query = """
        SELECT topic, current_volume, growth_rate, trend_type 
        FROM trend_results 
        ORDER BY growth_rate DESC, current_volume DESC 
        LIMIT %s;
    """
    try:
        with get_db_connection() as conn:
            df = pd.read_sql_query(query, conn, params=(limit,))
        return {"trends": df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))