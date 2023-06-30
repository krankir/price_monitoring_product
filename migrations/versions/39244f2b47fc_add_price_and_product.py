"""Add Price and Product

Revision ID: 39244f2b47fc
Revises: 
Create Date: 2023-06-27 20:58:38.720024

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '39244f2b47fc'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('products',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('url', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('rating', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('url')
    )
    op.create_table('prices',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('price', sa.Numeric(), nullable=False),
    sa.Column('price_at', sa.TIMESTAMP(), nullable=True),
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('prices')
    op.drop_table('products')
    # ### end Alembic commands ###
