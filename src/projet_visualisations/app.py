import streamlit as st
import pandas as pd
import json
from llm import VizOrchestrator
from vis_utils import render_chart

st.set_page_config(page_title="Dauphine Viz AI", layout="wide")

def main():
    st.title("🤖 Assistant DataViz Intelligent")
    st.caption("Projet Master 2 BDIA - Dauphine PSL")
    
    orchestrator = VizOrchestrator()

    # --- ÉTAPE 1 : INPUTS (Problématique & Dataset) ---
    with st.sidebar:
        st.header("1. Configuration")
        uploaded_file = st.file_uploader("Charger un dataset (CSV)", type="csv")
        user_query = st.text_area("Votre problématique :", placeholder="Ex: Impact du genre sur l'énergie des titres")
        
        if st.button("Analyser & Proposer"):
            if uploaded_file and user_query:
                df = pd.read_csv(uploaded_file)
                st.session_state['df'] = df
                st.session_state['query'] = user_query
                
                with st.spinner("L'IA réfléchit aux propositions..."):
                    props = orchestrator.get_propositions(df.head(5).to_string(), user_query)
                    st.session_state['proposals'] = props
                    st.session_state['step'] = 'selection'
            else:
                st.error("Fichier et problématique requis.")

    # --- ÉTAPE 2 : SÉLECTION (Scaffolding) ---
    if st.session_state.get('step') == 'selection':
        st.header("2. Propositions de l'IA")
        props = st.session_state['proposals']
        keys = ['prop1', 'prop2', 'prop3']

        cols = st.columns(3)
        for i, key in enumerate(keys):
            if key in props:
                with cols[i]:
                    st.info(f"**{props[key]['titre']}**")
                    st.write(props[key]['justification'])

        choix = st.radio("Sélectionnez la meilleure option :", options=keys, 
                         format_func=lambda x: props[x].get('titre', x))

        if st.button("Générer la visualisation"):
            df = st.session_state['df']
            with st.spinner("Codage en cours..."):
                desc = f"{props[choix]['titre']} : {props[choix]['justification']}"
                code = orchestrator.generate_code(desc, df.columns.tolist(), len(df))
                st.session_state['generated_code'] = code
                st.session_state['step'] = 'viz'

    # --- ÉTAPE 3 : RENDU & EXPORT PNG ---
    if st.session_state.get('step') == 'viz':
        st.header("3. Visualisation Finale")
        df = st.session_state['df']
        clean_code = st.session_state['generated_code'].replace("```python", "").replace("```", "").strip()
        
        try:
            import plotly.express as px
            local_vars = {'df': df, 'px': px}
            exec(clean_code, {}, local_vars)
            
            if 'fig' in local_vars:
                # Appel à viz_utils pour l'export PNG et le style final
                render_chart(local_vars['fig'], st.session_state['query'])
            else:
                st.error("L'IA n'a pas généré l'objet 'fig'.")
        except Exception as e:
            st.error(f"Erreur d'exécution : {e}")
            st.code(clean_code)

        if st.button("🔄 Recommencer"):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()

if __name__ == "__main__":
    main()