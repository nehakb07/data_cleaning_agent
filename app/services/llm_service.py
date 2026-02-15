import os
import json
from groq import Groq


class GroqService:

    def __init__(self, model: str = "llama-3.3-70b-versatile"):
        """
        Generic Groq LLM wrapper.
        """
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")

        self.client = Groq(api_key=api_key)
        self.model = model

    def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0):
        """
        Generic chat completion call.

        Returns:
            Raw text response
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature
        )

        return response.choices[0].message.content

    def chat_json(self, system_prompt: str, user_prompt: str, temperature: float = 0):

        response_text = self.chat(system_prompt, user_prompt, temperature)

        # 🔥 Remove markdown code fences if present
        cleaned = response_text.strip()

        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]  # remove first fence
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]  # remove 'json'
            cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            raise ValueError(
                "LLM did not return valid JSON. Response was:\n"
                + response_text
            )

