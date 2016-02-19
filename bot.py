import os
import telegram
from bs4 import BeautifulSoup
import requests as req
from time import sleep
import re


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
    r = req.get('http://www.isfahanlug.org/doku.php?id=%D8%AA%D9%85%D8%A7%D8%B3_%D8%A8%D8%A7_%D9%85%D8%A7')

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

    # get ilug page html
    news_url = 'http://lists.isfahanlug.org/pipermail/news/'
    r = req.get(news_url)

    if r.ok:
        # get groups' this week session
        r.encoding = 'utf-8'
        source_code = BeautifulSoup(r.text, 'html.parser')

        # Find last month in the table (sorted in date)
        last_month_url = news_url + source_code.find_all('a', href=re.compile(r'^.*/date.html'))[0]['href']

        r = req.get(last_month_url)

        if r.ok:
            # get groups' this week session
            r.encoding = 'utf-8'
            source_code = BeautifulSoup(r.text, 'html.parser')
            ul = source_code.find_all('ul')[1]
            ul = re.sub(r'</i>\n(</li>)*</ul>', r'</i></ul>', ul.encode())
            ul = ul.replace('<li>', '</li><li>')
            ul = ul.replace('<ul>\n</li>', '<ul>')

            source_code = BeautifulSoup(ul, 'html.parser')
            last_ten_news = source_code.find_all('li')[-10:]
            last_ten_news.reverse()

            result = []
            for news in last_ten_news:
                result.append((news.get_text() + '\n\n' + last_month_url.replace('date.html', '') + news.find('a')['href'] + '\n\n')
                              .encode('utf-8'))

            return result
    # TODO else

if __name__ == '__main__':

    # assign bot and ilug url
    global bot, ilugurl
    bot = telegram.Bot(token=open('ilugbot.token').read())
    ilugurl = 'http://drupal.isfahanlug.org/'

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
                    for message in command['func']():
                        bot.sendMessage(chat_id=update.message.chat.id, text=message)
                    break
            sleep(3)
