import requests
from bs4 import BeautifulSoup as bs
import re
import datetime
now = datetime.datetime.now()

headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9}',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'}

# В дальнейшем будет инпут через Jupyter Notebook
base_url = 'https://auto.ru/cars/bmw/1er/20371753/all/?sort=fresh_relevance_1-desc&output_type=table&km_age_to=100000&km_age_from=50000&page=1'

class CarAdItem:
    """
    Auto RU ad item
    """
    def __init__(self, ad):
        """
        Class contructor
        :param ad: bs4 html container of ad
        """
        self.title = ad.find('a',attrs={'class':'ListingItemTitle-module__link'}).text
        self.cost, self.currency = self.get_cost_info(ad)
        self.km = self.get_km(ad)
        self.car_age = self.get_age(ad)
        self.location = ad.find('div', attrs={'class':'ListingItemSequential-module__place'}).text
        self.link = ad.find('a', attrs={'class':'ListingItemTitle-module__link'})['href']
    def get_cost_info(self, item):
        cost = item.find('div',attrs = {'class':'ListingItemPrice-module__content'}).text
        if re.search('₽', str(cost)) != None:
            currency = 'RUB'
        elif re.search('€', str(cost)) != None:
            currency = 'EUR'
        elif re.search('$', str(cost)) != None:
            currency = 'USD'
        cost = re.sub('[^0-9]','',cost)
        return cost, currency
    def get_km(self, item):
        km = item.find('div', attrs={'class':'ListingItemSequential-module__kmAge'}).text
        return re.sub('[^0-9]','',km)
    def get_age(self, item):
        produced_year = item.find('div', attrs={'class':'ListingItemSequential-module__year'}).text
        return now.year - int(produced_year)
    def show_info(self):
        print('Title:', self.title)
        print('Cost:', self.cost, self.currency)
        print('Killometrage:', self.km)
        print('Age:', self.car_age)
        print('Location:', self.location)
        print('Link:', self.link)

def auto_ru_parce(base_url, headers):
    session = requests.Session()
    request = session.get(base_url,headers = headers)
    if request.status_code == 200:
        soup = bs(request.content, 'html.parser')

        items = soup.find_all("div", attrs = {'class':'ListingCars-module__listingItem'})
        # items - blocks with one car in each
        for item in items:
            ad = CarAdItem(item)
            ad.show_info()
    else:
        print('Fail')

auto_ru_parce(base_url,headers)
