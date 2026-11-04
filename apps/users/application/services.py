from apps.users.domain.entities import User
from apps.users.domain.ports import UserRepositoryPort


class AuthenticationService:
    def __init__(self, user_repository: UserRepositoryPort):
        self._user_repository = user_repository

    def authenticate(self, username: str, password: str) -> User | None:
        return self._user_repository.get_by_credentials(username, password)
