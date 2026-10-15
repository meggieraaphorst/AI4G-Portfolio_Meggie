
import pandas as pd

# Read our manually labeled Excel file
df = pd.read_excel("SolarMood_ Human Sentiment Evaluation (1).xlsx")

# Keep only articles with a human sentiment label
df = df.dropna(subset=["Human Sentiment"]).copy()

# Make labels consistent
df["Human Sentiment"] = df["Human Sentiment"].str.strip().str.lower()
df["sentiment"] = df["sentiment"].str.strip().str.lower()

# Compare the AI predictions with human judgments
df["correct"] = df["sentiment"] == df["Human Sentiment"]

total = len(df)
correct = df["correct"].sum()
accuracy = correct / total * 100

print("Articles evaluated:", total)
print("Correct predictions:", correct)
print(f"Accuracy: {accuracy:.1f}%")

# Show which sentiments the model confuses
labels = ["negative", "neutral", "positive"]

matrix = pd.crosstab(
    df["Human Sentiment"],
    df["sentiment"],
    rownames=["Human label"],
    colnames=["AI prediction"]
)

matrix = matrix.reindex(
    index=labels,
    columns=labels,
    fill_value=0
)

print("\nConfusion matrix:")
print(matrix)

# Save the comparison for our report
df.to_csv("sentiment_evaluation_results.csv", index=False)

# Show examples where AI and humans disagree
print("\nExamples of disagreements:")
for _, row in df[~df["correct"]].head(3).iterrows():
    print("\nHeadline:", row["title"])
    print("Human:", row["Human Sentiment"])
    print("AI:", row["sentiment"])
