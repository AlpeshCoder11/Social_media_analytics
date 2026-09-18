import asyncio
from app.collector.telegram import TelegramCollector
from app.database.postgres import init_postgres_db
from app.database.neo4j import neo4j_client

async def main():
    # 1. Ensure schemas exist
    init_postgres_db()
    neo4j_client.init_schema()

    # 2. Initialize collector
    collector = TelegramCollector()
    await collector.start()

    # 3. Test backfill on a public news channel
    target_groups = [
        "ASPIRANTMATERIALHUB"
    ]
    print(f"Starting test ingestion for {len(target_groups)} groups...")
    await collector.fetch_history_multiple(target_groups, limit=300)

    await collector.stop()
    print("Ingestion test completed successfully.")

if __name__ == "__main__":
    asyncio.run(main())