import os

import requests


class Renaming:
    def __init__(self, sources_path):
        self.sources_path = sources_path
        self.file_names = self.get_file_names()
        self.unique_series = set()

    def get_file_names(self):
        file_names = os.listdir(self.sources_path)
        return file_names

    def prepare_series_names(self):
        for file_name in self.file_names:
            if file_name.endswith('.jpg'):
                raise ValueError('jpg extension is not allowed')
            photo_name, extension = file_name.split('.')
            if photo_name.count('_') > 1:
                print(photo_name)
                continue
            if '_' in photo_name:
                series_name, angle = photo_name.split('_')
            else:
                series_name = photo_name
            self.unique_series.add(series_name)

    def make_requests(self):
        url = os.getenv('URL')
        user = os.getnv('USERNAME_1C')
        password = os.getenv('PASSWORD_1C')
        data = {'series': self.unique_series}
        response = requests.post(url, data=data, auth=(user, password))


def main():
    source_path = r'E:\PHOTO_SOURCES\SOURCES'
    renaming = Renaming(source_path)
    renaming.prepare_series_names()
    renaming.make_request()
    1



if __name__ == '__main__':
    main()
