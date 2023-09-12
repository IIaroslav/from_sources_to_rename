from utils import list_dst_files_that_src_doesnt_have


def main():
    src_path = r'E:\PHOTO_SOURCES\SOURCES'
    dst_path = r'E:\photo backup\NORMALISING\photo_team_all_converted'
    res = list_dst_files_that_src_doesnt_have(src_path, dst_path)


if __name__ == '__main__':
    main()
