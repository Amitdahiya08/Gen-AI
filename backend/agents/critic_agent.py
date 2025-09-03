from backend.config import Config
import requests
from backend.utils.helpers import log_agent_action

class CriticAgent:
    """Critic agent to review content for bias, completeness, and sensitive data leakage."""

    def review_summary(self, summary: str) -> dict:
        headers = {"Content-Type": "application/json", "api-key": Config.AZURE_OPENAI_API_KEY}
        body = {
            "messages": [
                {"role": "system", "content": "You are a critic. Check for bias, completeness, and sensitive info."},
                {"role": "user", "content": f"Review this summary:\n{summary}"}
            ],
            "max_tokens": 300,
        }
        resp = requests.post(
            f"{Config.AZURE_OPENAI_ENDPOINT}/openai/deployments/{Config.AZURE_OPENAI_DEPLOYMENT_NAME}/chat/completions?api-version=2024-05-01-preview",
            headers=headers, json=body
        )
        if resp.status_code == 200:
            review = resp.json()["choices"][0]["message"]["content"].strip()
            result = {"status": "reviewed", "critic_notes": review}
            log_agent_action("CriticAgent", "review_summary", review[:200])
            return result
        return {"status": "failed", "reason": resp.text}
