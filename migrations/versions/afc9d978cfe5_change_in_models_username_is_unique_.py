"""Change in models, username is unique, photos add qr_path and transformation, and longer description, comment longer text, tags tag_name unique

Revision ID: afc9d978cfe5
Revises: 47585adda035
Create Date: 2024-05-01 18:04:16.505441

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'afc9d978cfe5'
down_revision: Union[str, None] = '47585adda035'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('comments', 'text',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=1000),
               existing_nullable=False)
    op.add_column('photos', sa.Column('qr_path', sa.String(length=255), nullable=False))
    op.add_column('photos', sa.Column('transformation', sa.JSON(), nullable=True))
    op.alter_column('photos', 'description',
               existing_type=sa.VARCHAR(length=500),
               type_=sa.String(length=1000),
               existing_nullable=False)
    op.create_unique_constraint(None, 'tags', ['tag_name'])
    op.create_unique_constraint(None, 'users', ['username'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_constraint(None, 'tags', type_='unique')
    op.alter_column('photos', 'description',
               existing_type=sa.String(length=1000),
               type_=sa.VARCHAR(length=500),
               existing_nullable=False)
    op.drop_column('photos', 'transformation')
    op.drop_column('photos', 'qr_path')
    op.alter_column('comments', 'text',
               existing_type=sa.String(length=1000),
               type_=sa.VARCHAR(length=255),
               existing_nullable=False)
    # ### end Alembic commands ###