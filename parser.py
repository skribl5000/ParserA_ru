import requests
from bs4 import BeautifulSoup as bs
import re
import time
import datetime
import pandas as pd
import openpyxl
now = datetime.datetime.now()

headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'}

# В дальнейшем будет инпут через Jupyter Notebook
base_url = 'https://auto.ru/moskva/cars/toyota/land_cruiser/7953212/all/?sort=fresh_relevance_1-desc'
base_url = re.sub('&page=1','',base_url)
base_url = re.sub('output_type=list','output_type=table',base_url)

class CarAdItem:
    """
    Auto RU ad item
    """
    def __init__(self, ad):
        """
        Class contructor
        :param ad: bs4 html container of ad
        """
        self.title = ad.find('a',attrs={'class': 'ListingItemTitle-module__link'}).text
        self.cost, self.currency = self.get_cost_info(ad)
        self.km = self.get_km(ad)
        self.car_age = self.get_age(ad)
        self.location = self.get_location(ad)
        self.link = ad.find('a', attrs={'class': 'ListingItemTitle-module__link'})['href']
    def get_cost_info(self, item):
        """"
        Currency check and separate
        """
        cost = item.find('div',attrs = {'class': 'ListingItemPrice-module__content'}).text
        if re.search('₽', str(cost)) != None:
            currency = 'RUB'
        elif re.search('€', str(cost)) != None:
            currency = 'EUR'
        elif re.search('$', str(cost)) != None:
            currency = 'USD'
        else:
            currency = 'Unknown'
        cost = int(re.sub('[^0-9]', '', cost))
        return cost, currency
    def get_km(self, item):
        """
        Killometrage formating
        """
        km = item.find('div', attrs={'class': 'ListingItemSequential-module__kmAge'})
        if km == None:
            km = item.find('div', attrs={'class': 'ListingItem-module__kmAge'})
        if km == None:
            print('Killometrage does not found')
            return 'Undefinded'
        return int(re.sub('[^0-9]', '', km.text))
    def get_age(self, item):
        """
        car's age calculation
        """
        produced_year = item.find('div', attrs={'class': 'ListingItemSequential-module__year'})
        if produced_year == None:
            produced_year = item.find('div', attrs={'class': 'ListingItem-module__year'})
        if produced_year == None:
            print('Age does not found')
            return 'Undefinded'
        return now.year - int(produced_year.text)
    def get_location(self, item):
        """
        getting ad's location
        """
        loc = item.find('div', attrs={'class': 'ListingItemSequential-module__place'})
        if loc == None:
            loc = item.find('span', attrs={'class': 'MetroListPlace__regionName'})
        if loc == None:
            print('Location does not found')
            return 'Undefinded'
        return loc.text

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
    def ad_insert(self, df):
        """
        inserts ad to DataFrame
        :param df: pandas DataFrame for appending new ad
        :returns: None
        """
        i = len(df)
        df.loc[i] = [self.title] + [self.cost] + [self.currency]\
         + [self.km] + [self.car_age] + [self.location] + [self.link]


def auto_ru_parce(base_url, df, headers = headers):
    """
    Parser for web site AUTO.ru
    Approximately 3-5 secs for one page parse
    :param base_url: Url from auto.ru to parse (all pages will parser)
    :param headers: param for request - optional
    :returns: df - dataframe with ad data
    also create excel file - Output.xlsx - in current directory with data of df
    """
    session = requests.Session()
    request = session.get(base_url, headers = headers)
    if request.status_code == 200:
        soup = bs(request.content, 'html.parser')
        url = base_url
        request = session.get(url, headers = headers)
        items = soup.find_all("div", attrs = {'class': 'ListingCars-module__listingItem'})
        # items - blocks with one car in each
        for item in items:
            ad = CarAdItem(item)
            ad.show_info()
            ad.ad_insert(df)
            print('')
        next = soup.find('link',attrs={'rel': 'next'})
        if next != None:
            # If there is "NEXT" button => continue parsing to the next page
            time.sleep(2)
            next_url = next['href']
            auto_ru_parce(next_url, df, headers)
        else:
            df.to_excel('Output.xlsx', encoding='utf-8-sig', index=False)
            return df
    else:
        print('Fail')
        return 1

df = pd.DataFrame(columns=['Title', 'Cost', 'Currency', 'Killometrage', 'Age', 'Location', 'link'])
auto_ru_parce(base_url, df, headers)
