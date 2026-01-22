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
            "Tu es un expert en Data Visualization. Réponds UNIQUEMENT par un objet JSON."
            "Structure requise : {'propositions': [{'titre': '...', 'justification': '...'}, ...]}"
        )
        user_prompt = f"Problématique : {problematique}\n\nDonnées : {df_head}"
        raw_response = self._call_llm(self.model_analyst, system_prompt, user_prompt)
        
        try:
            start_idx = raw_response.find('{')
            end_idx = raw_response.rfind('}') + 1
            data = json.loads(raw_response[start_idx:end_idx])
            
            # On extrait la liste des propositions peu importe la clé racine
            if isinstance(data, dict):
                # Si c'est un dict de dict (prop1, prop2...), on prend les valeurs
                if 'propositions' in data: return data['propositions']
                return list(data.values()) 
            return data
        except Exception:
            return [
                {"titre": "Analyse 1", "justification": "Description par défaut 1"},
                {"titre": "Analyse 2", "justification": "Description par défaut 2"},
                {"titre": "Analyse 3", "justification": "Description par défaut 3"}
            ]

    def generate_code(self, selected_viz, columns_info, n_rows):
        """ÉTAPE 2 : Génération de code Plotly pilotée par les contraintes de volume."""
        system_prompt = (
            "Génère uniquement du code Python utilisant Plotly Express (px). "
            "Le DataFrame s'appelle 'df'. L'objet final doit être 'fig'. "
            "RÈGLES DE LISIBILITÉ :\n"
            f"- Dataset de {n_rows} lignes.\n"
            "- Si type=box et n_rows > 500 : utilise points='outliers' uniquement.\n"
            "- Si nuage de points et n_rows > 1000 : utilise opacity=0.3.\n"
            "- Si trop de catégories (>15) : filtre le Top 10 avant de tracer.\n"
            "Ne mets pas de balises markdown ```python."
        )
        user_prompt = f"Graphique choisi : {selected_viz}. Colonnes : {columns_info}"
        return self._call_llm(self.model_coder, system_prompt, user_prompt)