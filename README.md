# News Summarizer Project Documentation

## Project Overview

This project provides a web application that allows users to input search queries for news articles, which are then summarized using custom extractive summarization. The application retrieves news articles, processes them, and displays both the summarized content and the sources of the information.

<div>
  <img align="center" src="references/example.gif">
</div>

## Directory Structure

```plaintext
├── src
│   ├── __init__.py
│   ├── custom_summarizer.py
│   └── detik_scraper.py
├── static
│   ├── script.js
│   └── styles.css
├── templates
│   └── index.html
├── app.py
├── pyproject.toml
├── uv.lock
├── EXPLANATION.md
└── README.md
```

## Files and Directories

### Core Files

- `app.py`: Main Flask application file
- `EXPLANATION.md`: Detailed explanation of how the summarizer works
- `pyproject.toml`: Project dependencies and metadata
- `uv.lock`: Lock file for uv dependency management

### Source Code (`src/`)

- `custom_summarizer.py`: Custom extractive summarization implementation
- `detik_scraper.py`: DetikNews scraping functionality
- `__init__.py`: Package initialization file

### Web Assets

- `static/`: CSS and JavaScript files
- `templates/`: HTML template files

## Setup and Installation

1. **Clone the repository**

2. **Install uv** (if not already installed):

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Create virtual environment and install dependencies**:

   ```bash
   uv venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   uv sync
   ```

4. Make sure to create `.env` file

   ```
   cp .env.example .env
   ```

5. Fill in the values of Api From Groq Console

6. **Run the Flask application**:

   ```bash
   python app.py
   ```

7. **Access the application** at `http://127.0.0.1:3333/`

## Usage

1. Enter a search query in the input field
2. Click "Get Summary" to process news articles
3. View:
   - Original collected articles
   - Sentence analysis and scoring
   - Final generated summary
   - Source article links

## Core Features

- Custom extractive summarization (no external API dependency)
- Indonesian language support
- Multi-article processing
- Detailed process visualization
- Source article tracking

## Dependencies

Major dependencies include:

- `Flask`: Web framework
- `requests`: HTTP client
- `beautifulsoup4`: HTML parsing
- `nltk`: Natural language processing
- `numpy`: Numerical computations
- `networkx`: Graph algorithms

For a complete list of dependencies, see `pyproject.toml`.

## Development

To add new dependencies:

```bash
uv add <package-name>
```

To update dependencies:

```bash
uv sync
```

## Documentation

For detailed information about how the summarizer works, please refer to `EXPLANATION.md`.
