import re
from typing import Dict, List, Optional

from app.extensions.utils.house_helper import HouseHelper
from core.domains.house.entity.house_entity import PublicSaleReportEntity
from core.domains.report.enum.report_enum import RegionEnum


class ReportHelper:
    @classmethod
    def sort_domain_list_to_region(cls, target_list: List):
        sort_dict = {
            RegionEnum.THE_AREA.value: 0,
            RegionEnum.OTHER_GYEONGGI.value: 1,
            RegionEnum.OTHER_REGION.value: 2,
        }

        for target_domain in target_list:
            end = len(target_domain) - 1
            while end > 0:
                last_swap = 0
                for i in range(end):
                    if sort_dict.get(target_domain[i]["region"]) > sort_dict.get(
                        target_domain[i + 1]["region"]
                    ):
                        target_domain[i], target_domain[i + 1] = (
                            target_domain[i + 1],
                            target_domain[i],
                        )
                        last_swap = i
                end = last_swap

    @classmethod
    def convert_area_type_dict(cls, convert_target_dict: Dict, key_name: str) -> Dict:
        result_dict = dict()

        domain_list = list(convert_target_dict.keys())
        for domain in domain_list:
            convert_dict = dict()
            domain_target_dict = convert_target_dict.get(domain)
            key_list = list(convert_target_dict.get(domain).keys())
            for key in key_list:
                domain_target = domain_target_dict.get(key)
                area_type = domain_target.get(key_name)
                if re.search("\d", area_type):
                    new_key = re.sub(r"[^0-9]", "", area_type)
                    convert_dict.setdefault(new_key, []).append(
                        domain_target_dict.get(key)
                    )
                else:
                    convert_dict.setdefault(key, []).append(domain_target_dict.get(key))

            result_dict.setdefault(domain, dict()).update(convert_dict)

        return result_dict

    @classmethod
    def sort_area_type_by_dict(cls, convert_target_dict: Dict, key_name: str) -> None:
        key_list = convert_target_dict.keys()
        for key in key_list:
            area_type_dict = convert_target_dict.get(key)
            area_type_keys = area_type_dict.keys()

            for area_type_key in area_type_keys:
                area_type_list = area_type_dict.get(area_type_key)
                end = len(area_type_list) - 1
                while end > 0:
                    last_swap = 0
                    for i in range(end):
                        # 102A, 84A str로 비교시 84A가 크기 때문에 숫자로 재비교
                        number1 = "".join(
                            re.findall("\d+", area_type_list[i].get(key_name))[0]
                        )
                        number2 = "".join(
                            re.findall("\d+", area_type_list[i + 1].get(key_name))[0]
                        )

                        if int(number1) > int(number2):
                            area_type_list[i], area_type_list[i + 1] = (
                                area_type_list[i + 1],
                                area_type_list[i],
                            )
                            last_swap = i
                    end = last_swap

                end = len(area_type_list) - 1
                while end > 0:
                    last_swap = 0
                    for i in range(end):
                        # 위의 숫자기반 정렬을 알파벳 순으로 다시 재정렬
                        word1 = "".join(
                            re.findall("[a-zA-Z]+", area_type_list[i].get(key_name))
                        )
                        word2 = "".join(
                            re.findall("[a-zA-Z]+", area_type_list[i + 1].get(key_name))
                        )

                        number1 = "".join(
                            re.findall("\d+", area_type_list[i].get(key_name))[0]
                        )
                        number2 = "".join(
                            re.findall("\d+", area_type_list[i + 1].get(key_name))[0]
                        )

                        if (number1 == number2) and (word1 > word2):
                            area_type_list[i], area_type_list[i + 1] = (
                                area_type_list[i + 1],
                                area_type_list[i],
                            )
                            last_swap = i
                    end = last_swap

    @classmethod
    def make_response_object_to_public_sale_details(
        cls, report_recently_public_sale_info: PublicSaleReportEntity,
    ) -> Optional[Dict]:
        if not report_recently_public_sale_info:
            return None

        public_sale_detail_dict = dict()
        public_sale_detail_list = list()

        competitions = report_recently_public_sale_info.public_sale_details
        for competition in competitions:
            key = "{}_{}_{}".format(
                competition.supply_area,
                competition.private_area,
                competition.supply_area,
            )

            detail_dict = dict(
                area_type=competition.area_type,
                special_household=competition.special_household,
                general_household=competition.general_household,
                total_household=competition.total_household,
                price_per_meter=competition.price_per_meter,
                private_area=competition.private_area,
                private_pyoung_number=HouseHelper().convert_area_to_pyoung(
                    competition.private_area
                ),
                pyoung_number=competition.pyoung_number,
                acquisition_tax=competition.acquisition_tax,
                supply_area=competition.supply_area,
                supply_price=competition.supply_price,
                public_sale_detail_photo=competition.public_sale_detail_photo,
            )

            if public_sale_detail_dict.get(key):
                public_sale_detail_list.append(detail_dict)
            else:
                public_sale_detail_list = [detail_dict]

            public_sale_detail_dict.setdefault(key, dict()).update(detail_dict)

        convert_target_dict = dict(public_sale_details=public_sale_detail_dict,)

        result_dict: Dict = cls.convert_area_type_dict(
            convert_target_dict=convert_target_dict, key_name="area_type"
        )

        cls.sort_area_type_by_dict(
            convert_target_dict=result_dict, key_name="area_type"
        )
        return result_dict

    @classmethod
    def make_response_object_to_house_applicants(
        cls, report_recently_public_sale_info: PublicSaleReportEntity,
    ) -> Optional[Dict]:
        if not report_recently_public_sale_info:
            return None
        (
            domain_marry_list,
            domain_first_life_list,
            domain_children_list,
            domain_old_parent_list,
            domain_normal_list,
        ) = (list(), list(), list(), list(), list())
        (
            domain_marry_dict,
            domain_first_life_dict,
            domain_children_dict,
            domain_old_parent_dict,
            domain_normal_dict,
        ) = (dict(), dict(), dict(), dict(), dict())

        competitions = report_recently_public_sale_info.public_sale_details
        for competition in competitions:
            key = "{}_{}_{}".format(
                competition.area_type, competition.private_area, competition.supply_area
            )

            for special_supply_result in competition.special_supply_results:
                domain_common_dict = dict(
                    region=special_supply_result.region,
                    region_percentage=special_supply_result.region_percent,
                )
                marry_dict = dict(
                    competition=None,
                    applicant=special_supply_result.newlywed_vol,
                    score=None,
                )
                first_life_dict = dict(
                    competition=None,
                    applicant=special_supply_result.first_life_vol,
                    score=None,
                )
                children_dict = dict(
                    competition=None,
                    applicant=special_supply_result.multi_children_vol,
                    score=None,
                )
                old_parent_dict = dict(
                    competition=None,
                    applicant=special_supply_result.old_parent_vol,
                    score=None,
                )

                marry_dict.update(domain_common_dict)
                first_life_dict.update(domain_common_dict)
                children_dict.update(domain_common_dict)
                old_parent_dict.update(domain_common_dict)

                if domain_marry_dict.get(key):
                    domain_marry_list.append(marry_dict)
                    domain_first_life_list.append(first_life_dict)
                    domain_children_list.append(children_dict)
                    domain_old_parent_list.append(old_parent_dict)
                else:
                    domain_marry_list = [marry_dict]
                    domain_first_life_list = [first_life_dict]
                    domain_children_list = [children_dict]
                    domain_old_parent_list = [old_parent_dict]

                # 각 타입별 마지막 지역(해당지역,기타경기,기타지역)이 들어오면 지역순서대로 정렬
                if len(domain_marry_list) == 3:
                    cls.sort_domain_list_to_region(
                        target_list=[
                            domain_marry_list,
                            domain_first_life_list,
                            domain_children_list,
                            domain_old_parent_list,
                            domain_normal_list,
                        ]
                    )

                domain_marry_dict.setdefault(key, dict()).update(
                    house_structure_type=competition.area_type,
                    supply_household=competition.newlywed_household,
                    infos=domain_marry_list,
                )
                domain_first_life_dict.setdefault(key, dict()).update(
                    house_structure_type=competition.area_type,
                    supply_household=competition.first_life_household,
                    infos=domain_first_life_list,
                )
                domain_children_dict.setdefault(key, dict()).update(
                    house_structure_type=competition.area_type,
                    supply_household=competition.multi_children_household,
                    infos=domain_children_list,
                )
                domain_old_parent_dict.setdefault(key, dict()).update(
                    house_structure_type=competition.area_type,
                    supply_household=competition.old_parent_household,
                    infos=domain_old_parent_list,
                )

            for general_supply_result in competition.general_supply_results:
                domain_common_dict = dict(
                    region=general_supply_result.region,
                    region_percentage=general_supply_result.region_percent,
                )
                normal_dict = dict(
                    competition=general_supply_result.competition_rate,
                    applicant=general_supply_result.applicant_num,
                    score=general_supply_result.win_point,
                )

                normal_dict.update(domain_common_dict)

                if domain_normal_dict.get(key):
                    domain_normal_list.append(normal_dict)
                else:
                    domain_normal_list = [normal_dict]

                domain_normal_dict.setdefault(key, dict()).update(
                    house_structure_type=competition.area_type,
                    supply_household=competition.general_household,
                    infos=domain_normal_list,
                )

        convert_target_dict = dict(
            marry=domain_marry_dict,
            first_life=domain_first_life_dict,
            children=domain_children_dict,
            old_parent=domain_old_parent_dict,
            normal=domain_normal_dict,
        )

        house_applicants_dict: Dict = cls.convert_area_type_dict(
            convert_target_dict=convert_target_dict, key_name="house_structure_type"
        )

        cls.sort_area_type_by_dict(
            convert_target_dict=house_applicants_dict, key_name="house_structure_type"
        )
        return house_applicants_dict
