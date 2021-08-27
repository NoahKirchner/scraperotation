import requests
from bs4 import BeautifulSoup
import re
import base64


class ProxyScraper:

    # Init function. For now the proxy source is hardcoded because this scraper will only work for this site.
    def __init__(self, pages: int = 1, number: int = 10):
        self.proxy_source   =   "http://free-proxy.cz/en/proxylist/country/all/all/ping/level1/{}"

        self.proxy_list     =   self._clean_dict(   # Kind of ugly, but uses all of the helper
            self._clean_proxies(                    # functions to generate a list of valid proxy
                self._return_raw_proxies(           # dictionaries.
                    self.proxy_source, pages)))

        self.proxy_list     =   self._test_list(        # Tests the proxies to make sure that they work,
            self.proxy_list, number)                    # trims the proxy_list to the desired length

    # Refresh method. Separate from init but functionally very similar.
    def refresh(self, pages: int = 1, number: int = 10):
        self.proxy_list     = list()
        self.proxy_list     = self._clean_dict(self._clean_proxies(self._return_raw_proxies(self.proxy_source, pages)))
        self.proxy_list     = self._test_list(self.proxy_list, number)

    # Just a simple way to not have to constantly be updating a "size of list" property.
    def size(self):
        return len(self.proxy_list)

    # These methods are DESTRUCTIVE, they remove the proxy from the list entirely to prevent
    # programs from cycling through the same ones. There are non-destructive methods below.
    def get_tuple(self, number: int = 1):   # Returns list of tuples in (ip, port) format.
        return_list = list()
        if number > len(self.proxy_list):
            number = len(self.proxy_list)
        for i in range(1, number + 1):
            return_list.append((self.proxy_list[i]['ip'], self.proxy_list[i]['port']))
            self.proxy_list.pop(i)
        return return_list

    def get(self, number: int = 1):         # Returns a list of the full proxy dictionaries.
        return_list = list()
        if number > len(self.proxy_list):
            number = len(self.proxy_list)
        for i in range(1, number + 1):
            return_list.append(self.proxy_list.pop(i))
        return return_list

    # These methods are NOT destructive. They will maintain the internal proxy_list, but will
    # require you to specify an index or range of proxies to return.

    def get_tuple_safe(self, number):    # Returns an (ip, port) proxy without removing the item from the list.
        return_list = list()
        if number > len(self.proxy_list):
            number = len(self.proxy_list)
        for i in range(1, number + 1):
            return_list.append((self.proxy_list[i]['ip'], self.proxy_list[i]['port']))
        return return_list

    def get_safe(self, number):          # Returns a proxy dict without removing the item from the list.
        return_list = list()
        if number > len(self.proxy_list):
            number = len(self.proxy_list)
        for i in range(1, number + 1):
            return_list.append(self.proxy_list[i])
        return return_list

    def get_all(self):                   # Returns an exact copy of the internal list.
        return self.proxy_list

    def get_range(self, first, second):  # Returns a range from the internal list safely.
        if first < 0:
            first = 0
        if second > len(self.proxy_list):
            second = len(self.proxy_list)
        return self.proxy_list[first:second]

    # HELPERS #

    @staticmethod
    def _return_raw_proxies(proxy_source, pages: int = 5):  # Scrapes the initial list of untested, raw info.
        encode_regex    = re.compile(r'".+"')  # Each proxy on the website has different amounts of info, so
        content_list    = list()    # The list cannot be combined into dicts at the beginning.
        raw_list        = list()
        for i in range(1, pages+1):
            content_list.append(requests.get(proxy_source.format(i)))

        for i in content_list:
            soup = BeautifulSoup(i.content, 'html.parser')
            proxy_list = soup.find(id='proxy_list').findAll('td')
            for td in proxy_list:
                if td.find('script'):
                    for line in td.find('script'):
                        base64_string = encode_regex.search(line).group().replace('"', '')
                        raw_list.append([base64.b64decode(base64_string.encode('ascii')).decode('ascii')])
                        # Changing this type to list so that we can combine this data into individual tuples
                        # later. Right now it is just one big stream of data, but changing the type of the
                        # first element allows us to easily split the data up.

                line = td.text
                if line and line[0] is " ":  # Text re-formatting
                    line = line.replace(" ", "", 1)
                if len(line) > 1:
                    raw_list.append(line)
        return raw_list

    @staticmethod
    def _clean_proxies(raw_list: list):  # Turns the raw stream of data into a list of lists.
        buffer = list()
        out_list = list()

        for item in raw_list:
            if buffer and type(item) is list:
                out_list.append(list(buffer))
                buffer = list()
                buffer.append(item)
            else:
                buffer.append(item)

        for i, item in enumerate(out_list):
            item[0] = item[0][0]

        for i, item in enumerate(out_list):
            if len(item) != 11:
                out_list.pop(i)

        return out_list

    @staticmethod
    def _clean_dict(in_list: list):  # Assigns the values in the list of lists into dictionaries with keys
        out_list = list()   # that represent their relevant values.
        for item in in_list:
            new_entry = dict()
            new_entry['ip']         =   item[0]     # IP Addr
            new_entry['port']       =   item[1]     # Port
            new_entry['protocol']   =   item[2]     # Protocol (SOCKS, HTTP, etc)
            new_entry['country']    =   item[3]     # Country
            new_entry['level']      =   item[6]     # Level of protection
            new_entry['speed']      =   item[7]     # Speed of proxy
            out_list.append(new_entry)

        return out_list

    @staticmethod
    def _test_list(input_list: list, size: int = 50):  # Uses sessions to test the validity of the proxies,
        output_list = list()    # This is the largest bottleneck, and could be improved with concurrency.

        for item in input_list[0:size]:
            test_session = requests.session()
            test_session.proxies.update({(item['ip'], item['port'])})
            if test_session.get("http://google.com"):
                output_list.append(item)

        return output_list

Test = ProxyScraper()