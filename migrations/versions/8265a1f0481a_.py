"""empty message

Revision ID: 8265a1f0481a
Revises: a75e5cbedaad
Create Date: 2021-05-21 11:09:55.586665

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8265a1f0481a'
down_revision = 'a75e5cbedaad'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('message',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('conversation_id', sa.Integer(), nullable=False),
    sa.Column('sender_id', sa.Integer(), nullable=False),
    sa.Column('sent_at', sa.DateTime(), nullable=True),
    sa.Column('message', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['conversation_id'], ['conversation.id'], ),
    sa.ForeignKeyConstraint(['sender_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('message')
    # ### end Alembic commands ###
