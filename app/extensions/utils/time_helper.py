from datetime import datetime, date, timedelta


def get_server_timestamp():
    return datetime.now()


def get_month_from_today():
    return date.today() - timedelta(days=30)
