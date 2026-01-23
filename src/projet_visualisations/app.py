import streamlit as st
import pandas as pd
from llm import VizOrchestrator
from vis_utils import render_chart 

st.set_page_config(page_title="Dauphine Viz AI", layout="wide")

def main():
    st.title("🤖 Assistant DataViz Intelligent")
    st.caption("Projet Master 2 BDIA - Dauphine PSL")
    
    orchestrator = VizOrchestrator()

    # --- ÉTAPE 1 : CONFIGURATION (Sidebar) ---
    with st.sidebar:
        st.header("1. Données & Analyse")
        uploaded_file = st.file_uploader("Charger un dataset (CSV)", type="csv")
        user_query = st.text_area("Votre problématique :")
        
        analyze_btn = st.button("🚀 Lancer l'analyse complète")
        
        if analyze_btn:
            if uploaded_file and user_query:
                # Chargement du fichier
                df = pd.read_csv(uploaded_file)
                st.session_state['df'] = df
                st.session_state['query'] = user_query
                
                with st.spinner("L'IA prépare vos 4 analyses stratégiques..."):
                    # 1. On récupère les propositions structurées
                    props = orchestrator.get_propositions(df.head(5).to_string(), user_query)
                    
                    if props:
                        st.session_state['proposals'] = props
                        codes = []
                        
                        # 2. Génération et nettoyage du code pour chaque proposition
                        for p in props:
                            desc = f"{p['titre']} : {p['justification']}"
                            raw_code = orchestrator.generate_code(desc, df.columns.tolist(), len(df))
                            
                            # --- NETTOYAGE ANTI-HALLUCINATION ---
                            # On retire les balises markdown et les lignes dangereuses
                            clean_c = raw_code.replace("```python", "").replace("```", "").strip()
                            lines = clean_c.split('\n')
                            
                            safe_lines = []
                            for line in lines:
                                # Supprime les tentatives de lecture de fichier ou d'imports redondants
                                if any(bad in line for bad in ["pd.read_csv", "import pandas", "pd.DataFrame", "fig.show()"]):
                                    continue
                                safe_lines.append(line)
                            
                            codes.append('\n'.join(safe_lines))
                        
                        st.session_state['generated_codes'] = codes
                        st.session_state['ready'] = True
                    else:
                        st.error("Erreur lors de la génération des propositions.")
            else:
                st.error("Veuillez fournir un fichier et une problématique.")

    # --- ÉTAPE 2 : AFFICHAGE DANS LES TABS ---
    if st.session_state.get('ready'):
        st.header("Analyse Multidimensionnelle")
        df = st.session_state['df']
        props_list = st.session_state['proposals']
        codes_list = st.session_state['generated_codes']

        # Création dynamique des 4 onglets
        titres = [p.get('titre', f"Analyse {i+1}") for i, p in enumerate(props_list)]
        tabs = st.tabs(titres)

        for i, tab in enumerate(tabs):
            with tab:
                prop = props_list[i]
                clean_code = codes_list[i]
                
                try:
                    import plotly.express as px
                    # On injecte le df et px dans l'environnement d'exécution
                    ldict = {'df': df, 'px': px}
                    exec(clean_code, globals(), ldict)
                    
                    if 'fig' in ldict:
                        # Rendu du graphique avec style Dauphine
                        render_chart(ldict['fig'], prop['titre'])
                        
                        # --- BLOC D'INTERPRÉTATION (INSIGHTS) ---
                        st.markdown("---")
                        st.subheader("🎯 Insights Stratégiques")
                        
                        insights = prop.get('insights', {})
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.info(f"**🧐 Constat**\n\n{insights.get('constat', 'Analyse des données indisponible.')}")
                        with col2:
                            st.warning(f"**🧠 Analyse**\n\n{insights.get('analyse', 'Interprétation métier indisponible.')}")
                        with col3:
                            st.success(f"**🚀 Action**\n\n{insights.get('action', 'Recommandation stratégique indisponible.')}")
                    else:
                        st.error("L'IA n'a pas pu créer l'objet graphique 'fig'.")
                        st.code(clean_code) # Affiche le code pour debug
                        
                except Exception as e:
                    st.error(f"Erreur d'exécution du graphique : {e}")
                    with st.expander("Voir le code généré"):
                        st.code(clean_code)

        # Bouton de réinitialisation pour changer de dataset proprement
        if st.button("🔄 Nouvelle Analyse / Réinitialiser"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

if __name__ == "__main__":
    main()