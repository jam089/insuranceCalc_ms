"""create insurance_rates table

Revision ID: b9e8811c69fc
Revises: 
Create Date: 2024-12-01 04:57:58.157057

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b9e8811c69fc"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "insurance_rates",
        sa.Column("data", sa.Date(), nullable=False),
        sa.Column("cargo_type", sa.String(), nullable=False),
        sa.Column("rate", sa.Float(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("insurance_rates")
