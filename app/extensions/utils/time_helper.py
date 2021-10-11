import random
from datetime import datetime, timedelta
from pytz import timezone


def get_server_timestamp():
    return datetime.now(timezone('Asia/Seoul'))


def get_month_from_today():
    return datetime.now(timezone('Asia/Seoul')) - timedelta(days=30)


def get_month_from_date(date_from: str):
    """
        date_from example: 20210915
    """
    date = datetime.strptime(date_from, "%Y%m%d")
    return date - timedelta(days=30)


def get_random_date_about_one_month_from_today():
    """
        현재 날짜로부터 1달 이내 랜덤 날짜 구하기
    """
    start_date = get_month_from_today()
    end_date = get_server_timestamp()

    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + timedelta(days=random_number_of_days)
