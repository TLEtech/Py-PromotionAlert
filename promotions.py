import os
from pathlib import Path
import requests
from bs4 import BeautifulSoup as bs4
import logbook
import mailmessage
import json

# Logging settings
log_name = 'history.log'
log_path = os.getcwd() + os.sep + log_name
log_handler = logbook.FileHandler(log_path)
log_handler.push_application()

# R/W to this file
f_name = 'promotions.json'
f_path = os.getcwd() + os.sep + f_name

url_base = 'https://website.com'
url_page = '{url_base}/default.asp'.format(url_base=url_base)


def get_promotions():
    # function to send request, parse html, read promotions into json format
    r = requests.get(url_base)
    soup = bs4(r.content, 'html.parser')
    elm_promos = soup.find('div', {'class': 'prod_1'})
    if elm_promos:
        curr_promos = {}
        curr_promos['promotions'] = []
        for i in elm_promos.findChildren('a'):
            promo_title = i.text.strip('"')
            promo_link = i.get('href')
            promo_addr = '{url_base}/{url_promo}'.format(url_base=url_base,url_promo=promo_link)
            curr_promos['promotions'].append({
                'title': promo_title,
                'link': promo_addr
                })
        return curr_promos



def read_promotions(curr_promos, file):
    # read json from file, compare against current promotions 
    fieldnames = ['title', 'link']
    with open(file, 'r', newline='') as f:
        f_promos = json.load(f)
        if f_promos == curr_promos:
            return 0
        else:
            return 1


def write_promotions(promotions, file):
    # write to file. json makes it so easy. never do csv ever again
    with open(file, 'w', newline='') as f:
        json.dump(promotions, f)


def compose_message(json):
    # sort of  a roundabout way to compose a mailmessage, but I have little experience with automation of mail.
    # this seemed like the easiest way to do it - make a list, iterate over the dictionary, join the list.
    message = []
    message.append('Promotions have been updated.\n\n')
    for k in json['promotions']:
        text = 'Title: {0}\nURL: {1}\n'.format(k['title'], k['link'])
        message.append(text)
    message = ''.join(message)
    return message


if __name__=='__main__':
    # log everything
    l = logbook.Logger()
    # check if it's first run
    if not os.path.isfile(f_path):
        initial = 1
    else:
        initial = 0
    # get current promotions
    curr_promos = get_promotions()
    if initial:
        l.info('Initial run.')
        l.info('Writing initial promos to file.')
        write_promotions(curr_promos, f_path)
        l.info('Sending mail message.')
        message = compose_message(curr_promos)
        mailmessage.send_promotions(message)
    else:
        updated = read_promotions(curr_promos, f_path)
        if not updated:
            l.info('No changes.')
        if updated:
            l.info('New promotions.')
            write_promotions(curr_promos, f_path)
            l.info('Sending mail message.')
            message = compose_message(curr_promos)
            mailmessage.send_promotions(message)
