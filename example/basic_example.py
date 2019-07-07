from effortless_config import Config


class config(Config):  # lowercase "c" optional

    SOME_INTEGER_SETTING = 10
    FLOAT_SETTING = 0.5
    A_BOOLEAN = False
    MY_STRING_SETTING = 'foo'


def main():
    print(f'SOME_INTEGER_SETTING is {config.SOME_INTEGER_SETTING}')
    print(f'FLOAT_SETTING is {config.FLOAT_SETTING}')
    print(f'A_BOOLEAN is {config.A_BOOLEAN}')
    print(f'MY_STRING_SETTING is {config.MY_STRING_SETTING}')


if __name__ == '__main__':
    config.parse_args()
    main()
