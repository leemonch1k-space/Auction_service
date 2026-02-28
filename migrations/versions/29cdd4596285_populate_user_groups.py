"""populate user groups

Revision ID: 29cdd4596285
Revises: 2720a8297e11
Create Date: 2026-02-28 13:19:08.750603

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from src.enums import UserGroupEnum

# revision identifiers, used by Alembic.
revision: str = '29cdd4596285'
down_revision: Union[str, Sequence[str], None] = '2720a8297e11'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    user_groups_table = table(
        'user_groups',
        column('id', sa.Integer),
        column('name', sa.Enum(UserGroupEnum, name='usergroupenum'))
    )
    op.bulk_insert(
        user_groups_table,
        [
            {'name': UserGroupEnum.USER},
            {'name': UserGroupEnum.ADMIN},
        ]
    )


def downgrade() -> None:
    op.execute("DELETE FROM user_groups WHERE name IN ('USER', 'ADMIN')")