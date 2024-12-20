"""empty message

Revision ID: 53bc57d34ac5
Revises: 50aeea48d3b6
Create Date: 2024-12-10 17:09:27.400334

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '53bc57d34ac5'
down_revision = '50aeea48d3b6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Card', schema=None) as batch_op:
        batch_op.add_column(sa.Column('card_update_time', sa.Date(), nullable=True))

    with op.batch_alter_table('Card_Version', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cv_update_time', sa.Date(), nullable=True))
        batch_op.drop_column('card_update_time')

    with op.batch_alter_table('SS', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ss_update_time', sa.Date(), nullable=True))

    with op.batch_alter_table('SS_Version', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ssv_update_time', sa.Date(), nullable=True))
        batch_op.drop_column('ss_update_time')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('SS_Version', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ss_update_time', sa.DATE(), autoincrement=False, nullable=True))
        batch_op.drop_column('ssv_update_time')

    with op.batch_alter_table('SS', schema=None) as batch_op:
        batch_op.drop_column('ss_update_time')

    with op.batch_alter_table('Card_Version', schema=None) as batch_op:
        batch_op.add_column(sa.Column('card_update_time', sa.DATE(), autoincrement=False, nullable=True))
        batch_op.drop_column('cv_update_time')

    with op.batch_alter_table('Card', schema=None) as batch_op:
        batch_op.drop_column('card_update_time')

    # ### end Alembic commands ###
