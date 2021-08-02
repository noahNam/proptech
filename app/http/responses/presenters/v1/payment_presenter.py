from http import HTTPStatus
from typing import Union

from pydantic import ValidationError
from app.http.responses import failure_response, success_response
from core.domains.payment.schema.payment_schema import (
    GetTicketUsageResultResponseSchema, UseTicketResponseSchema,
)
from core.use_case_output import UseCaseSuccessOutput, UseCaseFailureOutput, FailureType


class GetTicketUsageResultPresenter:
    def transform(self, output: Union[UseCaseSuccessOutput, UseCaseFailureOutput]):
        if isinstance(output, UseCaseSuccessOutput):
            try:
                schema = GetTicketUsageResultResponseSchema(houses=output.value)
            except ValidationError:
                return failure_response(
                    UseCaseFailureOutput(
                        type="response schema validation error",
                        message=FailureType.INTERNAL_ERROR,
                        code=HTTPStatus.INTERNAL_SERVER_ERROR,
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


class GetTicketUsageResultPresenter2:
    def transform(self, output: Union[UseCaseSuccessOutput, UseCaseFailureOutput]):
        test = 1
        if isinstance(output, UseCaseSuccessOutput):
            try:
                schema = UseTicketResponseSchema(result=output.value)
            except ValidationError:
                return failure_response(
                    UseCaseFailureOutput(
                        type="response schema validation error",
                        message=FailureType.INTERNAL_ERROR,
                        code=HTTPStatus.INTERNAL_SERVER_ERROR,
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
