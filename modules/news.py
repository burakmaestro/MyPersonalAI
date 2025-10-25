import feedparser

# RSS kaynakları
RSS_FEEDS = {
    "genel": [
        "https://www.hurriyet.com.tr/rss/gundem",
        "https://www.ntv.com.tr/son-dakika.rss",
        "https://www.milliyet.com.tr/rss/rssNew/gundemRss.xml"
    ],
    "spor": [
        "https://www.fanatik.com.tr/rss",
        "https://www.ntvspor.net/rss",
        "https://www.trtspor.com.tr/rss"
    ],
    "teknoloji": [
        "https://www.webtekno.com/feed",
        "https://shiftdelete.net/feed",
        "https://www.donanimhaber.com/rss/teknoloji.xml"
    ]
}

def get_top_headlines(query=None, max_items=5):
    """
    RSS feedlerden haber başlıklarını çeker.
    
    query: None, "genel", "spor", "teknoloji"
    max_items: dönecek maksimum haber sayısı
    """
    query = (query or "genel").lower()
    feeds = RSS_FEEDS.get(query, RSS_FEEDS["genel"])
    
    headlines = []
    
    for url in feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                if entry.title not in headlines:
                    headlines.append(entry.title)
                if len(headlines) >= max_items:
                    break
            if len(headlines) >= max_items:
                break
        except Exception as e:
            continue
    
    if not headlines:
        return [f"Haber bulunamadı: {query}"]
    
    return headlines
