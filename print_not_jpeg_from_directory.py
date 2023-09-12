import os


def main():
    folder = r'E:\photo backup\NORMALISING\photo_team_all_converted'
    for file_name in os.listdir(folder):
        if not file_name.endswith('.jpeg'):
            print(file_name)


if __name__ == '__main__':
    main()
