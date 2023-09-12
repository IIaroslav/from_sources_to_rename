import os

from utils import convert_from_jpg_to_jpeg


def main():
    src_path = r'E:\photo backup\NORMALISING\photo_team_all'
    dst_path = r'E:\photo backup\NORMALISING\photo_team_all_converted'
    source_files = os.listdir(src_path)
    counting = {}
    for source_file_name in source_files:
        barcode_and_angle = source_file_name.split('.')[0]
        current_value = counting.get(barcode_and_angle, 0)
        counting[barcode_and_angle] = current_value + 1

    duplicates = [key for key, value in counting.items() if value > 1]
    if duplicates:
        print('\n'.join(duplicates))
        raise ValueError('Same name with different extensions')

    convert_from_jpg_to_jpeg(src_path, dst_path)

if __name__ == '__main__':
    main()
