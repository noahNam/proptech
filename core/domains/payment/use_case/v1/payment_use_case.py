import json
import re
from http import HTTPStatus
from typing import Union, List, Optional

import inject
import requests

from app.extensions.utils.event_observer import send_message, get_event_object
from core.domains.house.entity.house_entity import GetPublicSaleOfTicketUsageEntity
from core.domains.house.enum import HouseTopicEnum
from core.domains.payment.dto.payment_dto import (
    PaymentUserDto,
    UseHouseTicketDto,
    CreateTicketDto,
    UseRecommendCodeDto,
    UseUserTicketDto,
)
from core.domains.payment.entity.payment_entity import (
    PromotionEntity,
    RecommendCodeEntity,
)
from core.domains.payment.enum.payment_enum import (
    TicketTypeDivisionEnum,
    TicketSignEnum,
    PromotionTypeEnum,
    RecommendCodeMaxCountEnum,
    PromotionDivEnum,
    CallJarvisEnum,
)
from core.domains.payment.repository.payment_repository import PaymentRepository
from core.domains.report.entity.report_entity import TicketUsageResultEntity
from core.domains.report.enum import ReportTopicEnum
from core.domains.report.enum.report_enum import TicketUsageTypeEnum
from core.domains.user.entity.user_entity import UserProfileEntity
from core.domains.user.enum import UserTopicEnum
from core.domains.user.enum.user_enum import UserSurveyStepEnum
from core.use_case_output import UseCaseSuccessOutput, UseCaseFailureOutput, FailureType


class PaymentBaseUseCase:
    @inject.autoparams()
    def __init__(self, payment_repo: PaymentRepository):
        self._payment_repo = payment_repo

    def _get_user_profile(self, user_id: int) -> Optional[UserProfileEntity]:
        send_message(
            topic_name=UserTopicEnum.GET_USER_PROFILE, user_id=user_id,
        )
        return get_event_object(topic_name=UserTopicEnum.GET_USER_PROFILE)

    def _make_create_use_ticket_dto(
        self, user_id: int, type_: int, amount: int, sign: TicketSignEnum
    ) -> CreateTicketDto:
        return CreateTicketDto(
            user_id=user_id, type=type_, amount=amount, sign=sign, created_by="system",
        )

    def _update_ticket_usage_result(
        self, user_id: int, house_id: Optional[int], ticket_id: int
    ) -> bool:
        send_message(
            topic_name=ReportTopicEnum.UPDATE_TICKET_USAGE_RESULT,
            user_id=user_id,
            house_id=house_id,
            ticket_id=ticket_id,
        )
        return get_event_object(topic_name=ReportTopicEnum.UPDATE_TICKET_USAGE_RESULT)

    def _is_promotion_available(self, promotion: PromotionEntity) -> bool:
        if not promotion.promotion_usage_count:
            return True

        return (
            True
            if promotion.max_count > promotion.promotion_usage_count.usage_count
            else False
        )


class GetTicketUsageResultUseCase(PaymentBaseUseCase):
    def execute(
        self, dto: PaymentUserDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        ticket_usage_results: List[
            TicketUsageResultEntity
        ] = self._get_ticket_usage_results(
            user_id=dto.user_id, type_=TicketUsageTypeEnum.HOUSE.value
        )
        result = list()
        if ticket_usage_results:
            result: List[
                GetPublicSaleOfTicketUsageEntity
            ] = self._get_public_sales_of_ticket_usage(
                public_house_ids=[
                    ticket_usage_result.public_house_id
                    for ticket_usage_result in ticket_usage_results
                ]
            )

        return UseCaseSuccessOutput(value=result)

    def _get_ticket_usage_results(
        self, user_id: int, type_: str
    ) -> List[TicketUsageResultEntity]:
        send_message(
            topic_name=ReportTopicEnum.GET_TICKET_USAGE_RESULTS,
            user_id=user_id,
            type_=type_,
        )
        return get_event_object(topic_name=ReportTopicEnum.GET_TICKET_USAGE_RESULTS)

    def _get_public_sales_of_ticket_usage(
        self, public_house_ids: List[int]
    ) -> List[GetPublicSaleOfTicketUsageEntity]:
        send_message(
            topic_name=HouseTopicEnum.GET_PUBLIC_SALES_TO_TICKET_USAGE,
            public_house_ids=public_house_ids,
        )
        return get_event_object(
            topic_name=HouseTopicEnum.GET_PUBLIC_SALES_TO_TICKET_USAGE
        )


class UseHouseTicketUseCase(PaymentBaseUseCase):
    def execute(
        self, dto: UseHouseTicketDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        # 유저 설문을 완료하지 않은 경우 사용 X
        if (
            self._get_user_profile(user_id=dto.user_id).survey_step
            != UserSurveyStepEnum.STEP_COMPLETE.value
        ):
            return UseCaseFailureOutput(
                type=HTTPStatus.BAD_REQUEST,
                message="needs user surveys",
                code=HTTPStatus.BAD_REQUEST,
            )

        # 이미 티켓을 사용한 분양건인 경우 사용 X
        if self._is_ticket_usage_for_house(user_id=dto.user_id, house_id=dto.house_id):
            return UseCaseFailureOutput(
                type=HTTPStatus.BAD_REQUEST,
                message="this is product where tickets have already been used",
                code=HTTPStatus.BAD_REQUEST,
            )

        promotion: Optional[PromotionEntity] = self._payment_repo.get_promotion(
            user_id=dto.user_id, div=PromotionDivEnum.HOUSE.value
        )
        if not promotion:
            # 프로모션은 없지만 유료 티켓을 사용하는 경우
            number_of_ticket: int = self._payment_repo.get_number_of_ticket(
                user_id=dto.user_id
            )
            if not number_of_ticket:
                # 티켓 수가 부족할 때
                return UseCaseFailureOutput(
                    type=HTTPStatus.BAD_REQUEST,
                    message="insufficient number of tickets",
                    code=HTTPStatus.BAD_REQUEST,
                )

            result: Optional[
                UseCaseFailureOutput
            ] = self._use_ticket_to_house_by_charged(dto=dto)
            if isinstance(result, UseCaseFailureOutput):
                return result
        else:
            # 적용 프로모션이 있는 경우
            if promotion.type == PromotionTypeEnum.ALL.value:
                """
                모든 분양에 프로모션을 적용하는 경우
                    promotion_houses 스키마 사용 X
                    promotion.max_count 전부 사용하면 프로모션 사용 X
                        however, 유료티켓이 있는 경우는 유료티켓 사용
                    
                    MVP 때는 promoion.type == all  +  promoion.max_count = 999 로 모든 분양건에 대해서 무제한 푼다.
                """
                # 프로모션 사용 횟수 체크
                is_promotion_available: bool = self._is_promotion_available(
                    promotion=promotion
                )

                if not is_promotion_available:
                    # 프로모션 횟수는 전부 사용했지만 유료 티켓이 있는 경우
                    number_of_ticket: int = self._payment_repo.get_number_of_ticket(
                        user_id=dto.user_id
                    )
                    if not number_of_ticket:
                        # 티켓 수가 부족할 때
                        return UseCaseSuccessOutput(
                            value=self._make_failure_dict(
                                message="no ticket for promotion"
                            )
                        )

                    result: Optional[
                        UseCaseFailureOutput
                    ] = self._use_ticket_to_house_by_charged(dto=dto)
                    if isinstance(result, UseCaseFailureOutput):
                        return result

                else:
                    # 프로모션 횟수가 남아있는 경우
                    return self._use_ticket_to_house_by_promotion(
                        dto=dto, promotion=promotion
                    )
            elif promotion.type == PromotionTypeEnum.SOME.value:
                """
                특정 분양에 프로모션을 적용하는 경우
                    promotion_houses 스키마 사용 O
                    promotion.max_count 전부 사용하면 프로모션 사용 X
                    
                    아래의 두가지 경우가 있을 수 있음
                    1. max_count == 프로모션 상품
                    2. max_count < 프로모션 상품
                """
                # house_id 가 프로모션에 속하는지 확인
                promotion_house_id = [
                    promotion_houses.house_id
                    for promotion_houses in promotion.promotion_houses
                ]

                if dto.house_id not in promotion_house_id:
                    # 프로모션에 속하지 않은 분양건이면 유료티켓 사용
                    number_of_ticket: int = self._payment_repo.get_number_of_ticket(
                        user_id=dto.user_id
                    )
                    if not number_of_ticket:
                        # 티켓 수가 부족할 때
                        return UseCaseFailureOutput(
                            type=HTTPStatus.BAD_REQUEST,
                            message="insufficient number of tickets",
                            code=HTTPStatus.BAD_REQUEST,
                        )

                    result: Optional[
                        UseCaseFailureOutput
                    ] = self._use_ticket_to_house_by_charged(dto=dto)
                    if isinstance(result, UseCaseFailureOutput):
                        return result
                else:
                    # 프로모션에 속하는 분양건이면 프로모션 횟수 차감
                    # 프로모션 사용 횟수 체크
                    is_promotion_available: bool = self._is_promotion_available(
                        promotion=promotion
                    )

                    if not is_promotion_available:
                        # 프로모션 횟수는 전부 사용했지만 유료 티켓이 있는 경우
                        number_of_ticket: int = self._payment_repo.get_number_of_ticket(
                            user_id=dto.user_id
                        )
                        if not number_of_ticket:
                            # 티켓 수가 부족할 때
                            return UseCaseSuccessOutput(
                                value=self._make_failure_dict(
                                    message="no ticket for promotion"
                                )
                            )

                        result: Optional[
                            UseCaseFailureOutput
                        ] = self._use_ticket_to_house_by_charged(dto=dto)
                        if isinstance(result, UseCaseFailureOutput):
                            return result

                    else:
                        # 프로모션 횟수가 남아있는 경우
                        return self._use_ticket_to_house_by_promotion(
                            dto=dto, promotion=promotion
                        )
        return UseCaseSuccessOutput(value=dict(type="success", message="ticket used"))

    def _is_ticket_usage_for_house(self, user_id: int, house_id: int) -> bool:
        send_message(
            topic_name=ReportTopicEnum.IS_TICKET_USAGE_FOR_HOUSE,
            user_id=user_id,
            house_id=house_id,
        )
        return get_event_object(topic_name=ReportTopicEnum.IS_TICKET_USAGE_FOR_HOUSE)

    def _make_failure_dict(self, message: str) -> dict:
        return dict(type="failure", message=message)

    def _call_jarvis_house_analytics_api(self, dto: UseHouseTicketDto) -> int:
        data = dict(user_id=dto.user_id, house_id=dto.house_id,)
        print("----------- jarvis call start")
        response = requests.post(
            url=CallJarvisEnum.JARVIS_BASE_URL.value
            + CallJarvisEnum.CALL_PREDICT_HOUSE.value,
            headers={
                "Content-Type": "application/json",
                "Cache-Control": "no-cache",
                "Authorization": dto.auth_header,
            },
            data=json.dumps(data),
        )
        print("----------- jarvis call end")
        return response.status_code

    def _use_ticket_to_house_by_charged(
        self, dto: UseHouseTicketDto
    ) -> Optional[UseCaseFailureOutput]:
        response: int = self._call_jarvis_house_analytics_api(dto=dto)
        print("------> jarvis response : ", response)
        if response == HTTPStatus.OK:
            print("@@@@ no enter")
            # 티켓 사용 히스토리 생성 (tickets 스키마)
            create_use_ticket_dto: CreateTicketDto = self._make_create_use_ticket_dto(
                user_id=dto.user_id,
                type_=TicketTypeDivisionEnum.USED_TICKET_TO_HOUSE.value,
                amount=1,
                sign=TicketSignEnum.MINUS.value,
            )
            ticket_id: int = self._payment_repo.create_ticket(dto=create_use_ticket_dto)

            # 사용한 티켓 타겟 생성 (ticket_targets 스키마)
            self._payment_repo.create_ticket_target(dto=dto, ticket_id=ticket_id)

            # 티켓 사용 결과 ticket_id 업데이트 (ticket_usage_results 스키마)
            self._update_ticket_usage_result(
                user_id=dto.user_id, house_id=dto.house_id, ticket_id=ticket_id
            )
        else:
            # jarvis response 로 200 이외의 값을 받았을 때
            return UseCaseFailureOutput(
                type=HTTPStatus.INTERNAL_SERVER_ERROR,
                message="error on jarvis (use_ticket_to_house_by_charged)",
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
            )
        return None

    def _use_ticket_to_house_by_promotion(
        self, dto: UseHouseTicketDto, promotion: PromotionEntity
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        response: int = self._call_jarvis_house_analytics_api(dto=dto)
        if response == HTTPStatus.OK:
            # 티켓 사용 히스토리 생성 (tickets 스키마)
            create_use_ticket_dto: CreateTicketDto = self._make_create_use_ticket_dto(
                user_id=dto.user_id,
                type_=TicketTypeDivisionEnum.USED_PROMOTION_TO_HOUSE.value,
                amount=0,
                sign=TicketSignEnum.MINUS.value,
            )
            ticket_id: int = self._payment_repo.create_ticket(dto=create_use_ticket_dto)

            # 사용한 티켓 타겟 생성 (ticket_targets 스키마)
            self._payment_repo.create_ticket_target(dto=dto, ticket_id=ticket_id)

            # 티켓 사용 결과 ticket_id 업데이트 (ticket_usage_results 스키마)
            self._update_ticket_usage_result(
                user_id=dto.user_id, house_id=dto.house_id, ticket_id=ticket_id
            )

            #  프로모션 사용횟수 생성 (promotion_usage_counts 스키마)
            if promotion.promotion_usage_count:
                self._payment_repo.update_promotion_usage_count(
                    user_id=dto.user_id, promotion_id=promotion.id
                )
            else:
                self._payment_repo.create_promotion_usage_count(
                    user_id=dto.user_id, promotion_id=promotion.id
                )
        else:
            # jarvis response 로 200 이외의 값을 받았을 때
            return UseCaseFailureOutput(
                type=HTTPStatus.INTERNAL_SERVER_ERROR,
                message="error on jarvis (use_ticket_to_house_by_promotion)",
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
            )
        return UseCaseSuccessOutput(
            value=dict(type="success", message="promotion used")
        )


class UseUserTicketUseCase(PaymentBaseUseCase):
    def execute(
        self, dto: UseUserTicketDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        # 유저 설문을 완료하지 않은 경우 사용 X
        if (
            self._get_user_profile(user_id=dto.user_id).survey_step
            != UserSurveyStepEnum.STEP_COMPLETE.value
        ):
            return UseCaseFailureOutput(
                type=HTTPStatus.BAD_REQUEST,
                message="needs user surveys",
                code=HTTPStatus.BAD_REQUEST,
            )

        # 유저 분석 프로모션은 한번 구입 시 무제한 사용 가능 -> 유저 설문을 바꿔보면서 분석 가능
        if self._is_ticket_usage_for_user(user_id=dto.user_id):
            # 재분석 실행(무료)
            response: int = self._call_jarvis_user_analytics_api(dto=dto)
            if response == HTTPStatus.OK:
                return UseCaseSuccessOutput(
                    value=dict(type="success", message="ticket reused")
                )
            else:
                # jarvis response 로 200 이외의 값을 받았을 때
                return UseCaseFailureOutput(
                    type=HTTPStatus.INTERNAL_SERVER_ERROR,
                    message="error on jarvis (reuse_ticket_to_user)",
                    code=HTTPStatus.INTERNAL_SERVER_ERROR,
                )
        else:
            promotion: Optional[PromotionEntity] = self._payment_repo.get_promotion(
                user_id=dto.user_id, div=PromotionDivEnum.USER.value
            )
            if not promotion:
                # 프로모션은 없지만 유료 티켓을 사용하는 경우
                number_of_ticket: int = self._payment_repo.get_number_of_ticket(
                    user_id=dto.user_id
                )
                if not number_of_ticket:
                    # 티켓 수가 부족할 때
                    return UseCaseFailureOutput(
                        type=HTTPStatus.BAD_REQUEST,
                        message="insufficient number of tickets",
                        code=HTTPStatus.BAD_REQUEST,
                    )

                result: Optional[
                    UseCaseFailureOutput
                ] = self._use_ticket_to_user_by_charged(dto=dto)
                if isinstance(result, UseCaseFailureOutput):
                    return result
            else:
                # 적용 프로모션이 있는 경우 무조건 사용 가능
                """
                    MVP 때는 promoion.type == all  +  promoion.max_count = 1
                    1. 유저분석 프로모션은 1회 사용 시 평생 무료이므로 max_count 즉, 사용횟수는 의미가 없다. 즉, 입력되는 1은 무시해도 되는 값
                    2. 유저분석 프로모션은 1회 사용 시 평생 무료이므로 promotion_usage_counts 가 의미가 없으나 어느시점의 프로모션에서 유저가 사용을 했는지 히스토리성으로 사용하기로 한다.
                """
                return self._use_ticket_to_user_by_promotion(
                    dto=dto, promotion=promotion
                )
        return UseCaseSuccessOutput(value=dict(type="success", message="ticket used"))

    def _is_ticket_usage_for_user(self, user_id: int) -> bool:
        send_message(
            topic_name=ReportTopicEnum.IS_TICKET_USAGE_FOR_USER, user_id=user_id,
        )
        return get_event_object(topic_name=ReportTopicEnum.IS_TICKET_USAGE_FOR_USER)

    def _call_jarvis_user_analytics_api(self, dto: UseUserTicketDto) -> int:
        # todo. 유저 분석 자비스 API 만들어지면 변경 필요
        # response = requests.get(
        #     url="https://www.apartalk.com/api/jarvis/v1/predict/execute?public_sales_id=1",
        #     headers={
        #         "Content-Type": "application/json",
        #         "Cache-Control": "no-cache",
        #         "Authorization": dto.auth_header,
        #     },
        # )

        # return response.status_code
        return 500

    def _use_ticket_to_user_by_charged(
        self, dto: UseUserTicketDto
    ) -> Optional[UseCaseFailureOutput]:
        response: int = self._call_jarvis_user_analytics_api(dto=dto)
        if response == HTTPStatus.OK:
            """
            유저 분석시에는 ticket_targets 생성 X
            """
            # 티켓 사용 히스토리 생성 (tickets 스키마)
            create_use_ticket_dto: CreateTicketDto = self._make_create_use_ticket_dto(
                user_id=dto.user_id,
                type_=TicketTypeDivisionEnum.USED_TICKET_TO_USER.value,
                amount=1,
                sign=TicketSignEnum.MINUS.value,
            )
            ticket_id: int = self._payment_repo.create_ticket(dto=create_use_ticket_dto)

            # 티켓 사용 결과 ticket_id 업데이트 (ticket_usage_results 스키마)
            self._update_ticket_usage_result(
                user_id=dto.user_id, house_id=None, ticket_id=ticket_id
            )
        else:
            # jarvis response 로 200 이외의 값을 받았을 때
            return UseCaseFailureOutput(
                type=HTTPStatus.INTERNAL_SERVER_ERROR,
                message="error on jarvis (use_ticket_to_user_by_charged)",
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
            )
        return None

    def _use_ticket_to_user_by_promotion(
        self, dto: UseUserTicketDto, promotion: PromotionEntity
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        response: int = self._call_jarvis_user_analytics_api(dto=dto)
        if response == HTTPStatus.OK:
            """
            유저 분석시에는 ticket_targets 생성 X
            """
            # 티켓 사용 히스토리 생성 (tickets 스키마)
            create_use_ticket_dto: CreateTicketDto = self._make_create_use_ticket_dto(
                user_id=dto.user_id,
                type_=TicketTypeDivisionEnum.USED_PROMOTION_TO_USER.value,
                amount=0,
                sign=TicketSignEnum.MINUS.value,
            )
            ticket_id: int = self._payment_repo.create_ticket(dto=create_use_ticket_dto)

            # 티켓 사용 결과 ticket_id 업데이트 (ticket_usage_results 스키마)
            self._update_ticket_usage_result(
                user_id=dto.user_id, house_id=None, ticket_id=ticket_id
            )

            #  프로모션 사용횟수 생성 (promotion_usage_counts 스키마)
            self._payment_repo.create_promotion_usage_count(
                user_id=dto.user_id, promotion_id=promotion.id
            )
        else:
            # jarvis response 로 200 이외의 값을 받았을 때
            return UseCaseFailureOutput(
                type=HTTPStatus.INTERNAL_SERVER_ERROR,
                message="error on jarvis (use_ticket_to_user_by_promotion)",
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
            )
        return UseCaseSuccessOutput(
            value=dict(type="success", message="promotion used")
        )


class CreateRecommendCodeUseCase(PaymentBaseUseCase):
    def execute(
        self, dto: PaymentUserDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        recommend_code: RecommendCodeEntity = self._payment_repo.create_recommend_code(
            user_id=dto.user_id
        )

        # 추천 코드 생성 (code_group + code)
        full_code = str(recommend_code.code_group) + recommend_code.code

        return UseCaseSuccessOutput(value=full_code)


class GetRecommendCodeUseCase(PaymentBaseUseCase):
    def execute(
        self, dto: PaymentUserDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        recommend_code: RecommendCodeEntity = self._payment_repo.get_recommend_code_by_user_id(
            user_id=dto.user_id
        )
        if not recommend_code:
            return UseCaseFailureOutput(
                type="recommend code",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        full_code = str(recommend_code.code_group) + recommend_code.code
        return UseCaseSuccessOutput(value=full_code)


class UseRecommendCodeUseCase(PaymentBaseUseCase):
    def execute(
        self, dto: UseRecommendCodeDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        receiver_recommend_code: RecommendCodeEntity = self._payment_repo.get_recommend_code_by_user_id(
            user_id=dto.user_id
        )

        # 추천코드 입력하는 유저가 본인의 코드 정보가 없다면 recommend_codes 스키마를 생성해준다. -> recommend_codes 에서 추천코드 관리를 하기 때문에
        if not receiver_recommend_code:
            receiver_recommend_code: RecommendCodeEntity = self._payment_repo.create_recommend_code(
                user_id=dto.user_id
            )

        # 이미 추천 코드를 입력한 유저
        if receiver_recommend_code.is_used:
            return UseCaseFailureOutput(
                type="user already used code",
                message=FailureType.INVALID_REQUEST_ERROR,
                code=HTTPStatus.BAD_REQUEST,
            )

        # full_code -> code_group + code
        code_dict: dict = self._split_code_by_code_group(full_code=dto.code)

        # 본인의 코드를 입력한 유저
        if receiver_recommend_code.code == code_dict["code"]:
            return UseCaseFailureOutput(
                type="not available code",
                message=FailureType.INVALID_REQUEST_ERROR,
                code=HTTPStatus.BAD_REQUEST,
            )

        provider_recommend_code: RecommendCodeEntity = self._payment_repo.get_recommend_code_by_code(
            code=code_dict["code"], code_group=code_dict["code_group"]
        )

        # 존재하지 않는 추천 코드
        if not provider_recommend_code:
            return UseCaseFailureOutput(
                type="code does not exist",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        # 만료된 코드(사용횟수가 2회 전부 사용)
        if (
            provider_recommend_code.code_count
            >= RecommendCodeMaxCountEnum.MAX_COUNT.value
        ):
            return UseCaseFailureOutput(
                type="code already been all used",
                message=FailureType.INVALID_REQUEST_ERROR,
                code=HTTPStatus.BAD_REQUEST,
            )

        # 무료 ticket 추가, 티켓 히스토리 생성 (tickets 스키마)
        create_use_ticket_dto: CreateTicketDto = self._make_create_use_ticket_dto(
            user_id=dto.user_id,
            type_=TicketTypeDivisionEnum.SHARE_PROMOTION.value,
            amount=1,
            sign=TicketSignEnum.PLUS.value,
        )
        self._payment_repo.create_ticket(dto=create_use_ticket_dto)

        # 추천 티켓 사용 카운트 +1
        self._payment_repo.update_recommend_code_count(
            recommend_code=provider_recommend_code
        )

        # 무료 코드 사용 상태 업데이트(Receiver)
        self._payment_repo.update_recommend_code_is_used(
            recommend_code=receiver_recommend_code
        )

        return UseCaseSuccessOutput()

    def _split_code_by_code_group(self, full_code: str) -> dict:
        # todo. 잘못된 형식에 대한 return 필요함
        code_group_list = re.findall("\d", full_code)
        code_group = "".join(code_group_list)
        return dict(code=full_code.split(code_group)[1], code_group=code_group)
