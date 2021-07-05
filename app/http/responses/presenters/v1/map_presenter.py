from http import HTTPStatus
from typing import Union

from pydantic import ValidationError

from app.extensions.utils.log_helper import logger_
from app.http.responses import failure_response, success_response
from core.domains.map.schema.map_schema import BoundingResponseSchema
from core.use_case_output import UseCaseSuccessOutput, UseCaseFailureOutput, FailureType

logger = logger_.getLogger(__name__)


class BoundingPresenter:
    def transform(self, output: Union[UseCaseSuccessOutput, UseCaseFailureOutput]):
        if isinstance(output, UseCaseSuccessOutput):
            value = output.value
            value_to_json = value.get_json()
            try:
                schema = BoundingResponseSchema(result=value_to_json())
            except ValidationError as e:
                logger.error(f"[BoundingPresenter][transform] value : {value} error : {e}")
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
