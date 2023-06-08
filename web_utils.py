import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
from tqdm import tqdm
import json

clean_texts = dict()


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)


def getdata(url):
    # add header to prevent being blocked (403 error) by wordpress websites
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    r = requests.get(url, headers=headers)
    return r.text


def get_links(website_link, website):
    html_data = getdata(website_link)
    soup = BeautifulSoup(html_data, "html.parser")
    text = text_from_html(html_data)
    clean_texts[website_link] = text
    list_links = []
    for link in soup.find_all("a", href=True):
        # Append to list if new link contains original link
        if str(link["href"]).startswith((str(website))):
            list_links.append(link["href"])

        # Include all href that do not start with website link but with "/"
        if str(link["href"]).startswith("/"):
            if link["href"] not in dict_href_links:
                print(link["href"])
                dict_href_links[link["href"]] = None
                link_with_www = website + link["href"][1:]
                print("adjusted link =", link_with_www)
                list_links.append(link_with_www)

    # Convert list of links to dictionary and define keys as the links and the values as "Not-checked"
    dict_links = dict.fromkeys(list_links, "Not-checked")
    return dict_links


def get_subpage_links(l, website):
    for link in tqdm(l):
        # If not crawled through this page start crawling and get links
        if l[link] == "Not-checked":
            dict_links_subpages = get_links(link, website)
            # Change the dictionary value of the link to "Checked"
            l[link] = "Checked"
        else:
            # Create an empty dictionary in case every link is checked
            dict_links_subpages = {}
        # Add new dictionary to old dictionary
        l = {**dict_links_subpages, **l}
    return l


def get_subpages(link):
    global clean_texts
    website = link
    dict_links = {website: "Not-checked"}
    clean_texts = dict()

    counter, counter2 = None, 0
    while counter != 0:
        counter2 += 1
        dict_links2 = get_subpage_links(dict_links, website)
        counter = sum(value == "Not-checked" for value in dict_links2.values())
        dict_links = dict_links2
    return clean_texts


if __name__ == "__main__":
    dict_href_links = {}
    get_subpages("https://www.edulai.com/")
