"""initial SupplyMind schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-08-24
"""
from alembic import op
import sqlalchemy as sa
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None
def upgrade():
    op.create_table("users", sa.Column("id", sa.Integer, primary_key=True), sa.Column("email", sa.String(255), unique=True, nullable=False), sa.Column("hashed_password", sa.String(255), nullable=False), sa.Column("role", sa.String(30), nullable=False))
    op.create_table("vendors", sa.Column("id", sa.Integer, primary_key=True), sa.Column("name", sa.String(200), nullable=False), sa.Column("region", sa.String(80), nullable=False), sa.Column("reliability_score", sa.Float, nullable=False), sa.Column("contract_terms", sa.Text, nullable=False))
    op.create_table("shipments", sa.Column("id", sa.Integer, primary_key=True), sa.Column("po_number", sa.String(80), unique=True, nullable=False), sa.Column("vendor_id", sa.Integer, sa.ForeignKey("vendors.id"), nullable=False), sa.Column("status", sa.String(40), nullable=False), sa.Column("eta", sa.DateTime, nullable=False), sa.Column("actual_delivery", sa.DateTime), sa.Column("origin", sa.String(120), nullable=False), sa.Column("destination", sa.String(120), nullable=False))
    op.create_table("inventory", sa.Column("id", sa.Integer, primary_key=True), sa.Column("sku", sa.String(80), nullable=False), sa.Column("warehouse_id", sa.String(80), nullable=False), sa.Column("quantity", sa.Integer, nullable=False), sa.Column("reorder_point", sa.Integer, nullable=False))
    op.create_table("incidents", sa.Column("id", sa.Integer, primary_key=True), sa.Column("shipment_id", sa.Integer, sa.ForeignKey("shipments.id")), sa.Column("type", sa.String(80), nullable=False), sa.Column("description", sa.Text, nullable=False), sa.Column("resolution", sa.Text, nullable=False), sa.Column("embedding", sa.JSON, nullable=False))
    op.create_table("agent_runs", sa.Column("id", sa.Integer, primary_key=True), sa.Column("scenario", sa.String(200), nullable=False), sa.Column("steps", sa.JSON, nullable=False), sa.Column("status", sa.String(40), nullable=False), sa.Column("created_at", sa.DateTime, server_default=sa.func.now()))
    op.create_table("approvals", sa.Column("id", sa.Integer, primary_key=True), sa.Column("agent_run_id", sa.Integer, sa.ForeignKey("agent_runs.id"), nullable=False), sa.Column("proposed_action", sa.JSON, nullable=False), sa.Column("risk_score", sa.Float, nullable=False), sa.Column("status", sa.String(30), nullable=False), sa.Column("approved_by", sa.String(255)))
def downgrade():
    for name in ("approvals", "agent_runs", "incidents", "inventory", "shipments", "vendors", "users"): op.drop_table(name)
