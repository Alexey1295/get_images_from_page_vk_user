import vk_requests
import time
import pandas as pd
import os
from dotenv import load_dotenv
import logging
import logging.config
import yaml
import argparse

from utils import data


load_dotenv('envs/.env')
token_vk = os.environ.get('token')
api = vk_requests.create_api(service_token=token_vk)


LOGGING_CFG_PATH = "cfg/logging.cfg.yaml"   # путь к конфигу с настройками для логирования

def get_logger(logging_cfg_path: str) -> None:
    """
    Функция для загрузки параметров для logging и создания объекта logging.
    """
    logger = logging.getLogger('logger')
    with open(logging_cfg_path) as config_fin:
        logging.config.dictConfig(yaml.safe_load(config_fin.read()))
    return logger


class GetImages:
    """
    Класс для локального сохранения изображений со страницы профиля vk.com
    """
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id

    def save_photos_profile(self):
        """
        Сохранение изображений со страницы профиля
        """
        list_photos_profile = []
        try:
            count_photos_profile = api.photos.get(owner_id=self.user_id,
                                                  album_id='profile')['count']
            for i in range(0, count_photos_profile + 1, 1000):
                photos_profile = api.photos.get(owner_id=self.user_id,
                                                album_id='profile',
                                                photo_sizes=1,
                                                count=1000,
                                                offset=i)
                list_photos_profile.extend(photos_profile['items'])
                time.sleep(0.34)
            data_photos_profile = pd.json_normalize(list_photos_profile)
            data_photos_profile['url_img'] = data_photos_profile.sizes.apply(data.get_url)
            folder_name = 'PHOTOS_PROFILE'
            data.save_img(self.user_id, data_photos_profile, folder_name=folder_name)
            logger.info(f'Данные о фотографиях профиля пользователя id={self.user_id} успешно выгружены!')
        except Exception as e:
            logger.exception(f'Данные о фотографиях профиля пользователя id={self.user_id} не удалось выгрузить!'
                             f' Ошибка: {e}')

    def save_photos_wall_from_posts_of_owner(self):
        """
        Сохранение изображений со стены профиля, опубликованных владельцем страницы
        """
        list_photos_wall = []
        try:
            count_photos_wall = api.photos.get(owner_id=self.user_id,
                                               album_id='wall')['count']
            for i in range(0, count_photos_wall + 1, 1000):
                photos_wall = api.photos.get(owner_id=self.user_id,
                                             album_id='wall',
                                             photo_sizes=1,
                                             count=1000,
                                             offset=i)
                list_photos_wall.extend(photos_wall['items'])
                time.sleep(0.34)
            if list_photos_wall == []:
                logger.info(f'У пользователя {self.user_id} отсутствуют фотографии со стены, опубликованных владельцем'
                      f' страницы')
            else:
                data_photos_wall = pd.json_normalize(list_photos_wall)
                data_photos_wall['url_img'] = data_photos_wall.sizes.apply(data.get_url)
                folder_name = 'PHOTOS_WALL'
                data.save_img(self.user_id, data_photos_wall, folder_name=folder_name)
                logger.info(f'Данные о фотографиях со стены пользователя id={self.user_id}, опубликованных владельцем'
                             f' страницы, успешно выгружены!')
        except Exception as e:
            logging.exception(f'Данные о фотографиях со стены пользователя id={self.user_id}, опубликованных владельцем'
                              f' страницы, не удалось выгрузить! Ошибка: {e}')

    def save_photos_albums(self):
        """
        Сохранение изображений из альбомов профиля
        """
        try:
            albums = api.photos.getAlbums(owner_id=self.user_id)
            time.sleep(0.34)
            data_albums = pd.json_normalize(albums['items'])
            id_albums = list(data_albums['id'])
            list_photos_albums = []
            for album_id in id_albums:
                count_photos_albums = api.photos.get(owner_id=self.user_id,
                                                     album_id=album_id)['count']
                time.sleep(0.34)
                for i in range(0, count_photos_albums + 1, 1000):
                    photos_albums = api.photos.get(owner_id=self.user_id,
                                                   album_id=album_id,
                                                   photo_sizes=1,
                                                   count=1000,
                                                   offset=i)
                    list_photos_albums.extend(photos_albums['items'])
                    time.sleep(0.34)
            if list_photos_albums == []:
                logger.info(f'У пользователя {self.user_id} отсутствуют фотографии из альбомов')
            else:
                data_photos_albums = pd.json_normalize(list_photos_albums)
                data_photos_albums['url_img'] = data_photos_albums.sizes.apply(data.get_url)
                folder_name = 'PHOTOS_ALBUMS'
                data.save_img(self.user_id, data_photos_albums, folder_name=folder_name)
                logger.info(f'Данные о фотографиях из альбомов пользователя id={self.user_id} успешно выгружены!')
        except Exception as e:
            logging.exception(f'Данные о фотографиях из альбомов пользователя id={self.user_id} не удалось выгрузить!'
                              f'Ошикбка: {e}')

    def save_photos_with_user(self):
        """
        Сохранение изображений, на которых был отмечен пользователь заданного профиля
        """
        list_photos_with_user = []
        try:
            count_photos_with_user = api.photos.getUserPhotos(user_id=self.user_id)['count']
            for i in range(0, count_photos_with_user + 1, 1000):
                photos_with_user = api.photos.getUserPhotos(user_id=self.user_id,
                                                            extend=1,
                                                            count=1000,
                                                            offset=i)
                list_photos_with_user.extend(photos_with_user['items'])
                time.sleep(0.34)
            if list_photos_with_user == []:
                logger.info(f'У пользователя {self.user_id} отсутствуют фотографии из альбомов')
            else:
                data_photos_with_user = pd.json_normalize(list_photos_with_user)
                data_photos_with_user['url_img'] = data_photos_with_user.sizes.apply(data.get_url)
                folder_name = 'PHOTOS_WITH_USER'
                data.save_img(self.user_id, data_photos_with_user, folder_name=folder_name)
                logger.info(f'Данные о фотографиях, на которых отмечен пользователь id={self.user_id} успешно '
                             f'выгружены!')
        except Exception as e:
            logging.exception(f'Данные о фотографиях, на которых отмечен пользователь id={self.user_id}, не удалось'
                              f' выгрузить! Ошибка: {e}')


    def __call__(self) -> None:
        """
        Вызывать методы сохранения изображений со страницы пользователя в зависимости от настроек
        """
        self.save_photos_profile()
        self.save_photos_wall_from_posts_of_owner()
        self.save_photos_albums()
        self.save_photos_with_user()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--user_id', required=True)
    args = parser.parse_args()

    get_images = GetImages(user_id=args.user_id,)
    get_images()


if __name__ == "__main__":
    logger = get_logger(logging_cfg_path=LOGGING_CFG_PATH)
    main()