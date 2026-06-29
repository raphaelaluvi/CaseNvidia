from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from src.extraction import extract_startup_profile, save_extraction_result
from src.models import Recommendation, ScrapeRun, StartupClassification
from src.rag.api import answer_query
from src.scraping.relevancia import calcular_score_relevancia_ia
from src.scraping.search_and_fetch import DATA_RAW_DIR, coletar_startup
from src.storage import InMemoryStructuredRepository, StructuredRepository

from .state import PipelineState


def _log(state: PipelineState, message: str) -> list[str]:
    return [*(state.get("logs") or []), message]


def _error(state: PipelineState, message: str) -> dict:
    return {
        "errors": [*(state.get("errors") or []), message],
        "logs": _log(state, f"erro: {message}"),
    }


def _pick_target_startup(state: PipelineState) -> str | None:
    if state.get("target_startup"):
        return state["target_startup"]
    candidates = state.get("candidate_startups") or []
    return candidates[0] if candidates else None


def planner_node(state: PipelineState) -> dict:
    query = (state.get("query") or "").strip()
    target = state.get("target_startup")
    candidates = list(state.get("candidate_startups") or [])

    if not target and query:
        if not candidates:
            candidates.append(query)
        target = candidates[0]

    return {
        "target_startup": target,
        "candidate_startups": candidates,
        "logs": _log(state, f"planner definiu startup alvo: {target or 'nenhuma'}"),
    }


def scraper_node(state: PipelineState) -> dict:
    startup_name = _pick_target_startup(state)
    if not startup_name:
        return _error(state, "Nenhuma startup alvo disponivel para scraping.")

    existing_documents = state.get("raw_documents") or []
    if existing_documents:
        discovered_urls = [doc.get("url") for doc in existing_documents if doc.get("url")]
        scrape_run = ScrapeRun(
            query=state.get("query") or startup_name,
            startup_name=startup_name,
            status="reused_input_documents",
            urls_requested=discovered_urls,
            documents_collected=len(existing_documents),
            finished_at=datetime.now(timezone.utc).isoformat(),
            metadata={"source": "state.raw_documents"},
        )
        return {
            "discovered_urls": discovered_urls,
            "raw_documents": existing_documents,
            "scrape_run": scrape_run,
            "logs": _log(state, f"scraper reutilizou {len(existing_documents)} documentos pre-carregados"),
        }

    documents = coletar_startup(startup_name)
    discovered_urls = [doc.get("url") for doc in documents if doc.get("url")]
    artifact_dir = str(DATA_RAW_DIR / startup_name.strip().lower().replace(" ", "_").replace("/", "-"))
    scrape_run = ScrapeRun(
        query=state.get("query") or startup_name,
        startup_name=startup_name,
        status="completed",
        urls_requested=discovered_urls,
        documents_collected=len(documents),
        raw_artifact_dir=artifact_dir if Path(artifact_dir).exists() else None,
        finished_at=datetime.now(timezone.utc).isoformat(),
    )

    return {
        "discovered_urls": discovered_urls,
        "raw_documents": documents,
        "scrape_run": scrape_run,
        "logs": _log(state, f"scraper coletou {len(documents)} documentos para {startup_name}"),
    }


def extractor_node(state: PipelineState) -> dict:
    startup_name = _pick_target_startup(state)
    documents = state.get("raw_documents") or []
    if not startup_name:
        return _error(state, "Extractor sem startup alvo.")

    result = extract_startup_profile(startup_name, documents)
    paths = save_extraction_result(result)
    startup = result.startup
    startup.metadata["artifact_paths"] = paths
    evidences = result.evidences

    return {
        "structured_startup": startup,
        "validated_evidences": evidences,
        "logs": _log(
            state,
            f"extractor estruturou startup e {len(evidences)} evidencias em {paths['startup_path']}",
        ),
    }


def classifier_node(state: PipelineState) -> dict:
    startup = state.get("structured_startup")
    evidences = state.get("validated_evidences") or []
    if startup is None:
        return _error(state, "Classifier sem startup estruturada.")

    base_text = "\n\n".join(filter(None, [startup.short_description] + [e.excerpt for e in evidences]))
    relevance = calcular_score_relevancia_ia(base_text)
    classification = StartupClassification(
        label="ai_native_candidate" if relevance["vale_aprofundar"] else "uncertain",
        score=float(relevance["score"]),
        rationale="Classificacao inicial heuristica baseada em termos e evidencias coletadas.",
        signals=[
            *relevance["termos_fortes_encontrados"],
            *relevance["termos_medios_encontrados"],
        ],
    )

    startup.classification = classification
    startup.ai_native_score = float(relevance["score"])
    for evidence in evidences:
        evidence.is_validated = evidence.is_validated and not bool(evidence.error)
        evidence.relevance_score = float(relevance["score"])

    return {
        "structured_startup": startup,
        "initial_classification": classification,
        "validated_evidences": evidences,
        "logs": _log(state, f"classifier marcou startup como {classification.label}"),
    }


def rag_node(state: PipelineState) -> dict:
    startup = state.get("structured_startup")
    query = state.get("query") or (startup.name if startup else "")
    if not query:
        return _error(state, "RAG sem query disponivel.")

    try:
        rag_context = answer_query(query)
        logs = _log(state, "rag recuperou contexto em Chroma")
    except Exception as exc:
        rag_context = (
            "Contexto RAG indisponivel nesta execucao. "
            "TODO: validar embeddings/colecao Chroma/credenciais do reranker."
        )
        logs = _log(state, f"rag fallback acionado: {exc}")
    return {
        "rag_context": rag_context,
        "logs": logs,
    }


def recommendation_node(
    state: PipelineState,
    repository: StructuredRepository | None = None,
) -> dict:
    repository = repository or InMemoryStructuredRepository()
    startup = state.get("structured_startup")
    classification = state.get("initial_classification")
    rag_context = state.get("rag_context") or ""
    evidences = state.get("validated_evidences") or []

    if startup is None:
        return _error(state, "Recommendation sem startup estruturada.")

    recommendation = Recommendation(
        startup_name=startup.name,
        summary=(
            f"{startup.name} apresenta sinais iniciais de aderencia ao ecossistema NVIDIA."
            if classification and classification.label == "ai_native_candidate"
            else f"{startup.name} ainda precisa de validacao adicional antes de uma recomendacao forte."
        ),
        rationale=(
            "Versao inicial baseada em heuristica + contexto RAG. "
            "TODO: substituir por agente de recomendacao com grounding e citacoes."
        ),
        matched_products=[],
        matched_context_snippets=[rag_context[:500]] if rag_context else [],
        confidence=classification.score if classification and classification.score is not None else None,
        next_steps=[
            "Validar evidencias corporativas primarias da startup.",
            "Substituir classificacao heuristica por julgamento via LLM com citacoes.",
        ],
    )

    repository.save_startup(startup)
    repository.save_evidences(evidences)
    if state.get("scrape_run"):
        repository.save_scrape_run(state["scrape_run"])
    repository.save_recommendations([recommendation])

    return {
        "recommendations": [recommendation],
        "logs": _log(state, "recommendation gerou recomendacao inicial e persistiu camada estruturada"),
    }


def briefing_node(state: PipelineState) -> dict:
    startup = state.get("structured_startup")
    classification = state.get("initial_classification")
    recommendations = state.get("recommendations") or []
    evidences = state.get("validated_evidences") or []

    if startup is None:
        return _error(state, "Briefing sem startup estruturada.")

    recommendation_summary = recommendations[0].summary if recommendations else "Sem recomendacao gerada."
    briefing = (
        f"Startup analisada: {startup.name}\n"
        f"Classificacao inicial: {classification.label if classification else 'unknown'}\n"
        f"Evidencias validadas: {sum(1 for item in evidences if item.is_validated)}/{len(evidences)}\n"
        f"Resumo: {recommendation_summary}"
    )
    return {
        "final_briefing": briefing,
        "logs": _log(state, "briefing consolidou saida final do fluxo"),
    }
