import requests
from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk import download
import re

# Download necessary NLTK data
download("punkt")

# Define Indonesian stopwords
indonesian_stopwords = set(
    [
        "yang",
        "dan",
        "di",
        "dari",
        "ke",
        "adalah",
        "ini",
        "itu",
        "pada",
        "untuk",
        "dengan",
        "saya",
        "kami",
        "kita",
        "anda",
        "mereka",
        "itu",
        "itu",
        "tersebut",
        "sebuah",
        "sebagai",
        # Add more Indonesian stopwords as needed
    ]
)


def extract_popular_words(articles, num_words=20):
    """Extract popular words from a list of articles."""
    stop_words = indonesian_stopwords
    words = []

    for article in articles:
        tokens = word_tokenize(article.lower())
        filtered_words = [
            word for word in tokens if word.isalpha() and word not in stop_words
        ]
        words.extend(filtered_words)

    word_freq = Counter(words)
    popular_words = word_freq.most_common(num_words)
    return popular_words


def clean_article_text(text):
    """Remove unwanted text patterns from the article."""
    patterns = ["ADVERTISEMENT", "SCROLL TO CONTINUE WITH CONTENT"]
    # Create a regex pattern to match any of the unwanted texts
    combined_pattern = "|".join(map(re.escape, patterns))
    # Replace unwanted text with an empty string
    cleaned_text = re.sub(combined_pattern, "", text, flags=re.IGNORECASE)
    return cleaned_text


def summarize_with_groq(api_key, text, popular_words):
    """Send text and popular words to Groq API for summarization."""
    from groq import Groq

    client = Groq(
        api_key=api_key,
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Summarize this Indonesia in article :{text}, based on this list of popular words: {popular_words}, this come from more than 1 different news article in same topic, write output also in Bahasa Indonesia",
            }
        ],
        model="llama-3.1-8b-instant",
    )

    return chat_completion.choices[0].message.content
