import requests
import json
import time
from tqdm import tqdm

VK_TOKEN = ''

class Start:
    vk_id = input('VK ID: ')
    ya_token = input('Я.Токен: ')


class VKClient:
    API_BASE_URL = 'https://api.vk.com/method'
    photo_urls = []

    def __init__(self, token):
        self.token = token

    def get_common_params(self):
        return {
            'access_token': self.token,
            'v': '5.131'
        }

    def get_photos(self):
        print('\nПолучаем фотографии из VK:')
        photos = []
        same_names = []
        params = self.get_common_params()
        params.update(
            {
                'owner_id': Start.vk_id,
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
        print('Готово!')


class YADisk:
    BASE_URL = 'https://cloud-api.yandex.net'
    CREATING_FOLDER_URL = f'{BASE_URL}/v1/disk/resources'
    UPLOADING_URL = f'{CREATING_FOLDER_URL}/upload'
    UPLOADING_FOLDER = 'VK Backups'

    def upload_photos(self):
        print('\nЗагружаем фотографии на Я.Диск:')
        headers = {
            'Authorization': Start.ya_token
        }
        folder_params = {
            'path': self.UPLOADING_FOLDER
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
                'path': f'{self.UPLOADING_FOLDER}/{photo["file_name"]}',
                'url': photo['url']
            }
            requests.post(
                self.UPLOADING_URL, headers=headers, params=upload_params
            )
            time.sleep(.05)
        print('Готово!')


if __name__ == '__main__':
    s = Start()
    vk = VKClient(VK_TOKEN)
    vk.get_photos()
    ya = YADisk()
    ya.upload_photos()
