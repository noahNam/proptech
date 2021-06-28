import json

from pydantic import BaseModel


class SenderDto(BaseModel):
    msg_type: str = None
    msg: dict = None
    msg_created_at: str = None

    def to_dict(self):
        return self.dict()

    def to_json(self) -> str:
        return json.dumps(self.to_dict())
