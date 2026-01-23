import plotly.express as px
import plotly.io as pio
import streamlit as st

def apply_style_constraints(fig):
    fig.update_layout(
        template="plotly", # On retire 'plotly_white' pour retrouver tes couleurs
        paper_bgcolor='rgba(0,0,0,0)', # Fond transparent pour s'adapter à Streamlit
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=60, b=40),
    )
    # On garde les axes propres sans toucher aux couleurs des données
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='LightGray')
    return fig

def render_chart(fig, chart_title):
    """Affiche le graphique proprement dans l'onglet Streamlit."""
    
    # 1. Appliquer le style
    fig = apply_style_constraints(fig)
    
    # 2. AFFICHAGE (Crucial : pas de pio.to_image ici !)
    # On affiche le graphique directement dans l'onglet
    st.plotly_chart(fig, use_container_width=True)
    
    # 3. EXPORT PNG (On le met dans un bouton pour éviter l'ouverture de page auto)
    with st.expander("💾 Exporter cette vue"):
        if st.button(f"Préparer le téléchargement pour : {chart_title}"):
            with st.spinner("Génération de l'image..."):
                try:
                    # Kaleido ne s'active qu'ici, sur demande
                    img_bytes = pio.to_image(fig, format="png", engine="kaleido")
                    
                    st.download_button(
                        label="📥 Télécharger en PNG",
                        data=img_bytes,
                        file_name=f"{chart_title.replace(' ', '_')}.png",
                        mime="image/png"
                    )
                except Exception as e:
                    st.error("Erreur d'export. Vérifiez que 'kaleido' est installé.")