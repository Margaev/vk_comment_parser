import requests
import time
import re
import os
import json

current_time = time.time()


def main():
    group_id = '-67034604'
    app_id = '7557721'
    count = 100
    token = ''
    if os.path.exists('config.json'):
        with open('config.json', 'r') as f:
            data = json.load(f)
            token = data['token']
            token_is_valid = True
            if 'time_period' in data:
                time_period = get_time_period()
            else:
                time_period = set_time_period()
                if token_is_valid:
                    data = {
                        'token': token,
                        'time_period': time_period
                    }
                    json.dump(data, f)
    else:
        token_is_valid = False
        time_period = set_time_period()

    is_parsed = False
    while not is_parsed:
        if token_is_valid and time_period:
            try:
                comments = get_all_comments(group_id, token, count, time_period)
                customers_list = get_customers_list(comments, group_id)
                if customers_list:
                    with open('Покупатели.txt', 'w', encoding="utf-8") as f:
                        for key, value in customers_list.items():
                            if key.find('-') == -1:
                                values = value.split('|')
                                user_name = get_user_name(key, token)
                                f.write(user_name + '\t' + 'https://vk.com/id' + key + '\n')
                                for s in values:
                                    s += '\n'
                                    f.write(s)
                                f.write('\n')
                else:
                    print('Не найдено коментариев за заданный период времени')
                is_parsed = True

                with open('config.json', 'w') as f:
                    data = {
                        'token': token,
                        'time_period': time.time()
                    }
                    json.dump(data, f)
            except KeyError:
                print('Токен не действителен')
                token_is_valid = False
        else:
            url = auth(app_id)
            token = re.search('access_token=(.*)&expires_in', url).group(1)
            with open('config.json', 'w') as f:
                data = {
                    'token': token,
                    'time_period': time_period
                }
                json.dump(data, f)
            token_is_valid = True


def auth(app_id, redirect_uri=r'https://oauth.vk.com/blank.html'):
    requests_params = {
        'client_id': app_id,
        'redirect_uri': redirect_uri,
        'display': 'page',
        'scope': 'photos,offline',
        'response_type': 'token',
        'v': '5.85'
    }
    r = requests.get('https://oauth.vk.com/authorize', params=requests_params)
    print('Скопируйте ссылку и вставьте в адресную строку в браузере: ', r.url)
    url = input('Вствьте ссылку из адресной строки браузера: ')
    return url


def get_customers_list(comments, group_id):
    customers_list = {}
    for comment in comments:
        key = str(comment['from_id'])
        t = comment['text']
        t = t.replace('\n', ' ')
        if customers_list.get(key) is None:
            customers_list[key] = ''

        # value = customers_list.get(key) \
        #     + time.strftime("%d %b %Y %H:%M", time.localtime(int(comment.get('date')))) + '\t' \
        #     + 'https://vk.com/photo' + str(group_id) + '_' + str(comment.get('pid')) \
        #     + '\t' + '[' + t + ']' + '|'

        value = customers_list.get(key) \
            + '[' + t + ']' + '\t' \
            + time.strftime("%d %b %Y %H:%M", time.localtime(int(comment.get('date')))) + '\t' \
            + 'https://vk.com/photo' + str(group_id) + '_' + str(comment.get('pid')) + '|'

        customers_list[key] = value
        if customers_list.get(key) == '':
            customers_list.pop(key, None)
    return customers_list


def get_all_comments(group_id, token, count, time_period):
    offset = 0
    request_params = {
        'owner_id': group_id,
        'offset': offset,
        'count': count,
        'access_token': token,
        'v': '5.85'
    }
    comments = []
    while True:
        r = requests.get('https://api.vk.com/method/photos.getAllComments', params=request_params).json()
        r = r['response']['items']
        r = list(filter(lambda x: x if x['date'] > time_period else None, r))
        comments.extend(r)
        request_params['offset'] += count
        if len(comments) < count:
            break
        time.sleep(0.25)
    return comments


def get_user_name(user_id, token):
    request_params = {
        'user_ids': user_id,
        'access_token': token,
        'v': '5.85'
    }
    r = requests.get('https://api.vk.com/method/users.get', params=request_params).json()
    time.sleep(0.25)
    try:
        name = r['response'][0]['first_name'] + ' ' + r['response'][0]['last_name']
    except KeyError:
        return user_id
    return name


def set_time_period():
    time_period = input('За сколько дней собрать комментарии: ')
    if time_period.isdigit():
        try:
            time_period = time.time() - int(time_period) * 86400
        except ValueError:
            print('Нужно ввести целое число дней')
            return None
        return time_period
    else:
        print('Неверные входные данные')
        return None


def get_time_period():
    with open('config.json', 'r') as f:
        data = json.load(f)
        time_period = data['time_period']
        if not time_period:
            time_period = set_time_period()
        return time_period


def check_comment(t):
    return (('1' in t or '2' in t or '3' in t or '4' in t or '5' in t
            or '6' in t or '7' in t or '8' in t or '9' in t)
            and ('+' in t or 'кат' in t or 'шт' in t))


def check_comment_digit(t):
    return ('1' in t or '2' in t or '3' in t or '4' in t or '5' in t
            or '6' in t or '7' in t or '8' in t or '9' in t)


if __name__ == "__main__":
    main()
