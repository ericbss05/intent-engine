"""Consentements : journal en ajout seulement (`consents`) + état courant.

Le journal est la source de vérité (preuve : qui a accepté quoi, quand, quelle version du
texte). `user_profile.ai_assist_consent` n'en est qu'une copie pratique, gardée synchronisée.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.domain.models import Consent, utcnow
from app.domain.reference import ConsentTexts
from app.domain.schemas import ConsentKind, ConsentState
from app.services import user_data

KINDS: tuple[ConsentKind, ...] = ("privacy_notice", "ai_assist")


def latest_consent(db: Session, user_id: str, kind: str) -> Consent | None:
    return db.scalars(
        select(Consent)
        .where(Consent.user_id == user_id, Consent.kind == kind)
        .order_by(Consent.id.desc())
        .limit(1)
    ).first()


def consent_states(db: Session, user_id: str, texts: ConsentTexts) -> list[ConsentState]:
    states = []
    for kind in KINDS:
        row = latest_consent(db, user_id, kind)
        states.append(
            ConsentState(
                kind=kind,
                granted=bool(row and row.granted),
                version_text=row.version_text if row else None,
                recorded_at=row.created_at if row else None,
                current_version=texts.for_kind(kind).version,
            )
        )
    return states


def change_consent(
    db: Session,
    user_id: str,
    kind: ConsentKind,
    granted: bool,
    version_text: str,
    texts: ConsentTexts,
) -> None:
    """Enregistre un accord ou un retrait. Idempotent : pas de ligne si rien ne change."""
    if version_text != texts.for_kind(kind).version:
        # L'étudiant a vu une ancienne version du texte : son accord ne vaudrait rien.
        raise ApiError(409, "consent_text_outdated", "The text has changed, please reload")
    if kind == "privacy_notice" and not granted:
        raise ApiError(422, "validation_error", "The information notice can only be acknowledged")

    current = latest_consent(db, user_id, kind)
    if current is not None and current.granted == granted and current.version_text == version_text:
        return
    if current is None and not granted:
        # Refus initial : rien à journaliser (l'état par défaut est déjà « non »).
        return

    user_data.record_consent(db, user_id, kind, granted, version_text)
    if kind == "ai_assist":
        profile = user_data.ensure_profile(db, user_id)
        profile.ai_assist_consent = granted
        profile.ai_assist_consent_at = utcnow()
