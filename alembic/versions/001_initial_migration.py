"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2025-01-01 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create animal_locations table
    op.create_table(
        'animal_locations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('animal_id', sa.String(), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_animal_id', 'animal_locations', ['animal_id'], unique=False)
    op.create_index('idx_timestamp', 'animal_locations', ['timestamp'], unique=False)
    op.create_index(op.f('ix_animal_locations_id'), 'animal_locations', ['id'], unique=False)
    op.create_index(op.f('ix_animal_locations_animal_id'), 'animal_locations', ['animal_id'], unique=False)
    op.create_index(op.f('ix_animal_locations_timestamp'), 'animal_locations', ['timestamp'], unique=False)
    
    # Create geofence_boundaries table
    op.create_table(
        'geofence_boundaries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('boundary_points', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_geofence_boundaries_id'), 'geofence_boundaries', ['id'], unique=False)
    
    # Create alerts table
    op.create_table(
        'alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('animal_id', sa.String(), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('alert_type', sa.String(), nullable=False),
        sa.Column('message', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_alerts_id'), 'alerts', ['id'], unique=False)
    op.create_index(op.f('ix_alerts_animal_id'), 'alerts', ['animal_id'], unique=False)
    op.create_index(op.f('ix_alerts_timestamp'), 'alerts', ['timestamp'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_alerts_timestamp'), table_name='alerts')
    op.drop_index(op.f('ix_alerts_animal_id'), table_name='alerts')
    op.drop_index(op.f('ix_alerts_id'), table_name='alerts')
    op.drop_table('alerts')
    
    op.drop_index(op.f('ix_geofence_boundaries_id'), table_name='geofence_boundaries')
    op.drop_table('geofence_boundaries')
    
    op.drop_index(op.f('ix_animal_locations_timestamp'), table_name='animal_locations')
    op.drop_index(op.f('ix_animal_locations_animal_id'), table_name='animal_locations')
    op.drop_index(op.f('ix_animal_locations_id'), table_name='animal_locations')
    op.drop_index('idx_timestamp', table_name='animal_locations')
    op.drop_index('idx_animal_id', table_name='animal_locations')
    op.drop_table('animal_locations')

