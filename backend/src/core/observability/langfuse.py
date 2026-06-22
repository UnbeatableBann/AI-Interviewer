import os
from typing import Dict, Any, Optional
from langfuse import Langfuse
from src.core.observability.logging import get_logger

logger = get_logger("src.core.observability.langfuse")


class LangfuseLogger:
    """Wrapper encapsulating Langfuse tracing integration with mock/dry-run fallbacks."""

    def __init__(self) -> None:
        self.public_key = os.environ.get("LANGFUSE_PUBLIC_KEY")
        self.secret_key = os.environ.get("LANGFUSE_SECRET_KEY")
        self.host = os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com")

        # Enable only if key properties are present
        self.enabled = bool(self.public_key and self.secret_key)
        self.client: Optional[Langfuse] = None

        if self.enabled:
            try:
                self.client = Langfuse(
                    public_key=self.public_key,
                    secret_key=self.secret_key,
                    host=self.host,
                )
                logger.info("Langfuse SDK client initialized successfully.")
            except Exception as e:
                logger.warning("Failed to initialize Langfuse client: %s", e)
                self.enabled = False

    def trace_generation(
        self,
        name: str,
        prompt: str,
        completion: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        latency_seconds: float,
        tenant_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """Traces an LLM generation call, recording prompts, outputs, token usage, and cost indicators."""
        if not self.enabled or not self.client:
            return None

        try:
            meta = metadata or {}
            meta["tenant_id"] = tenant_id

            trace_obj = self.client.trace(
                name=name,
                user_id=tenant_id,
                metadata=meta,
            )

            trace_obj.generation(
                name=name,
                model=model,
                input=prompt,
                output=completion,
                usage={
                    "input": input_tokens,
                    "output": output_tokens,
                },
                metadata=meta,
            )
            return trace_obj.id
        except Exception as e:
            logger.warning("Failed to trace generation in Langfuse: %s", e)
            return None

    def log_score(
        self,
        trace_id: str,
        name: str,
        value: float,
        comment: Optional[str] = None,
    ) -> None:
        """Attaches evaluative scores (e.g. faithfulness, rubric ratings, hallucination checks) to a trace."""
        if not self.enabled or not self.client or not trace_id:
            return

        try:
            self.client.score(
                trace_id=trace_id,
                name=name,
                value=value,
                comment=comment,
            )
        except Exception as e:
            logger.warning("Failed to log score to Langfuse: %s", e)


# Global singleton instance for platform-wide import
langfuse_logger = LangfuseLogger()
