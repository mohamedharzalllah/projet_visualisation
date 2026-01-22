import plotly.express as px
import plotly.io as pio
import streamlit as st

def apply_style_constraints(fig):
    """
    Applique les bonnes pratiques de visualisation :
    - Maximise le data-ink ratio 
    - Supprime le chartjunk 
    """
    fig.update_layout(
        template="plotly_white",  # Fond blanc pour plus de clarté
        margin=dict(l=40, r=40, t=60, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    # Suppression du quadrillage inutile pour le data-ink ratio
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='LightGray')
    return fig

def render_chart(fig, chart_title):
    """
    Affiche le graphique dans Streamlit et prépare l'export PNG.
    """
    st.subheader(chart_title)
    
    # Application des contraintes de style avant affichage
    fig = apply_style_constraints(fig)
    
    # Affichage interactif
    st.plotly_chart(fig, use_container_width=True)
    
    # Préparation du bouton de téléchargement PNG 
    img_bytes = pio.to_image(fig, format="png")
    
    st.download_button(
        label="💾 Télécharger la visualisation (PNG)",
        data=img_bytes,
        file_name=f"{chart_title.replace(' ', '_')}.png",
        mime="image/png"
    )
    