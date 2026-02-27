from decimal import Decimal
from typing import List, TYPE_CHECKING

from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    Enum,
    CheckConstraint,
    Numeric
)
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.database import Base
from src.enums import UserGroupEnum
from src.security import hash_password, verify_password


if TYPE_CHECKING:
    from src.database.models.auction import CollectionModel


class UserGroupModel(Base):
    """
        Table model for user's permission group.
    """
    __tablename__ = "user_groups"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[UserGroupEnum] = mapped_column(
        Enum(UserGroupEnum), nullable=False, unique=True
    )

    users: Mapped[List["UserModel"]] = relationship(
        "UserModel", back_populates="group"
    )

    def __repr__(self) -> str:
        return f"<UserGroupModel(id={self.id}, name={self.name})>"


class UserModel(Base):
    """
        Table model for user.
        As simplification i didn't do a lot for it, so it is just a simple model for user
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    login: Mapped[str] = mapped_column(
        String(30), nullable=False, unique=True, index=True
    )
    _hashed_password: Mapped[str] = mapped_column(
        "hashed_password", String(255), nullable=False
    )
    balance: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2),
        CheckConstraint("balance >= 0", name="check_balance_positive"),
        nullable=False,
        default=0.00
    )
    group_id: Mapped[int] = mapped_column(
        ForeignKey("user_groups.id", ondelete="CASCADE"), nullable=False
    )

    group: Mapped["UserGroupModel"] = relationship(
        "UserGroupModel", back_populates="users"
    )
    collection: Mapped["CollectionModel"] = relationship(
        "CollectionModel",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False
    )

    @property
    def password(self) -> None:
        raise AttributeError(
            "Password is write-only."
        )

    @password.setter
    def password(self, password: str) -> None:
        hashed_password = hash_password(password)
        self._hashed_password = hashed_password

    def check_password(self, password: str) -> bool:
        return verify_password(password, self._hashed_password)

    def has_group(self, group_name: UserGroupEnum) -> bool:
        return self.group.name == group_name

    def __repr__(self) -> str:
        return (
            f"<UserModel(id={self.id}, login={self.login}"
        )
