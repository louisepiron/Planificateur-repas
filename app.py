import streamlit as st
import json
import os
import random
from datetime import date, timedelta

# --------- Custom Style for Modern Sidebar ---------
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #F9F9F9 50%, #E3E8F0 100%);
        color: #2D3748;
        font-family: 'Segoe UI', 'Roboto', sans-serif;
        border-right: 1px solid #e1e5ea;
    }
    .sidebar-title {
        font-size: 1.5em;
        font-weight: bold;
        letter-spacing: 1px;
        color: #2B6CB0;
        margin-bottom: 1.5em;
        margin-top: 1em;
        text-align: center;
    }
    .stRadio > label {display:none;}
    [data-testid="stSidebarNav"] svg {display: none;}
    </style>
""", unsafe_allow_html=True)

# --------- Constants ---------
RECIPES_FILE = "recettes.json"
USERS_FILE = "users.json"
MENUS_FILE = "menus.json"
SAISONS = ["Printemps", "Été", "Automne", "Hiver"]
TAGS_NUTRITION = [
    "Poisson maigre", "Poisson gras", "Viande blanche", "Viande rouge", "Végétarien", "Vegan"
]
TYPES_REPAS = ["Petit déjeuner", "Lunch", "Dîner", "Dessert"]

# --------- Helper functions for JSON storage ---------
def charger_json(filename, default):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def sauvegarder_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def charger_recettes():
    return charger_json(RECIPES_FILE, [])

def sauvegarder_recettes(recettes):
    sauvegarder_json(recettes, RECIPES_FILE)

def charger_users():
    return charger_json(USERS_FILE, {})

def sauvegarder_users(users):
    sauvegarder_json(users, USERS_FILE)

def charger_menus():
    return charger_json(MENUS_FILE, {})

def sauvegarder_menus(menus):
    sauvegarder_json(menus, MENUS_FILE)

# --------- User Authentication ---------
def user_login():
    st.sidebar.markdown('<div class="sidebar-title">🍽️ Famille Menu</div>', unsafe_allow_html=True)
    users = charger_users()
    usernames = list(users.keys())
    if 'username' not in st.session_state or not st.session_state['username']:
        login_mode = st.sidebar.radio("Connexion", ["Se connecter", "Créer un compte"], key="login_radio")
        if login_mode == "Se connecter":
            username = st.sidebar.text_input("Nom d'utilisateur", key="login_user")
            password = st.sidebar.text_input("Mot de passe", type="password", key="login_pw")
            if st.sidebar.button("Se connecter"):
                if username in users and users[username]["password"] == password:
                    st.session_state['username'] = username
                    st.experimental_rerun()
                else:
                    st.sidebar.error("Nom d'utilisateur ou mot de passe incorrect.")
            st.stop()
        else:
            new_username = st.sidebar.text_input("Choisir un nom d'utilisateur", key="new_user")
            new_password = st.sidebar.text_input("Choisir un mot de passe", type="password", key="new_pw")
            if st.sidebar.button("Créer le compte"):
                if not new_username or not new_password:
                    st.sidebar.warning("Remplis tous les champs.")
                elif new_username in users:
                    st.sidebar.error("Nom d'utilisateur déjà pris.")
                else:
                    users[new_username] = {
                        "password": new_password,
                        "favorites": []
                    }
                    sauvegarder_users(users)
                    st.session_state['username'] = new_username
                    st.experimental_rerun()
            st.stop()
    else:
        st.sidebar.markdown(f"👤 <b>{st.session_state['username']}</b>", unsafe_allow_html=True)
        if st.sidebar.button("Se déconnecter"):
            st.session_state['username'] = ""
            st.experimental_rerun()
        return st.session_state['username']

# --------- Initialisation session_state ---------
if 'recipes' not in st.session_state:
    st.session_state['recipes'] = charger_recettes()
if 'menu_semaine' not in st.session_state:
    st.session_state['menu_semaine'] = {}
if 'nb_personnes_repas' not in st.session_state:
    st.session_state['nb_personnes_repas'] = {}
if 'username' not in st.session_state:
    st.session_state['username'] = ""

# --------- Auth ---------
user = user_login()
users = charger_users()  # refresh to get up-to-date favorites

# --------- Modern Sidebar Navigation ---------
with st.sidebar:
    menu_options = {
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

# --------- PAGE : Générateur de menus ---------
if page == "Générateur de menus":
    st.header("🗓️ Planifier le menu de la semaine")

    saison_courante = st.selectbox("Saison actuelle", SAISONS)
    st.markdown("**Sélectionne les types de repas à planifier et combien de recettes de chaque type tu veux cette semaine :**")
    types_selectionnes = st.multiselect("Types de repas à planifier", TYPES_REPAS, default=TYPES_REPAS)

    nb_recettes_par_type = {}
    nb_personnes_repas = {}
    st.markdown("**Pour chaque type de repas, indique le nombre de recettes et le nombre de personnes par repas :**")
    for repas_type in types_selectionnes:
        cols = st.columns(2)
        nb_recettes = cols[0].number_input(
            f"Nombre de recettes '{repas_type}'", min_value=0, max_value=14, value=2, key=f"nb_{repas_type}"
        )
        nb_personnes = cols[1].number_input(
            f"Nombre de personnes pour '{repas_type}'", min_value=1, max_value=20, value=4, key=f"pers_{repas_type}"
        )
        nb_recettes_par_type[repas_type] = nb_recettes
        nb_personnes_repas[repas_type] = nb_personnes
    st.session_state['nb_personnes_repas'] = nb_personnes_repas

    st.markdown("**Contraintes nutritionnelles recommandées pour la semaine :**")
    contraintes_defaut = {
        "Poisson maigre": 1,
        "Poisson gras": 1,
        "Viande blanche": 1,
        "Viande rouge": 1,
        "Végétarien": 1
    }
    contraintes = {}
    for tag in contraintes_defaut:
        contraintes[tag] = st.number_input(
            f"{tag} (fois/semaine)", min_value=0, max_value=sum(nb_recettes_par_type.values()),
            value=min(contraintes_defaut[tag], sum(nb_recettes_par_type.values()))
        )

    if st.button("Générer le menu de la semaine"):
        recettes = [
            r for r in st.session_state['recipes']
            if not r['saison'] or saison_courante in r['saison']
        ]
        menu = {rtype: [] for rtype in types_selectionnes}
        contraintes_temp = contraintes.copy()
        recettes_shuffled = recettes.copy()
        random.shuffle(recettes_shuffled)
        erreurs = []
        deja_choisies = set()  # Pour éviter les doublons

        for repas_type in types_selectionnes:
            recettes_type = [r for r in recettes_shuffled if repas_type in r['type'] and r['name'] not in deja_choisies]
            recettes_type_tags = {tag: [r for r in recettes_type if tag in r['tags']] for tag in contraintes_temp}
            nb_a_choisir = nb_recettes_par_type[repas_type]
            selection = []

            # Satisfy constraints first
            for tag, quota in contraintes_temp.items():
                if quota > 0 and len(selection) < nb_a_choisir:
                    candidats = [r for r in recettes_type_tags[tag] if r['name'] not in deja_choisies and r not in selection]
                    while quota > 0 and candidats and len(selection) < nb_a_choisir:
                        choix = candidats.pop()
                        selection.append(choix)
                        deja_choisies.add(choix['name'])
                        contraintes_temp[tag] -= 1
                        quota -= 1

            # Fill with other recipes of this type
            candidats_restants = [r for r in recettes_type if r['name'] not in deja_choisies and r not in selection]
            while len(selection) < nb_a_choisir and candidats_restants:
                choix = candidats_restants.pop()
                selection.append(choix)
                deja_choisies.add(choix['name'])

            if len(selection) < nb_a_choisir:
                erreurs.append(f"Pas assez de recettes pour {repas_type} ({len(selection)}/{nb_a_choisir}). Ajoutez-en plus !")

            menu[repas_type] = [
                {"recette": recette, "nb_personnes": nb_personnes_repas[repas_type]}
                for recette in selection
            ]

        st.session_state['menu_semaine'] = menu

        # Sauvegarde historique (par utilisateur)
        menus = charger_menus()
        history = menus.get(user, {})
        today = date.today()
        key = today.strftime("%Y-%W")  # année-semaine
        # On sauvegarde aussi le nombre de personnes par repas dans l'historique pour chaque recette
        history[key] = menu
        menus[user] = history
        sauvegarder_menus(menus)

        if erreurs:
            st.warning("\n".join(erreurs))

    # Affichage du menu
    if st.session_state['menu_semaine']:
        st.subheader("Menu proposé :")
        users = charger_users()
        for repas_type, recettes_liste in st.session_state['menu_semaine'].items():
            st.write(f"### {repas_type}")
            for data in recettes_liste:
                recette = data["recette"]
                nb_personnes = data["nb_personnes"]
                fav = "⭐" if recette['name'] in users[user].get("favorites", []) else ""
                st.write(f"- **{recette['name']}** {fav} ({', '.join(recette['tags']) if recette['tags'] else 'Aucun tag'}) — pour {nb_personnes} personnes")
        # Liste de courses
        if st.button("🛒 Générer la liste de courses pour la semaine"):
            ingredients_total = {}
            for recettes_liste in st.session_state['menu_semaine'].values():
                for data in recettes_liste:
                    recette = data["recette"]
                    nb_personnes = data["nb_personnes"]
                    facteur = nb_personnes / recette.get("nb_personnes", 4)
                    for ing in recette['ingredients']:
                        parts = ing.split(" ", 2)
                        if len(parts) >= 3 and parts[0].replace(',', '.').replace('/', '').replace('-', '').replace('.', '').isdigit():
                            try:
                                quantite = float(parts[0].replace(',', '.'))
                                unite = parts[1]
                                nom = parts[2]
                                cle = f"{unite} {nom}"
                                if cle not in ingredients_total:
                                    ingredients_total[cle] = 0
                                ingredients_total[cle] += quantite * facteur
                            except:
                                if ing not in ingredients_total:
                                    ingredients_total[ing] = 0
                                ingredients_total[ing] += 1 * facteur
                        else:
                            if ing not in ingredients_total:
                                ingredients_total[ing] = 0
                            ingredients_total[ing] += 1 * facteur
            st.subheader("Liste de courses :")
            liste_courses = "\n".join(
                f"{round(qty, 2)} {cle}" if qty != 1 else cle for cle, qty in ingredients_total.items()
            )
            st.text_area("À copier dans vos notes :", value=liste_courses, height=250)
    else:
        st.info("Générez un menu pour afficher la liste de courses !")

# --------- PAGE : Ajouter une recette ---------
elif page == "Ajouter une recette":
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

# --------- PAGE : Répertoire de recettes ---------
elif page == "Répertoire de recettes":
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

# --------- PAGE : Mes favoris ---------
elif page == "Mes favoris":
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

# --------- PAGE : Historique des menus ---------
elif page == "Historique des menus":
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

# --------- PAGE : Modifier une recette ---------
elif page == "Modifier une recette":
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

# --------- PAGE : Supprimer une recette ---------
elif page == "Supprimer une recette":
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