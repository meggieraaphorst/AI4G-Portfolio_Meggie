import streamlit as st
import pandas as pd

# Page title
st.title("☀️ SolarMood")
st.write("Solar Energy News Sentiment Dashboard")

# Load collected news data
df = pd.read_csv("solarmood.csv")

# Show total number of articles
st.metric("Total articles", len(df))

# Show sentiment distribution
st.subheader("News Sentiment")

sentiment_counts = df["sentiment"].value_counts()

st.bar_chart(
    sentiment_counts,
    y_label="Number of articles",
    x_label="Sentiment"
)



# Show sentiment over time
st.subheader("Sentiment Over Time")

# Convert publication dates to hours
df["hour"] = pd.to_datetime(df["date"], utc=True).dt.floor("h")

# Count articles per hour and sentiment
hourly_sentiment = (
    df.groupby(["hour", "sentiment"])
    .size()
    .unstack(fill_value=0)
)

# Display the hourly results
st.line_chart(hourly_sentiment)


# Show collected articles
st.subheader("Collected News Articles")

# Choose a sentiment
selected_sentiment = st.selectbox(
    "Filter by sentiment",
    ["All", "positive", "neutral", "negative"]
)

# Choose an hour
available_hours = sorted(df["hour"].dropna().unique())
selected_hour = st.selectbox(
    "Filter by hour",
    ["All"] + [str(hour) for hour in available_hours]
)

# Apply the selected filters
filtered_df = df.copy()

if selected_sentiment != "All":
    filtered_df = filtered_df[
        filtered_df["sentiment"] == selected_sentiment
    ]

if selected_hour != "All":
    filtered_df = filtered_df[
        filtered_df["hour"].astype(str) == selected_hour
    ]

# Show matching articles
st.write("Matching articles:", len(filtered_df))
st.dataframe(filtered_df)


# Compare the two sentiment models
st.subheader("AI Model Comparison")

st.write(
    "We compared two sentiment models using "
    "50 manually labelled solar news headlines."
)

# Results from our evaluation
results = pd.DataFrame({
    "Model": ["RoBERTa", "VADER"],
    "Agreement (%)": [42, 38]
})

# Show the comparison
st.bar_chart(
    results.set_index("Model")
)

st.write(
    "RoBERTa agreed with 21 out of 50 human labels (42%). "
    "VADER agreed with 19 out of 50 (38%)."
)

st.info(
    "These scores measure agreement with our human labels, "
    "not necessarily the true accuracy of the models. "
    "The models analyse the tone of headlines, while human "
    "labels may also reflect the impact on the solar industry."
)
