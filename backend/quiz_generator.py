import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Initialisation du client OpenAI
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

def generate_quiz_from_text(course_text, n_questions=5):
    """
    Génère un quiz QCM à partir d'un texte de cours en utilisant OpenAI.
    Retourne une liste de dictionnaires contenant les questions et réponses.
    """
    prompt = f"""
    Tu es un assistant éducatif intelligent.
    Ton objectif est de générer EXACTEMENT {n_questions} questions de type QCM basées sur le texte suivant :

    --- Début du cours ---
    {course_text}
    --- Fin du cours ---

    ✅ Règles :
    - Donne exactement {n_questions} questions.
    - Chaque question doit avoir 4 choix (A, B, C, D).
    - Réponds UNIQUEMENT en format JSON valide, sans texte avant ni après.
    - Si le texte est trop court, crée des questions logiques liées au sujet principal du texte.

    Format attendu :
    [
      {{
        "question": "Quel est le rôle principal de Jenkins ?",
        "options": [
          "A. Automatiser les tests",
          "B. Gérer les serveurs",
          "C. Compiler le code",
          "D. Surveiller le réseau"
        ],
        "correct_answer": "A"
      }}
    ]
    """

    try:
        # Appel à l'API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=800
        )

        # Réponse brute
        raw_output = response.choices[0].message.content.strip()

        # 🔍 Tentative de parsing direct
        try:
            data = json.loads(raw_output)
            if isinstance(data, list) and data:
                return data
        except json.JSONDecodeError:
            # Nettoyage si le modèle a ajouté du texte inutile
            start = raw_output.find('[')
            end = raw_output.rfind(']')
            if start != -1 and end != -1:
                cleaned = raw_output[start:end + 1]
                data = json.loads(cleaned)
                if isinstance(data, list) and data:
                    return data

        # Si le modèle a renvoyé du vide
        return [{"error": "Aucune question générée. Vérifiez le texte envoyé."}]

    except Exception as e:
        return [{"error": str(e)}]


# 🔧 Test local (si exécuté directement)
if __name__ == "__main__":
    sample_text = "Jenkins est un outil d'intégration continue utilisé pour automatiser les builds, les tests et les déploiements."
    quiz = generate_quiz_from_text(sample_text)
    print(json.dumps(quiz, indent=2, ensure_ascii=False))
