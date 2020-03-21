"""add timestamp for sensor value

Revision ID: ce25863c6c71
Revises: 35875580996e
Create Date: 2020-03-21 07:55:25.447344

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ce25863c6c71'
down_revision = '35875580996e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sensor', sa.Column('sensor_time', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('sensor', 'sensor_time')
    # ### end Alembic commands ###
