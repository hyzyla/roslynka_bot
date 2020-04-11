"""Initial migration

Revision ID: b55acd292ade
Revises: 
Create Date: 2020-04-11 16:11:03.395718

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b55acd292ade'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'homes',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('date_created', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id'),
    )
    op.create_table(
        'plants',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('watering_interval', sa.Interval(), nullable=False),
        sa.Column('date_created', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id'),
    )
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('date_created', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id'),
    )
    op.create_table(
        'home_plants',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('home_id', postgresql.UUID(), nullable=False),
        sa.Column('plant_id', postgresql.UUID(), nullable=False),
        sa.Column('date_created', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(('home_id',), ['homes.id'], ),
        sa.ForeignKeyConstraint(('plant_id',), ['plants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id'),
    )
    op.create_table(
        'home_users',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('home_id', postgresql.UUID(), nullable=False),
        sa.Column('plant_id', postgresql.UUID(), nullable=False),
        sa.Column('date_created', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(('home_id',), ['homes.id'], ),
        sa.ForeignKeyConstraint(('plant_id',), ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id'),
    )
    op.create_table(
        'telegram_users',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('date_created', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(('user_id',), ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id'),
        sa.UniqueConstraint('user_id'),
    )


def downgrade():
    op.drop_table('telegram_users')
    op.drop_table('home_users')
    op.drop_table('home_plants')
    op.drop_table('users')
    op.drop_table('plants')
    op.drop_table('homes')
