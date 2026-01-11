from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
import google.generativeai as genai
import re

genai.configure(api_key=settings.NLP_API_KEY)


def clean_ai_text(text: str) -> str:
    if not text:
        return ""

    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"^\s*[-•]\s*", "- ", text, flags=re.MULTILINE)
    text = re.sub(r"(\d+)\.\s*", r"\n\1. ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


@api_view(["POST"])
def generate_advice(request):
    disease_name = request.data.get("disease_name")
    question = request.data.get("question")

    if not disease_name:
        return Response({"error": "disease_name is required"}, status=400)

    if not question:
        return Response({"error": "question is required"}, status=400)

    prompt = f"""
You are Crop Guard AI, an agricultural assistant for small-scale cassava farmers.

A cassava leaf disease has been detected using AI image analysis.

Disease detected: {disease_name}

The farmer asks:
"{question}"

Respond clearly and practically.
- Give actionable advice
- Focus on prevention, control, and safety

and respond to anyother question that is might not be related to crop disease.

 Separate your response into paragraphs for readability
"""

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)

        cleaned_answer = clean_ai_text(response.text)

        return Response({
            "disease": disease_name,
            "answer": cleaned_answer
        })

    except Exception as e:
        return Response(
            {
                "error": "Failed to generate response",
                "details": str(e)
            },
            status=500
        )
