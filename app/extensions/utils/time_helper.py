from datetime import datetime, date, timedelta


def get_server_timestamp():
    return datetime.now()


def get_month_from_today():
    return datetime.now() - timedelta(days=30)
