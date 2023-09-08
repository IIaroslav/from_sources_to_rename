import os
from datetime import datetime

import requests

from dotenv import load_dotenv


def timestamp_to_datetime(timestamp):
    dt_obj = datetime.fromtimestamp(timestamp)
    formatting = '%d.%m.%Y %H:%M:%S'
    return dt_obj.strftime(formatting)


class Renaming:
    def __init__(self, sources_path):
        self.errors = []
        self.unique_aims = set()
        self.unique_series = set()
        self.sources_path = sources_path
        self.main_table = self.create_main_table()
        self.main_tree = {}

    def determine_angle(self, file_name):
        if '_' not in file_name:
            return 1

        name, extension = file_name.split('.')
        barcode, angle = name.split('_')
        if angle != '2':
            self.errors.append(f'{file_name} has an angle problem')
            return None
        return 3

    def create_main_table(self):
        table = []
        for file_name in os.listdir(self.sources_path):
            angle = self.determine_angle(file_name)
            if not angle:
                continue
            full_path_file_name = os.path.join(self.sources_path, file_name)
            creation_time = os.path.getctime(full_path_file_name)
            current_line = {
                'file_name': file_name,
                'creation_time': creation_time,
                'barcode': self.get_barcode_from_file_name(file_name),
                'datetime': timestamp_to_datetime(creation_time),
                'angle': angle,
            }
            table.append(current_line)
        return table

    def prepare_unique_series(self):
        for line in self.main_table:
            file_name = line['file_name']
            if file_name.endswith('.jpg'):
                print(file_name)
                raise ValueError('jpg extension is not allowed')

            photo_name, extension = file_name.split('.')
            if photo_name.count('_') > 1:
                print(file_name)
                raise ValueError('filename has more than 1 underscore')

            self.unique_series.add(self.get_barcode_from_file_name(file_name))

    def make_request(self):
        self.prepare_unique_series()
        url = os.getenv('URL')
        user = os.getenv('USERNAME_1C')
        password = os.getenv('PASSWORD_1C')
        data = {'series': list(self.unique_series)}
        response = requests.post(url, json=data, auth=(user, password))
        self.response_json = response.json()

    def save_unique_series_to_file(self):
        series = list(self.unique_series)
        with open('series.txt', 'w') as file:
            file.writelines('\n'.join(series))

    def prepare_unique_aim(self):
        for line in self.response_json:
            aim = line['Трим_Аим']
            if aim:
                self.unique_aims.add(aim)

    def get_barcode_from_file_name(self, file_name):
        name, extension = file_name.split('.')
        return name.split('_')[0]

    def add_aim_and_check_series_existence_to_main_table(self):
        for line in self.main_table:
            barcode = line['barcode']
            found_dict = next(
                item
                for item in self.response_json
                if item.get('ШК') == barcode
            )
            line['aim'] = found_dict['Трим_Аим']
            line['series_exists'] = bool(found_dict['Наименование'])

    def group_by_aim(self):
        for unique_aim in self.unique_aims:
            if not unique_aim:
                continue
            aim_table = []
            aim_table_line = {
                'aim': unique_aim,
                'angle1': [],
                'angle3': []
            }
            for line in self.main_table:
                if unique_aim == line['aim'] and line['series_exists']:
                    pass
            # self.main_tree[unique_aim] = aim_lines
        1



def main():
    load_dotenv()
    source_path = r'E:\PHOTO_SOURCES\SOURCES'
    renaming = Renaming(source_path)
    renaming.make_request()
    # renaming.save_unique_series_to_file()
    renaming.prepare_unique_aim()
    renaming.add_aim_and_check_series_existence_to_main_table()
    renaming.group_by_aim()
    1



if __name__ == '__main__':
    main()
