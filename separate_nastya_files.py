import os
import re
import shutil

import requests
from dotenv import load_dotenv

from utils import list_dst_files_that_src_doesnt_have


def from_sources_to_nastya_all():
    src_path = r'E:\photo backup\NORMALISING\photo_team_all_converted'
    dst_path = r'E:\photo backup\NORMALISING\SOURCES_06092023\SOURCES'

    nastya_all = r'E:\photo backup\NORMALISING\nastya\all'
    nastya_photos = list_dst_files_that_src_doesnt_have(src_path, dst_path)
    for file_name in nastya_photos:
        src = os.path.join(dst_path, file_name)
        dst = os.path.join(nastya_all, file_name)
        shutil.copy2(src, dst)


def get_barcode_from_file_name(file_name):
    name, extension = file_name.split('.')
    return name.split('_')[0]


def determine_angle(file_name):
    if '_' not in file_name:
        return 0
    name, extension = file_name.split('.')
    barcode, angle = name.split('_')
    return angle


def create_files_table(source_path):
    table = []
    pattern = r'^\d+(?:_[12])?\.jpeg$'

    for file_name in os.listdir(source_path):
        correct_file_name = False
        angle = None
        barcode = None
        if re.match(pattern, file_name):
            correct_file_name = True
            barcode = get_barcode_from_file_name(file_name)
            angle = determine_angle(file_name)
        current_line = {
            'file_name': file_name,
            'correct_file_name': correct_file_name,
            'barcode': barcode,
            'angle': angle,
            'aim': None,
            'series': None,
        }
        table.append(current_line)
    return table


def join_1c_data(table):
    unique_series = set()
    for line in table:
        if line['correct_file_name']:
            unique_series.add(line['barcode'])
    url = os.getenv('URL')
    user = os.getenv('USERNAME_1C')
    password = os.getenv('PASSWORD_1C')
    data = {'series': list(unique_series)}
    response = requests.post(url, json=data, auth=(user, password))
    response_json = response.json()
    for line in table:
        barcode = line['barcode']
        if not barcode:
            continue
        found_dict = next(
            item
            for item in response_json
            if item.get('ШК') == barcode
        )
        line['aim'] = found_dict['Трим_Аим']
        line['series'] = found_dict['Наименование']

def sort_table(files_table, result):
    sorted_by_barcode = result['sorted_by_barcode']
    doesnt_have_series = result['doesnt_have_series']
    incorrect_name = result['incorrect_name']
    for file in files_table:
        if file['series']:
            if file['series'] not in sorted_by_barcode:
                sorted_by_barcode[file['series']] = []
            sorted_by_barcode[file['series']].append(file)
            continue
        if file['correct_file_name']:
            doesnt_have_series.append(file)
            continue
        incorrect_name.append(file)

def carry_out_copy_ops(result):
    parent_folder = r'E:\photo backup\NORMALISING\nastya'
    all = 'all'
    for barcode, files in result['sorted_by_barcode'].items():
        dst_folder = str(len(files))
        for file in files:
            src = os.path.join(parent_folder, all, file['file_name'])
            dst = os.path.join(parent_folder, dst_folder, file['file_name'])
            shutil.copy2(src, dst)

def main():
    load_dotenv()

    # from_sources_to_nastya_all()
    source_path = r'E:\photo backup\NORMALISING\nastya\all'
    files_table = create_files_table(source_path)
    join_1c_data(files_table)
    result = {
        'sorted_by_barcode': {},
        'doesnt_have_series': [],
        'incorrect_name': []
    }
    sort_table(files_table, result)
    carry_out_copy_ops(result)


if __name__ == '__main__':
    main()
