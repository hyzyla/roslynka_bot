"""Remove redundant tables

Revision ID: 644b929c2de6
Revises: e4291a4575cc
Create Date: 2020-04-12 09:10:10.964475

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '644b929c2de6'
down_revision = 'e4291a4575cc'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('home_users')
    op.drop_table('home_plants')
    op.create_unique_constraint(None, 'homes', ['id'])
    op.create_unique_constraint(None, 'plants', ['id'])
    op.create_unique_constraint(None, 'users', ['id'])
    op.add_column('plants', sa.Column('home_id', postgresql.UUID(), nullable=False))
    op.add_column('users', sa.Column('home_id', postgresql.UUID(), nullable=True))
    op.create_foreign_key(None, 'plants', 'homes', ['home_id'], ['id'])
    op.create_foreign_key(None, 'users', 'homes', ['home_id'], ['id'])


def downgrade():
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_column('users', 'home_id')
    op.drop_constraint(None, 'plants', type_='foreignkey')
    op.drop_constraint(None, 'plants', type_='unique')
    op.drop_column('plants', 'home_id')
    op.drop_constraint(None, 'homes', type_='unique')
    op.create_table(
        'home_plants',
        sa.Column('id', postgresql.UUID(), autoincrement=False, nullable=False),
        sa.Column('home_id', postgresql.UUID(), autoincrement=False, nullable=False),
        sa.Column('plant_id', postgresql.UUID(), autoincrement=False, nullable=False),
        sa.Column(
            'date_created',
            postgresql.TIMESTAMP(), autoincrement=False,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ('home_id',),
            ['homes.id'],
            name='home_plants_home_id_fkey',
        ),
        sa.ForeignKeyConstraint(
            ('plant_id',),
            ['plants.id'],
            name='home_plants_plant_id_fkey',
        ),
        sa.PrimaryKeyConstraint('id', name='home_plants_pkey')
    )
    op.create_table(
        'home_users',
        sa.Column('id', postgresql.UUID(), autoincrement=False, nullable=False),
        sa.Column('home_id', postgresql.UUID(), autoincrement=False, nullable=False),
        sa.Column('plant_id', postgresql.UUID(), autoincrement=False, nullable=False),
        sa.Column(
            'date_created',
            postgresql.TIMESTAMP(),
            autoincrement=False,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ('home_id',),
            ['homes.id'],
            name='home_users_home_id_fkey',
        ),
        sa.ForeignKeyConstraint(
            ('plant_id',),
            ['users.id'],
            name='home_users_plant_id_fkey',
        ),
        sa.PrimaryKeyConstraint('id', name='home_users_pkey')
    )
