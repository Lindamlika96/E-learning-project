"""add admin_logs

Revision ID: afe5a0407987
Revises: ada533620f7d
Create Date: 2025-10-24 15:41:15.609915
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'afe5a0407987'
down_revision = 'ada533620f7d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if "admin_logs" not in inspector.get_table_names():
        op.create_table(
            'admin_logs',
            sa.Column('id', sa.Integer(), primary_key=True, index=True),
            sa.Column('admin_id', sa.Integer(), sa.ForeignKey('users.id')),
            sa.Column('action', sa.String()),
            sa.Column('target_user_id', sa.Integer(), nullable=True),
            sa.Column('timestamp', sa.DateTime(), nullable=False),
            sa.Column('details', sa.String(), nullable=True)
        )
    else:
        print("✅ Table 'admin_logs' déjà existante, migration ignorée.")



def downgrade() -> None:
    op.drop_table('admin_logs')
