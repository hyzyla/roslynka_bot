"""Add plant_watering table

Revision ID: bf6159e2c233
Revises: e7d802864d74
Create Date: 2020-04-20 09:08:52.267631

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'bf6159e2c233'
down_revision = 'e7d802864d74'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'plant_watering',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('plant_id', postgresql.UUID(), nullable=False),
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.ForeignKeyConstraint(('plant_id',), ['plants.id'], ),
        sa.ForeignKeyConstraint(('user_id',), ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )


def downgrade():
    op.drop_table('plant_watering')
