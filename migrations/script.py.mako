"""Generic Alembic script template."""

revision = "${up_revision}"
down_revision = ${down_revision}
branch_labels = ${branch_labels}
depends_on = ${depends_on}

from alembic import op
import sqlalchemy as sa

def upgrade():
    pass

def downgrade():
    pass
