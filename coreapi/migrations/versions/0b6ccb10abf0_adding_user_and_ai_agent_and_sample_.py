"""Adding User and Ai_Agent and Sample_Voice and Sample_Dialog Table

Revision ID: 0b6ccb10abf0
Revises: 
Create Date: 2023-05-25 11:03:01.046590

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0b6ccb10abf0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), sa.Identity(always=False, start=1, cycle=True), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('email', sa.String(length=100), nullable=True),
    sa.Column('line_id', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('pinecone_index', sa.String(length=255), nullable=True),
    sa.Column('access_token', sa.String(length=1000), nullable=True),
    sa.Column('refresh_token', sa.String(length=255), nullable=True),
    sa.Column('user_name', sa.String(length=255), nullable=True),
    sa.Column('rich_menu_id', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_table('ai_agents',
    sa.Column('id', sa.Integer(), sa.Identity(always=False, start=1, cycle=True), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('introduction', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('pdf_file', sa.String(length=255), nullable=True),
    sa.Column('icon_file', sa.String(length=255), nullable=True),
    sa.Column('voice_model_file', sa.String(length=255), nullable=True),
    sa.Column('pinecone_namespace', sa.String(length=255), nullable=True),
    sa.Column('age', sa.Integer(), nullable=True),
    sa.Column('first_person_pronoun', sa.String(length=255), nullable=True),
    sa.Column('second_person_pronoun', sa.String(length=255), nullable=True),
    sa.Column('activity', sa.String(length=255), nullable=True),
    sa.Column('hobbies', sa.String(length=255), nullable=True),
    sa.Column('occupation', sa.String(length=255), nullable=True),
    sa.Column('speaking_style', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_agents_id'), 'ai_agents', ['id'], unique=False)
    op.create_table('sample_dialogs',
    sa.Column('id', sa.Integer(), sa.Identity(always=False, start=1, cycle=True), nullable=False),
    sa.Column('agent_id', sa.Integer(), nullable=True),
    sa.Column('content', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['agent_id'], ['ai_agents.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sample_dialogs_id'), 'sample_dialogs', ['id'], unique=False)
    op.create_table('sample_voices',
    sa.Column('id', sa.Integer(), sa.Identity(always=False, start=1, cycle=True), nullable=False),
    sa.Column('agent_id', sa.Integer(), nullable=True),
    sa.Column('file', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['agent_id'], ['ai_agents.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sample_voices_id'), 'sample_voices', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_sample_voices_id'), table_name='sample_voices')
    op.drop_table('sample_voices')
    op.drop_index(op.f('ix_sample_dialogs_id'), table_name='sample_dialogs')
    op.drop_table('sample_dialogs')
    op.drop_index(op.f('ix_ai_agents_id'), table_name='ai_agents')
    op.drop_table('ai_agents')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###
