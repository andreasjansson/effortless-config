from effortless_config import Config, setting


class config(Config):
    groups = ['large', 'small']

    NUM_LAYERS = setting(default=5, large=10, small=3)
    NUM_UNITS = setting(default=128, large=512, small=32)
    USE_SKIP_CONNECTIONS = setting(default=True, small=False)
    LEARNING_RATE = 0.1
    OPTIMIZER = 'adam'


def main():
    print(f'NUM_LAYERS is {config.NUM_LAYERS}')
    print(f'NUM_UNITS is {config.NUM_UNITS}')
    print(f'USE_SKIP_CONNECTIONS is {config.USE_SKIP_CONNECTIONS}')
    print(f'LEARNING_RATE is {config.LEARNING_RATE}')
    print(f'OPTIMIZER is {config.OPTIMIZER}')


if __name__ == '__main__':
    config.parse_args()
    main()
