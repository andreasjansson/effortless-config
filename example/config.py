from effortless_config import Config, setting


class config(Config):  # notice lowercase c

    groups = ['experiment1', 'experiment2']

    SOME_INTEGER_SETTING = setting(10, experiment1=20, experiment2=30)
    FLOAT_SETTING = setting(0.5)
    A_BOOLEAN = setting(False, experiment1=True)
    MY_STRING_SETTING = setting('foo', experiment2='bar')
    SOME_OTHER_INTEGER = 100
