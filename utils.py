import yaml


def load_config(path='config.yaml'):
    with open(path, 'r') as stream:
        config = yaml.safe_load(stream)
    return config

def get_timestamp(days_later):
    import datetime
    import time

    three_months_later = datetime.datetime.now() + datetime.timedelta(days=days_later)
    timestamp = int(time.mktime(three_months_later.timetuple()))
    return timestamp
