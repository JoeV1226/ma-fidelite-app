import streamlit as st
import pandas as pd
import datetime
import os
import smtplib
from email.mime.text import MIMEText

# ---------------- CONFIGURATION & BDD ---------------- #
DB_FILE = "clients_db.csv"

def charger_donnees():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Nom", "Prenom", "Age", "Email", "Password", "Points", "Statut"])

def sauvegarder_donnees(df):
    df.to_csv(DB_FILE, index=False)

if "clients" not in st.session_state:
    st.session_state.clients = charger_donnees()
if "user_connected" not in st.session_state:
    st.session_state.user_connected = None
if "show_signup" not in st.session_state:
    st.session_state.show_signup = False

# ---------------- FONCTION ENVOI EMAIL ---------------- #
def envoyer_confirmation(email_dest, nom_client):
    # Remplace par tes vrais identifiants (Attention: utilise un mot de passe d'application)
    msg = MIMEText(f"Bonjour {nom_client},\n\nVotre compte VM Magasin a été créé avec succès ! Vous pouvez maintenant vous connecter.")
    msg['Subject'] = 'Confirmation de création de compte VM Magasin'
    msg['From'] = "ton-email@gmail.com"
    msg['To'] = email_dest

    # Simulation d'envoi (pour éviter de bloquer sans config SMTP)
    st.info(f"📨 Un e-mail de confirmation a été envoyé à {email_dest}")
    
    # Décommenter ci-dessous pour activer le vrai envoi (nécessite config SMTP)
    # with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
    #     server.login("ton-email@gmail.com", "ton-mot-de-passe-application")
    #     server.sendmail("ton-email@gmail.com", email_dest, msg.as_string())

# ---------------- INTERFACE SIDEBAR ---------------- #
with st.sidebar:
    st.markdown("### 🔑 Connexion")
    
    if st.session_state.user_connected is None:
        email_input = st.text_input("Email")
        pass_input = st.text_input("Mot de passe", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Se connecter"):
                user = st.session_state.clients[
                    (st.session_state.clients["Email"] == email_input) & 
                    (st.session_state.clients["Password"] == pass_input)
                ]
                if not user.empty:
                    st.session_state.user_connected = user.iloc[0].to_dict()
                    st.session_state.show_signup = False
                    st.rerun()
                else:
                    st.error("Identifiants incorrects")
        
        with col2:
            if st.button("S'inscrire"):
                st.session_state.show_signup = True
                st.rerun()
    else:
        st.success(f"Connecté : {st.session_state.user_connected['Nom']}")
        if st.button("Déconnexion"):
            st.session_state.user_connected = None
            st.rerun()

# ---------------- PAGE INSCRIPTION ---------------- #
if st.session_state.show_signup and st.session_state.user_connected is None:
    st.header("📝 Créer mon compte VM Magasin")
    with st.form("inscription_complete"):
        col_n, col_p = st.columns(2)
        nom = col_n.text_input("Nom")
        prenom = col_p.text_input("Prénom")
        age = st.number_input("Âge", min_value=12, max_value=100)
        email = st.text_input("Adresse Email")
        mdp = st.text_input("Choisissez un mot de passe", type="password")
        
        if st.form_submit_button("Valider l'inscription"):
            if email in st.session_state.clients["Email"].values:
                st.error("Cet e-mail est déjà utilisé.")
            elif not email or not mdp:
                st.error("Veuillez remplir tous les champs.")
            else:
                # Ajout à la base
                new_user = pd.DataFrame([{
                    "Nom": nom, "Prenom": prenom, "Age": age, 
                    "Email": email, "Password": mdp, "Points": 0, "Statut": "Actif"
                }])
                st.session_state.clients = pd.concat([st.session_state.clients, new_user], ignore_index=True)
                sauvegarder_donnees(st.session_state.clients)
                
                # Email
                envoyer_confirmation(email, prenom)
                
                st.success("Compte créé ! Vous pouvez maintenant vous connecter à gauche.")
                st.session_state.show_signup = False

# ---------------- CONTENU PRINCIPAL ---------------- #
if not st.session_state.show_signup:
    st.title("🛒 Bienvenue chez VM Magasin")
    
    # Ici tu remets tes onglets (Offres, Catalogue, Points)
    t1, t2 = st.tabs(["🔥 Offres", "💎 Mes Points"])
    
    with t1:
        st.write("Découvrez nos promos ici...")
        
    with t2:
        if st.session_state.user_connected:
            pts = st.session_state.user_connected['Points']
            st.metric("Mon solde", f"{pts} points")
        else:
            st.info("Connectez-vous pour voir vos points.")
