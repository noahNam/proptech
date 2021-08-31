from http import HTTPStatus
from typing import Union

from pydantic import ValidationError

from app.http.responses import failure_response, success_response
from core.domains.user.schema.user_schema import (
    CreateUserResponseSchema,
    CreateAppAgreeTermsResponseSchema,
    UpsertUserInfoResponseSchema,
    GetUserInfoResponseSchema,
    GetUserResponseSchema,
    PatchUserOutResponseSchema,
    GetUserMainResponseSchema,
    GetSurveysResponseSchema,
    GetUserProfileResponseSchema,
    UpdateUserProfileResponseSchema,
)
from core.use_case_output import UseCaseSuccessOutput, UseCaseFailureOutput, FailureType


class GetUserPresenter:
    def transform(self, output: Union[UseCaseSuccessOutput, UseCaseFailureOutput]):
        if isinstance(output, UseCaseSuccessOutput):
            user = output.value
            try:
                if user:
                    schema = GetUserResponseSchema(user=output.value)
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
                "data": schema.dict() if user else dict(user=None),
                "meta": output.meta,
            }
            return success_response(result=result)
        elif isinstance(output, UseCaseFailureOutput):
            return failure_response(output=output, status_code=output.code)


class CreateUserPresenter:
    def transform(self, output: Union[UseCaseSuccessOutput, UseCaseFailureOutput]):
        if isinstance(output, UseCaseSuccessOutput):
            try:
                schema = CreateUserResponseSchema(result=output.type)
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


class CreateAppAgreeTermsPresenter:
    def transform(self, output: Union[UseCaseSuccessOutput, UseCaseFailureOutput]):
        if isinstance(output, UseCaseSuccessOutput):
            try:
                schema = CreateAppAgreeTermsResponseSchema(result=output.type)
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


class UpsertUserInfoPresenter:
    def transform(self, output: Union[UseCaseSuccessOutput, UseCaseFailureOutput]):
        if isinstance(output, UseCaseSuccessOutput):
            try:
                schema = UpsertUserInfoResponseSchema(result=output.type)
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


class GetUserInfoPresenter:
    def transform(self, output: Union[UseCaseSuccessOutput, UseCaseFailureOutput]):
        if isinstance(output, UseCaseSuccessOutput):
            try:
                schema = GetUserInfoResponseSchema(surveys=output.value)
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


class PatchUserOutPresenter:
    def transform(self, output: Union[UseCaseSuccessOutput, UseCaseFailureOutput]):
        if isinstance(output, UseCaseSuccessOutput):
            try:
                schema = PatchUserOutResponseSchema(result=output.type)
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


class GetUserMainPresenter:
    def transform(self, output: Union[UseCaseSuccessOutput, UseCaseFailureOutput]):
        if isinstance(output, UseCaseSuccessOutput):
            try:
                schema = GetUserMainResponseSchema(result=output.value)
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


class GetSurveysPresenter:
    def transform(self, output: Union[UseCaseSuccessOutput, UseCaseFailureOutput]):
        if isinstance(output, UseCaseSuccessOutput):
            try:
                schema = GetSurveysResponseSchema(user_infos=output.value)
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


class GetUserProfilePresenter:
    def transform(self, output: Union[UseCaseSuccessOutput, UseCaseFailureOutput]):
        if isinstance(output, UseCaseSuccessOutput):
            try:
                schema = GetUserProfileResponseSchema(user=output.value)
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


class UpdateUserProfilePresenter:
    def transform(self, output: Union[UseCaseSuccessOutput, UseCaseFailureOutput]):
        if isinstance(output, UseCaseSuccessOutput):
            try:
                schema = UpdateUserProfileResponseSchema(result=output.type)
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
