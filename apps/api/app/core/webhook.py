"""Vérification de la signature des webhooks Clerk (schéma Svix / « Standard Webhooks »).

Pourquoi : n'importe qui peut envoyer une requête POST à notre URL de webhook. Sans
signature, un inconnu pourrait supprimer le compte de n'importe quel étudiant.
Clerk signe « {id}.{timestamp}.{corps} » avec HMAC-SHA256 et un secret partagé.
On écrit la vérification nous-mêmes (≈ 20 lignes) plutôt que d'ajouter une dépendance.
"""

import base64
import binascii
import hashlib
import hmac

TOLERANCE_SECONDS = 300  # refuse les messages trop vieux : limite le rejeu d'un message capturé


def _decode_secret(secret: str) -> bytes:
    raw = secret.removeprefix("whsec_")
    try:
        return base64.b64decode(raw, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("Invalid webhook secret format") from exc


def sign(secret: str, msg_id: str, timestamp: str, body: bytes) -> str:
    key = _decode_secret(secret)
    signed = f"{msg_id}.{timestamp}.".encode() + body
    return base64.b64encode(hmac.new(key, signed, hashlib.sha256).digest()).decode()


def verify_signature(
    secret: str,
    msg_id: str,
    timestamp: str,
    signature_header: str,
    body: bytes,
    now_epoch: float,
) -> bool:
    try:
        ts = int(timestamp)
    except ValueError:
        return False
    if abs(now_epoch - ts) > TOLERANCE_SECONDS:
        return False
    expected = sign(secret, msg_id, timestamp, body)
    # L'en-tête peut contenir plusieurs signatures (« v1,xxx v1,yyy ») pendant une rotation.
    for part in signature_header.split():
        version, _, value = part.partition(",")
        # compare_digest : comparaison en temps constant (évite les attaques par chronométrage).
        if version == "v1" and hmac.compare_digest(value, expected):
            return True
    return False
