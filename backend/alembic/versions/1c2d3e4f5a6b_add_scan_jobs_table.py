"""add scan_jobs table

Revision ID: 1c2d3e4f5a6b
Revises: 8b47e12af44c
Create Date: 2025-11-08 12:00:00
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1c2d3e4f5a6b'
down_revision = '8b47e12af44c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum type for status
    scan_job_status = sa.Enum('queued', 'running', 'done', 'failed', name='scan_job_status')
    scan_job_status.create(op.get_bind(), checkfirst=True)

    # Create table
    op.create_table(
        'scan_jobs',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('url', sa.String(length=2000), nullable=False),
        sa.Column('status', scan_job_status, nullable=False, server_default='queued'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    # Index on url
    op.create_index('ix_scan_jobs_url', 'scan_jobs', ['url'], unique=False)


def downgrade() -> None:
    # Drop index then table
    op.drop_index('ix_scan_jobs_url', table_name='scan_jobs')
    op.drop_table('scan_jobs')

    # Drop enum type
    scan_job_status = sa.Enum('queued', 'running', 'done', 'failed', name='scan_job_status')
    scan_job_status.drop(op.get_bind(), checkfirst=True)