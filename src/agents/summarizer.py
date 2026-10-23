
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


class Summarizer:
    """Create a dynamic PowerPoint plan using Google Gemini."""

    def __init__(self):
        api_key = (
            os.getenv("GEMINI_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
        )

        if not api_key:
            raise ValueError(
                "Set GEMINI_API_KEY in the project root .env file."
            )

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-2.5-flash",
        )

        self.client = genai.Client(api_key=api_key)

    def summarize_text(self, text: str) -> dict:
        """
        Input: Extracted document text.
        Output: A structured presentation plan.
        """

        if not isinstance(text, str) or not text.strip():
            raise ValueError("The document contains no readable text.")

        # Initial version supports a limited document size.
        # Chunking for very large documents can be added later.
        text = text[:25000]

        prompt = f"""
You are an expert presentation designer and content analyst.

Analyze the source material and create a useful PowerPoint plan
based only on information supported by the document.

Requirements:
- Choose a suitable presentation title.
- Create a logical sequence of slides.
- Give each slide a meaningful, topic-specific title.
- Provide 3 to 5 concise bullet points per slide where possible.
- Adapt the number of slides to the amount of useful content.
- Preserve important figures, dates, names and findings.
- Do not invent facts or unsupported conclusions.
- Avoid duplicate points and repetitive slides.
- Include an introduction or conclusion when appropriate.
- For CSV data, describe only patterns supported by the supplied data.
- Return valid JSON only. Do not use Markdown code fences.

Required JSON structure:
{{
  "presentation_title": "A suitable title",
  "slides": [
    {{
      "title": "A specific slide title",
      "bullets": [
        "First key point",
        "Second key point",
        "Third key point"
      ]
    }}
  ]
}}

SOURCE DOCUMENT:
<source>
{text}
</source>
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "temperature": 0.3,
            },
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        try:
            plan = json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "Gemini returned invalid JSON."
            ) from exc

        if not isinstance(plan, dict):
            raise ValueError("Expected a JSON object from Gemini.")

        title = plan.get("presentation_title")
        slides = plan.get("slides")

        if not isinstance(title, str) or not title.strip():
            raise ValueError("The presentation title is missing.")

        if not isinstance(slides, list) or not slides:
            raise ValueError("Gemini did not generate any slides.")

        cleaned_slides = []

        for item in slides:
            if not isinstance(item, dict):
                continue

            slide_title = item.get("title")
            bullets = item.get("bullets")

            if not isinstance(slide_title, str):
                continue

            if not isinstance(bullets, list):
                continue

            cleaned_bullets = [
                bullet.strip()
                for bullet in bullets
                if isinstance(bullet, str) and bullet.strip()
            ]

            if cleaned_bullets:
                cleaned_slides.append({
                    "title": slide_title.strip(),
                    "bullets": cleaned_bullets,
                })

        if not cleaned_slides:
            raise ValueError("No valid slides were generated.")

        return {
            "presentation_title": title.strip(),
            "slides": cleaned_slides,
        }
