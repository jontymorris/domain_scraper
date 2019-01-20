from threading import Thread
from requests import request
import urllib3, requests, re
from bs4 import BeautifulSoup, SoupStrainer

# disable insecure warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Worker:
    """ Crawls a domain for emails """
    
    def __init__(self, domain, urls, search_source):
        self.domain = domain
        self.urls = urls
        self.extra_urls = []

        self.emails = []
        self.emails += self.find_emails(search_source)

        print "> Scraping {}".format(domain)
        self.thread = Thread(target=self.run)
        self.thread.start()
    
    def run(self):
        """ Starts the crawling """
        for url in self.urls:
            self.crawl(url, extra_crawl=True)
        
        for url in self.extra_urls:
            self.crawl(url)
    
    def crawl(self, url, extra_crawl=False):
        """ Crawls a url for emails relating to the domain. Can optionally
        find extra urls relating to the domain to crawl later """

        # check for a schema
        if not url.startswith("https://") and not url.startswith("http://"):
            url = "http://" + url

        try:
            # make the request
            headers = {"User-Agent": "Googlebot/2.1 (+http://www.google.com/bot.html"}
            response = requests.get(url, headers=headers, verify=False, timeout=8)

            # check if the request was successful
            if response.status_code == 200:
                response_text = response.text

                # remove bad characters
                for badchar in (">", ":", "=", "<", "/", "\\", ";", "&", "%3A", "%3D", "%3C"):
                    response_text = response_text.replace(badchar, " ")
                
                # find all the emails
                self.emails += self.find_emails(response_text)

                # check if extra crawling should be done
                if extra_crawl:
                    # parse all links in BeautifulSoup
                    for link in BeautifulSoup(response.text, parse_only=SoupStrainer("a"), features="lxml"):
                        try:
                            # check if link has a destination
                            if link.has_attr("href"):
                                # check it isn't an email link
                                if "mailto:" in link["href"] or "@" in link["href"]:
                                    continue
                                
                                # is it a duplicate?
                                if link["href"] in self.urls or link["href"] in self.extra_urls:
                                    continue

                                # is it the full link?
                                if link["href"].startswith("/"):
                                    link["href"] = url + link["href"]

                                # check it relates to domain and there isn't too many extra urls
                                if self.domain in link["href"] and len(self.extra_urls) < 20:
                                    self.extra_urls.append(link["href"])
                        except:
                            pass
        except Exception, ex:
            pass
    
    def find_emails(self, source):
        """ Finds all of the emails relating to the domain """

        emails = re.findall(r"[\w\.-]+@" + self.domain, source, re.I)

        if emails == None:
            emails = []

        return emails

    def wait(self):
        """ Wait until the worker has finished """

        # wait for thread to finish
        self.thread.join()

        # tidy up the emails
        for i in range(len(self.emails)):
            self.emails[i] = self.emails[i].lower()
        
        # remove duplicate emails
        self.emails = list(set(self.emails))

        print "> {} finished".format(self.domain)