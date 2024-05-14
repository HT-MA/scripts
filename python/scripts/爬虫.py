import os
import time
import requests
from bs4 import BeautifulSoup
import re
import json
import urllib.request

def get_html(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    return response.text

def get_data(html):
    soup = BeautifulSoup(html, 'lxml')
    data = soup.find_all('div', class_='item')
