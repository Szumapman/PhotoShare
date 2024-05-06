"""Init

Revision ID: 548d4017c9a3
Revises: 
Create Date: 2024-05-06 12:37:33.916250

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '548d4017c9a3'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tags',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tag_name', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('tag_name')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('username', sa.String(length=255), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('confirmed', sa.Boolean(), nullable=True),
    sa.Column('role', sa.Enum('admin', 'moderator', 'standard', name='user_roles'), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('avatar', sa.String(length=255), nullable=True),
    sa.Column('refresh_token', sa.String(length=255), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_table('photos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('file_path', sa.String(length=255), nullable=False),
    sa.Column('qr_path', sa.String(length=255), nullable=False),
    sa.Column('transformation', sa.JSON(), nullable=True),
    sa.Column('description', sa.String(length=1000), nullable=False),
    sa.Column('upload_date', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('comments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('text', sa.String(length=1000), nullable=False),
    sa.Column('date_posted', sa.DateTime(), nullable=True),
    sa.Column('date_updated', sa.DateTime(), nullable=True),
    sa.Column('photo_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['photo_id'], ['photos.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('photo_tags',
    sa.Column('photo_id', sa.Integer(), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['photo_id'], ['photos.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ),
    sa.PrimaryKeyConstraint('photo_id', 'tag_id')
    )
    op.create_table('ratings',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('photo_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('score', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['photo_id'], ['photos.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('photo_id', 'user_id', name='photo_user_uc')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ratings')
    op.drop_table('photo_tags')
    op.drop_table('comments')
    op.drop_table('photos')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_table('tags')
    # ### end Alembic commands ###
