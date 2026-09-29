"""Add unique constraints to OrganizationUser and TeamMember

Revision ID: d52199e3a844
Revises: 390366244e37
Create Date: 2026-09-30 00:06:50.398288

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd52199e3a844'
down_revision: Union[str, Sequence[str], None] = '390366244e37'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint("uq_organization_user", "organization_users", ["organization_id", "user_id"])
    op.create_unique_constraint("uq_team_user", "team_members", ["team_id", "user_id"])
    op.create_unique_constraint("uq_integration_provider", "integration_connections", ["organization_id", "provider"])
    op.create_index("ix_audit_logs_org_created_at", "audit_logs", ["organization_id", "created_at"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_audit_logs_org_created_at", table_name="audit_logs")
    op.drop_constraint("uq_integration_provider", "integration_connections", type_="unique")
    op.drop_constraint("uq_team_user", "team_members", type_="unique")
    op.drop_constraint("uq_organization_user", "organization_users", type_="unique")
