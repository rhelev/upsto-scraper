import requests
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError

MAIN_URL = "http://tess2.uspto.gov"
SEARCH_URL = "http://tmsearch.uspto.gov"


class UsptoParser():
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.80 Safari/537.36 Edg/86.0.622.48'}

    def get_search_url(self, url):
        '''
        Create search url
        :param url: str
        :return: str
        '''
        return url.replace("gate.exe?f=tess",
                           "showfield?f=toc") + "&p_search=searchstr&BackReference=&p_L=100&p_plural=yes&p_s_PARA1=20201124&p_tagrepl~%3A=PARA1%24PO&expr=PARA1+and+PARA2&p_s_PARA2=&p_tagrepl~%3A=PARA1%24ALL&a_default=search&a_search=Submit+Query"

    def get_response_data_url(self, url):
        '''
        Make request
        :param url: str
        :return: set(responce.text, responce.url)
        '''
        data = None
        response_url = None
        try:
            response = self.session.get(url, headers=self.headers)
            data = response.text
            response_url = response.url
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        return (data, response_url)

    def parse_search_table(self, data):
        '''
        Get urls from table
        :param data: responce.text
        :return: list
        '''
        soup = BeautifulSoup(data, 'html.parser')
        records_info = soup.find('font', attrs={'size': '+2'}).text.split()
        if not records_info:
            print("Records not found")
            return False
        records_count = records_info[0]
        table = soup.find('table', attrs={'border': '2'})
        result = []
        if table:
            link = table.find('a')
            if link:
                query = link.get('href').rstrip("1")
                if query.startswith("/bin/showfield?f=doc&state"):
                    for i in range(1, int(records_count) + 1):
                        result.append(f"{SEARCH_URL}{query}{i}")
                else:
                    print("Undefined query")
                    return False
        return result

    def check_responce_data(self, data):
        '''
        :param data: (responce.text, responce.url)
        :return: bool
        '''
        if data[1] is None:
            return False
        if data[0] is None or data[0].find("TESS -- Error") != -1:
            print(f"Page with error: {data[0]}")
            return False
        return True


def main():
    parser = UsptoParser()
    main_url_responce = parser.get_response_data_url(MAIN_URL)
    if parser.check_responce_data(main_url_responce):
        search_url = parser.get_search_url(main_url_responce[1])
        search_responce = parser.get_response_data_url(search_url)
        if parser.check_responce_data(search_responce):
            table_urls = parser.parse_search_table(search_responce[0])
            if table_urls:
                print(f"URLS_COUNT:{len(table_urls)}")
                # Parse urls


if __name__ == '__main__':
    main()
