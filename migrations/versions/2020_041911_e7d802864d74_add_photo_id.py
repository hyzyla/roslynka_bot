"""Add photo_id

Revision ID: e7d802864d74
Revises: 644b929c2de6
Create Date: 2020-04-19 11:04:31.617599

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e7d802864d74'
down_revision = '644b929c2de6'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('plants', sa.Column('photo_id', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('plants', 'photo_id')
