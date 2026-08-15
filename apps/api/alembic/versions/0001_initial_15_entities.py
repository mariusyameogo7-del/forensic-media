"""Initial 15 entities migration

Revision ID: 0001_initial_15_entities
Revises: 
Create Date: 2026-08-15 19:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001_initial_15_entities"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("supabase_user_id", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("account_type", sa.String(50), nullable=False, server_default="standard"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_supabase_user_id", "users", ["supabase_user_id"], unique=True)
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # 2. user_preferences
    op.create_table(
        "user_preferences",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("retain_analysis_history", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("retain_original_files", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_user_preferences_user_id", "user_preferences", ["user_id"], unique=True)

    # 3. analyses
    op.create_table(
        "analyses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("public_id", sa.String(32), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("file_size", sa.BigInteger(), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("phash", sa.String(64), nullable=True),
        sa.Column("claim", sa.Text(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("conclusion_level", sa.String(50), nullable=True),
        sa.Column("provenance_status", sa.String(50), nullable=True),
        sa.Column("integrity_status", sa.String(50), nullable=True),
        sa.Column("ai_status", sa.String(50), nullable=True),
        sa.Column("context_status", sa.String(50), nullable=True),
        sa.Column("error_code", sa.String(100), nullable=True),
        sa.Column("public_error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_analyses_public_id", "analyses", ["public_id"], unique=True)
    op.create_index("ix_analyses_user_id", "analyses", ["user_id"])
    op.create_index("ix_analyses_sha256", "analyses", ["sha256"])
    op.create_index("ix_analyses_phash", "analyses", ["phash"])
    op.create_index("ix_analyses_status", "analyses", ["status"])
    op.create_index("idx_analyses_user_created", "analyses", ["user_id", sa.text("created_at DESC")])

    # 4. analysis_access_tokens
    op.create_table(
        "analysis_access_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("analysis_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_analysis_access_tokens_analysis_id", "analysis_access_tokens", ["analysis_id"])
    op.create_index("ix_analysis_access_tokens_token_hash", "analysis_access_tokens", ["token_hash"], unique=True)

    # 5. stored_objects
    op.create_table(
        "stored_objects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("analysis_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("object_type", sa.String(50), nullable=False),
        sa.Column("bucket_name", sa.String(100), nullable=False),
        sa.Column("storage_path", sa.String(500), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("file_size", sa.BigInteger(), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_stored_objects_analysis_id", "stored_objects", ["analysis_id"])
    op.create_index("idx_stored_objects_analysis_type", "stored_objects", ["analysis_id", "object_type"])

    # 6. analysis_engine_runs (exact 15 columns from Section 17)
    op.create_table(
        "analysis_engine_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("analysis_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("engine_code", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("attempt_no", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("provider", sa.String(100), nullable=False),
        sa.Column("engine_version", sa.String(50), nullable=True),
        sa.Column("provider_version", sa.String(50), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("error_code", sa.String(100), nullable=True),
        sa.Column("public_error_message", sa.Text(), nullable=True),
        sa.Column("private_error_details", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_analysis_engine_runs_analysis_id", "analysis_engine_runs", ["analysis_id"])
    op.create_index("ix_analysis_engine_runs_status", "analysis_engine_runs", ["status"])
    op.create_index("idx_engine_runs_analysis_engine", "analysis_engine_runs", ["analysis_id", "engine_code"])

    # 7. c2pa_results
    op.create_table(
        "c2pa_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("analysis_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("engine_run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analysis_engine_runs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("has_manifest", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_valid", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("signature_status", sa.String(50), nullable=False, server_default="unknown"),
        sa.Column("claim_generator", sa.String(255), nullable=True),
        sa.Column("issuer", sa.String(255), nullable=True),
        sa.Column("digital_source_type", sa.String(255), nullable=True),
        sa.Column("ai_declared", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("actions", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("manifest_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_c2pa_results_analysis_id", "c2pa_results", ["analysis_id"], unique=True)

    # 8. metadata_results
    op.create_table(
        "metadata_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("analysis_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("engine_run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analysis_engine_runs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("make", sa.String(100), nullable=True),
        sa.Column("model", sa.String(100), nullable=True),
        sa.Column("software", sa.String(150), nullable=True),
        sa.Column("original_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("modify_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("has_gps", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("gps_latitude", sa.Float(), nullable=True),
        sa.Column("gps_longitude", sa.Float(), nullable=True),
        sa.Column("image_width", sa.Integer(), nullable=True),
        sa.Column("image_height", sa.Integer(), nullable=True),
        sa.Column("color_space", sa.String(50), nullable=True),
        sa.Column("raw_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_metadata_results_analysis_id", "metadata_results", ["analysis_id"], unique=True)

    # 9. ai_results
    op.create_table(
        "ai_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("analysis_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("engine_run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analysis_engine_runs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("provider", sa.String(100), nullable=False),
        sa.Column("model_version", sa.String(50), nullable=True),
        sa.Column("raw_score", sa.Float(), nullable=True),
        sa.Column("category", sa.String(50), nullable=False, server_default="indeterminate"),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_ai_results_analysis_id", "ai_results", ["analysis_id"], unique=True)

    # 10. web_matches
    op.create_table(
        "web_matches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("analysis_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("engine_run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analysis_engine_runs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("domain", sa.String(255), nullable=True),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("match_type", sa.String(50), nullable=False, server_default="similar"),
        sa.Column("match_score", sa.Float(), nullable=True),
        sa.Column("earliest_date_found", sa.DateTime(timezone=True), nullable=True),
        sa.Column("raw_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_web_matches_analysis_id", "web_matches", ["analysis_id"])

    # 11. fact_check_matches
    op.create_table(
        "fact_check_matches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("analysis_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("engine_run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analysis_engine_runs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("publisher_name", sa.String(255), nullable=False),
        sa.Column("publisher_site", sa.String(255), nullable=True),
        sa.Column("claim_reviewed", sa.Text(), nullable=False),
        sa.Column("rating", sa.String(100), nullable=False),
        sa.Column("review_url", sa.Text(), nullable=False),
        sa.Column("review_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("language", sa.String(20), nullable=True),
        sa.Column("raw_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_fact_check_matches_analysis_id", "fact_check_matches", ["analysis_id"])

    # 12. synthesis_results
    op.create_table(
        "synthesis_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("analysis_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("conclusion_level", sa.String(50), nullable=False),
        sa.Column("provenance_status", sa.String(50), nullable=False),
        sa.Column("integrity_status", sa.String(50), nullable=False),
        sa.Column("ai_status", sa.String(50), nullable=False),
        sa.Column("context_status", sa.String(50), nullable=False),
        sa.Column("summary_fr", sa.Text(), nullable=False),
        sa.Column("synthesis_version", sa.String(50), nullable=False, server_default="1.0.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_synthesis_results_analysis_id", "synthesis_results", ["analysis_id"], unique=True)

    # 13. synthesis_evidence
    op.create_table(
        "synthesis_evidence",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("synthesis_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("synthesis_results.id", ondelete="CASCADE"), nullable=False),
        sa.Column("analysis_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("evidence_type", sa.String(50), nullable=False),
        sa.Column("title_fr", sa.String(255), nullable=False),
        sa.Column("description_fr", sa.Text(), nullable=False),
        sa.Column("source_engine", sa.String(50), nullable=False),
        sa.Column("severity", sa.String(50), nullable=False, server_default="info"),
        sa.Column("reference_id", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_synthesis_evidence_synthesis_id", "synthesis_evidence", ["synthesis_id"])
    op.create_index("ix_synthesis_evidence_analysis_id", "synthesis_evidence", ["analysis_id"])
    op.create_index("idx_synthesis_evidence_type", "synthesis_evidence", ["analysis_id", "evidence_type"])

    # 14. analysis_reports
    op.create_table(
        "analysis_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("analysis_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("report_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("template_version", sa.String(50), nullable=False, server_default="1.0.0"),
        sa.Column("snapshot_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("pdf_stored_object_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("stored_objects.id", ondelete="SET NULL"), nullable=True),
        sa.Column("pdf_sha256", sa.String(64), nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_analysis_reports_analysis_id", "analysis_reports", ["analysis_id"])
    op.create_index("idx_analysis_reports_version", "analysis_reports", ["analysis_id", "report_version"])

    # 15. analysis_events
    op.create_table(
        "analysis_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("analysis_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("message", sa.String(255), nullable=False),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_analysis_events_analysis_id", "analysis_events", ["analysis_id"])
    op.create_index("ix_analysis_events_event_type", "analysis_events", ["event_type"])
    op.create_index("idx_analysis_events_created", "analysis_events", ["analysis_id", "created_at"])


def downgrade() -> None:
    op.drop_table("analysis_events")
    op.drop_table("analysis_reports")
    op.drop_table("synthesis_evidence")
    op.drop_table("synthesis_results")
    op.drop_table("fact_check_matches")
    op.drop_table("web_matches")
    op.drop_table("ai_results")
    op.drop_table("metadata_results")
    op.drop_table("c2pa_results")
    op.drop_table("analysis_engine_runs")
    op.drop_table("stored_objects")
    op.drop_table("analysis_access_tokens")
    op.drop_table("analyses")
    op.drop_table("user_preferences")
    op.drop_table("users")
