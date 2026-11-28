import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.core.config import Settings
from app.domain.reference import NafMapping, load_reference_data


def _real() -> NafMapping:
    return load_reference_data(Settings(app_env="test", _env_file=None).resolved_data_dir).naf


def test_real_naf_mapping_is_valid() -> None:
    naf = _real()
    assert 15 <= len(naf.sectors) <= 25
    assert all(s.label for s in naf.sectors)


def test_naf_codes_do_not_overlap_by_accident() -> None:
    # Un même code dans deux secteurs doit être un choix conscient : on le détecte.
    seen: dict[str, str] = {}
    for sector in _real().sectors:
        for code in sector.naf:
            assert code not in seen, f"{code} is in both {seen[code]} and {sector.id}"
            seen[code] = sector.id


def test_naf_mapping_is_flagged_as_draft_until_validated() -> None:
    # Garde-fou : quand l'utilisateur aura validé le fichier, ce test sera mis à jour avec lui.
    assert "brouillon" in _real().status


@pytest.mark.parametrize(
    "bad",
    [
        {"id": "ok", "label": "x", "naf": ["6201Z"]},  # point manquant
        {"id": "ok", "label": "x", "naf": ["62.01z"]},  # minuscule
        {"id": "ok", "label": "x", "naf": []},
        {"id": "ok", "label": "x", "naf": ["62", "62"]},
        {"id": "Bad Id", "label": "x", "naf": ["62"]},
    ],
)
def test_invalid_sectors_are_rejected(bad: dict[str, object]) -> None:
    doc = {"version": "1", "status": "s", "note": "n", "sectors": [bad]}
    with pytest.raises(ValidationError):
        NafMapping.model_validate(doc)


def test_duplicate_sector_ids_are_rejected() -> None:
    sector = {"id": "dup", "label": "x", "naf": ["62"]}
    with pytest.raises(ValidationError):
        NafMapping.model_validate(
            {"version": "1", "status": "s", "note": "n", "sectors": [sector, sector]}
        )


def test_corrupted_data_file_stops_loading(tmp_path: Path) -> None:
    (tmp_path / "naf_mapping.json").write_text(json.dumps({"sectors": "oops"}))
    (tmp_path / "consent_texts.json").write_text("{}")
    with pytest.raises(ValidationError):
        load_reference_data(tmp_path)
