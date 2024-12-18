from flask import Flask, render_template, request
from src import CustomSummarizer, DetikNewsApi
from src.groq_summarizer import summarize_with_groq
import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
app = Flask(__name__)
GROQ_API = os.getenv("GROQ_API")
DN_API = DetikNewsApi()
summarizer = CustomSummarizer()


@app.route("/", methods=["GET", "POST"])
def index():
    summary_final = None
    results = []

    if request.method == "POST":
        query = request.form.get("query")
        logger.info(f"Processing search query: {query}")

        if query:
            try:
                results = DN_API.search(query, page_number=1, detail=True, limit=5)
                logger.info(f"Found {len(results)} articles for query: {query}")

                if not results:
                    return render_template(
                        "index.html",
                        summary_details="No articles found. Please try a different search term.",
                        sources=[],
                    )

                # Prepare original articles
                original_articles = []
                for idx, result in enumerate(results, 1):
                    original_articles.append(
                        {
                            "index": idx,
                            "text": result["body"],
                            "length": len(result["body"]),
                        }
                    )

                # Get initial summary and analysis
                articles = [result["body"] for result in results]
                summary_details = summarizer.summarize(articles)

                # Get Groq summary
                groq_summary = summarize_with_groq(
                    api_key=GROQ_API, text=summary_details["final_summary"]
                )

                # Combine all details
                summary_final = {
                    "original_articles": original_articles,
                    "sentence_details": summary_details.get("sentence_details", []),
                    "selected_sentences": summary_details.get("selected_sentences", []),
                    "final_summary": groq_summary,  # Use Groq summary as final summary
                }

                logger.info("Successfully generated complete analysis")

            except Exception as e:
                logger.error(f"Error processing request: {str(e)}")
                return render_template(
                    "index.html",
                    summary_details=f"An error occurred: {str(e)}",
                    sources=[],
                )

    return render_template("index.html", summary_details=summary_final, sources=results)


if __name__ == "__main__":
    if not GROQ_API:
        logger.warning("GROQ_API environment variable is not set!")

    app.run(port=3333, debug=True)
