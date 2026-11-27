# 06 — Interfaces (ports) et contrats

> Squelettes indicatifs en Python (Protocols + modèles Pydantic). Claude Code les affine à l'implémentation, mais **garde les principes** : chaque interface est remplaçable, retourne des objets validés, et expose provenance + statut. Les adaptateurs vivent dans `apps/api/app/adapters/<fournisseur>/`.

## Types communs

```python
from enum import Enum
from datetime import datetime
from pydantic import BaseModel

class Origin(str, Enum):
    published = "published"
    inferred = "inferred"
    provider = "provider"

class Provenance(BaseModel):
    source: str            # ex: "sirene", "firecrawl:careers_page", "hunter"
    source_url: str | None = None
    fetched_at: datetime
    origin: Origin | None = None

class StepStatus(str, Enum):
    found = "found"
    not_found = "not_found"      # honnête : pas d'invention
    failed = "failed"            # erreur fournisseur (déclenche le disjoncteur)
    skipped = "skipped"          # budget/quota/exclusion
```

## CvParser (partie 3)
```python
class CvProfile(BaseModel):
    skills: list[str]
    languages: list[dict]          # {"lang": "fr", "level": "C2"}
    certifications: list[str]
    education: list[dict]          # texte résumé validé par l'étudiant
    experiences: list[dict]
    # AUCUN champ identifiant (nom, email, téléphone, adresse, photo, date de naissance)

class CvParser(Protocol):
    def parse(self, pdf_bytes: bytes) -> "CvParseResult": ...   # en mémoire ; jamais de stockage

class CvParseResult(BaseModel):
    profile_draft: CvProfile       # à valider par l'étudiant
    evidence: dict[str, str]       # compétence -> extrait de texte qui l'a déclenchée
    warnings: list[str]            # ex: PDF scanné refusé, texte vide
```

## Anonymizer (partie 4)
```python
class AnonymizeResult(BaseModel):
    text: str                      # texte masqué
    removed_sections: list[str]
    detections: dict[str, int]     # type -> nombre (pas les valeurs)

class Anonymizer(Protocol):
    def anonymize(self, text: str) -> AnonymizeResult: ...
```

## LLMClient (partie 5, 10)
```python
class LLMClient(Protocol):
    def structured(self, *, system: str, user: str, schema: type[BaseModel],
                   purpose: str) -> BaseModel: ...
    # Contraintes : sortie validée par `schema` ; jamais d'appel sans consentement/porte ouverte ;
    # journaliser modèle, version, durée, coût — PAS le contenu.
```

## Matcher (parties 7 et 10)
```python
class MatchResult(BaseModel):
    score: float
    breakdown: dict[str, float]    # contribution de chaque critère
    explanation: str               # en français, lisible par l'étudiant
    cited_evidence: list[str] = [] # éléments du texte source (pour le jugement LLM)

class Matcher(Protocol):
    def score(self, profile: CvProfile, prefs: "Preferences", company: "CompanyCard") -> MatchResult: ...
# RulesMatcher : fonction pure, reproductible. LlmMatcher : optionnel, reçoit UNIQUEMENT profil structuré + texte public.
```

## CompanyDiscovery (partie 6)
```python
class CompanyCard(BaseModel):
    siren: str
    name: str
    naf: str
    city: str | None
    postcode: str | None
    headcount_band: str | None
    diffusion_status: str          # respecter la diffusion partielle
    provenance: Provenance

class CompanyDiscovery(Protocol):
    def search(self, prefs: "Preferences", page: int, per_page: int) -> list[CompanyCard]: ...
# Exclure les entreprises individuelles ; gérer limites de débit et retries.
```

## WebsiteFinder / PageFetcher (partie 9)
```python
class WebsiteResult(BaseModel):
    status: StepStatus
    url: str | None
    phone: str | None
    provenance: Provenance | None

class WebsiteFinder(Protocol):
    def find(self, company: CompanyCard) -> WebsiteResult: ...

class PageResult(BaseModel):
    status: StepStatus
    markdown: str | None
    url: str
    provenance: Provenance | None

class PageFetcher(Protocol):
    def fetch(self, url: str) -> PageResult: ...    # respecte robots.txt, domaines exclus
```

## ContactFinder (partie 11)
```python
class ContactCandidate(BaseModel):
    name: str | None
    title: str | None
    generic: bool                  # contact@, rh@ ... préféré si suffisant
    email: str | None
    provenance: Provenance         # origin: published | inferred | provider

class ContactFinder(Protocol):
    def find(self, company: CompanyCard, website: str | None) -> list[ContactCandidate]: ...
# Cascade configurable : arrêt au premier résultat fiable ; vérifier la liste de suppression avant.
```

## EmailVerifier (partie 11)
```python
class EmailVerdict(str, Enum):
    valid = "valid"
    invalid = "invalid"
    catch_all = "catch_all"        # JAMAIS présenté comme « vérifié »
    unknown = "unknown"

class VerifyResult(BaseModel):
    verdict: EmailVerdict
    provider: str | None
    checked_at: datetime

class EmailVerifier(Protocol):
    def verify(self, address: str) -> VerifyResult: ...
# Étapes internes gratuites d'abord (syntaxe, MX), cache par adresse, puis fournisseur.
```

## Disjoncteur (circuit breaker) — commun aux adaptateurs
États `closed → open → half_open` ; ouverture après N échecs consécutifs ou taux d'échec > seuil sur une fenêtre ; réessai en `half_open` après un délai ; état persisté dans `provider_usage` ; alerte (event `run_events` niveau `error`). Les seuils sont dans `admin_config`.

## Tests des adaptateurs
Un fichier de **fixtures** de réponses réelles (anonymisées/synthétiques) par fournisseur ; aucun appel réseau dans les tests unitaires ; tests de contrat communs à tous les adaptateurs d'une même interface.
