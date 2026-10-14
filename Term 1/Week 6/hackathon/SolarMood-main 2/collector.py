import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from urllib.parse import quote
import pandas as pd

search_terms = [
    "solar energy",
    "solar panels",
    "solar power",
    "solar technology"
]

articles = {}

for term in search_terms:
    url = (
        "https://news.google.com/rss/search?q="
        + quote(term + " when:1d")
        + "&hl=en-US&gl=US&ceid=US:en"
    )

    response = requests.get(url, timeout=20)
    response.raise_for_status()

    root = ET.fromstring(response.content)

    for item in root.findall(".//item"):
        title = item.findtext("title", "")
        link = item.findtext("link", "")
        date = item.findtext("pubDate", "")

        articles[link or title] = {
            "title": title,
            "date": date
        }

print("Found", len(articles), "unique articles")

from transformers import pipeline

# Load our pretrained AI model
sentiment_model = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
    device=-1
)

# Load previously saved articles
df = pd.read_csv("solarmood.csv")

# Analyze only articles we haven't saved yet
new_articles = []

for article in articles.values():
    if article["title"] not in df["title"].values:

        prediction = sentiment_model(
            article["title"],
            truncation=True
        )[0]

        new_articles.append({
            "title": article["title"],
            "date": article["date"],
            "sentiment": prediction["label"],
            "confidence": round(prediction["score"], 2),
            "collected_at": datetime.now(timezone.utc).isoformat()
        })

# Add new articles to our existing data
df = pd.concat(
    [df, pd.DataFrame(new_articles)],
    ignore_index=True
)

df.to_csv("solarmood.csv", index=False)

print("New articles:", len(new_articles))
print("Total saved articles:", len(df))
