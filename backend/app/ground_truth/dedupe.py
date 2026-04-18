import re
from urllib.parse import urlparse, urlunparse

from app.schemas.ground_truth import ExternalPaperId, PaperAuthor, PaperCandidate


def normalize_title(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", " ", value.lower())
    return " ".join(normalized.split())


def normalize_author_name(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", " ", value.lower())
    return " ".join(normalized.split())


def _normalize_url(value: str) -> str:
    parsed = urlparse(value)
    return urlunparse(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path.rstrip("/"),
            "",
            "",
            "",
        )
    )


def _arxiv_id(value: str) -> str:
    value = value.strip().lower().removeprefix("arxiv:").rstrip("/")
    value = value.rsplit("/", 1)[-1]
    return re.sub(r"v\d+$", "", value)


def _external_id_keys(external_ids: list[ExternalPaperId]) -> list[str]:
    keys: list[str] = []
    for external_id in external_ids:
        provider = external_id.provider.lower()
        value = external_id.value.strip()
        if not value:
            continue
        if provider == "doi":
            keys.append(f"doi:{value.lower().removeprefix('https://doi.org/')}")
        elif provider == "arxiv":
            keys.append(f"arxiv:{_arxiv_id(value)}")
        elif provider == "openalex":
            keys.append(f"openalex:{value}")
        elif provider in {"semantic_scholar", "semanticscholar", "paperid"}:
            keys.append(f"semantic_scholar:{value}")
    return keys


def candidate_merge_keys(candidate: PaperCandidate) -> list[str]:
    keys = _external_id_keys(candidate.external_ids)
    for url in (candidate.source_url, candidate.landing_page_url, candidate.pdf_url):
        if url:
            keys.append(f"url:{_normalize_url(url)}")

    if not keys:
        title = normalize_title(candidate.title)
        authors = ":".join(normalize_author_name(author.name) for author in candidate.authors[:3])
        if title and authors:
            keys.append(f"title_authors:{title}:{authors}")

    return list(dict.fromkeys(keys))


def _merge_external_ids(left: list[ExternalPaperId], right: list[ExternalPaperId]) -> list[ExternalPaperId]:
    merged: dict[tuple[str, str], ExternalPaperId] = {
        (item.provider.lower(), item.value.lower()): item for item in left
    }
    for item in right:
        merged.setdefault((item.provider.lower(), item.value.lower()), item)
    return list(merged.values())


def _merge_authors(left: list[PaperAuthor], right: list[PaperAuthor]) -> list[PaperAuthor]:
    merged: dict[str, PaperAuthor] = {normalize_author_name(author.name): author for author in left}
    for author in right:
        key = normalize_author_name(author.name)
        if key in merged:
            merged[key].external_ids = _merge_external_ids(merged[key].external_ids, author.external_ids)
        else:
            merged[key] = author
    return list(merged.values())


def _confidence(value: float | None) -> float:
    return value if value is not None else 0.0


def _merge_into(target: PaperCandidate, candidate: PaperCandidate) -> None:
    if _confidence(candidate.confidence) > _confidence(target.confidence):
        for field_name in ("title", "abstract", "source_url", "pdf_url", "landing_page_url", "confidence"):
            value = getattr(candidate, field_name)
            if value:
                setattr(target, field_name, value)
        target.kind = candidate.kind

    target.external_ids = _merge_external_ids(target.external_ids, candidate.external_ids)
    target.authors = _merge_authors(target.authors, candidate.authors)
    target.discovery_paths.extend(candidate.discovery_paths)
    if not target.pdf_url:
        target.pdf_url = candidate.pdf_url
    if not target.landing_page_url:
        target.landing_page_url = candidate.landing_page_url
    if not target.source_url:
        target.source_url = candidate.source_url

    raw = target.raw_provider_data.setdefault("merged_candidates", [])
    raw.append(candidate.model_dump(mode="json"))
    target.raw_provider_data["merge_keys"] = candidate_merge_keys(target)


def merge_candidates(candidates: list[PaperCandidate]) -> list[PaperCandidate]:
    merged: list[PaperCandidate] = []
    key_to_candidate: dict[str, PaperCandidate] = {}

    for candidate in candidates:
        keys = candidate_merge_keys(candidate)
        match = next((key_to_candidate[key] for key in keys if key in key_to_candidate), None)
        if match is None:
            candidate.raw_provider_data.setdefault("merge_keys", keys)
            merged.append(candidate)
            for key in keys:
                key_to_candidate[key] = candidate
            continue

        _merge_into(match, candidate)
        for key in candidate_merge_keys(match):
            key_to_candidate[key] = match

    return merged
