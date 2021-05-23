"""empty message

Revision ID: 520f9f05e787
Revises: 59a21ced4ab2
Create Date: 2021-05-20 18:02:22.622933

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '520f9f05e787'
down_revision = '59a21ced4ab2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('conversation',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('creator_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['creator_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('conversation')
    # ### end Alembic commands ###