from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
import google.generativeai as genai
from crawl4ai import AsyncWebCrawler  # Importing the correct class
import asyncio

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("Please set the GEMINI_API_KEY environment variable in .env")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-001')

app = Flask(__name__, template_folder='.')

def fetch_content_crawl4ai(url: str) -> str:
    """Fetches webpage content using crawl4ai asynchronously."""
    from crawl4ai import AsyncWebCrawler
    import asyncio

    async def crawl():
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url)
            if result.success:
                return result.markdown.raw_markdown
            else:
                print(f"crawl4ai failed to crawl: {url}")
                return None

    try:
        return asyncio.run(crawl())
    except Exception as e:
        print(f"Error during crawl4ai fetching: {e}")
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        url = request.form["url"]
        try:
            content = fetch_content_crawl4ai(url)

            if content:
                # Basic prompt for summarization (you can customize this)
                prompt = f"Summarize the following web content:\n\n{content}"
                response = model.generate_content(prompt)
                result = response.text
            else:
                result = "Could not fetch content from the provided URL."

        except Exception as e:
            result = f"An error occurred: {e}"

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)