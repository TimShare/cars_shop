"""Create tables cars images

Revision ID: d273afecfca9
Revises: 9bcbaeff929c
Create Date: 2025-03-12 05:47:17.166000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd273afecfca9'
down_revision: Union[str, None] = '9bcbaeff929c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cars',
    sa.Column('make', sa.String(), nullable=False),
    sa.Column('model', sa.String(), nullable=False),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('mileage', sa.Integer(), nullable=False),
    sa.Column('fuel_type', sa.String(), nullable=False),
    sa.Column('engine_capacity', sa.Float(), nullable=False),
    sa.Column('transmission', sa.String(), nullable=False),
    sa.Column('body_style', sa.String(), nullable=False),
    sa.Column('color', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('condition', sa.String(), nullable=False),
    sa.Column('vin', sa.String(), nullable=False),
    sa.Column('features', sa.String(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('vin')
    )
    op.create_table('images',
    sa.Column('car_id', sa.UUID(), nullable=False),
    sa.Column('url', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('is_main', sa.Boolean(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['car_id'], ['cars.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('images')
    op.drop_table('cars')
    # ### end Alembic commands ###
