from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
import google.generativeai as genai

# Configure Gemini once
genai.configure(api_key=settings.NLP_API_KEY)

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
- Use simple, farmer-friendly language
- Give actionable advice
- Focus on prevention, control, and safety

and respond to anyother question that is might not be related to crop disease.
"""

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)

        return Response({
            "disease": disease_name,
            "answer": response.text.strip()
        })

    except Exception as e:
        return Response(
            {
                "error": "Failed to generate response",
                "details": str(e)
            },
            status=500
        )
