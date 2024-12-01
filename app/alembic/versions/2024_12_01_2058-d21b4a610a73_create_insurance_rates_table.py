"""create insurance_rates table

Revision ID: d21b4a610a73
Revises: 
Create Date: 2024-12-01 20:58:13.567604

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d21b4a610a73"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "insurance_rates",
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("cargo_type", sa.String(), nullable=False),
        sa.Column("rate", sa.Float(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("date"),
    )


def downgrade() -> None:
    op.drop_table("insurance_rates")
