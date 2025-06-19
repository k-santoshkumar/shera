from langchain_core.documents import Document #type:ignore
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import Html2TextTransformer

def scrape_website_oman(url: str):
    documents = []
    endpoint_lst = [773, 748, 882, 883, 884, 886, 918, 941, 943, 744, 878, 880, 881, 810]
    # final_text = ""
    # return
    for i in endpoint_lst:
        current_url = f"https://www.omaninfo.om/en/pages/204/show/{i}"
        response = requests.get(current_url, verify=False).text
        soup = BeautifulSoup(response, 'lxml')
        respon = soup.find('body')
        title = soup.title.string if soup.title else "No Title"
        text = respon.get_text(separator='\n', strip=True) if respon else ""
        # final_text += f"\n{text}, CURRENT_URL : {current_url}"
        
        documents.append(
        Document(
            page_content=f"\n{text}, \n CURRENT_URL : {current_url}",
            metadata={"source": current_url}
        )
    )
    return documents

def scraper(urls):
    loader = AsyncHtmlLoader(urls)
    docs = loader.load()
    html2text = Html2TextTransformer()
    docs_transformed = html2text.transform_documents(docs)
    return docs_transformed

def crawl_website(base_url, max_depth=1):
    visited = set()  # To keep track of visited URLs
    to_visit = [(base_url, 0)]  # Queue of URLs to visit with their depth
    found_pages = []  # List to store all discovered pages

    while to_visit:
        current_url, depth = to_visit.pop(0)

        # Stop if depth exceeds max_depth
        if depth > max_depth:
            continue

        # Skip if already visited
        if current_url in visited:
            continue

        visited.add(current_url)
        print(f"Visiting: {current_url} (Depth: {depth})")

        try:
            # Fetch the page content
            response = requests.get(current_url, timeout=5, verify=False)
            if response.status_code != 200:
                continue

            found_pages.append(current_url)

            # Parse the page
            soup = BeautifulSoup(response.text, "html.parser")
            for link in soup.find_all("a", href=True):
                href = link.get("href")
                # Resolve relative URLs
                full_url = urljoin(current_url, href)

                # Ensure the URL is part of the same domain
                if urlparse(full_url).netloc == urlparse(base_url).netloc:
                    to_visit.append((full_url, depth + 1))
            if len(found_pages) >= 25:
                print(f"Collected {len(found_pages)} pages so far...")
                break
        except Exception as e:
            print(f"Error visiting {current_url}: {e}")

    return found_pages

def scrape_website(url: str):
    if url.startswith("https://www.omaninfo.om"):
        return scrape_website_oman(url)
    else:
        pages = crawl_website(url)
        documents = scraper(pages)
        return documents

# # Base URL of the website to crawl
# BASE_URL = "https://www.shera.com/en"
# # Start crawling
# pages = crawl_website(BASE_URL)



