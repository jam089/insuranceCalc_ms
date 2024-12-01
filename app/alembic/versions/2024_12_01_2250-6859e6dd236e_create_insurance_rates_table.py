"""create insurance_rates table

Revision ID: 6859e6dd236e
Revises: 
Create Date: 2024-12-01 22:50:51.647681

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6859e6dd236e"
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
        sa.UniqueConstraint("date", "cargo_type", name="uix_date_cargo_type"),
    )


def downgrade() -> None:
    op.drop_table("insurance_rates")
