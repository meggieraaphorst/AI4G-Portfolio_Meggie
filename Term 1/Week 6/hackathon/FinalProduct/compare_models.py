
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# 1. Read the 50 manually labeled news headlines
df = pd.read_csv("sentiment_evaluation_results.csv")

# 2. Create the second sentiment analysis method
vader = SentimentIntensityAnalyzer()

# 3. Classify each headline using VADER
def vader_sentiment(title):
    score = vader.polarity_scores(str(title))["compound"]

    if score >= 0.05:
        return "positive"
    elif score <= -0.05:
        return "negative"
    else:
        return "neutral"

df["vader_sentiment"] = df["title"].apply(vader_sentiment)

# 4. Compare both methods with human labels
human = df["Human Sentiment"].str.strip().str.lower()
huggingface = df["sentiment"].str.strip().str.lower()

hf_accuracy = (huggingface == human).mean() * 100
vader_accuracy = (df["vader_sentiment"] == human).mean() * 100

print("Number of articles:", len(df))
print(f"Hugging Face accuracy: {hf_accuracy:.1f}%")
print(f"VADER accuracy: {vader_accuracy:.1f}%")

# 5. Show VADER's confusion matrix
print("\nVADER confusion matrix:")
print(pd.crosstab(
    human,
    df["vader_sentiment"],
    rownames=["Human label"],
    colnames=["VADER prediction"]
))

# 6. Save the results for our report
df.to_csv("model_comparison_results.csv", index=False)

print("\nResults saved to model_comparison_results.csv")
