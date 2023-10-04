import requests
import json
import time
from colorama import Fore, Style
from urllib.parse import urlencode
from tqdm import tqdm


class VKClient:
    APP_ID = '51755696'
    API_BASE_URL = 'https://api.vk.com/method'
    OAUTH_BASE_URL = 'https://oauth.vk.com/authorize'
    photo_urls = []

    def __init__(self):
        self.vk_token = None
        self.vk_id = None

    def get_token(self):
        params = {
            'client_id': self.APP_ID,
            'redirect_uri': 'https://oauth.vk.com/blank.html',
            'display': 'page',
            'scope': 'photos',
            'response_type': 'token'
        }
        outh_link = f'{self.OAUTH_BASE_URL}?{urlencode(params)}'
        print(f'1. Перейдите по ссылке: {outh_link}')
        print('2. Подтвердите, что хотите передавать ваши данные приложению.')
        print('3. Скопируйте адрес открывшейся страницы из адресной строки браузера.')
        token_address = input('4. Вставьте скопированный адрес сюда и нажмите Enter: ')
        self.vk_token = token_address[
                   token_address.index('=') + 1:token_address.index('&')
                        ]
        return self.vk_token

    def ask_vk_id(self):
        self.vk_id = input('5. Укажите ID профиля, из которого брать фото: ')
        return self.vk_id

    def get_common_params(self):
        return {
            'access_token': self.vk_token,
            'v': '5.131'
        }

    def get_photos(self):
        print(f'{Fore.BLUE}\nСтартуем', end='')
        for i in range(5):
            time.sleep(0.5)
            print('.', end='')
        print(f'{Style.RESET_ALL}\n\nПолучаем фотографии из VK:')
        photos = []
        same_names = []
        params = self.get_common_params()
        params.update(
            {
                'owner_id': self.vk_id,
                'album_id': 'profile',
                'extended': '1'
            }
        )
        response = requests.get(f'{self.API_BASE_URL}/photos.get', params=params)
        items = response.json()['response']['items']

        for item in tqdm(items):
            name = item['likes']['count']
            if name not in same_names:
                same_names.append(name)
            else:
                name = f'{name}_{item["date"]}'
            photo = {
                'file_name': f'{name}.jpg',
                'size': item['sizes'][-1]['type']
            }
            photos.append(photo)
            self.photo_urls.append(item['sizes'][-1]['url'])
            time.sleep(.05)
        with open('photos.json', 'w') as file:
            json.dump(photos, file, indent=2)
        print(f'{Fore.BLUE}Готово!{Style.RESET_ALL}')


class YADisk:
    BASE_URL = 'https://cloud-api.yandex.net'
    CREATING_FOLDER_URL = f'{BASE_URL}/v1/disk/resources'
    UPLOADING_URL = f'{CREATING_FOLDER_URL}/upload'

    def __init__(self):
        self.ya_token = None

    def ask_ya_token(self):
        self.ya_token = input('6. Введите ваш Я.Токен: ')
        return self.ya_token

    def upload_photos(self, upload_folder='VK Backup'):
        print('\nЗагружаем фотографии на Я.Диск:')
        headers = {
            'Authorization': self.ya_token
        }
        folder_params = {
            'path': upload_folder
        }
        requests.put(
            self.CREATING_FOLDER_URL, headers=headers, params=folder_params
        )
        with open('photos.json') as file:
            photos = json.load(file)

        for i in range(len(photos)):
            photos[i]['url'] = VKClient.photo_urls[i]

        for photo in tqdm(photos):
            upload_params = {
                'path': f'{upload_folder}/{photo["file_name"]}',
                'url': photo['url']
            }
            requests.post(
                self.UPLOADING_URL, headers=headers, params=upload_params
            )
            time.sleep(.05)
        print(f'{Fore.BLUE}Готово!{Style.RESET_ALL}')
        print(f'{Fore.LIGHTGREEN_EX}\nФотографии успешно загружены '
              f'на Я.Диск в папку {upload_folder}{Style.RESET_ALL}')


print('VK BACKUP\n')
vk = VKClient()
ya = YADisk()
vk.get_token()
vk.ask_vk_id()
ya.ask_ya_token()
vk.get_photos()
ya.upload_photos()
