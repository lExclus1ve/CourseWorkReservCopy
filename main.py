import requests
import json
import datetime
import sys
import time

vk_token = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'

def bar_progress():
    sys.stdout.write("#")
    sys.stdout.flush()
    time.sleep(0.2)


class VkCopy:
    def __init__(self, token, user_id):
        self.token = token
        self.list_photo = []
        self.user_id = user_id

    def get_url_files(self):
        url = 'http://api.vk.com/method/photos.get'
        params = {
        'owner_id': self.user_id,
        'album_id': 'profile',
        'access_token': self.token,
        'extended': 1,
        'v': '5.131',
        'count': 1000
    }
        response = requests.get(url, params=params).json()['response']['items']
        return response

    def sorted_files(self, count_photo=5):
        now = datetime.datetime.now()
        date = now.strftime('%d_%m_%Y')

        for photo in self.get_url_files():
            bar_progress()

            big_photo = photo['sizes'][-1]
            self.list_photo.append({'size': big_photo['type'], 'size_ab': big_photo['height'] + big_photo['width'],
                                   'url': big_photo['url'], 'likes': photo['likes']['count'], 'date': date})
        self.list_photo = sorted(self.list_photo, key=lambda k: k['size_ab'], reverse=True)
        return self.list_photo[:count_photo]


class YaUploader():
    def __init__(self, token, file_name='photo'):
        self.token = token
        self.file_name = file_name

    def get_headers(self):
        return {
            "Accept": "application/json",
            "Authorization": f'OAuth {self.token}'
        }

    def _create_a_folder(self):
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = self.get_headers()
        params = {'path': self.file_name}
        response = requests.put(url, params=params, headers=headers).json()

    def _get_upload_link(self):
        upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload/'
        headers = self.get_headers()
        params = {'path': self.file_name, 'overwrite': 'true'}
        response = requests.get(upload_url, headers=headers, params=params)
        return response.json()

    def upload_file_to_disk(self, list_photo):
        self._create_a_folder()
        count = 0
        for link in list_photo:
            bar_progress()

            url = 'https://cloud-api.yandex.net/v1/disk/resources/upload/'
            headers = self.get_headers()
            params = {
                'path': f'/{self.file_name}/{list_photo[count]["likes"]}.jpg',
                'url': f'{link["url"]}'
            }
            response = requests.post(url, params=params, headers=headers).json()
            count += 1


class JsonCreate(VkCopy):
    def write_json_file(self):
        count = 0
        for i in self.sorted_files():
            bar_progress()

            to_json = [{'file_name': f"{self.list_photo[count]['likes']}.jpg", 'size': self.list_photo[count]['size']}]
            with open('photo_name.json', 'a') as f:
                json.dump(to_json, f)
            count += 1


if __name__ == '__main__':
    USER_ID = int(input('Введите id пользователя: '))
    ya_token = input('Введите Токен Яндекс.Полигона: ')
    print('\nProgress Bar')

    vk = VkCopy(token=vk_token, user_id=USER_ID)
    ya = YaUploader(token=ya_token)
    json_file = JsonCreate(token=vk_token, user_id=USER_ID)

    ya.upload_file_to_disk(vk.sorted_files())
    json_file.write_json_file()

