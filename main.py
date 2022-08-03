import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import os

def findAllHtmlPages(mainPageUrl):
    request = requests.get(mainPageUrl,allow_redirects = True)
    data = BeautifulSoup(request.text,'lxml')
    all_pages = data.find_all('a', itemprop="url")
    return all_pages

def photoDowloader(url, urlPrefix, count):
    request = requests.get(url,allow_redirects = True)
    data = BeautifulSoup(request.text,'lxml')
    image_url = data.find('a', id="resolution")
    filePostfix = data.find('meta', itemprop="keywords")['content'].replace(" ", "-").replace(",", "")[:20]
    if image_url != None:
        i_url = image_url['href']
        try:
            response = requests.get(urlPrefix + i_url, stream=True)
            total_size_in_bytes= int(response.headers.get('content-length', 0))
            block_size = 1024 #1 Kibibyte
            progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
            with open(f'{count}-{filePostfix}.jpg', 'wb') as file:
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    file.write(data)
            progress_bar.close()
            if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
                print("ERROR, something went wrong")
        except:
            print("it might be the Connection broken :|")
            

if __name__ == "__main__":
    allPages = findAllHtmlPages("https://4kwallpapers.com/random-wallpapers/")
    count = 0
    os.chdir(os.path.expanduser('~/Pictures'))
    for page in allPages:
        url = page['href']
        photoDowloader(url, "https://4kwallpapers.com", count)
        count += 1
