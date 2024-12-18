"""
This program downloads a given number of random images from 4kwallpapers.com.

Program: random-4k-image-downloader
License: MIT
Modified: 18-10-2024
"""

import logging
import os
from typing import Generator

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

BLOCK_SIZE = 1024 * 1024  # 1 MB
WALLPAPER_URL = "https://4kwallpapers.com"
RANDOM_WALLPAPERS_URL = "https://4kwallpapers.com/random-wallpapers/"
PICTURES_DIR = "~/Pictures"

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def fetch_html(url: str) -> BeautifulSoup:
    """Fetch the HTML content of a given URL."""
    try:
        response = requests.get(url, allow_redirects=True)
        response.raise_for_status()
        return BeautifulSoup(response.text, "lxml")
    except requests.RequestException as err:
        logging.error(f"Failed to fetch HTML: {err}")
        raise


def find_pages(base_url: str) -> Generator[str, None, None]:
    """Yield all page URLs from the given base URL."""
    soup = fetch_html(base_url)
    for link in soup.find_all("a", itemprop="url"):
        yield link["href"]


def extract_image_metadata(soup: BeautifulSoup) -> tuple[str, str]:
    """Extract image metadata from parsed HTML."""
    image_tag = soup.find("a", id="resolution")
    if not image_tag:
        raise ValueError("Image resolution link not found")
    postfix = soup.find("meta", itemprop="keywords")["content"]  # pyright: ignore
    href = image_tag["href"]  # pyright: ignore
    return postfix.replace(" ", "-").replace(",", "")[:20], href  # pyright: ignore


def download_image(url: str, filepath: str):
    """Download an image and save it to a file with a progress bar."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get("content-length", 0))

        with open(filepath, "wb") as file, tqdm(
            total=total_size, unit="B", unit_scale=True, desc="Downloading"
        ) as progress_bar:
            for chunk in response.iter_content(BLOCK_SIZE):
                file.write(chunk)
                progress_bar.update(len(chunk))
    except requests.RequestException as err:
        logging.error(f"Failed to download {url}: {err}")
        raise


def process_page(url: str, index: int):
    """Process a single page and download the corresponding image."""
    soup = fetch_html(url)
    postfix, href = extract_image_metadata(soup)
    image_url = WALLPAPER_URL + href
    filepath = os.path.join(os.getcwd(), f"{index}-{postfix}.jpg")
    download_image(image_url, filepath)


def main():
    """Entry point to the program."""
    os.makedirs(os.path.expanduser(PICTURES_DIR), exist_ok=True)
    os.chdir(os.path.expanduser(PICTURES_DIR))

    for index, page_url in enumerate(find_pages(RANDOM_WALLPAPERS_URL)):
        try:
            logging.info(f"Processing page {page_url}")
            process_page(page_url, index)
        except Exception as e:
            logging.error(f"Error processing page {page_url}: {e}")


if __name__ == "__main__":
    main()
