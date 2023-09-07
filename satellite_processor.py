from sys import argv
from src.utils import process_satellite_data_for_filepath


def main():
    print(argv)
    if len(argv) < 2:
        raise Exception("File path not entered")
    file_path = argv[1]
    process_satellite_data_for_filepath(file_path)
    

if __name__ == "__main__":
    main()