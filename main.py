import json
import os
import re
import shutil
import time
from datetime import datetime

import requests

from dotenv import load_dotenv


def timestamp_to_datetime(timestamp):
    dt_obj = datetime.fromtimestamp(timestamp)
    formatting = '%d.%m.%Y %H:%M:%S'
    return dt_obj.strftime(formatting)


class Renaming:
    def __init__(self, source_path, destination_path):
        self.source_path = source_path
        self.destination_path = destination_path
        self.files_table = self.create_files_table()

        self.unique_aims = set()
        self.unique_series = set()
        self.aim_table = []

    def create_files_table(self):
        table = []
        pattern = r'^\d+(?:_2)?\.jpeg$'

        for file_name in os.listdir(self.source_path):
            full_path_file_name = os.path.join(self.source_path, file_name)
            created_at = os.path.getctime(full_path_file_name)
            correct_file_name = False
            angle = None
            barcode = None
            if re.match(pattern, file_name):
                correct_file_name = True
                barcode = self.get_barcode_from_file_name(file_name)
                angle = [1, 3]['_' in file_name]
            current_line = {
                'file_name': file_name,
                'created_at': created_at,
                'datetime': timestamp_to_datetime(created_at),
                'correct_file_name': correct_file_name,
                'barcode': barcode,
                'angle': angle,
                'aim': None,
                'series': None,
            }
            table.append(current_line)
        return table

    def prepare_unique_series(self):
        for line in self.files_table:
            if line['correct_file_name']:
                self.unique_series.add(line['barcode'])

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

    def get_barcode_from_file_name(self, file_name):
        name, extension = file_name.split('.')
        return name.split('_')[0]

    def join_1c_data(self):
        for line in self.files_table:
            barcode = line['barcode']
            if not barcode:
                continue
            found_dict = next(
                item
                for item in self.response_json
                if item.get('ШК') == barcode
            )
            line['aim'] = found_dict['Трим_Аим']
            line['series'] = found_dict['Наименование']

    def create_aim_table(self):
        for line in self.files_table:
            if line['aim']:
                self.unique_aims.add(line['aim'])
        for aim in self.unique_aims:
            new_line = {
                'aim': aim,
                'angle1': [],
                'angle3': [],
            }
            for file in (
                line for line in self.files_table if line.get('aim') == aim
            ):
                if file['angle'] == 1:
                    new_line['angle1'].append(file)
                elif file['angle'] == 3:
                    new_line['angle3'].append(file)
            new_line['angle1'].sort(
                key=lambda x: x['created_at'], reverse=True
            )
            new_line['angle3'].sort(
                key=lambda x: x['created_at'], reverse=True
            )
            self.aim_table.append(new_line)

    def empty_destination(self):
        for file_name in os.listdir(self.destination_path):
            full_path = os.path.join(self.destination_path, file_name)
            os.remove(full_path)

    def rename(self):
        start = time.time()
        for aim in self.aim_table:
            if aim['angle1']:
                photo_file = aim['angle1'][0]
                src = os.path.join(self.source_path, photo_file['file_name'])
                new_file_name = f'{aim["aim"]}.jpeg'
                dst = os.path.join(self.destination_path, new_file_name)
                shutil.copy2(src, dst)
            if aim['angle3']:
                photo_file = aim['angle3'][0]
                src = os.path.join(self.source_path, photo_file['file_name'])
                new_file_name = f'{aim["aim"]}_2.jpeg'
                dst = os.path.join(self.destination_path, new_file_name)
                shutil.copy2(src, dst)
        end = time.time()
        print(f'The renaming operation took {end - start:.0f} seconds.')

    def provide_report(self):
        wrong_file_name = []
        barcode_doesnt_exist = []
        series_doesnt_have_aim = []
        for file in self.files_table:
            if not file['correct_file_name']:
                wrong_file_name.append(file)
                continue
            if not file['barcode']:
                barcode_doesnt_exist.append(file)
                continue
            if not file['aim']:
                series_doesnt_have_aim.append(file)

        with open('report.json', 'w') as file_json:
            json.dump(series_doesnt_have_aim, file_json, indent=2)



def main():
    load_dotenv()
    source_path = r'E:\PHOTO_SOURCES\SOURCES'
    destination_path = r'E:\PHOTO_SOURCES\renamed_test'
    renaming = Renaming(source_path, destination_path)
    renaming.make_request()
    # renaming.save_unique_series_to_file()
    renaming.join_1c_data()
    renaming.create_aim_table()
    renaming.empty_destination()
    renaming.rename()
    renaming.provide_report()


if __name__ == '__main__':
    main()
