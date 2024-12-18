from flask import Flask, render_template, request
from src import CustomSummarizer, DetikNewsApi
from src.groq_summarizer import summarize_with_groq
import os
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)

GROQ_API = os.getenv("GROQ_API")

DN_API = DetikNewsApi()
summarizer = CustomSummarizer()

@app.route("/", methods=["GET", "POST"])
def index():
    summary_details = None
    results = []
    
    if request.method == "POST":
        query = request.form.get("query")
        if query:
            try:
                results = DN_API.search(query, page_number=1, detail=True, limit=5)
                articles = [result["body"] for result in results]
                summary_details = summarizer.summarize(articles)
                summary_text = summary_details['final_summary']
                summary_final = summarize_with_groq(api_key=GROQ_API, text=summary_text)
            except Exception as e:
                summary_details = {"error": str(e)}
    
    return render_template(
        "index.html",
        summary_details=summary_final,
        sources=results
    )
    
if __name__ == "__main__":
    app.run(port=3333, debug=True)