import feedparser
import asyncio
from typing import List, Dict
from src.collectors.base import BaseCollector

class RSSFetcher(BaseCollector):
    """
    Fetches latest funding news from RSS feeds.
    """

    # We use a couple of standard tech feeds that report on funding
    FEEDS = [
        "https://techcrunch.com/category/startups/feed/",
        "https://feeds.feedburner.com/VentureBeat",
    ]

    # Keywords to filter out completely irrelevant articles before hitting the LLM
    KEYWORDS = ["funding", "raises", "series a", "series b", "seed round", "capital", "investment"]

    async def fetch_signals(self) -> List[Dict]:
        """
        Fetch and parse RSS feeds, returning a list of potentially relevant articles.
        """
        raw_signals = []

        # feedparser is blocking, but fetching a few feeds is fast enough. 
        # For a truly massive scale, we'd use httpx + an async XML parser.
        # Here we run it in a threadpool to not block the async event loop.
        def fetch_all():
            results = []
            for url in self.FEEDS:
                feed = feedparser.parse(url)
                results.extend(feed.entries)
            return results

        entries = await asyncio.to_thread(fetch_all)

        for entry in entries:
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            link = entry.get("link", "")
            
            # Simple keyword matching to save LLM costs
            combined_text = (title + " " + summary).lower()
            if any(keyword in combined_text for keyword in self.KEYWORDS):
                raw_signals.append({
                    "title": title,
                    "summary": summary,
                    "source_url": link,
                    "raw_text": f"Title: {title}\nSummary: {summary}"
                })

        return raw_signals
