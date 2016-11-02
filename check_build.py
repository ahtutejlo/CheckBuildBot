import sqlite3
import threading
import time

import bs4
import requests
import telepot
from telepot.namedtuple import ReplyKeyboardMarkup

from config import *

bot = telepot.Bot(bot_token)


def handle(msg):
    chat_id, command = get_msg_info(msg)
    markup = ReplyKeyboardMarkup(keyboard=[
        ['Check once'],
        ['Start auto informer']
    ])
    markup_stop = ReplyKeyboardMarkup(keyboard=[
        ['Check once'],
        ['Stop auto informer']
    ])

    if command == '/start':
        bot.sendMessage(chat_id, 'Choose option:', reply_markup=markup)
    elif command == "Check once":
        if is_exist(chat_id):
            bot.sendMessage(chat_id, check_build(), reply_markup=markup_stop)
        else:
            bot.sendMessage(chat_id, check_build(), reply_markup=markup)
    elif command == "Start auto informer":
        insert_new_user_if_not_exist(chat_id)
        bot.sendMessage(chat_id, "Ok. I'll notify you on every new build until you send me command /stop",
                        reply_markup=markup_stop)
    elif command in ["Stop auto informer", '/stop']:
        delete_user(chat_id)
        bot.sendMessage(chat_id, "Got you.", reply_markup=markup)


def check_build():
    url = "http://bg-cas-web1.bg.playtech.corp/launcher/"
    try:
        soup = bs4.BeautifulSoup(requests.get(url).text, 'html.parser')
        latest = bs4.BeautifulSoup(str(soup.select('option[value*="skywind"]')[0]), 'html.parser').get_text()
        return 'Current build: {}'.format(latest)
    except:
        logger.error("Can't connect to server.")
        return "Can't connect to server. Try again later."


def repeat_until_new_build():
        build = check_build()
        while True:
            build_new = check_build()
            if build == build_new:
                time.sleep(10)
            elif build_new == "Can't connect to server. Try again later.":
                time.sleep(10)
            else:
                logger.debug('New build: {}'.format(build_new))
                users = get_all_users()
                logger.debug("Qty of users to notify: {}".format(len(users)))
                if len(users) > 0:
                    for user in users:
                        logger.debug('Sending message to user {}'.format(user[0]))
                        bot.sendMessage(user[0], 'There is a new build!\n\n' + build_new)
                build = build_new


def connect_to_db(db_name):
    conn = sqlite3.connect(db_name)
    return conn


def get_all_users():
    conn = connect_to_db(database)
    c = conn.cursor()
    try:
        result = c.execute('SELECT chat_id FROM users').fetchall()
        return result
    finally:
        c.close()
        conn.close()


def create_table():
    conn = connect_to_db(database)
    c = conn.cursor()
    try:
        c.execute('''CREATE TABLE users (chat_id);''')
        conn.commit()
    finally:
        c.close()
        conn.close()


def is_exist(chat_id):
    conn = connect_to_db(database)
    c = conn.cursor()
    try:
        result = c.execute('SELECT chat_id FROM users WHERE chat_id = ?;', (chat_id,)).fetchall()
        logger.debug(result)
        logger.debug(len(result))
        if len(result) == 0:
            return False
        else:
            return True
    finally:
        c.close()
        conn.close()


def insert_new_user_if_not_exist(chat_id):
    conn = connect_to_db(database)
    c = conn.cursor()
    try:
        result = c.execute('SELECT chat_id FROM users WHERE chat_id = ?;', (chat_id,)).fetchall()
        if len(result) == 0:
            logger.debug('Adding user to database...')
            c.execute("INSERT INTO users VALUES (?);", (chat_id,))
            conn.commit()
    finally:
        c.close()
        conn.close()


def delete_user(chat_id):
    conn = connect_to_db(database)
    c = conn.cursor()
    try:
        result = c.execute('SELECT chat_id FROM users WHERE chat_id = ?;', (chat_id,)).fetchall()
        if len(result) != 0:
            c.execute('DELETE FROM users WHERE chat_id = ?;', (chat_id,))
            conn.commit()
    finally:
        c.close()
        conn.close()


def get_msg_info(msg):
    chat_id = msg['chat']['id']
    command = msg['text']
    first_name = msg['chat']['first_name']
    try:
        last_name = ' ' + msg['chat']['last_name']
    except KeyError:
        last_name = ''
    full_name = first_name + last_name
    try:
        username = msg['chat']['username']
    except KeyError:
        username = 'No username'
    logger.debug('New message:\nUser: {}\nNickname: {}\nGot command: {}'.format(full_name, username, command))
    return chat_id, command


logger.debug("Users to notify: {}".format(get_all_users()))
logger.debug(check_build())
th = threading.Thread(target=repeat_until_new_build, args=[], daemon=True)
th.start()
bot.message_loop(handle)

# Keep the program running.
while 1:
    time.sleep(10)
