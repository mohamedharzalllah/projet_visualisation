import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

class VizOrchestrator:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.model_analyst = os.getenv("MODEL_ANALYST", "anthropic/claude-3.5-sonnet")
        self.model_coder = os.getenv("MODEL_CODER", "openai/gpt-4o")

    def _call_llm(self, model, system_prompt, user_prompt):
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1
        }
        try:
            response = requests.post(self.url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            raise Exception(f"Erreur API : {str(e)}")

    def get_propositions(self, df_head, problematique):
        system_prompt = (
        "Tu es un expert en Business Intelligence et Data Storytelling. "
        "Réponds UNIQUEMENT par un objet JSON contenant exactement 4 propositions. "
        "Chaque proposition DOIT contenir des analyses réelles basées sur les données fournies.\n"
        "Structure JSON stricte :\n"
        "{\n"
        "  'propositions': [\n"
        "    {\n"
        "      'titre': 'Nom du graphique',\n"
        "      'justification': 'Pourquoi ce choix',\n"
        "      'insights': {\n"
        "        'constat': 'Décris une tendance spécifique visible dans les données (ex: Corrélation de 0.8 entre X et Y)',\n"
        "        'analyse': 'Explique l'impact métier de ce constat',\n"
        "        'action': 'Donne une recommandation concrète pour l'entreprise'\n"
        "      }\n"
        "    }\n"
        "  ]\n"
        "}"
    )
       
        user_prompt = f"Problématique : {problematique}\n\nDonnées : {df_head}"
        
        # Initialisation d'une réponse de secours (fallback)
        fallback = [
            {
                "titre": "Analyse descriptive", 
                "justification": "Aperçu général",
                "insights": {"constat": "Données chargées", "analyse": "Analyse en attente", "action": "Vérifier l'API"}
            }
        ]

        try:
            raw_response = self._call_llm(self.model_analyst, system_prompt, user_prompt)
            if not raw_response:
                return fallback

            start_idx = raw_response.find('{')
            end_idx = raw_response.rfind('}') + 1
            data = json.loads(raw_response[start_idx:end_idx])
            
            # Extraction sécurisée de la liste
            if isinstance(data, dict) and 'propositions' in data:
                return data['propositions']
            elif isinstance(data, list):
                return data
            else:
                return fallback
        except Exception as e:
            print(f"Erreur détaillée : {e}") # Pour débugger dans ton terminal
            return fallback
       
    def generate_code(self, selected_viz, columns_info, n_rows):
        """Génération de code Plotly STRICTE sans rechargement de fichier."""
        system_prompt = (
        "Génère uniquement du code Plotly Express (px). "
        "CONSIGNES POUR VARIABLES CATÉGORIELLES :\n"
        "- Si tu utilises une colonne de texte sur un axe numérique, utilise toujours une agrégation (ex: .groupby().mean() ou .value_counts()).\n"
        "- NE JAMAIS tenter de convertir un ID ou un texte en entier (ex: pas de .astype(int) sur des strings).\n"
        f"- Colonnes réelles : {columns_info}.\n"
        "RÈGLES CRITIQUES :\n"
        "- Utilise le DataFrame 'df' déjà chargé. Ne pas utiliser pd.read_csv().\n"
        "- L'objet final doit être 'fig'."
    )
        user_prompt = f"Graphique choisi : {selected_viz}. Colonnes : {columns_info}"
        return self._call_llm(self.model_coder, system_prompt, user_prompt)