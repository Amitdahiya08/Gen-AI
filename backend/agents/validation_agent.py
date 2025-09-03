from backend.utils.helpers import log_agent_action

class ValidationAgent:
    """Validates previous agent outputs and triggers rollback if needed."""

    def validate_summary(self, summary: str) -> bool:
        ok = bool(summary and len(summary.split()) > 5)
        log_agent_action("ValidationAgent", "validate_summary", str(ok))
        return ok

    def validate_entities(self, entities: dict) -> bool:
        ok = any(len(v) > 0 for v in entities.values())
        log_agent_action("ValidationAgent", "validate_entities", str(ok))
        return ok

    def rollback_summary(self):
        msg = "Summary rolled back due to low quality."
        log_agent_action("ValidationAgent", "rollback_summary", msg)
        return msg

    def rollback_entities(self):
        msg = "Entities rolled back due to low confidence."
        log_agent_action("ValidationAgent", "rollback_entities", msg)
        return msg
