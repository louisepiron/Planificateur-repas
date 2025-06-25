import streamlit as st
from storage import charger_menus

def show_historique(user):
    st.header("📆 Historique de mes menus")
    menus = charger_menus()
    user_menus = menus.get(user, {})
    if not user_menus:
        st.info("Aucun menu généré pour ce compte.")
    else:
        for week in sorted(user_menus.keys(), reverse=True):
            menu = user_menus[week]
            with st.expander(f"Semaine {week}"):
                for repas_type, recettes_liste in menu.items():
                    st.write(f"### {repas_type}")
                    for data in recettes_liste:
                        recette = data["recette"]
                        nb_personnes = data["nb_personnes"]
                        st.write(f"- **{recette['name']}** ({', '.join(recette['tags']) if recette['tags'] else 'Aucun tag'}) — pour {nb_personnes} personnes")