"""empty message

Revision ID: 57ed8e7c989f
Revises: 5981b5d68f85
Create Date: 2018-08-11 08:19:46.337088

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '57ed8e7c989f'
down_revision = '5981b5d68f85'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('web_authn_credential_public_key_key', 'web_authn_credential', type_='unique')
    op.drop_column('web_authn_credential', 'public_key')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('web_authn_credential', sa.Column('public_key', sa.VARCHAR(length=65), autoincrement=False, nullable=True))
    op.create_unique_constraint('web_authn_credential_public_key_key', 'web_authn_credential', ['public_key'])
    # ### end Alembic commands ###