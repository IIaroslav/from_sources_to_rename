import os


def main():
    source_path = r'E:\PHOTO_SOURCES\SOURCES'
    source_files = os.listdir(source_path)
    for source_file in source_files:
        if source_file.endswith('.jpg'):
            print(source_file)


if __name__ == '__main__':
    main()
