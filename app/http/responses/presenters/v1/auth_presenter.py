from http import HTTPStatus
from typing import Union

from pydantic import ValidationError

from app.http.responses import failure_response, success_response
from core.domains.authentication.schema.authentication import (
    AuthenticationResponseSchema,
)
from core.use_case_output import UseCaseSuccessOutput, FailureType, UseCaseFailureOutput


class AuthenticationPresenter:
    def transform(
        self, response: UseCaseSuccessOutput,
    ):
        try:
            schema = AuthenticationResponseSchema(result=response.type)
        except ValidationError as e:
            print(e)
            return failure_response(
                UseCaseFailureOutput(
                    type=FailureType.SYSTEM_ERROR,
                    message="response schema validation error",
                )
            )
        result = {
            "data": schema.dict(),
            "meta": response.meta,
        }
        return success_response(result=result)


class AuthSmsSendPresenter:
    def transform(self, output: Union[UseCaseSuccessOutput, UseCaseFailureOutput]):
        if isinstance(output, UseCaseSuccessOutput):
            try:
                schema = AuthenticationResponseSchema(result=output.type)
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


class AuthSmsConfirmPresenter:
    def transform(self, output: Union[UseCaseSuccessOutput, UseCaseFailureOutput]):
        if isinstance(output, UseCaseSuccessOutput):
            try:
                schema = AuthenticationResponseSchema(result=output.value)
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
