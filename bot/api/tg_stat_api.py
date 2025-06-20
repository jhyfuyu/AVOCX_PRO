import requests
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

API_KEY = '98402c53500c2c0e7f0d3a659f1c6d2b'
BASE_URL = 'https://api.tgstat.ru'

current_date = str(datetime.now())[:10]

def get_channel_stats(channel_name):
    today = datetime.now()
    yesterday = str(today - timedelta(days=1))[:10]
    a_week_ago = str(today - timedelta(weeks=1))[:10]
    a_month_ago = str(today - relativedelta(months=1))[:10]
    today = str(today)[:10]
    print(a_month_ago)

    # Получаем статистику канала
    response_stat = requests.get(f'https://api.tgstat.ru/channels/stat?token={API_KEY}&channelId={channel_name}')
    sub_today = requests.get(f'https://api.tgstat.ru/channels/subscribers?token={API_KEY}&channelId={channel_name}&startDate={today}&endDate={today}')
    sub_month = requests.get(f'https://api.tgstat.ru/channels/subscribers?token={API_KEY}&channelId={channel_name}&startDate={a_month_ago}&endDate={a_month_ago}')
    forwards = requests.get(f'https://api.tgstat.ru/channels/forwards?token={API_KEY}&channelId={channel_name}&startTime={today}&endTime={a_month_ago}')
    posts = requests.get(f'https://api.tgstat.ru/channels/posts?token={API_KEY}&channelId={channel_name}')

    if response_stat.status_code != 200:
        print(f"Ошибка: {response_stat.json()}")
        return

    data = response_stat.json()['response']
    forwards_quality = len(forwards.json()['response'])
    
    # Извлекаем необходимые данные
    channel_info = {
        'название канала': data['title'],
        '🔷 существует': data.get('exists'),
        '🔷 ПДП': data['participants_count'],
        '  ER 24ч': data["err24_percent"],
        '🔷 Охват': data["er_percent"],
        '   24 часа': data["adv_post_reach_24h"],
        '   48 часов': data["adv_post_reach_48h"],
        '🔷 число пересылок за месяц': forwards_quality,
        '🔷 упоминания в телеграме': data["mentions_count"],
        '🔷 постов за месяц': posts.json()['response']['total_count']
    }
    
    # Выводим информацию
    return channel_info
