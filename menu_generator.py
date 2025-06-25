import streamlit as st
import random
from datetime import date
from storage import charger_recettes, sauvegarder_menus, charger_menus, charger_users

SAISONS = ["Printemps", "Été", "Automne", "Hiver"]
TYPES_REPAS = ["Petit déjeuner", "Lunch", "Dîner", "Dessert"]
TAGS_NUTRITION = [
    "Poisson maigre", "Poisson gras", "Viande blanche", "Viande rouge", "Végétarien", "Vegan"
]

def show_menu_generator(user):
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

            # Ajoute le nb de personnes pour chaque plat
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
                nb_personnes = data.get("nb_personnes", 4)
                fav = "⭐" if recette['name'] in users[user].get("favorites", []) else ""
                st.write(f"- **{recette['name']}** {fav} ({', '.join(recette['tags']) if recette['tags'] else 'Aucun tag'}) — pour {nb_personnes} personnes")
        # Liste de courses
        if st.button("🛒 Générer la liste de courses pour la semaine"):
            ingredients_total = {}
            for recettes_liste in st.session_state['menu_semaine'].values():
                for data in recettes_liste:
                    recette = data["recette"]
                    nb_personnes = data.get("nb_personnes", 4)
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