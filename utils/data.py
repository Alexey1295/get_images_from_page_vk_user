import requests
import os
import pandas as pd
import uuid


def get_url(list_js: dict) -> str:
    """
    Получение из json-файла данных об изображении из vk.com, полученного через методы api.vk, url изображения с наибольшими размерами изображения
    """
    h_max = list_js[0]['height']
    j = 0
    for i in range(len(list_js) - 1):
        if list_js[i + 1]['height'] > h_max:
            h_max = list_js[i + 1]['height']
            j = i + 1
    return list_js[j]['url']

def save_img(user_id: int, df: pd.DataFrame, folder_name: str) -> None:
    """
    Сохранение изображения со страницы пользовательской страницы vk.com локально по url из датафрейма
    """
    list_img_url = list(df['url_img'])
    try:
        os.mkdir('results')
    except Exception:
        pass
    try:
        os.mkdir(f'results/Images_user_id{user_id}')
    except Exception:
        pass
    try:
        os.mkdir(os.path.join(f'results/Images_user_id{user_id}', f'{folder_name}_user_id{user_id}'))
    except Exception as e:
        pass
    for url_img in list_img_url:
        img_data = requests.get(url_img).content
        name_img_file = str(uuid.uuid4()) + '.jpg'  # с помощью библиотеки uuid задаем имя файла
        with open(os.path.join(f'results/Images_user_id{user_id}', f'{folder_name}_user_id{user_id}', f'{name_img_file}'), 'wb') as handler:
            handler.write(img_data)