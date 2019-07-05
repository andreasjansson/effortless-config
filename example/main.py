from .config import config


# python -m example.main
if __name__ == '__main__':
    config.parse_args()
    print(f'SOME_INTEGER_SETTING is {config.SOME_INTEGER_SETTING}')
    print(f'FLOAT_SETTING is {config.FLOAT_SETTING}')
    print(f'A_BOOLEAN is {config.A_BOOLEAN}')
    print(f'MY_STRING_SETTING is {config.MY_STRING_SETTING}')
    print(f'SOME_OTHER_INTEGER is {config.SOME_OTHER_INTEGER}')
