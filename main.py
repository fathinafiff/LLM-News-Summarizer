from flask import Flask, render_template, request
import os
import requests
from dotenv import load_dotenv
from src import (
    DetikNewsApi,
    extract_popular_words,
    summarize_with_groq,
    clean_article_text,
)

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Initialize DetikNewsApi
DN_API = DetikNewsApi()

# Groq API URL and key
api_key = os.getenv("GROQ_API")


@app.route("/", methods=["GET", "POST"])
def index():
    summary = ""
    sources = []
    if request.method == "POST":
        query = request.form.get("query")
        if query:
            # Fetch news articles
            results = DN_API.search(query, page_number=1, detail=True, limit=5)

            # Extract and clean articles
            articles = [result["body"] for result in results]
            cleaned_articles = [clean_article_text(article) for article in articles]
            popular_words = extract_popular_words(cleaned_articles)

            # Concatenate articles for summarization
            text_to_summarize = " ".join(cleaned_articles)

            # Get the summary
            summary = summarize_with_groq(api_key, text_to_summarize, popular_words)

            # Collect source information
            sources = [
                {"title": result["judul"], "link": result["link"]} for result in results
            ]

    return render_template("index.html", summary=summary, sources=sources)


if __name__ == "__main__":
    app.run(debug=True)
