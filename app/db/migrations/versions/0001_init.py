from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = '0001_init'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'user',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.Text, nullable=False, unique=True),
        sa.Column('hashed_password', sa.Text, nullable=False),
        sa.Column('full_name', sa.Text),
        sa.Column('is_active', sa.Boolean, server_default=sa.text('true'), nullable=False),
        sa.Column('is_superuser', sa.Boolean, server_default=sa.text('false'), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
    )
    op.create_table(
        'project',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.Text, nullable=False),
        sa.Column('key', sa.Text, nullable=False, unique=True),
        sa.Column('description', sa.Text),
        sa.Column('created_by', UUID(as_uuid=True), sa.ForeignKey('user.id')),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
    )
    op.create_table(
        'membership',
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('user.id'), primary_key=True),
        sa.Column('project_id', UUID(as_uuid=True), sa.ForeignKey('project.id'), primary_key=True),
        sa.Column('role', sa.Text, nullable=False),
    )
    op.create_index('ix_membership_project_role', 'membership', ['project_id', 'role'])
    op.create_table(
        'sprint',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', UUID(as_uuid=True), sa.ForeignKey('project.id')),
        sa.Column('name', sa.Text, nullable=False),
        sa.Column('start_date', sa.Date),
        sa.Column('end_date', sa.Date),
        sa.Column('state', sa.Text, server_default=sa.text("'planned'"), nullable=False),
    )
    op.create_table(
        'task',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', UUID(as_uuid=True), sa.ForeignKey('project.id')),
        sa.Column('sprint_id', UUID(as_uuid=True), sa.ForeignKey('sprint.id'), nullable=True),
        sa.Column('parent_id', UUID(as_uuid=True), sa.ForeignKey('task.id'), nullable=True),
        sa.Column('title', sa.Text, nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('status', sa.Text, server_default=sa.text("'todo'"), nullable=False),
        sa.Column('priority', sa.Text, server_default=sa.text("'medium'"), nullable=False),
        sa.Column('assignee_id', UUID(as_uuid=True), sa.ForeignKey('user.id'), nullable=True),
        sa.Column('reporter_id', UUID(as_uuid=True), sa.ForeignKey('user.id')),
        sa.Column('estimate', sa.Integer),
        sa.Column('due_date', sa.Date),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_task_project_status_assignee', 'task', ['project_id', 'status', 'assignee_id'])
    op.create_table(
        'tasktag',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', UUID(as_uuid=True), sa.ForeignKey('project.id')),
        sa.Column('name', sa.Text, nullable=False),
    )
    op.create_index('uq_tasktag_project_name', 'tasktag', ['project_id', 'name'], unique=True)
    op.create_table(
        'tasktaglink',
        sa.Column('task_id', UUID(as_uuid=True), sa.ForeignKey('task.id'), primary_key=True),
        sa.Column('tag_id', UUID(as_uuid=True), sa.ForeignKey('tasktag.id'), primary_key=True),
    )
    op.create_table(
        'comment',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('task_id', UUID(as_uuid=True), sa.ForeignKey('task.id')),
        sa.Column('author_id', UUID(as_uuid=True), sa.ForeignKey('user.id')),
        sa.Column('body', sa.Text, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_comment_task_created', 'comment', ['task_id', 'created_at'])
    op.create_table(
        'attachment',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('task_id', UUID(as_uuid=True), sa.ForeignKey('task.id')),
        sa.Column('uploader_id', UUID(as_uuid=True), sa.ForeignKey('user.id')),
        sa.Column('filename', sa.Text),
        sa.Column('content_type', sa.Text),
        sa.Column('size', sa.BigInteger),
        sa.Column('storage_url', sa.Text),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
    )
    op.create_table(
        'activity',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('project_id', UUID(as_uuid=True), sa.ForeignKey('project.id')),
        sa.Column('actor_id', UUID(as_uuid=True), sa.ForeignKey('user.id')),
        sa.Column('entity_type', sa.Text),
        sa.Column('entity_id', sa.Text),
        sa.Column('action', sa.Text),
        sa.Column('meta', sa.JSON),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
    )


def downgrade() -> None:
    op.drop_table('activity')
    op.drop_table('attachment')
    op.drop_index('ix_comment_task_created', table_name='comment')
    op.drop_table('comment')
    op.drop_table('tasktaglink')
    op.drop_index('uq_tasktag_project_name', table_name='tasktag')
    op.drop_table('tasktag')
    op.drop_index('ix_task_project_status_assignee', table_name='task')
    op.drop_table('task')
    op.drop_table('sprint')
    op.drop_index('ix_membership_project_role', table_name='membership')
    op.drop_table('membership')
    op.drop_table('project')
    op.drop_table('user')
