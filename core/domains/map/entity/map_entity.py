from datetime import date, datetime

from geojson_pydantic import Point
from pydantic import BaseModel


class RealEstateEntity(BaseModel):
    id: int
    name: str
    road_address: str
    jibun_address: str
    si_do: str
    si_gun_gu: str
    dong_myun: str
    ri: str
    road_name: str
    road_number: str
    land_number: str
    is_available: bool
    coordinates: Point


class RealTradeEntity(BaseModel):
    id: int
    real_estate_id: int
    area: float
    supply_area: float
    contract_date: date
    deposit_price: int
    rent_price: int
    trade_price: int
    floor: int
    trade_type: str
    building_type: str
    is_available: bool
    created_at: datetime
    updated_at: datetime


class PreSaleEntity(BaseModel):
    id: int
    real_estate_id: int
    name: str
    region: str
    housing_category: str
    rent_type: str
    trade_type: str
    construct_company: str
    housing_type: str
    supply_price: int
    supply_area: float
    supply_household: int
    notes: str
    is_available: bool
    created_at: datetime
    updated_at: datetime


class SubscriptionScheduleEntity(BaseModel):
    id: int
    pre_sales_id: int
    offer_date: date
    subscription_start_date: date
    subscription_end_date: date
    special_supply_date: date
    special_supply_etc_date: date
    first_supply_date: date
    first_supply_etc_date: date
    second_supply_date: date
    second_supply_etc_date: date
    notice_winner_date: date
    contract_start_date: date
    contract_end_date: date
    move_in_year: int
    move_in_month: int
