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
    max_age_seconds = config.get('max_message_age_seconds', 300)

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

        processed_text = clean_text_for_tts(raw_text, delete_pattern, url_pattern, tts_replacements)
        if not processed_text:
            continue

        is_critical = any(crit.lower() in processed_text.lower() for crit in config.get('critical_key_words', []))

        # Відправка в HA
        supervisor_token = os.environ.get('SUPERVISOR_TOKEN', '')
        ha_url = "http://supervisor/core/api/states/sensor.radar_status"
        #ha_url = "http://supervisor/core/api/events/ua_alerts_monitor_new_message"
        headers = {
            "Authorization": f"Bearer {supervisor_token}",
            "Content-Type": "application/json; charset=UTF-8"
        }
        payload = {
            "state": str(msg_id),
            "attributes": {
                "message": processed_text,
                "critical": "true" if is_critical else "false",
                "friendly_name": "Радар повідомлення",
                "icon": "mdi:radar"
            }
        }

        #payload = {
        #    "message": processed_text,
        #    "critical": is_critical,
        #    "channel": channel,
        #    "msg_id": key
        #}
        
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
