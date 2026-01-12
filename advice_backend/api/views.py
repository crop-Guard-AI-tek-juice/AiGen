from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
import google.generativeai as genai
import re

genai.configure(api_key=settings.NLP_API_KEY)


def clean_ai_text(text: str) -> str:
    if not text:
        return ""

    # 1. Remove markdown formatting (**bold**, *italic*)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)

    # 2. Normalize bullets
    text = re.sub(r"^\s*[-•]\s*", "- ", text, flags=re.MULTILINE)

    # 3. Ensure numbered lists start on new lines
    text = re.sub(r"(\n?)(\d+)\.\s*", r"\n\2. ", text)

    # 4. Add paragraph breaks after common section starters
    section_keywords = [
        r"What is",
        r"What does it look like",
        r"What can you do",
        r"What to do now",
        r"How to prevent",
        r"Prevention",
        r"Control",
        r"Important safety tips",
        r"Safety tips",
        r"Conclusion",
    ]

    for keyword in section_keywords:
        text = re.sub(
            rf"({keyword}.*?:)",
            r"\n\n\1\n",
            text,
            flags=re.IGNORECASE,
        )

    # 5. Add paragraph break after greetings
    text = re.sub(
        r"(Hello|Good day|Okay, I understand\.?)",
        r"\1\n\n",
        text,
        flags=re.IGNORECASE,
    )

    # 6. Clean excessive newlines
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
