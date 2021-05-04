import inject

from core.domains.user.repository.user_repository import UserRepository


class UserBaseUseCase:
    @inject.autoparams()
    def __init__(self, user_repo: UserRepository):
        self.__user_repo = user_repo
