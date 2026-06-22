from typing import Dict
from prometheus_client import Counter, Histogram

# Model Pricing in USD per 1M tokens (Standard pricing profiles)
MODEL_PRICING: Dict[str, Dict[str, float]] = {
    "gpt-4o-mini": {"input": 0.15 / 1_000_000, "output": 0.60 / 1_000_000},
    "gpt-4o": {"input": 5.00 / 1_000_000, "output": 15.00 / 1_000_000},
    "gemini-1.5-flash": {"input": 0.075 / 1_000_000, "output": 0.30 / 1_000_000},
    "claude-3-5-sonnet": {"input": 3.00 / 1_000_000, "output": 15.00 / 1_000_000},
    "default": {"input": 0.15 / 1_000_000, "output": 0.60 / 1_000_000},
}

# 1. Latency Metrics
HTTP_REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds",
    "HTTP request latency in seconds",
    ["method", "path", "status_code"],
)

LLM_LATENCY = Histogram(
    "llm_latency_seconds",
    "LLM call execution latency in seconds",
    ["model", "operation", "tenant_id"],
)

RETRIEVAL_LATENCY = Histogram(
    "retrieval_latency_seconds",
    "RAG retrieval query execution latency in seconds",
    ["tenant_id"],
)

# 2. Token & Cost Metrics
LLM_TOKEN_USAGE = Counter(
    "llm_token_usage_total",
    "Total LLM token usage",
    ["model", "type", "tenant_id"],  # type can be "input" or "output"
)

LLM_COST = Counter(
    "llm_cost_usd_total",
    "Total LLM cost in USD",
    ["model", "tenant_id"],
)

# 3. Candidate Evaluation Metrics
EVALUATION_SCORE = Histogram(
    "evaluation_score_points",
    "Candidate evaluation score points (0.0 to 5.0)",
    [
        "dimension",
        "tenant_id",
    ],  # dimensions: technical_accuracy, communication, depth, problem_solving, confidence, completeness, overall
)

HALLUCINATION_COUNT = Counter(
    "evaluation_hallucinations_total",
    "Total candidate evaluation hallucinations detected",
    ["tenant_id"],
)

FAITHFULNESS_SCORE = Histogram(
    "evaluation_faithfulness_ratio",
    "Candidate faithfulness validation score ratio (0.0 to 1.0)",
    ["tenant_id"],
)


def record_llm_metrics(
    model: str,
    tenant_id: str,
    input_tokens: int,
    output_tokens: int,
    latency_seconds: float,
    operation: str = "query",
) -> float:
    """Records LLM latency, token counts, and calculates USD cost using pricing indexes."""
    # Observe execution speed
    LLM_LATENCY.labels(model=model, operation=operation, tenant_id=tenant_id).observe(
        latency_seconds
    )

    # Track usage counters
    LLM_TOKEN_USAGE.labels(model=model, type="input", tenant_id=tenant_id).inc(
        input_tokens
    )
    LLM_TOKEN_USAGE.labels(model=model, type="output", tenant_id=tenant_id).inc(
        output_tokens
    )

    # Calculate costs
    rates = MODEL_PRICING.get(model.lower(), MODEL_PRICING["default"])
    cost = (input_tokens * rates["input"]) + (output_tokens * rates["output"])
    LLM_COST.labels(model=model, tenant_id=tenant_id).inc(cost)

    return cost


def record_evaluation_metrics(
    tenant_id: str,
    scores: Dict[str, float],
    hallucinations_count: int,
    faithfulness: float,
) -> None:
    """Records rubric assessment levels, faithfulness scores, and detected hallucination triggers."""
    # Record scores per dimension
    for dim, score in scores.items():
        EVALUATION_SCORE.labels(dimension=dim, tenant_id=tenant_id).observe(score)

    # Record hallucinations counts
    if hallucinations_count > 0:
        HALLUCINATION_COUNT.labels(tenant_id=tenant_id).inc(hallucinations_count)

    # Record faithfulness ratio
    FAITHFULNESS_SCORE.labels(tenant_id=tenant_id).observe(faithfulness)
