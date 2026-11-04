from apps.users.domain.entities import User
from apps.users.domain.ports import UserRepositoryPort
from apps.users.models import UserModel


class DjangoUserRepository(UserRepositoryPort):
    def get_by_credentials(self, username: str, password: str) -> User | None:
        row = UserModel.objects.filter(username=username).first()
        if row is None or not row.check_password(password):
            return None
        return User(id=row.id, username=row.username, role=row.role)
