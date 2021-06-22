from dataclasses import dataclass


@dataclass
class UserEntity:
    id: int = None
    nickname: str = None
    status: str = None
    sex: str = None
