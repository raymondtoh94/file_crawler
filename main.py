import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def extract_leaf_links(root_url, file_extension, exclude_path):
    visited_urls = set(exclude_path)
    file_meta = []

    def crawl(url):
        if url in visited_urls or url.endswith(file_extension):
            return
        visited_urls.add(url)

        try:
            response = requests.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            for a_tag in soup.find_all('a', href=True):
                link = a_tag['href']
                if link in exclude_path:
                        continue
                if not link.startswith('http'):
                    link = urljoin(url, link)

                if link not in visited_urls:
                    if link.endswith(file_extension):
                        meta = {}
                        meta["filename"] = link.split("/")[-1]
                        meta["url"] = link
                        file_meta.append(meta)
                    else:
                        print(f"crawling link - {link}")
                        crawl(link)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching page: {e}")

    crawl(root_url)
    return file_meta

if __name__ == '__main__':
    DOWNLOAD_PATH = "./paper"
    file_extension = ".pdf"
    url_index = "https://sapgrp.com/FreeTestPapers/"
    exclude_path = [
        '?C=N;O=D', '?C=M;O=A', '?C=S;O=A', '?C=D;O=A', '/', '/FreeTestPapers/'
    ]

    file_meta = extract_leaf_links(url_index, file_extension, exclude_path)

    if os.path.exists(DOWNLOAD_PATH):
        print("Folder already exists")
    else:
        os.mkdir(DOWNLOAD_PATH)

    # Get response object for link
    for file in file_meta:
        response = requests.get(file["url"])

        # Write content in pdf file
        PATH = os.path.join(DOWNLOAD_PATH, file["filename"])
        pdf = open(PATH, 'wb')
        pdf.write(response.content)
        pdf.close()

        print(f'{file["filename"]} downloaded')