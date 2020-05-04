import requests
from bs4 import BeautifulSoup as bs
import re
import time
import datetime
import pandas as pd
import openpyxl

now = datetime.datetime.now()

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9}',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'}

# В дальнейшем будет инпут через Jupyter Notebook
base_url = 'https://auto.ru/moskva/cars/bmw/1er/all/?sort=fresh_relevance_1-desc'
base_url = re.sub('&page=1', '', base_url)
base_url = re.sub('output_type=list', 'output_type=table', base_url)


class CarAdItem:
    """
    Auto RU ad item
    """

    def __init__(self, ad):
        """
        Class constructor
        :param ad: bs4 html container of ad
        """
        self.title = ad.find('a', attrs={'class': 'ListingItemTitle-module__link'}).text
        self.cost, self.currency = self._get_cost_info(ad)
        self.km = self._get_km(ad)
        self.car_age = self._get_age(ad)
        self.location = self._get_location(ad)
        self.link = ad.find('a', attrs={'class': 'ListingItemTitle-module__link'})['href']

    def show_info(self):
        """
        show info about ad
        """
        print('Title:', self.title)
        print('Cost:', self.cost, self.currency)
        print('Killometrage:', self.km)
        print('Age:', self.car_age)
        print('Location:', self.location)
        print('Link:', self.link)

    def get_info(self) -> dict:
        """
        getting information about ad
        """
        return {
            'Title': self.title,
            'Cost': self.cost,
            'Currency': self.currency,
            'Killometrage': self.km,
            'Age': self.car_age,
            'Location': self.location,
            'Link': self.link,
        }

    @staticmethod
    def _get_location(item):
        """
        getting ad's location
        """
        loc = item.find('div', attrs={'class': 'ListingItemSequential-module__place'})
        if loc is None:
            loc = item.find('span', attrs={'class': 'MetroListPlace__regionName'})
        if loc is None:
            print('Location does not found')
            return 'Undefended'
        return loc.text

    @staticmethod
    def _get_age(item):
        """
        car's age calculation
        """
        produced_year = item.find('div', attrs={'class': 'ListingItemSequential-module__year'})
        if produced_year is None:
            produced_year = item.find('div', attrs={'class': 'ListingItem-module__year'})
        if produced_year is None:
            print('Age does not found')
            return 'Undefended'
        return now.year - int(produced_year.text)

    @staticmethod
    def _get_km(item):
        """
        Killometrage formating
        """
        km = item.find('div', attrs={'class': 'ListingItemSequential-module__kmAge'})
        if km is None:
            km = item.find('div', attrs={'class': 'ListingItem-module__kmAge'})
        if km is None:
            print('Killometrage does not found')
            return 'Undefended'
        if km.text == 'Новый':
            return 0
        return int(re.sub('[^0-9]', '', km.text))

    @staticmethod
    def _get_cost_info(item):
        """"
        Currency check and separate
        """
        cost = item.find('div', attrs={'class': 'ListingItemPrice-module__content'}).text
        if re.search('₽', str(cost)) is not None:
            currency = 'RUB'
        elif re.search('€', str(cost)) is not None:
            currency = 'EUR'
        elif re.search('$', str(cost)) is not None:
            currency = 'USD'
        else:
            currency = 'Unknown'
        cost = int(re.sub('[^0-9]', '', cost))
        return cost, currency


def parse_page(page_url, headers=headers):
    page_data = []
    session = requests.Session()
    try:
        request = session.get(page_url, headers=headers)
    except requests.exceptions.ConnectionError:
        return []
    if request.status_code == 200:
        soup = bs(request.content, 'html.parser')
        url = page_url
        items = soup.find_all("div", attrs={'class': 'ListingItem-module__main'})
        # items - blocks with one car in each
        for item in items:
            ad = CarAdItem(item)
            ad.show_info()
            page_data.append(ad.get_info())
            print(item)
            print(ad.get_info())

    next_page = soup.find('link', attrs={'rel': 'next'})
    if next_page is not None:
        next_page_url = next_page['href']
    else:
        next_page_url = None
    return page_data, next_page_url


def auto_ru_parse(base_url, headers=headers) -> list:
    """
    Parser for web site AUTO.ru
    Approximately 3-5 secs for one page parse
    :param base_url: Url from auto.ru to parse (all pages will parser)
    :param headers: param for request - optional
    also create excel file - Output.xlsx - in current directory with ad_data
    """
    ad_data = []
    url = base_url
    while True:
        time.sleep(2)
        page_data, url = parse_page(url, headers)
        print(url)
        ad_data += page_data
        if url is None:
            break
    df = pd.DataFrame(ad_data)
    df.to_excel('Output.xlsx', encoding='utf-8-sig', index=False)
    return ad_data


auto_ru_parse(base_url, headers)
