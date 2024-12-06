"""create insurance_action_logs table

Revision ID: 02b902253a0e
Revises: 6859e6dd236e
Create Date: 2024-12-06 03:30:41.022942

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "02b902253a0e"
down_revision: Union[str, None] = "6859e6dd236e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "insurance_action_logs",
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("date_time", sa.DateTime(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.drop_table("insurance_rates")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "insurance_rates",
        sa.Column("date", sa.DATE(), autoincrement=False, nullable=False),
        sa.Column(
            "cargo_type", sa.VARCHAR(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "rate",
            sa.DOUBLE_PRECISION(precision=53),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id", name="insurance_rates_pkey"),
        sa.UniqueConstraint("date", "cargo_type", name="uix_date_cargo_type"),
    )
    op.drop_table("insurance_action_logs")
    # ### end Alembic commands ###
