import os
import re
import json
import time
import socket
import logging
import requests
import configparser
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup
from retrying import retry

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def retry_if_request_exception(exception):
    """Return True if we should retry (in this case when it's an RequestException), False otherwise"""
    return isinstance(exception, requests.RequestException)

@retry(stop_max_attempt_number=2, wait_fixed=4000, retry_on_exception=retry_if_request_exception)
def fetch_data(url):
    headers = {"X-Requested-With": "XMLHttpRequest"}
    response = requests.get(url, headers=headers, timeout=(4, 10))
    response.raise_for_status()
    return response

def parse_data(content, channel, message_id, max_message_length, skip_key_words, delete_key_words, critical_key_words):
    data = content.replace('\\','')
    data = BeautifulSoup(data[1:-1].replace('&nbsp;', ' ').replace('<br/>', ' ').replace('  ', ' '), features='html.parser')

    messages = []
    for message_text in data.find_all('div', class_ = 'tgme_widget_message_text js-message_text'):
        soup = BeautifulSoup(str(message_text), 'html.parser')
        for emoji in soup.find_all('i', class_ = 'emoji'): 
            emoji.decompose()

        for emoji in soup.find_all('tg-emoji'): 
            emoji.decompose()

        messages.append(soup.get_text())

    message_ids = []
    message_ages = []
    dt_utcnow = datetime.now(timezone.utc)

    for link in data.find_all('a', class_ = 'tgme_widget_message_date'):
        href = BeautifulSoup(str(link), 'html.parser', multi_valued_attributes=None)
        dt_message = (datetime.strptime(href.time['datetime'], '%Y-%m-%dT%H:%M:%S%z'))
        delta = dt_utcnow - dt_message
        message_ages.append(delta.seconds)
        message_ids.append(href.a['href'].split('/')[-1])

    channel_texts = {}
    for key in message_ids:
        for value in messages:
            channel_texts[key] = value.strip()
            messages.remove(value)
            break

    return post_data(channel_texts, message_ids, message_ages, channel, message_id, max_message_length, skip_key_words, delete_key_words, critical_key_words)

def post_data(channel_texts, message_ids, message_ages, channel, message_id, max_message_length, skip_key_words, delete_key_words, critical_key_words):
    counter = 0

    if len(message_ids) > 0:
        with open(f'/share/alertsmonitor/{channel}.txt', 'w') as f:
            f.write(max(message_ids))
        
        for i, key in enumerate(channel_texts):
            if int(key) > int(message_id) and int(message_ages[i]) <= 60 and len(channel_texts[key]) <= int(max_message_length):
                output = [i for i in skip_key_words if(i.lower() in channel_texts[key].lower())]
                if bool(output) is False:
                    channel_texts[key] = re.sub(r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})", r"", channel_texts[key])
                    channel_texts[key] = re.sub(delete_key_words, r"", channel_texts[key])

                    channel_texts[key] = re.sub(r"невст.", r"невстановлені", channel_texts[key])
                    channel_texts[key] = re.sub(r"обл:", r"область", channel_texts[key])
                    channel_texts[key] = re.sub(r"вдсх", r"водосховище", channel_texts[key])
                    channel_texts[key] = re.sub(r"БПЛА", r"БПЛ-А", channel_texts[key], flags=re.I)
                    channel_texts[key] = re.sub(r"Чорнобильській ЗВ", r"Чорнобильській зоні", channel_texts[key], flags=re.I)
                    channel_texts[key] = re.sub(r"Чорнобильську ЗВ", r"Чорнобильську зону", channel_texts[key], flags=re.I)

                    channel_texts[key] = re.sub(r"1\sракет", r"одна ракет", channel_texts[key])
                    channel_texts[key] = re.sub(r"2\sракет", r"дві ракет", channel_texts[key])
                    channel_texts[key] = re.sub(r"1х\sракет", r"одна ракет", channel_texts[key])
                    channel_texts[key] = re.sub(r"2х\sракет", r"дві ракет", channel_texts[key])
                    channel_texts[key] = re.sub(r"1х\sавіаційн", r"одна авіаційн", channel_texts[key])
                    channel_texts[key] = re.sub(r"2х\sавіаційн", r"дві авіаційн", channel_texts[key])
                    channel_texts[key] = re.sub(r"1\sгрупа", r"одна група", channel_texts[key])
                    channel_texts[key] = re.sub(r"2\sгрупи", r"дві групи", channel_texts[key])
                    channel_texts[key] = re.sub(r"(\d+)x", r"'\1'", channel_texts[key])
                    channel_texts[key] = re.sub(r"(\d+)х", r"'\1'", channel_texts[key])
                    channel_texts[key] = re.sub(r"(\d+)\s", r"'\1' ", channel_texts[key])
                    channel_texts[key] = re.sub(r"(\d+)-", r"'\1'-", channel_texts[key])
                    channel_texts[key] = re.sub(r"(\d+)\sгруп", r"'\1' груп", channel_texts[key])

                    channel_texts[key] = re.sub(r"1\s?шт.?\s?", r"одна штука ", channel_texts[key])
                    channel_texts[key] = re.sub(r"2\s?шт.?\s?", r"дві штуки ", channel_texts[key])
                    channel_texts[key] = re.sub(r"3\s?шт.?\s?", r"три штуки ", channel_texts[key])
                    channel_texts[key] = re.sub(r"4\s?шт.?\s?", r"чотири штуки ", channel_texts[key])
                    channel_texts[key] = re.sub(r"(\d+)\s?шт.?\s?", r"'\1' штук ", channel_texts[key])

                    channel_texts[key] = re.sub(r"(\d+)\s?хв.?\s?", r"'\1' хвилин ", channel_texts[key])

                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    result = sock.connect_ex(('supervisor',80))
                    sock.close()

                    if result == 0:
                        critical = "true" if bool([i for i in critical_key_words if(i.lower() in channel_texts[key].lower())]) else "false"
                        logging.info("Updating Home Assistant sensor data")
                        TOKEN = "Bearer {}".format(os.environ['SUPERVISOR_TOKEN'])                           
                        url = "http://supervisor/core/api/states/sensor.radar_status"
                        headers = {"Authorization": TOKEN, "Content-Type": "application/json; charset=UTF-8"}
                        data = {"state": key, "attributes": {"message": channel_texts[key], "critical": critical, "friendly_name": "Радар повідомлення", "icon": "mdi:radar"}}
                        r = requests.post(url, headers=headers, json=data)
                        logging.info(f"{key} - {message_ages[i]} - {channel_texts[key]}")
                        counter += 1
                        time.sleep(5)

    return counter


def main():
    with open('/var/run/monitor.pid', 'w') as p:
        p.write(str(os.getpid()))
        p.close()
    
    with open('/data/options.json', 'r') as f:
        config = json.load(f)
        f.close()
    
    if len(config['channels']) > 0:

        msg_posted = 0

        for channel in config['channels']:
            message_id = 0
            url = f'https://t.me/s/{channel}'

            if os.path.exists(f'/share/alertsmonitor/{channel}.txt'):
                f = open(f'/share/alertsmonitor/{channel}.txt', 'r')
                message_id = f.read()
                f.close()

            if int(message_id) > 0:
                url = f'{url}?after={message_id}'

            try:
                response = fetch_data(url)
                msg_posted += parse_data(response.text, channel, message_id, config['max_message_length'], config['skip_key_words'], r"{}".format("|".join(config['delete_key_words'])), config['critical_key_words'])
            
                if channel == 'war_monitor' and msg_posted >= 2:
                    break

            except requests.HTTPError as e:
                logging.error(f'HTTP error occurred: {e}')
            except requests.RequestException as e:
                logging.error(f'Request exception occurred: {e}')
            except Exception as e:
                logging.error(f'An unexpected error occurred: {e}')
        
        if msg_posted > 0:
            logging.info(f"Sent {msg_posted} message(s)")

    else:
        logging.error(f'Telegram channels not defined')

    os.remove('/var/run/monitor.pid')


if __name__ == '__main__':
    main()
