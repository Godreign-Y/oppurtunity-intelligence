"""
app/services/funding/rss_fetcher.py

Fetches latest funding news from RSS feeds.
"""

import feedparser
import asyncio
from typing import List, Dict


class RSSFetcher:
    """
    Fetches latest funding news from RSS feeds.
    """

    FEEDS = [
        "https://techcrunch.com/category/startups/feed/",
        "https://feeds.feedburner.com/VentureBeat",
    ]

    KEYWORDS = ["funding", "raises", "series a", "series b", "seed round", "capital", "investment"]

    async def fetch_signals(self) -> List[Dict]:
        """
        Fetch and parse RSS feeds, returning a list of potentially relevant articles.
        """
        raw_signals = []

        def fetch_all():
            results = []
            for url in self.FEEDS:
                try:
                    feed = feedparser.parse(url)
                    results.extend(feed.entries)
                except Exception as e:
                    print(f"Error parsing RSS feed {url}: {e}")
            return results

        entries = await asyncio.to_thread(fetch_all)

        for entry in entries:
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            link = entry.get("link", "")
            
            combined_text = (title + " " + summary).lower()
            if any(keyword in combined_text for keyword in self.KEYWORDS):
                raw_signals.append({
                    "title": title,
                    "summary": summary,
                    "source_url": link,
                    "raw_text": f"Title: {title}\nSummary: {summary}"
                })

        return raw_signals
