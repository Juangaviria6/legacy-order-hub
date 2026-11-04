import abc

from apps.users.domain.entities import User


class UserRepositoryPort(abc.ABC):
    @abc.abstractmethod
    def get_by_credentials(self, username: str, password: str) -> User | None: ...
