from http import HTTPStatus
from typing import Union

from pydantic import ValidationError

from app.http.responses import failure_response, success_response
from core.domains.notification.schema.notification_schema import (
    GetNotificationResponseSchema,
    GetBadgeResponseSchema,
    UpdateNotificationResponseSchema,
    GetReceiveNotificationSettingResponseSchema,
    UpdateReceiveNotificationSettingResponseSchema,
)
from core.domains.post.schema.post_schema import (
    GetPostListResponseSchema,
    UpdatePostReadCountResponseSchema,
)
from core.domains.user.schema.user_schema import (
    CreateUserResponseSchema,
    CreateAppAgreeTermsResponseSchema,
    UpsertUserInfoResponseSchema,
    GetUserInfoResponseSchema,
    GetUserResponseSchema,
)
from core.use_case_output import UseCaseSuccessOutput, UseCaseFailureOutput, FailureType


class GetPostListPresenter:
    def transform(self, output: Union[UseCaseSuccessOutput, UseCaseFailureOutput]):
        if isinstance(output, UseCaseSuccessOutput):
            try:
                schema = GetPostListResponseSchema(posts=output.value)
            except ValidationError as e:
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


class UpdatePostReadCountPresenter:
    def transform(self, output: Union[UseCaseSuccessOutput, UseCaseFailureOutput]):
        if isinstance(output, UseCaseSuccessOutput):
            try:
                schema = UpdatePostReadCountResponseSchema(result=output.type)
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
