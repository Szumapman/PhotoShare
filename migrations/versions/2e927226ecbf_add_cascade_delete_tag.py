"""add cascade delete tag

Revision ID: 2e927226ecbf
Revises: d3464fc9dc89
Create Date: 2024-05-05 23:18:00.173224

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2e927226ecbf'
down_revision: Union[str, None] = 'd3464fc9dc89'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###