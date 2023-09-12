import json


def main():
    with open('report.json', 'r') as json_file:
        series_doesnt_have_aim = json.load(json_file)
    barcodes = {file['barcode'] for file in series_doesnt_have_aim}
    with open('barcodes_without_aim.txt', 'w') as json_file:
        json_file.writelines('\n'.join(list(barcodes)))

if __name__ == '__main__':
    main()
