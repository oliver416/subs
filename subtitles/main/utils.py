import requests
from bs4 import BeautifulSoup
from django.conf import settings


def translate_online(word):
    # TODO[upgrade]: create cache table
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                  'q=0.8,application/signed-exchange;v=b3',
        'Accept-Language': 'en-US,en;q=0.9',
        'Host': settings.DICTIONARY_HOST,
        'User-Agent': 'Opera/9.80 (Windows NT 6.1; WOW64) Presto/2.12.388 Version/12.18'}
    response = requests.get(settings.DICTIONARY_URL + word, headers=headers)
    if response.status_code == 200:
        response.encoding = 'utf8'
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        result = soup.find_all('div', class_='pr entry-body') + soup.find_all('div', class_='lmb-20')
        if result is None:
            result = """<h2>This word isn't in the dictionary</h2>"""
        else:
            result = result[0]
    else:
        result = """<h2>Bad response has received</h2>"""
    return result
