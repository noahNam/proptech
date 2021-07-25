INSERT INTO public.administrative_divisions (id, name, short_name, real_trade_price, real_rent_price, real_deposit_price, public_sale_price, "level", coordinates, created_at, updated_at) VALUES
(1, '서울특별시', '서울', 153000, 60, 75000, 88000, '1', '0101000020E6100000EB121FE99DBE5F403E4ADBAE86C84240', '2021-07-13 09:02:49.038447', '2021-07-13 09:02:49.038467'),
(2, '서울특별시 구로구', '구로구', 100000, 55, 45000, 70000, '2', '0101000020E6100000B1C05774EBB65F40C9D177126CBF4240', '2021-07-13 09:04:26.139913', '2021-07-13 09:04:26.139937'),
(3, '서울특별시 구로구 개봉동', '개봉동', 80000, 44, 23000, 50000, '3', '0101000020E61000005220FD4083B65F404E6ECACB50BF4240', '2021-07-13 09:05:41.171475', '2021-07-13 09:05:41.171492');

INSERT INTO public.real_estates (id, name, road_address, jibun_address, si_do, si_gun_gu, dong_myun, ri, road_name, road_number, land_number, is_available, coordinates) VALUES
(1, '래미안 원베일리', '서울특별시 서초구 신반포로19길 10', '서울특별시 서초구 반포동 1-1', '서울특별시', '서초구', '반포동', '-', '신반포로19길', '10', '1-1', 'True', '0101000020E6100000D578E92631BF5F40234A7B832FC04240'),
(2, '봉담자이 프라이드시티', '경기도 화성시 봉담 내리지구 A-1블록', '경기 화성시 봉담읍 내리 545', '경기도', '화성시', '봉담읍', '내리', '-', '-', '545', 'True', '0101000020E610000013EF004F5ABB5F4003B34291EE9D4240'),
(3, '개봉동한진아파트', '서울특별시 구로구 개봉로3길 87 개봉동한진아파트', '서울특별시 구로구 개봉동 478 개봉동한진아파트', '서울특별시', '구로구', '개봉동', '-', '개봉로3길 87', '87', '478', 'True', '0101000020E6100000AFEEB32586B65F400DFFE9060ABE4240');

INSERT INTO public.public_sales (id, real_estate_id, name, region, housing_category, rent_type, trade_type, construct_company, supply_household, is_available, offer_date, subscription_start_date, subscription_end_date, special_supply_date, special_supply_etc_date, first_supply_date, first_supply_etc_date, second_supply_date, second_supply_etc_date, notice_winner_date, contract_start_date, contract_end_date, move_in_year, move_in_month, min_down_payment, max_down_payment, down_payment_ratio, reference_url, created_at, updated_at) VALUES
(2, 2, '봉담자이 프라이드시티', '경기', '민영', '분양', '분양', '지에스건설(주)', 1701, 'True', '20210714', '20210617', '20210622', '20210617', '20210617', '20210618', '20210621', '20210622', '20210622', '20210628', '20210710', '20210716', 2024, 7, 31800000, 77580000, 10, 'https://xi.co.kr/pridecity', '2021-07-13 04:38:21.370035', '2021-07-13 04:38:21.370058'),
(1, 1, '래미안 원베일리', '서울', '민영', '분양', '분양', '삼성물산(주)', 224, 'True', '20210607', '20210617', '20210621', NULL, NULL, '20210714', '20210618', '20210621', '20210621', '20210625', '20210709', '20210713', 2023, 8, 181000000, 344000000, 20, 'https://www.raemian.co.kr', '2021-07-13 04:16:54.746256', '2021-07-13 04:16:54.74628');

INSERT INTO public.public_sale_details (id, public_sales_id, private_area, supply_area, supply_price, acquisition_tax) VALUES
(1, 1, '46.93', '62.6816', 92370, 30482100),
(2, 1, '59.96', '80.6362', 142500, 47025000),
(3, 1, '74.97', '100.2876', 176000, 58080000),
(4, 2, '59.6481', '82.5295', 34540, 3799400),
(5, 2, '72.018', '98.0448', 39460, 4340600);

INSERT INTO public.public_sale_photos (id, public_sales_id, file_name, "path", "extension", created_at, updated_at) VALUES
(1, 1, 'photo', 'public_sale_photos/2021/07/13/2c222a5b-b115-4330-8c88-9be638b14b46.png', 'png', '2021-07-13 04:30:32.749113', '2021-07-13 04:30:32.749154'),
(2, 2, 'photo_test', 'public_sale_photos/2021/07/13/e71dead1-212e-4cf4-84c1-51d2d166ab06.png', 'png', '2021-07-13 04:38:46.631388', '2021-07-13 04:38:46.631411');

INSERT INTO public.private_sales (id, real_estate_id, building_type, created_at, updated_at) VALUES
(1, 3, '아파트', '2021-07-13 08:56:59.486593', '2021-07-13 08:56:59.486611');

INSERT INTO public.private_sale_details (id, private_sales_id, private_area, supply_area, contract_date, deposit_price, rent_price, trade_price, floor, trade_type, is_available, created_at, updated_at) VALUES
(1, 1, '56', '84', '20210707', 0, 0, 100000, 3, '매매', 'True', '2021-07-13 08:56:59.486593', '2021-07-13 08:56:59.486611');