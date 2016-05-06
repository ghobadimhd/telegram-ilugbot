import os
import sys
import telegram
from bs4 import BeautifulSoup
import requests as req
from time import sleep
import re
import xml.etree.ElementTree as ET 

def get_mybb_feed(feed_link):
    r = req.get(feed_link)
    if r.ok :
        feed = r.content
        items = ET.fromstring(feed).find('channel').findall('item')
        feeds_str = ""
        for i in items :
            feeds_str += i.find('title').text + "\n"
            feeds_str += i.find('link').text + "\n\n"
    return feeds_str

def get_upcoming():
    """
    TODO Write Doc
    """

    # get ilug page html
    r = req.get(ilugurl)

    if r.ok:
        # get groups' this week session
        r.encoding = 'utf-8'
        source_code = BeautifulSoup(r.text, 'html.parser')
        divs = source_code.find_all('div',class_='col-md-6')
        upcoming = divs[0].text
        # removing extra lines 
        content = []
        count_lines = 0
        for line in upcoming.splitlines():
            if line.strip() :
                if count_lines > 0 :
                    content.append('\n')
                    count_lines =0
                content.append(line)
            else:
                count_lines += 1 
        upcoming = ''.join(content)

        return [upcoming]
    # TODO else


def get_contact_info():
    """
    TODO Write Doc
    """

    # get ilug contact us page 
    r = req.get(open('contact-us.link').readline())

    if r.ok:
        # get groups' this week session
        r.encoding = 'utf-8'
        source_code = BeautifulSoup(r.text, 'html.parser')
        contact_info = source_code.find('p',class_='divalign-left').text

        return [contact_info]
    # TODO else


def get_news():
    """
    TODO Write Doc
    """
    return [get_mybb_feed(open('news-feed.link').readline()) ]
    # TODO else

if __name__ == '__main__':

    # assign bot and ilug url
    global bot, ilugurl
    bot = telegram.Bot(token=open('ilugbot.token').read())
    ilugurl = open('ilug-url.link').readline()

    # Assign Commands
    commands = [
        {
            'match': r'^/upcoming',
            'func': get_upcoming,
        },
        {
            'match': r'^/irc',
            'func': get_contact_info,
        },
        {
            'match': r'^/news',
            'func': get_news,
        }
    ]

    if not os.path.isfile('last-update.id'):  # Check if file dose not exists
        open('last-update.id', 'w').write('0')
    last_update_id_file = open('last-update.id', 'r+')
    last_update_id = int(last_update_id_file.read())

    # listen for command
    while True:
        # get updates
        updates = bot.getUpdates(offset=last_update_id)

        # update offset of last update
        if updates:
            last_update_id_file.seek(0)
            last_update_id = updates[-1].update_id + 1
            last_update_id_file.write(str(last_update_id))
            last_update_id_file.truncate()

        for update in updates:
            print update
            for command in commands:
                if re.search(command['match'], update.message.text):
                    try:
                       for message in command['func']():
                           bot.sendMessage(chat_id=update.message.chat.id, text=message)
                    except :
                        print "Unexpected error:", sys.exc_info()[0]
                    break
        sleep(3)
