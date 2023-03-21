import types
import requests
import datetime
from bs4 import BeautifulSoup


domen = 'https://avs-auto.ru'


def extractor(cell: str, product_class: type):
    cell[5].value = float(cell[5].value.replace(',', '.'))
    if cell[5].value > 50:
        new_price = (cell[5].value * 1.4 // 5 + 1) * 5
    else:
        new_price = (cell[5].value * 1.7 // 5 + 1) * 5

    from_site = parser(cell[1].value, cell[2].value)
    time = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()
    return product_class(Id=cell[0].value,
                         DateBegin=(time if cell[6].value == "В наличии" else ''),
                         DateEnd=(time if cell[6].value != "В наличии" else ''),
                         Title=cell[2].value,
                         Description=from_site['description'],
                         Price=new_price,
                         ImageUrls=from_site['images'],
                         VideoUrl=from_site['video'],
                         OEM = from_site['articul'])


def parser(number: str, name: str):
    link_to_find = f'{domen}/catalog/all/?query={number}'
    response_to_find = requests.get(link_to_find).content
    soup_to_find = BeautifulSoup(response_to_find, 'html.parser')

    link_to_product = f'{domen}{soup_to_find.find("a", {"class": "wrapper"})["href"]}'
    response_to_product = requests.get(link_to_product).content
    soup_to_product = BeautifulSoup(response_to_product, 'html.parser')

    gallery = soup_to_product.find('div', {'class': 'product-main_photo rs-gallery-full'})
    videos = soup_to_product.find('div', {'class': 'youTubeProductVideo'})
    try:
        description = soup_to_product.find('div', {'id': 'property'}).contents
    except AttributeError:
        try:
            description = soup_to_product.find('div',
                                               {'class': 'page-product_description '
                                                         'characteristics left list-unstyled'}).contents
        except AttributeError:
            description = ''
    images_links = ''
    for i, image in zip(range(10), gallery.find_all('a')):
        images_links += f'{domen}{image["href"]} | '
    images_links = images_links[0:len(images_links) - 3]

    video = ''
    if videos != None:
        video = videos.find('iframe')['src']

    f_description = f'<p>Полное название: {name}</p>'\
                    f"<p>Артикул: {number}</p>"
    for string in description:
        f_description += str(string)
    f_description += '<p>__________________________________________________</p> ' \
                     '<p>❤ Добавляйте в ИЗБРАННОЕ, чтобы не потерять объявление из виду!</p> ' \
                     '<p>🔎Смотрите больше товаров в нашем магазине</p> ' \
                     '<p>📌Подписывайтесь, чтобы всегда знать об изменении цен и наличии товара!</p> ' \
                     '<p>💼Мы являемся официальным дилером ТМ RedVerg, Concorde, Квалитет</p> ' \
                     '<p>⚙У нас есть свой сервисный центр.</p> ' \
                     '<p>💰Для оптовиков особые условия.</p> ' \
                     '<p>🤝Работаем с организациями с НДС, без НДС.</p> ' \
                     '<p>📞Звоните или пишите в чат Avito, Whats App, Viber, ' \
                     'мы проконсультируем по всем интересующим вопросам.</p><br />'

    return {'images': images_links,
            'description': f_description,
            'video': video,
            'articul': number}
