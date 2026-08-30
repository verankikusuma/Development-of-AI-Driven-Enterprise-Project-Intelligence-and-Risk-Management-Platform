"""001_initial_schema

Revision ID: 001_initial
Revises: 
Create Date: 2026-08-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('deadline', sa.DateTime(), nullable=False),
        sa.Column('budget', sa.Float(), nullable=True),
        sa.Column('current_budget_used', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True)
    )

    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('team', sa.String(length=100), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('planned_end_date', sa.DateTime(), nullable=False),
        sa.Column('actual_end_date', sa.DateTime(), nullable=True),
        sa.Column('progress_percentage', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('priority', sa.String(length=50), nullable=True),
        sa.Column('estimated_duration', sa.Integer(), nullable=True),
        sa.Column('remaining_duration', sa.Integer(), nullable=True),
        sa.Column('resource_count', sa.Integer(), nullable=True),
        sa.Column('resource_availability', sa.Float(), nullable=True),
        sa.Column('pending_tasks', sa.Integer(), nullable=True),
        sa.Column('bugs_reported', sa.Integer(), nullable=True),
        sa.Column('requirement_changes', sa.Integer(), nullable=True),
        sa.Column('delay_days', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True)
    )

    op.create_table(
        'dependencies',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_task_id', sa.Integer(), sa.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('dependent_task_id', sa.Integer(), sa.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('dependency_type', sa.String(length=50), nullable=True),
        sa.Column('dependency_strength', sa.Float(), nullable=True)
    )

    op.create_table(
        'project_metrics',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('project_progress', sa.Float(), nullable=True),
        sa.Column('pending_tasks', sa.Integer(), nullable=True),
        sa.Column('completed_tasks', sa.Integer(), nullable=True),
        sa.Column('delayed_tasks', sa.Integer(), nullable=True),
        sa.Column('budget_utilization', sa.Float(), nullable=True),
        sa.Column('resource_availability', sa.Float(), nullable=True),
        sa.Column('team_productivity', sa.Float(), nullable=True),
        sa.Column('testing_progress', sa.Float(), nullable=True),
        sa.Column('testing_failures', sa.Integer(), nullable=True),
        sa.Column('bugs', sa.Integer(), nullable=True),
        sa.Column('requirement_changes', sa.Integer(), nullable=True),
        sa.Column('technical_issues', sa.Integer(), nullable=True),
        sa.Column('security_audit_progress', sa.Float(), nullable=True),
        sa.Column('communication_failures', sa.Integer(), nullable=True),
        sa.Column('external_risk', sa.Float(), nullable=True),
        sa.Column('dependency_delay', sa.Integer(), nullable=True),
        sa.Column('schedule_variance', sa.Float(), nullable=True)
    )

    op.create_table(
        'risk_predictions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('prediction_timestamp', sa.DateTime(), nullable=True),
        sa.Column('model_version', sa.String(length=50), nullable=True),
        sa.Column('risk_probability', sa.Float(), nullable=False),
        sa.Column('risk_level', sa.String(length=50), nullable=False),
        sa.Column('feature_snapshot', sa.JSON(), nullable=True),
        sa.Column('contributing_factors', sa.JSON(), nullable=True)
    )

def downgrade() -> None:
    op.drop_table('risk_predictions')
    op.drop_table('project_metrics')
    op.drop_table('dependencies')
    op.drop_table('tasks')
    op.drop_table('projects')
