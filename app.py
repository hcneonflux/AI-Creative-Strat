import streamlit as st
import pandas as pd
from textblob import TextBlob
import matplotlib.pyplot as plt
from collections import Counter
import re

# Streamlit UI Setup
st.title("AI-Powered Customer Research Tool")
st.write("Upload customer reviews, and get a structured report with insights, headlines, and ad ideas.")

# Upload file
uploaded_file = st.file_uploader("Upload a CSV file with customer reviews", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # Check for review column
    review_column = None
    for col in df.columns:
        if "review" in col.lower():
            review_column = col
            break
    
    if review_column is None:
        st.error("No column found with 'review' in its name. Please check your file format.")
    else:
        reviews = df[review_column].dropna()
        
        # Sentiment Analysis
        def get_sentiment(text):
            analysis = TextBlob(text)
            return "Positive" if analysis.sentiment.polarity > 0 else "Negative" if analysis.sentiment.polarity < 0 else "Neutral"
        
        df['Sentiment'] = reviews.apply(get_sentiment)
        
        # Emotional Breakdown Chart
        sentiment_counts = df['Sentiment'].value_counts()
        st.subheader("Emotional Breakdown")
        fig, ax = plt.subplots()
        ax.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', startangle=140)
        st.pyplot(fig)
        
        # Extract Key Themes
        all_words = " ".join(reviews).lower()
        all_words = re.findall(r'\b\w{4,}\b', all_words)
        common_words = Counter(all_words).most_common(10)
        
        st.subheader("Top 10 Keywords in Reviews")
        keyword_df = pd.DataFrame(common_words, columns=["Keyword", "Frequency"])
        st.table(keyword_df)
        
        # Generate Headlines & Ad Ideas
        positive_reviews = df[df['Sentiment'] == "Positive"][review_column]
        negative_reviews = df[df['Sentiment'] == "Negative"][review_column]
        
        st.subheader("Generated Headlines & Ad Ideas")
        if not positive_reviews.empty:
            st.write("✅ **Positive Hook:** " + positive_reviews.sample(1).values[0])
        if not negative_reviews.empty:
            st.write("⚠️ **Pain Point Hook:** " + negative_reviews.sample(1).values[0])
        
        st.write("💡 **Ad Idea:** Focus on solving " + keyword_df.iloc[0]['Keyword'] + " for customers.")
        
        # Download Report
        st.download_button("Download Report", data=df.to_csv(index=False), file_name="customer_insights.csv", mime="text/csv")
