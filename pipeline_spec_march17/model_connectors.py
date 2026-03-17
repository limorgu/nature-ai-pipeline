from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Protocol


@dataclass
class ClassificationResult:
    match_found: int
    category: str
    confidence: float
    model_id: str


@dataclass
class AuditResult:
    judge_match: int
    status: str
    fail_reason: str
    binary_drift: float
    judge_model_id: str


class WorkerConnector(Protocol):
    def classify_unit(self, text: str, taxonomy: List[str], label_keywords: Dict[str, List[str]]) -> ClassificationResult:
        ...


class JudgeConnector(Protocol):
    def audit_quote(self, quote: Dict, taxonomy: List[str], label_keywords: Dict[str, List[str]]) -> AuditResult:
        ...


class RulesWorkerConnector:
    model_id = "worker_rules_v1"

    def classify_unit(self, text: str, taxonomy: List[str], label_keywords: Dict[str, List[str]]) -> ClassificationResult:
        lowered = text.lower()
        best_label = "None"
        best_score = 0
        for label in taxonomy:
            score = sum(1 for keyword in label_keywords.get(label, []) if keyword.lower() in lowered)
            if score > best_score:
                best_score = score
                best_label = label

        match_found = 1 if best_score > 0 else 0
        confidence = min(1.0, round(best_score / 2.0, 3)) if match_found else 0.0
        return ClassificationResult(
            match_found=match_found,
            category=best_label if match_found else "None",
            confidence=confidence,
            model_id=self.model_id,
        )


class RulesJudgeConnector:
    judge_model_id = "judge_rules_v1"

    def audit_quote(self, quote: Dict, taxonomy: List[str], label_keywords: Dict[str, List[str]]) -> AuditResult:
        text = str(quote.get("quote", "")).lower()
        worker_match = int(quote.get("match_found", 0))
        worker_category = quote.get("category", "None")

        if worker_match == 0:
            return AuditResult(0, "FAIL", "Worker Miss", 0.0, self.judge_model_id)

        matched_keywords = [kw for kw in label_keywords.get(worker_category, []) if kw.lower() in text]
        if not matched_keywords:
            return AuditResult(0, "FAIL", "Out of Context", 1.0, self.judge_model_id)

        metaphor_cues = ["like a ", "as if", "as though", "kind of", "sort of"]
        if any(cue in text for cue in metaphor_cues) and worker_category in {"Fauna", "Flora"}:
            return AuditResult(0, "FAIL", "Metaphor Trap", 1.0, self.judge_model_id)

        return AuditResult(1, "PASS", "Literal Description", 0.0, self.judge_model_id)


class OpenAIWorkerConnector:
    model_id = "openai_worker_placeholder"

    def classify_unit(self, text: str, taxonomy: List[str], label_keywords: Dict[str, List[str]]) -> ClassificationResult:
        raise NotImplementedError("OpenAI worker connector is a placeholder. Wire API client here.")


class OpenAIJudgeConnector:
    judge_model_id = "openai_judge_placeholder"

    def audit_quote(self, quote: Dict, taxonomy: List[str], label_keywords: Dict[str, List[str]]) -> AuditResult:
        raise NotImplementedError("OpenAI judge connector is a placeholder. Wire API client here.")


class OllamaWorkerConnector:
    model_id = "ollama_worker_placeholder"

    def classify_unit(self, text: str, taxonomy: List[str], label_keywords: Dict[str, List[str]]) -> ClassificationResult:
        raise NotImplementedError("Ollama worker connector is a placeholder. Wire local model client here.")


class OllamaJudgeConnector:
    judge_model_id = "ollama_judge_placeholder"

    def audit_quote(self, quote: Dict, taxonomy: List[str], label_keywords: Dict[str, List[str]]) -> AuditResult:
        raise NotImplementedError("Ollama judge connector is a placeholder. Wire local model client here.")
