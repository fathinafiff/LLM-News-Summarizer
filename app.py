from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
from src.text_processor import TextProcessor
from src.detik_scraper import DetikNewsApi

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize DetikNewsApi
DN_API = DetikNewsApi()

processor = TextProcessor(api_key=os.getenv("GROQ_API"))

@app.route("/", methods=["GET", "POST"])
def index():
    summary = ""
    key_sentences = []
    results = []
    
    if request.method == "POST":
        query = request.form.get("query")
        if query:
            try:
                # Fetch news articles
                results = DN_API.search(query, page_number=1, detail=True, limit=5)
                articles = [result["body"] for result in results]
                
                # Process articles and get summary
                key_sentences, summary = processor.process_articles(articles)
                
            except Exception as e:
                summary = f"Error processing articles: {str(e)}"
                key_sentences = []
    
    return render_template(
        "index.html", 
        summary=summary, 
        key_sentences=key_sentences,
        sources=results
    )

if __name__ == "__main__":
    app.run(debug=True)