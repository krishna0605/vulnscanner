"""Initial database schema

Revision ID: 8b47e12af44c
Revises: 
Create Date: 2025-11-01 12:50:57.505920

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8b47e12af44c'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create profiles table
    op.create_table(
        'profiles',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('username', sa.String(50), unique=True, nullable=True),
        sa.Column('full_name', sa.String(100), nullable=True),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('role', sa.String(20), nullable=False, default='user'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    
    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('owner_id', sa.String(36), nullable=False),
        sa.Column('target_domain', sa.String(255), nullable=False),
        sa.Column('scope_rules', sa.JSON(), nullable=False, default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['owner_id'], ['profiles.id'], ondelete='CASCADE'),
    )
    
    # Create scan_sessions table
    op.create_table(
        'scan_sessions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, default='pending'),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('configuration', sa.JSON(), nullable=False),
        sa.Column('stats', sa.JSON(), nullable=False, default='{}'),
        sa.Column('created_by', sa.String(36), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['profiles.id']),
        sa.CheckConstraint("status IN ('pending', 'running', 'completed', 'failed', 'cancelled')", name='ck_scan_sessions_status'),
    )
    
    # Create discovered_urls table
    op.create_table(
        'discovered_urls',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('session_id', sa.String(36), nullable=False),
        sa.Column('url', sa.String(2000), nullable=False),
        sa.Column('parent_url', sa.String(2000), nullable=True),
        sa.Column('method', sa.String(10), nullable=False, default='GET'),
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('content_type', sa.String(100), nullable=True),
        sa.Column('content_length', sa.Integer(), nullable=True),
        sa.Column('response_time', sa.Integer(), nullable=True),
        sa.Column('page_title', sa.String(500), nullable=True),
        sa.Column('discovered_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['session_id'], ['scan_sessions.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('session_id', 'url', 'method', name='uq_discovered_urls_session_url_method'),
    )
    
    # Create extracted_forms table
    op.create_table(
        'extracted_forms',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('url_id', sa.String(36), nullable=False),
        sa.Column('form_action', sa.String(2000), nullable=True),
        sa.Column('form_method', sa.String(10), nullable=True),
        sa.Column('form_fields', sa.JSON(), nullable=False),
        sa.Column('csrf_tokens', sa.JSON(), nullable=False, default='[]'),
        sa.Column('authentication_required', sa.Boolean(), nullable=False, default=False),
        sa.ForeignKeyConstraint(['url_id'], ['discovered_urls.id'], ondelete='CASCADE'),
    )
    
    # Create technology_fingerprints table
    op.create_table(
        'technology_fingerprints',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('url_id', sa.String(36), nullable=False),
        sa.Column('server_software', sa.String(100), nullable=True),
        sa.Column('programming_language', sa.String(50), nullable=True),
        sa.Column('framework', sa.String(100), nullable=True),
        sa.Column('cms', sa.String(100), nullable=True),
        sa.Column('javascript_libraries', sa.JSON(), nullable=False, default='[]'),
        sa.Column('security_headers', sa.JSON(), nullable=False, default='{}'),
        sa.Column('detected_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['url_id'], ['discovered_urls.id'], ondelete='CASCADE'),
    )
    
    # Create vulnerabilities table
    op.create_table(
        'vulnerabilities',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('session_id', sa.String(36), nullable=False),
        sa.Column('url_id', sa.String(36), nullable=True),
        sa.Column('vulnerability_type', sa.String(50), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('evidence', sa.JSON(), nullable=False, default='{}'),
        sa.Column('remediation', sa.Text(), nullable=True),
        sa.Column('cwe_id', sa.String(20), nullable=True),
        sa.Column('cvss_score', sa.Float(), nullable=True),
        sa.Column('false_positive', sa.Boolean(), nullable=False, default=False),
        sa.Column('verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('discovered_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['session_id'], ['scan_sessions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['url_id'], ['discovered_urls.id'], ondelete='SET NULL'),
        sa.CheckConstraint("severity IN ('info', 'low', 'medium', 'high', 'critical')", name='ck_vulnerabilities_severity'),
    )
    
    # Create indexes for performance
    op.create_index('idx_projects_owner', 'projects', ['owner_id'])
    op.create_index('idx_scan_sessions_project', 'scan_sessions', ['project_id'])
    op.create_index('idx_scan_sessions_status', 'scan_sessions', ['status'])
    op.create_index('idx_discovered_urls_session', 'discovered_urls', ['session_id'])
    op.create_index('idx_discovered_urls_parent', 'discovered_urls', ['parent_url'])
    op.create_index('idx_extracted_forms_url', 'extracted_forms', ['url_id'])
    op.create_index('idx_tech_fingerprints_url', 'technology_fingerprints', ['url_id'])
    op.create_index('idx_vulnerabilities_session', 'vulnerabilities', ['session_id'])
    op.create_index('idx_vulnerabilities_type', 'vulnerabilities', ['vulnerability_type'])
    op.create_index('idx_vulnerabilities_severity', 'vulnerabilities', ['severity'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('idx_vulnerabilities_severity')
    op.drop_index('idx_vulnerabilities_type')
    op.drop_index('idx_vulnerabilities_session')
    op.drop_index('idx_tech_fingerprints_url')
    op.drop_index('idx_extracted_forms_url')
    op.drop_index('idx_discovered_urls_parent')
    op.drop_index('idx_discovered_urls_session')
    op.drop_index('idx_scan_sessions_status')
    op.drop_index('idx_scan_sessions_project')
    op.drop_index('idx_projects_owner')
    
    # Drop tables in reverse order (respecting foreign key constraints)
    op.drop_table('vulnerabilities')
    op.drop_table('technology_fingerprints')
    op.drop_table('extracted_forms')
    op.drop_table('discovered_urls')
    op.drop_table('scan_sessions')
    op.drop_table('projects')
    op.drop_table('profiles')
