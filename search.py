from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from random import choice, randint
from time import sleep


class SearchResult:
    """ Holds information about a search result """

    def __init__(self, urls, page_source):
        self.urls = urls
        self.page_source = page_source


class Searcher:
    """ Queires a search engine for information """

    def __init__(self, limit):
        self.limit = limit

        self.google_servers = [
            'google.co.in','google.com','google.hu','google.is','google.co.in','google.co.id',
            'google.dz','google.at','google.dk','google.fr','google.by','google.com.bo',
            'google.hr','google.ci','google.de','google.gr','google.gl','google.hk',
            'google.ie','google.la','google.lv','google.kz','google.lt',
            'google.com.tj','google.co.th','google.com.tr','google.fr','google.com.uy',
            'google.co.uz','google.com.ua','google.vu','google.com.vn'
        ]

        options = Options()
        options.set_headless(headless=False)

        self.browser = webdriver.Firefox(firefox_options=options, executable_path="./geckodriver")
        self.browser.set_page_load_timeout = 5
    
    def google_search(self, text, add_delay=True):
        """ Searches Google for the text """
        
        query = "https://www.{}/search?tbs=li:1&num={}&q={}".format(choice(self.google_servers), str(self.limit), "+".join(text.split(" ")))
        
        # query google
        try:
            self.browser.get(query)
        except:
            print "Failed to search for " + text

        # add delay
        if add_delay:
            sleep(randint(4, 7))

        # get all the links
        links = []
        for element in self.browser.find_elements_by_class_name("iUh30"):
            try:
                links.append(element.text)
            except:
                print "Something went wrong with Google"

        # record the page source
        page_source = ""
        if self.browser.page_source:
            page_source = self.browser.page_source

        # click a random link
        try:
            self.browser.get(choice(self.browser.find_elements_by_tag_name("a")).get_attribute("href"))
        except:
            pass

        # add another delay
        if add_delay:
            sleep(randint(20, 80))

        return SearchResult(links, page_source)

    def close(self):
        """ Tie up any loose ends """

        self.browser.quit()