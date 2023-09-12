import os
import shutil


def convert_from_jpg_to_jpeg(src_path, dst_path):
    all_files = os.listdir(src_path)
    for file_name in all_files:
        if file_name.endswith('.jpg'):
            series, _ = file_name.split('.')
            new_file_name = series + '.jpeg'
            src = os.path.join(src_path, file_name)
            dst = os.path.join(dst_path, new_file_name)
        else:
            src = os.path.join(src_path, file_name)
            dst = os.path.join(dst_path, file_name)
        shutil.copy2(src, dst)


def list_dst_files_that_src_doesnt_have(src_path, dst_path):
    src_files = os.listdir(src_path)
    dst_files = os.listdir(dst_path)
    lost_photos = [
        dst_file
        for dst_file in dst_files
        if dst_file not in src_files
    ]
    return lost_photos
