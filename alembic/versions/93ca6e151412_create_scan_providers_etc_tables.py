"""create scan, providers, etc tables

Revision ID: 93ca6e151412
Revises: 6b6393c8233a
Create Date: 2023-06-20 14:19:36.683431
"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '93ca6e151412'
down_revision = '6b6393c8233a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the scan, scan_profiles, scan_results, and providers tables"""
    op.create_table(
        'scan_results',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('scan_id', sa.INTEGER(), nullable=True),
        sa.Column('result', sa.VARCHAR(), nullable=True),
        sa.Column('created_at', sa.DATETIME(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.ForeignKeyConstraint(
            ['scan_id'],
            ['scans.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_scan_results_id', 'scan_results', ['id'], unique=False)

    op.create_table(
        'providers',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('name', sa.VARCHAR(), nullable=True),
        sa.Column('user_id', sa.INTEGER(), nullable=True),
        sa.Column('provider_type', sa.VARCHAR(), nullable=True),
        sa.Column('app_id', sa.VARCHAR(), nullable=True),
        sa.Column('bearer_token', sa.VARCHAR(), nullable=True),
        sa.Column('environment', sa.VARCHAR(), nullable=True),
        sa.Column('api_token', sa.VARCHAR(), nullable=True),
        sa.Column('index_name', sa.VARCHAR(), nullable=True),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['users.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_providers_id', 'providers', ['id'], unique=False)

    op.create_table(
        'configurations',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('name', sa.VARCHAR(), nullable=True),
        sa.Column('app_id', sa.VARCHAR(), nullable=True),
        sa.Column('bearer_token', sa.VARCHAR(), nullable=True),
        sa.Column('environment', sa.VARCHAR(), nullable=True),
        sa.Column('api_token', sa.VARCHAR(), nullable=True),
        sa.Column('index_name', sa.VARCHAR(), nullable=True),
        sa.Column('provider_id', sa.INTEGER(), nullable=True),
        sa.ForeignKeyConstraint(
            ['provider_id'],
            ['providers.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_configurations_id', 'configurations', ['id'], unique=False)

    op.create_table(
        'scans',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('name', sa.VARCHAR(), nullable=True),
        sa.Column('prompts', sa.VARCHAR(), nullable=True),
        sa.Column('flags', sa.VARCHAR(), nullable=True),
        sa.Column('severity', sa.INTEGER(), nullable=True),
        sa.Column('profile_id', sa.INTEGER(), nullable=True),
        sa.ForeignKeyConstraint(
            ['profile_id'],
            ['scan_profiles.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_scans_id', 'scans', ['id'], unique=False)

    op.create_table(
        'scan_profiles',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('name', sa.VARCHAR(), nullable=True),
        sa.Column('created_at', sa.DATETIME(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('user_id', sa.INTEGER(), nullable=True),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['users.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_scan_profiles_id', 'scan_profiles', ['id'], unique=False)


def downgrade() -> None:
    """Drop the scan, scan_profiles, scan_results, and providers tables"""
    op.drop_index('ix_scan_profiles_id', table_name='scan_profiles')
    op.drop_table('scan_profiles')
    op.drop_index('ix_scans_id', table_name='scans')
    op.drop_table('scans')
    op.drop_index('ix_providers_id', table_name='providers')
    op.drop_table('providers')
    op.drop_index('ix_scan_results_id', table_name='scan_results')
    op.drop_table('scan_results')
