"""empty message

Revision ID: 7c8f936cc64b
Revises: a9547cec52e6
Create Date: 2023-05-28 14:51:14.675743

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7c8f936cc64b'
down_revision = 'a9547cec52e6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('profile',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('date_of_birth', sa.Date(), nullable=True),
    sa.Column('photography', sa.String(), nullable=True),
    sa.Column('city_of_birth', sa.String(length=150), nullable=True),
    sa.Column('city_of_residence', sa.String(length=150), nullable=True),
    sa.Column('family_status', sa.String(length=150), nullable=True),
    sa.Column('additional_information', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('profile')
    # ### end Alembic commands ###