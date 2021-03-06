"""Migration commit

Revision ID: 57e781bc92f9
Revises: 
Create Date: 2021-07-13 20:01:37.590229

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '57e781bc92f9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('roles',
    sa.Column('idRole', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.PrimaryKeyConstraint('idRole')
    )
    op.create_table('users',
    sa.Column('jmbg', sa.String(length=13), nullable=False),
    sa.Column('forename', sa.String(length=256), nullable=False),
    sa.Column('surname', sa.String(length=256), nullable=False),
    sa.Column('email', sa.String(length=256), nullable=False),
    sa.Column('password', sa.String(length=256), nullable=False),
    sa.Column('idRole', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['idRole'], ['roles.idRole'], ),
    sa.PrimaryKeyConstraint('jmbg'),
    sa.UniqueConstraint('email')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    op.drop_table('roles')
    # ### end Alembic commands ###
