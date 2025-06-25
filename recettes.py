import streamlit as st
from storage import sauvegarder_recettes, charger_users, sauvegarder_users

TYPES_REPAS = ["Petit déjeuner", "Lunch", "Dîner", "Dessert"]
SAISONS = ["Printemps", "Été", "Automne", "Hiver"]
TAGS_NUTRITION = [
    "Poisson maigre", "Poisson gras", "Viande blanche", "Viande rouge", "Végétarien", "Vegan"
]

def show_recette_ajout():
    st.header("➕ Ajouter une recette")
    if 'ajout_recette' not in st.session_state:
        st.session_state['ajout_recette'] = {
            'name': '',
            'recipe_types': [],
            'prep_time': 30,
            'nb_personnes': 4,
            'saison': [],
            'tags': [],
            'ingredients_raw': ''
        }
    def reset_form():
        st.session_state['ajout_recette'] = {
            'name': '',
            'recipe_types': [],
            'prep_time': 30,
            'nb_personnes': 4,
            'saison': [],
            'tags': [],
            'ingredients_raw': ''
        }

    with st.form("Ajouter une recette", clear_on_submit=True):
        name = st.text_input("Nom de la recette", value=st.session_state['ajout_recette']['name'], key="form_name")
        recipe_types = st.multiselect("Types (tu peux en sélectionner plusieurs)", TYPES_REPAS, default=st.session_state['ajout_recette']['recipe_types'], key="form_types")
        prep_time = st.number_input("Temps de préparation (minutes)", min_value=1, max_value=240, value=st.session_state['ajout_recette']['prep_time'], key="form_prep_time")
        nb_personnes = st.number_input("Nombre de personnes pour la recette", min_value=1, max_value=20, value=st.session_state['ajout_recette']['nb_personnes'], key="form_nb_personnes")
        saison = st.multiselect("Saison(s) idéale(s)", SAISONS, default=st.session_state['ajout_recette']['saison'], key="form_saison")
        tags = st.multiselect("Tags nutritionnels", TAGS_NUTRITION, default=st.session_state['ajout_recette']['tags'], key="form_tags")
        ingredients_raw = st.text_area(
            "Ingrédients (un par ligne, format: quantité unité ingrédient, ex: 500 g carottes)",
            value=st.session_state['ajout_recette']['ingredients_raw'], key="form_ingredients"
        )
        submit = st.form_submit_button("Ajouter la recette")
        if submit:
            if name and ingredients_raw and recipe_types:
                recette = {
                    "name": name,
                    "type": recipe_types,
                    "prep_time": prep_time,
                    "nb_personnes": nb_personnes,
                    "saison": saison,
                    "tags": tags,
                    "ingredients": [i.strip() for i in ingredients_raw.splitlines() if i.strip()]
                }
                st.session_state['recipes'].append(recette)
                sauvegarder_recettes(st.session_state['recipes'])
                st.success(f"Recette ajoutée : {name}")
                reset_form()
            else:
                if not name:
                    st.warning("Merci de renseigner le nom de la recette.")
                if not recipe_types:
                    st.warning("Merci de sélectionner au moins un type de repas.")
                if not ingredients_raw:
                    st.warning("Merci de renseigner les ingrédients.")

def show_recette_liste(user):
    st.header("📖 Répertoire des recettes")
    if not st.session_state['recipes']:
        st.info("Aucune recette enregistrée.")
    else:
        users = charger_users()
        for recette in st.session_state['recipes']:
            fav = recette['name'] in users[user].get("favorites", [])
            with st.expander(f"{recette['name']} {'⭐' if fav else ''}"):
                st.write(f"Types : {', '.join(recette['type']) if isinstance(recette['type'], list) else recette['type']}")
                st.write(f"Temps de préparation : {recette['prep_time']} min")
                st.write(f"Pour : {recette['nb_personnes']} personne(s)")
                st.write(f"Saison(s) : {', '.join(recette['saison']) if recette['saison'] else 'Toutes'}")
                st.write(f"Tags nutritionnels : {', '.join(recette['tags']) if recette['tags'] else 'Non précisé'}")
                st.write("Ingrédients :")
                st.write('\n'.join(f"- {ing}" for ing in recette['ingredients']))
                if fav:
                    if st.button(f"Retirer des favoris", key=f"retirer_{recette['name']}"):
                        users[user]["favorites"].remove(recette['name'])
                        sauvegarder_users(users)
                        st.success("Recette retirée des favoris.")
                        st.experimental_rerun()
                else:
                    if st.button(f"Ajouter aux favoris", key=f"ajouter_{recette['name']}"):
                        users[user]["favorites"].append(recette['name'])
                        sauvegarder_users(users)
                        st.success("Recette ajoutée aux favoris.")
                        st.experimental_rerun()

def show_mes_favoris(user):
    st.header("⭐ Mes recettes favorites")
    users = charger_users()
    favs = users[user].get("favorites", [])
    if not favs:
        st.info("Aucune recette favorite.")
    else:
        for recette in st.session_state['recipes']:
            if recette['name'] in favs:
                with st.expander(f"{recette['name']} ⭐"):
                    st.write(f"Types : {', '.join(recette['type']) if isinstance(recette['type'], list) else recette['type']}")
                    st.write(f"Temps de préparation : {recette['prep_time']} min")
                    st.write(f"Pour : {recette['nb_personnes']} personne(s)")
                    st.write(f"Saison(s) : {', '.join(recette['saison']) if recette['saison'] else 'Toutes'}")
                    st.write(f"Tags nutritionnels : {', '.join(recette['tags']) if recette['tags'] else 'Non précisé'}")
                    st.write("Ingrédients :")
                    st.write('\n'.join(f"- {ing}" for ing in recette['ingredients']))
                    if st.button(f"Retirer des favoris", key=f"favretirer_{recette['name']}"):
                        users[user]["favorites"].remove(recette['name'])
                        sauvegarder_users(users)
                        st.success("Recette retirée des favoris.")
                        st.experimental_rerun()

def show_modifier_recette():
    st.header("✏️ Modifier une recette")
    recette_names = [rec['name'] for rec in st.session_state['recipes']]
    if recette_names:
        recette_a_modifier = st.selectbox("Choisis la recette à modifier :", recette_names, key="modifier_select")
        index = next((i for i, rec in enumerate(st.session_state['recipes']) if rec['name'] == recette_a_modifier), None)
        if index is not None:
            recette = st.session_state['recipes'][index]
            with st.form("Modifier la recette", clear_on_submit=False):
                name = st.text_input("Nom de la recette", value=recette['name'], key="edit_name")
                recipe_types = st.multiselect("Types (tu peux en sélectionner plusieurs)", TYPES_REPAS, default=recette['type'], key="edit_types")
                prep_time = st.number_input("Temps de préparation (minutes)", min_value=1, max_value=240, value=recette['prep_time'], key="edit_prep_time")
                nb_personnes = st.number_input("Nombre de personnes pour la recette", min_value=1, max_value=20, value=recette['nb_personnes'], key="edit_nb_personnes")
                saison = st.multiselect("Saison(s) idéale(s)", SAISONS, default=recette['saison'], key="edit_saison")
                tags = st.multiselect("Tags nutritionnels", TAGS_NUTRITION, default=recette['tags'], key="edit_tags")
                ingredients_raw = st.text_area(
                    "Ingrédients (un par ligne, format: quantité unité ingrédient, ex: 500 g carottes)",
                    value='\n'.join(recette['ingredients']), key="edit_ingredients"
                )
                submit = st.form_submit_button("Enregistrer les modifications")
                if submit:
                    if name and ingredients_raw and recipe_types:
                        nouvelle_recette = {
                            "name": name,
                            "type": recipe_types,
                            "prep_time": prep_time,
                            "nb_personnes": nb_personnes,
                            "saison": saison,
                            "tags": tags,
                            "ingredients": [i.strip() for i in ingredients_raw.splitlines() if i.strip()]
                        }
                        st.session_state['recipes'][index] = nouvelle_recette
                        sauvegarder_recettes(st.session_state['recipes'])
                        st.success(f"Modifications enregistrées pour : {name}")
                        st.experimental_rerun()
                    else:
                        if not name:
                            st.warning("Merci de renseigner le nom de la recette.")
                        if not recipe_types:
                            st.warning("Merci de sélectionner au moins un type de repas.")
                        if not ingredients_raw:
                            st.warning("Merci de renseigner les ingrédients.")
    else:
        st.info("Aucune recette à modifier.")

def show_supprimer_recette():
    st.header("🗑️ Supprimer une recette")
    recette_names = [rec['name'] for rec in st.session_state['recipes']]
    if recette_names:
        recette_a_supprimer = st.selectbox("Choisis la recette à supprimer :", recette_names)
        if st.button("Supprimer la recette sélectionnée"):
            for i, rec in enumerate(st.session_state['recipes']):
                if rec['name'] == recette_a_supprimer:
                    st.session_state['recipes'].pop(i)
                    sauvegarder_recettes(st.session_state['recipes'])
                    st.success(f"La recette '{recette_a_supprimer}' a été supprimée !")
                    st.experimental_rerun()
            else:
                st.warning("Aucune recette supprimée.")
    else:
        st.info("Aucune recette à supprimer.")