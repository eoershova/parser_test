import os, re, json
from selenium import webdriver
from bs4 import BeautifulSoup
os.environ['MOZ_HEADLESS'] = '1'


# получаю ссылку на выдачу и кол-во страниц от пользователя
def link_getter():
    print('Вставьте ссылку на ваш запрос, ее можно скопировать из адресной строки')
    link = input()
    cond = True
    while cond:
        if 'https://yandex.ru/search/' in link:
            cond = False
        else:
            print('неверный формат ссылки, она должна начинаться с https://yandex.ru/search/')
            print('попробуйте еще раз')
            link = input()

    print('Сколько страниц перебрать?')
    pages = input()
    cond = True
    while cond:
        if int(pages) > 0:
            cond = False
            link += '&p='
        else:
            print('Введите положительное число')
            pages = input()

    return link, pages


# перебирает выдачу по страницам
def link_handler(link, pages):
    count = int(pages)
    websites = []
    for i in range(1, count + 1):
        address = link + str(i)
        browser = webdriver.Firefox()
        browser.get(address)
        content = browser.page_source
        html = BeautifulSoup(content, features="html.parser")
        links = link_finder(html)
        for i in links:
            websites.append(i)
    websites = set(websites)
    return websites


# пишет данные в json
def json_writer(websites):
    data = {}
    n = 0
    for website in websites:
        n += 1
        single_web = {}
        address = website
        text = text_finder(website)
        single_web.update({'Ссылка': address, 'Текст': text})
        data.update({n: single_web})
    data_json = json.dumps(data)
    with open('data.json', 'w') as json_file:
        json.dump(data_json, json_file)


# ищет текст на сайте
def text_finder(website):
    address = website
    browser = webdriver.Firefox()
    browser.get(address)
    content = browser.page_source
    html = BeautifulSoup(content, features="html.parser")
    text = html.find_all('p')
    clean_text = ''
    for tag in text:
        tag = str(tag)
        tag = re.sub(r'[^А-ЯЁёа-я\s]', ' ', tag)
        while len(re.findall(r'\s\s', tag)) > 1:
            tag = re.sub(r'\s\s', ' ', tag)
        tag += ' '
        clean_text += tag


# ищет ссылки в выдаче
def link_finder(html):
    classes = html.find_all('a')
    links = []

    linker1 = ['link', 'link_theme_minor', 'sitelinks__link', 'i-bem']
    linker2 = ['link', 'link_theme_outer', 'path__item', 'i-bem']

    # собираю все ссылки
    for i in classes:
        atributes = i.attrs
        if (atributes['class']) == linker1 or (atributes['class']) == linker2:
            links.append(atributes['href'])

    # отделяю служебные сслыки
    good_links = []
    for link in links:
        if 'https:' in link:
            if 'yandex' not in link:
                good_links.append(link)

    # отделяю сслыки на сайт от ссылок на конректную страницу сайта
    sites = []
    for link in good_links:
        site = link.split('/')[2]
        sites.append(site)
    original_links = []
    for link in good_links:
        for site in sites:
            if site in link:
                if len(link) > (len(site) + 9):
                    original_links.append(link)
    original_links = set(original_links)

    return original_links


def main():
    link, pages = link_getter()
    websites = link_handler(link, pages)
    json_writer(websites)
    print('Обработка выдачи займет некоторое время')
    print('результаты будут здесь и в файле data.json')


if __name__ == '__main__':
    main()
