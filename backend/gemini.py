from google import genai

from config import Settings


class GeminiGenerator:
    def __init__(self, settings: Settings):
        self.settings = settings

        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )

        self.model = getattr(
            settings,
            "gemini_model",
            "gemini-3.6-flash",
        )

    def generate(
        self,
        query: str,
        context: str,
    ) -> str:
        prompt = f"""
You are a personal knowledge-base assistant.

Answer the user's question using ONLY the
information provided in the context.

Do not invent facts.

If the context does not contain enough
information to answer the question, clearly
say that the information is not available
in the uploaded documents.

Give a clear and concise answer.

USER QUESTION:
{query}

CONTEXT:
{context}

ANSWER:
""".strip()

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        if not response.text:
            return (
                "I couldn't generate an answer "
                "from the available information."
            )

        return response.text.strip()