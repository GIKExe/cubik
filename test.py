import requests, time

def email_finder(nick):
    rawlist, newlist = [], []

    # Делаем запрос на гитхаб, в запрос подставляем ник из входящего сообщения

    url = f'https://api.github.com/users/{nick}/events/public'
    r = requests.get(url)

    # Проверка существования адреса
    # Если пользователь найден - идем дальше по циклу, иначе выходим

    if r.status_code == 200:
        print('status 200 - OK')

        # Если пользователь найден, но возвращается пустой массив, то у юзера нет коммитов
        # Выходим из цикла с сообщением "Невозможно найти почту"

        if not r.json():
            return 'Пользователь найден. Невозможно найти email.'

    elif url_status == 404:
        return 'Юзер с таким ником не найден'
    else:
        return 'Неизвестная ошибка'

    # Поиск и выгрузка коммитов

    for element in r.json():
        if element['type'] == 'PushEvent':
            for commit in element['payload']['commits']:
            
                # Наполняем список всеми почтами из коммитов пользователя
                email = commit['author']['email']
                rawlist.append(email)
    f_list = 'Найдены электронные ящики: \n'

    # Удаляем повторы из списка и форматируем новый список

    for i in rawlist:
        if i not in newlist:
            newlist.append(i)
    for element in newlist:
        f_list = f_list + element + '\n'

    return f_list

print(email_finder('MeexReay'))