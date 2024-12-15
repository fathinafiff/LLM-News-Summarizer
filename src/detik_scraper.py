import re
from requests import get
from urllib.parse import urlsplit
from bs4 import BeautifulSoup


class DetikNewsApi:

    def __init__(self):
        """Search URL"""
        self.search_url = "https://www.detik.com/search/searchall?"

    def build_search_url(self, query: str, page_number: int):
        """Building search url with query input, we can jump to specific page number"""
        qs = f"query={query}"
        qs2 = "&siteid=3&sortby=time&sorttime=0&page="
        return self.search_url + qs + qs2 + str(page_number)

    def build_detail_url(self, url: str):
        """Build detail URL will turn off pagination in detail page"""
        a = urlsplit(url)
        qs = "single=1"
        detail_url = a.scheme + "://" + a.netloc + a.path + "?" + qs
        return detail_url

    def result_count(self, search_response):
        """Search result count, need search response page"""
        soup = BeautifulSoup(search_response.text, "html.parser")
        tag = soup.find("span", "fl text").text
        count = [int(s) for s in tag.split() if s.isdigit()]
        return count[0]

    def detail(self, url: str) -> str:
        detail_url = self.build_detail_url(url)
        req = get(detail_url)
        soup = BeautifulSoup(req.text, "html.parser")
        tag = soup.find("div", class_="detail__body-text")
        body = ""
        if tag:
            for p in tag.find_all("p"):
                body += p.text
        else:
            tag = soup.find("div", class_="itp_bodycontent")
            if tag:
                for p in tag.find_all("p"):
                    body += p.text
        return body

    def get_article(self, url: str) -> str:
        """Get article content from the given URL"""
        req = get(url)
        soup = BeautifulSoup(req.text, "html.parser")
        body = ""

        # Try to find content in 'detail__body-text' class
        detail_tag = soup.find("div", class_="detail__body-text")
        if detail_tag:
            for p in detail_tag.find_all("p"):
                body += p.text

        # If 'detail__body-text' is not found, try 'itp_bodycontent'
        if not body:
            itp_tag = soup.find("div", class_="itp_bodycontent")
            if itp_tag:
                for p in itp_tag.find_all("p"):
                    body += p.text

        return body

    def parse(self, search_response, detail=False, limit=None):
        soup = BeautifulSoup(search_response.text, "html.parser")
        tag = soup.find_all("article")
        data = []
        news_pattern = re.compile(r"https://news\.detik\.com/.*")
        count = 0

        for i in tag:
            if limit is not None and count >= limit:
                break

            judul = i.find("h3").find("a").text
            link = i.find("a").get("href")
            if not news_pattern.match(link):
                continue
            gambar = i.find("img").get("src")
            body = ""
            if detail:
                body = self.detail(link)
            waktu = i.find("div", class_="media__date").find("span").get("title")
            data.append(
                {
                    "judul": judul,
                    "link": link,
                    "gambar": gambar,
                    "body": body,
                    "waktu": waktu,
                }
            )
            count += 1
        return data

    def search(self, query, page_number=1, detail=False, limit=None):
        url = self.build_search_url(query, page_number)
        search_response = get(url)
        parse_result = self.parse(search_response, detail, limit)
        return parse_result


if __name__ == "__main__":
    DN_API = DetikNewsApi()

    # Example usage
    query = "covid"
    results = DN_API.search(query, page_number=1, detail=True, limit=5)

    for result in results:
        print(result["judul"])
        print(result["link"])
        print(result["gambar"])
        print(result["body"])  # Full article body
        print(result["waktu"])
        print("-" * 80)
