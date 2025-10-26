from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = 'ada533620f7d'
down_revision: Union[str, Sequence[str], None] = '9461f6e4e85b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.alter_column(
            "permissions",
            existing_type=sa.String(),
            nullable=True
        )

def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.alter_column(
            "permissions",
            existing_type=sa.String(),
            nullable=False
        )
