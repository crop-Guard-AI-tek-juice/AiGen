from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
import google.generativeai as genai

# Configure Gemini once
genai.configure(api_key=settings.NLP_API_KEY)

@api_view(["POST"])
def generate_advice(request):
    disease_name = request.data.get("disease_name")

    if not disease_name:
        return Response(
            {"error": "disease_name is required"},
            status=400
        )

    prompt = f"""
You are an agricultural extension assistant helping small-scale cassava farmers.

Disease detected: {disease_name}

Explain in simple, clear, farmer-friendly language:

1. What this disease is
2. How it affects cassava plants
3. Common causes and how it spreads
4. Practical prevention and control measures farmers can use
5. Common categories of pesticides or insecticides used (NO brand names, NO dosages)
6. Safety and environmental precautions farmers should follow

Avoid technical jargon. Be practical and clear.
"""

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)

        return Response({
            "disease": disease_name,
            "advice": response.text
        })

    except Exception as e:
        return Response(
            {
                "error": "Failed to generate advice",
                "details": str(e)
            },
            status=500
        )
