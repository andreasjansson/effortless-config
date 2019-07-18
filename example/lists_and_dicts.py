from effortless_config import Config


class config(Config):  # lowercase "c" optional

    MY_LIST = [10, 20, 30, 40]
    MY_DICT = {'a': 1, 'b': 2, 'c': 3}


def main():
    print(f'MY_LIST is {config.MY_LIST}')
    print(f'MY_DICT is {config.MY_DICT}')


if __name__ == '__main__':
    config.parse_args()
    main()
