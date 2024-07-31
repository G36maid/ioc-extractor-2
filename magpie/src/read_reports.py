import unicodedata

from bs4 import BeautifulSoup
from readability import Document

def preprocess_article(article):
    with open(article, encoding="utf-8") as file:
        data = file.read()
    doc = Document(data)  # from python library readability
    summary = doc.summary(html_partial=True) # get readable content with html tags
    soup = BeautifulSoup(summary, "lxml_html_clean")
    for drop_tags in soup.find_all(['pre', 'code']): # drop <pre> tag
        drop_tags.decompose()
    cleantext = unicodedata.normalize("NFKD",soup.text)
    article_list = [i for i in cleantext.splitlines() if (i != "" and i != " ")] # sequence
    return article_list
