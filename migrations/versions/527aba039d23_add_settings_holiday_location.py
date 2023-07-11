"""Add Settings.holiday_location

Revision ID: 527aba039d23
Revises: 284a39dbc7ab
Create Date: 2023-07-11 19:57:03.091741

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '527aba039d23'
down_revision = '284a39dbc7ab'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('holiday_location', sa.String(length=255), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.drop_column('holiday_location')

    # ### end Alembic commands ###
