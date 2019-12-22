import requests
from bs4 import BeautifulSoup as bs
import re

headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9}',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'}

# В дальнейшем будет инпут через Jupyter Notebook
base_url = 'https://auto.ru/cars/bmw/1er/20371753/all/?sort=fresh_relevance_1-desc&km_age_to=100000&km_age_from=50000&page=1'

class AdCarItem:
    def __init__(self, title, cost, currency, killometrage, car_age, location, link='-'):
        self.title = title
        self.cost = cost
        self.curreny = currency
        self.killometrage = killometrage
        self.car_age = car_age
        self.location = location
        if link != '-':
            self.link = link

def auto_ru_parce(base_url, headers):
    session = requests.Session()
    request = session.get(base_url,headers = headers)
    if request.status_code == 200:
        soup = bs(request.content, 'html.parser')

        # f = open('output.txt','w')
        # f.write(str(str(soup).encode("utf-8")))
        # f.close()

        items = soup.find_all("div", attrs = {'class':'ListingCars-module__listingItem'})
        # items - blocks with one car in each
        for item in items:
            # TITLE
            title = item.find('a',attrs={'class':'ListingItemTitle-module__link'}).text
            # COST + curreny
            cost = item.find('div',attrs = {'class':'ListingItemPrice-module__content'}).text
            if re.search('₽', str(cost)) != None:
                currency = 'RUB'
            elif re.search('€', str(cost)) != None:
                currency = 'EUR'
            elif re.search('$', str(cost)) != None:
                currency = 'USD'
            cost = re.sub('[^0-9]','',cost)
            print(title,cost,currency)
            # KM
            # YEAR
            # CAR_AGE
            # LOCATION
            # LINK
    else:
        print('Fail')

auto_ru_parce(base_url,headers)
