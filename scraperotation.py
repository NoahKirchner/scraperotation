import requests
from bs4 import BeautifulSoup

class Rotator:
    proxy_source    = None
    raw_proxy_list  = None
    safe_proxy_list = None


    def __init__(self):
        self.proxy_source = "http://free-proxy.cz/en/proxylist/country/all/all/ping/level1{}"

    def return_proxies(self, pages:int=1):
        content_list = list()
        for i in range(1,pages+1):
            content_list.append(requests.get(self.proxy_source.format(i)))
        for i in content_list:
            soup = BeautifulSoup(i.content, 'html.parser')
            proxy_list = soup.find(id='proxy_list').findAll('td')
            for td in proxy_list:
                print(td.text)


Test = Rotator().return_proxies(1)