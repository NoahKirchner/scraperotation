import requests
from bs4 import BeautifulSoup
import re
import base64

class Rotator:
    proxy_source    = None
    proxy_list = None


    def __init__(self):
        self.proxy_source   = "http://free-proxy.cz/en/proxylist/country/all/all/ping/level1{}"
        self.proxy_list     =   self._clean_dict(self._clean_proxies(self.return_raw_proxies(5)))

    def return_raw_proxies(self, pages:int=1):
        encode_regex    = re.compile(r'".+"')
        content_list    = list()
        raw_list        = list()
        for i in range(1,pages+1):
            content_list.append(requests.get(self.proxy_source.format(i)))
        for i in content_list:
            soup = BeautifulSoup(i.content, 'html.parser')
            proxy_list = soup.find(id='proxy_list').findAll('td')
            for td in proxy_list:
                if td.find('script'):
                    for line in td.find('script'):
                        base64_string = encode_regex.search(line).group().replace('"', '')
                        raw_list.append([base64.b64decode(base64_string.encode('ascii')).decode('ascii')])
                        #Changing this type to list so that we can combine this data into individual tuples
                        #later. Right now it is just one big stream of data, but changing the type of the
                        #first element allows us to easily split the data up.

                line = td.text
                if line and line[0] is " ":
                    line = line.replace(" ", "", 1)
                if len(line) > 1:
                    raw_list.append(line)
        return raw_list



    def _clean_proxies(self, raw_list:list):
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

        for item in out_list:
            if len(item) != 11:
                out_list.remove(item)

        return out_list

    def _clean_dict(self, in_list:list):
        out_list = list()
        for item in in_list:
            new_entry = dict()
            new_entry['ip']         =   item[0]     #IP Addr
            new_entry['port']       =   item[1]     #Port
            new_entry['protocol']   =   item[2]     #Protocol (SOCKS, HTTP, etc)
            new_entry['country']    =   item[3]     #Country
            new_entry['region']     =   item[4]     #Region of country
            new_entry['city']       =   item[5]     #City in country
            new_entry['level']      =   item[6]     #Level of protection
            new_entry['speed']      =   item[7]     #Speed of proxy
            new_entry['uptime']     =   item[8]     #Approximate percentage uptime
            new_entry['response']   =   item[9]     #Response speed from http request made
            out_list.append(new_entry)

        return out_list








Test = Rotator()