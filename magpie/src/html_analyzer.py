from typing import List
from readability import Document
from bs4 import BeautifulSoup
import unicodedata
import string

class Analyzer(object):

    remove_words = '!"#$%&\'()*+,-.:;<=>?@[\\]^_`{|}~' + string.whitespace

    def __init__(self, soup, tags):
        self.soup = soup
        self.replace_table_tag()
        self.delete_tags(tags)

    def replace_table_tag(self):
        
        """
        replace <table> with a couple of <p>
        """

        table = self.soup.find_all('table')
        for row in table:
            allcols = row.findAll('tr')
            for col in allcols:
                thestrings = [s for s in col.findAll(string=True)]
                thestrings.append(' ')
                thetext = ' '.join(thestrings)
                new_tag = self.soup.new_tag('p')
                new_tag.string = thetext
                self.soup.find('table').append(new_tag)
            self.soup.find('tbody').decompose()

    def delete_tags(self, tags: List[str]):
        
        """
        delete selected html tag(s)
        """

        for drop_tags in self.soup.find_all(tags): 
            drop_tags.decompose()

    def clean_article(article):
        
        """
        parse html website to clean text
        :param article's filepath
        """

        with open(article, encoding="utf-8") as file:
            data = file.read()
        doc = Document(data)  
        summary = doc.summary(html_partial=True)
        soup = BeautifulSoup(summary, "lxml")
        Analyzer(soup, tags=['pre', 'img', 'code'])
        cleantext = unicodedata.normalize("NFKD",soup.text)
        # lines = [i.rstrip(Analyzer.remove_words,) 
        #          for i in cleantext.splitlines() if (i != "" and i != " ")] 
        cleantext = list(map(lambda x: x.rstrip(Analyzer.remove_words,), cleantext.splitlines()))
        return cleantext
