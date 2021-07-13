from http import HTTPStatus
from typing import Union, List
from app.extensions.utils.log_helper import logger_
from core.domains.house.entity.house_entity import BoundingRealEstateEntity
from core.domains.house.schema.house_schema import BoundingResponseSchema
from pydantic import ValidationError
from app.http.responses import failure_response, success_response
from core.domains.notification.schema.notification_schema import UpdateNotificationResponseSchema
from core.use_case_output import UseCaseSuccessOutput, UseCaseFailureOutput, FailureType

logger = logger_.getLogger(__name__)


class UpsertInterestHousePresenter:
    def transform(self, output: Union[UseCaseSuccessOutput, UseCaseFailureOutput]):
        if isinstance(output, UseCaseSuccessOutput):
            try:
                schema = UpdateNotificationResponseSchema(result=output.type)
            except ValidationError as e:
                return failure_response(
                    UseCaseFailureOutput(
                        type="response schema validation error",
                        message=FailureType.INTERNAL_ERROR,
                        code=HTTPStatus.INTERNAL_SERVER_ERROR
                    ),
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                )
            result = {
                "data": schema.dict(),
                "meta": output.meta,
            }
            return success_response(result=result)
        elif isinstance(output, UseCaseFailureOutput):
            return failure_response(output=output, status_code=output.code)


class BoundingPresenter:
    def transform(self, output: Union[UseCaseSuccessOutput, UseCaseFailureOutput]):
        if isinstance(output, UseCaseSuccessOutput):
            value_list: List[BoundingRealEstateEntity] = output.value
            try:
                schema = BoundingResponseSchema(houses=value_list)
            except ValidationError as e:
                logger.error(f"[BoundingPresenter][transform] value : {value_list} error : {e}")
                return failure_response(
                    UseCaseFailureOutput(
                        type="response schema validation error",
                        message=FailureType.INTERNAL_ERROR,
                        code=HTTPStatus.INTERNAL_SERVER_ERROR
                    ),
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                )
            result = {
                "data": schema.dict(),
                "meta": output.meta,
            }
            return success_response(result=result)
        elif isinstance(output, UseCaseFailureOutput):
            return failure_response(output=output, status_code=output.code)
