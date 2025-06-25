import streamlit as st
from auth import user_login
from accueil import show_accueil
from menu_generator import show_menu_generator
from recettes import show_recette_ajout, show_recette_liste, show_mes_favoris, show_modifier_recette, show_supprimer_recette
from historique import show_historique

# --------- Initialisation session_state ---------
if 'recipes' not in st.session_state:
    from storage import charger_recettes
    st.session_state['recipes'] = charger_recettes()
if 'menu_semaine' not in st.session_state:
    st.session_state['menu_semaine'] = {}
if 'nb_personnes_repas' not in st.session_state:
    st.session_state['nb_personnes_repas'] = {}
if 'username' not in st.session_state:
    st.session_state['username'] = ""

# --------- Auth ---------
user = user_login()
from storage import charger_users
users = charger_users()  # refresh to get up-to-date favorites

# --------- Modern Sidebar Navigation ---------
with st.sidebar:
    menu_options = {
        "Accueil": "🏠 Accueil",
        "Générateur de menus": "🗓️ Générateur de menus",
        "Ajouter une recette": "➕ Ajouter une recette",
        "Répertoire de recettes": "📖 Répertoire de recettes",
        "Mes favoris": "⭐ Mes favoris",
        "Historique des menus": "📆 Historique",
        "Modifier une recette": "✏️ Modifier une recette",
        "Supprimer une recette": "🗑️ Supprimer une recette"
    }
    page = st.radio(
        "", list(menu_options.keys()),
        format_func=lambda x: menu_options[x],
        key="sidebar_nav"
    )

st.title("Planificateur de repas familial")

# --------- Appel des sous-modules ---------
if page == "Accueil":
    show_accueil()
elif page == "Générateur de menus":
    show_menu_generator(user)
elif page == "Ajouter une recette":
    show_recette_ajout()
elif page == "Répertoire de recettes":
    show_recette_liste(user)
elif page == "Mes favoris":
    show_mes_favoris(user)
elif page == "Historique des menus":
    show_historique(user)
elif page == "Modifier une recette":
    show_modifier_recette()
elif page == "Supprimer une recette":
    show_supprimer_recette()