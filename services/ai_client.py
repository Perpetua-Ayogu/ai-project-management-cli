import ollama


class AIClient:
    def __init__(self, model="llama3.2", host="http://localhost:11434"):
        self.model = model
        self.client = ollama.Client(host=host, timeout=60)

    def send(self, prompt):
        """Return model text or raise a readable service error."""
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")
        try:
            response = self.client.chat(model=self.model, messages=[{"role": "user", "content": prompt}])
            content = response.message.content
            if not isinstance(content, str) or not content.strip():
                raise ValueError("The model returned an empty response.")
            return content
        except Exception as error:
            raise RuntimeError(f"AI service unavailable: {error}") from error

