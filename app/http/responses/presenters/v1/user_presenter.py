from http import HTTPStatus
from typing import Union

from pydantic import ValidationError

from app.http.responses import failure_response, success_response
from core.domains.user.schema.user_schema import CreateUserResponseSchema, CreateAppAgreeTermsResponseSchema, \
    UpsertUserInfoResponseSchema, GetUserInfoResponseSchema
from core.use_case_output import UseCaseSuccessOutput, UseCaseFailureOutput, FailureType


class CreateUserPresenter:
    def transform(self, output: Union[UseCaseSuccessOutput, UseCaseFailureOutput]):
        if isinstance(output, UseCaseSuccessOutput):
            try:
                schema = CreateUserResponseSchema(result=output.type)
            except ValidationError as e:
                print(e)
                return failure_response(
                    UseCaseFailureOutput(
                        type="response schema validation error",
                        message=FailureType.INTERNAL_ERROR,
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


class CreateAppAgreeTermsPresenter:
    def transform(self, output: Union[UseCaseSuccessOutput, UseCaseFailureOutput]):
        if isinstance(output, UseCaseSuccessOutput):
            try:
                schema = CreateAppAgreeTermsResponseSchema(result=output.type)
            except ValidationError as e:
                print(e)
                return failure_response(
                    UseCaseFailureOutput(
                        type="response schema validation error",
                        message=FailureType.INTERNAL_ERROR,
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


class UpsertUserInfoPresenter:
    def transform(self, output: Union[UseCaseSuccessOutput, UseCaseFailureOutput]):
        if isinstance(output, UseCaseSuccessOutput):
            try:
                schema = UpsertUserInfoResponseSchema(result=output.type)
            except ValidationError as e:
                print(e)
                return failure_response(
                    UseCaseFailureOutput(
                        type="response schema validation error",
                        message=FailureType.INTERNAL_ERROR,
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


class GetUserInfoPresenter:
    def transform(self, output: Union[UseCaseSuccessOutput, UseCaseFailureOutput]):
        if isinstance(output, UseCaseSuccessOutput):
            try:
                schema = GetUserInfoResponseSchema(result=output.value)
            except ValidationError as e:
                print(e)
                return failure_response(
                    UseCaseFailureOutput(
                        type="response schema validation error",
                        message=FailureType.INTERNAL_ERROR,
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