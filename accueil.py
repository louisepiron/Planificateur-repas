import streamlit as st

def show_accueil():
    st.markdown(
        """
        <div style="background:linear-gradient(90deg,#fceabb 0,#f8b500 100%);padding:1.5em 2em 1.5em 2em;border-radius:18px;margin-top:1em;">
            <h1 style="color:#2B6CB0;margin-bottom:0.5em;">Bienvenue sur Famille Menu 👋</h1>
            <h3 style="color:#374151;font-weight:normal;margin-top:0;">Votre assistant pour planifier, cuisiner et profiter&nbsp;!</h3>
        </div>
        """, unsafe_allow_html=True
    )
    st.write(
        """
        Ce site vous aide à :
        - Générer automatiquement des menus variés et adaptés à vos envies.
        - Gérer votre répertoire de recettes familial.
        - Ajouter, modifier, supprimer ou marquer vos recettes préférées ⭐.
        - Adapter les quantités selon le nombre de personnes à table.
        - Garder une trace de vos menus semaine après semaine pour vous inspirer.
        - Partager la charge mentale du quotidien en famille !

        👉 Utilisez le menu à gauche pour démarrer.
        """
    )
    st.info("Sélectionnez une page via la barre latérale pour commencer à planifier vos repas ou gérer vos recettes.")