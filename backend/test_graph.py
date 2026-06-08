import asyncio
import logging
from app.services.pipeline_worker import graph

async def main():
    logging.basicConfig(level=logging.INFO)
    print("Testing LangGraph compilation and visualization")
    
    print(graph.get_graph().draw_ascii())

if __name__ == "__main__":
    asyncio.run(main())
