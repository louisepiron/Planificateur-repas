import streamlit as st
from storage import charger_users, sauvegarder_users

def user_login():
    st.sidebar.markdown('<div class="sidebar-title">🍽️ Famille Menu</div>', unsafe_allow_html=True)
    users = charger_users()
    if 'username' not in st.session_state or not st.session_state['username']:
        login_mode = st.sidebar.radio("Connexion", ["Se connecter", "Créer un compte"], key="login_radio")
        if login_mode == "Se connecter":
            username = st.sidebar.text_input("Nom d'utilisateur", key="login_user")
            password = st.sidebar.text_input("Mot de passe", type="password", key="login_pw")
            login_btn = st.sidebar.button("Se connecter", key="login_btn")
            if login_btn:
                if username in users and users[username]["password"] == password:
                    st.session_state['username'] = username
                    st.sidebar.success(f"Bienvenue {username} !")
                else:
                    st.sidebar.error("Nom d'utilisateur ou mot de passe incorrect.")
            st.stop()
        else:
            new_username = st.sidebar.text_input("Choisir un nom d'utilisateur", key="new_user")
            new_password = st.sidebar.text_input("Choisir un mot de passe", type="password", key="new_pw")
            create_btn = st.sidebar.button("Créer le compte", key="create_btn")
            if create_btn:
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
                    st.sidebar.success(f"Compte créé, bienvenue {new_username} !")
            st.stop()
    else:
        st.sidebar.markdown(f"👤 <b>{st.session_state['username']}</b>", unsafe_allow_html=True)
        if st.sidebar.button("Se déconnecter"):
            st.session_state['username'] = ""
            st.experimental_rerun()
        return st.session_state['username']