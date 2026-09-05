import os
import re
import json
import time
import logging
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def compile_regex_patterns(config):
    """Предкомпіляція регулярних виразів для прискорення обробки тексту."""
    delete_words = config.get('delete_key_words', [])
    delete_pattern = re.compile("|".join(map(re.escape, delete_words)), re.IGNORECASE) if delete_words else None

    url_pattern = re.compile(r"https?://\S+|www\.\S+")

    tts_replacements = [
        (re.compile(r"(\d+)\s?хв(\s|\.)?", re.I), r"'\1' хвилин "),
        (re.compile(r"\+/-"), "плюс мінус"),
        (re.compile(r"невст\.", re.I), "невстановлені"),
        (re.compile(r"обл:", re.I), "область"),
        (re.compile(r"вдсх", re.I), "водосховище"),
        (re.compile(r"БПЛА", re.I), "БПЛ-А"),
        (re.compile(r"Чорнобильській ЗВ", re.I), "Чорнобильській зоні"),
        (re.compile(r"Чорнобильську ЗВ", re.I), "Чорнобильську зону"),
        (re.compile(r"1\sракет", re.I), "одна ракет"),
        (re.compile(r"2\sракет", re.I), "дві ракет"),
        (re.compile(r"1х\sракет", re.I), "одна ракет"),
        (re.compile(r"2х\sракет", re.I), "дві ракет"),
        (re.compile(r"1х\sавіаційн", re.I), "одна авіаційн"),
        (re.compile(r"2х\sавіаційн", re.I), "дві авіаційн"),
        (re.compile(r"1\sгрупа", re.I), "одна група"),
        (re.compile(r"2\sгрупи", re.I), "дві групи"),
        (re.compile(r"(\d+)[xх]", re.I), r"'\1'"),
        (re.compile(r"(\d+)\sгруп", re.I), r"'\1' груп"),
        (re.compile(r"1\s?шт\.?\s?", re.I), "одна штука "),
        (re.compile(r"2\s?шт\.?\s?", re.I), "дві штуки "),
        (re.compile(r"3\s?шт\.?\s?", re.I), "три штуки "),
        (re.compile(r"4\s?шт\.?\s?", re.I), "чотири штуки "),
        (re.compile(r"(\d+)\s?шт\.?\s?", re.I), r"'\1' штук "),
        (re.compile(r"(\d+)\s"), r"'\1' "),
        (re.compile(r"(\d+)-"), r"'\1'-"),
    ]

    return delete_pattern, url_pattern, tts_replacements


def clean_text_for_tts(text, delete_pattern, url_pattern, tts_replacements):
    """Очищення та підготовка тексту для приємного звукового відтворення."""
    text = url_pattern.sub("", text)
    
    if delete_pattern:
        text = delete_pattern.sub("", text)

    for pattern, replacement in tts_replacements:
        text = pattern.sub(replacement, text)

    return text.strip()


def process_channel(session, channel, config, patterns, skip_sending=False):
    delete_pattern, url_pattern, tts_replacements = patterns
    
    file_path = f'/share/alertsmonitor/{channel}.txt'
    last_message_id = 0
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                content = f.read().strip()
                if content.isdigit():
                    last_message_id = int(content)
        except Exception as e:
            logging.error(f"Error reading state for {channel}: {e}")

    url = f'https://telegram.me/s/{channel}'
    if last_message_id > 0:
        url += f'?after={last_message_id}'

    try:
        response = session.get(url, headers={"X-Requested-With": "XMLHttpRequest"}, timeout=(5, 10))
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error fetching {channel}: {e}")
        return 0

    try:
        html_content = response.json()
    except (json.JSONDecodeError, ValueError):
        html_content = response.text

    soup = BeautifulSoup(html_content, 'html.parser')
    posts = soup.find_all('div', class_='tgme_widget_message')

    posted_count = 0
    max_id_in_batch = last_message_id
    dt_utcnow = datetime.now(timezone.utc)
    max_age_seconds = config.get('max_message_age_seconds', 60)

    for post in posts:
        date_link = post.find('a', class_='tgme_widget_message_date')
        text_div = post.find('div', class_='tgme_widget_message_text')

        if not date_link or not text_div:
            continue

        try:
            msg_id = int(date_link['href'].split('/')[-1])
        except (ValueError, KeyError, IndexError):
            continue

        # Фіксуємо максимальний ID у пачці незалежно від того, чи будемо відправляти
        if msg_id > max_id_in_batch:
            max_id_in_batch = msg_id

        if msg_id <= last_message_id:
            continue

        # Якщо ліміт перевищено — пропускаємо аналіз та відправку тексту
        if skip_sending:
            continue

        # Перевірка віку
        try:
            time_str = date_link.find('time')['datetime']
            dt_message = datetime.fromisoformat(time_str)
            age_seconds = (dt_utcnow - dt_message).total_seconds()
        except Exception:
            age_seconds = 0

        if max_age_seconds > 0 and age_seconds > max_age_seconds:
            continue

        # Очищення та підготовка тексту
        for emoji in text_div.find_all(['i', 'tg-emoji'], class_='emoji'):
            emoji.decompose()

        raw_text = text_div.get_text(separator=' ').strip()

        if len(raw_text) > config.get('max_message_length', 400):
            continue

        if any(skip.lower() in raw_text.lower() for skip in config.get('skip_key_words', [])):
            continue

        debug_mode = config.get('debug', False)
        if debug_mode:
            raw_text = "Тестове повідомлення"

        processed_text = clean_text_for_tts(raw_text, delete_pattern, url_pattern, tts_replacements)
        if not processed_text:
            continue

        is_critical = any(crit.lower() in processed_text.lower() for crit in config.get('critical_key_words', []))

        # Відправка в HA
        supervisor_token = os.environ.get('SUPERVISOR_TOKEN', '')
        #ha_url = "http://supervisor/core/api/states/sensor.radar_status"
        ha_url = "http://supervisor/core/api/events/ua_alerts_monitor_new_message"
        headers = {
            "Authorization": f"Bearer {supervisor_token}",
            "Content-Type": "application/json; charset=UTF-8"
        }
        #payload = {
        #    "state": str(msg_id),
        #    "attributes": {
        #        "message": processed_text,
        #        "critical": "true" if is_critical else "false",
        #        "friendly_name": "Радар повідомлення",
        #        "icon": "mdi:radar"
        #    }
        #}
        payload = {
            "message": processed_text,
            "critical": "true" if is_critical else "false",
            "msg_id": str(msg_id)
        }
        
        try:
            res = session.post(ha_url, headers=headers, json=payload, timeout=5)
            res.raise_for_status()
            posted_count += 1
            #print(f"[{channel}:{msg_id}] (Age: {int(age_seconds)}s) {processed_text}")
            log_fn = logging.warning if is_critical else logging.info
            log_fn(f"[{channel}:{msg_id}] (Age: {int(age_seconds)}s) {processed_text}")
            time.sleep(1)
        except requests.RequestException as e:
            logging.error(f"Failed to update HA state: {e}")

    # Файл стану оновлюється ЗАВЖДИ (навіть якщо skip_sending=True)
    if max_id_in_batch > last_message_id:
        try:
            with open(file_path, 'w') as f:
                f.write(str(max_id_in_batch))
        except Exception as e:
            logging.error(f"Failed to save state for {channel}: {e}")

    return posted_count


def main():
    session = requests.Session()
    logging.info("Starting UA Alerts Monitor service...")
    logging.info("Output flow to events...")

    try:
        with open('/data/options.json', 'r') as f:
            config = json.load(f)
    except Exception as e:
        logging.error(f"Failed to read configuration: {e}")
        return

    raw_channels = config.get('channels', [])
    sync_interval = config.get('sync_interval', 5)

    if not raw_channels:
        logging.error("No Telegram channels defined in configuration. Stopping service.")
        return

    # Примусово переміщуємо war_monitor у кінець списку
    channels = sorted(raw_channels, key=lambda x: x == 'war_monitor')
    patterns = compile_regex_patterns(config)

    while True:
        try:
            total_posted = 0

            for channel in channels:
                # Перевірка: якщо це war_monitor і з попередніх каналів вже є >= 2 повідомлень
                should_skip = (channel == 'war_monitor' and total_posted >= 2)

                if should_skip:
                    logging.info(f"Limit reached ({total_posted} msgs). Updating ID for {channel} without sending alerts.")

                count = process_channel(session, channel, config, patterns, skip_sending=should_skip)
                total_posted += count

            if total_posted > 0:
                logging.info(f"Cycle completed. Total messages sent: {total_posted}.")

        except Exception as e:
            logging.error(f"Unexpected error in main loop: {e}")

        time.sleep(sync_interval)

if __name__ == '__main__':
    main()
