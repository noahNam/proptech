from typing import Union

from pydantic import ValidationError

from app.http.responses import failure_response, success_response
from core.domains.user.schema.user_schema import CreateUserResponseSchema
from core.use_case_output import UseCaseSuccessOutput, UseCaseFailureOutput, FailureType


class UserPresenter:
    def transform(self, output: Union[UseCaseSuccessOutput, UseCaseFailureOutput]):
        if isinstance(output, UseCaseSuccessOutput):
            value = output.value
            try:
                schema = CreateUserResponseSchema(nickname=value)
            except ValidationError as e:
                print(e)
                return failure_response(
                    UseCaseFailureOutput(
                        type=FailureType.SYSTEM_ERROR,
                        message="response schema validation error",
                    )
                )
            result = {
                "data": {"user": schema.dict()},
                "meta": output.meta,
            }
            return success_response(result=result)
        elif isinstance(output, UseCaseFailureOutput):
            return failure_response(output=output)
