from bs4 import BeautifulSoup
import requests
from csv import writer
import csv
import urllib
import os.path
import json
import datetime

news_links = {}

search_terms = []

def search_term_scraper(dict_of_links, search_terms):
    potential_links = []
    for site,link in dict_of_links.items():
        res = requests.get(link)
        
        parsed_url = urllib.parse.urlparse(link)
        base_url = f'{parsed_url[0]}://{parsed_url[1]}'
        
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            list_of_links = soup.select('a')
            for item in list_of_links:
                if any(term in item.text for term in search_terms):
                    if 'http' in item['href']:
                        potential_links.append({'news agency': site, 'title': item.text.strip().split('\n')[0],'link': item['href']})
                    else:
                        relative_path = item['href']
                        complete_url = f'{base_url}{relative_path}'
                        potential_links.append({'news agency': site, 'title': item.text.strip().split('\n')[0],'link': complete_url})
        else:
            print(f'Error {res.status_code}: {link}')

    return potential_links

def list_to_csvs(scraper_results):
    if not(os.path.isfile('all_results.csv')):
        with open('all_results.csv', 'w', newline = '') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames = ['news agency', 'title', 'link'])
            csv_writer.writeheader()

    oldlinks = []
    oldlinks2 = []
    with open('all_results.csv', 'r', encoding = 'utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            oldlinks.append(row['link'])
            oldlinks2.append(row['link'])

    with open('new_results.csv', 'w', encoding = 'utf-8', newline="") as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames = ['news agency', 'title', 'link'])
        csv_writer.writeheader()
        for result in scraper_results:
            if result['link'] not in oldlinks:
                csv_writer.writerow(result)
                oldlinks.append(result['link'])

    with open('all_results.csv', 'a+', encoding = 'utf-8', newline="") as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames = ['news agency', 'title', 'link'])
        for result in scraper_results:
            if result['link'] not in oldlinks2:
                csv_writer.writerow(result)
                oldlinks2.append(result['link'])

results = search_term_scraper(news_links, search_terms)
list_to_csvs(results)