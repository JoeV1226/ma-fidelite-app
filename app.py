import streamlit as st
import pandas as pd
import datetime
import os

# ---------------- CONFIGURATION & FICHIER ---------------- #

DB_FILE = "database_fidelite.csv"

def charger_donnees():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        # S'assurer que la date est au bon format
        df["Dernier_Achat"] = pd.to_datetime(df["Dernier_Achat"]).dt.date
        return df
    else:
        return pd.DataFrame(columns=[
            "ID", "Nom", "Points", "Dernier_Achat", "Email", "Segment"
        ])

def sauvegarder_donnees():
    st.session_state.clients.to_csv(DB_FILE, index=False)

# ---------------- INITIALISATION ---------------- #

st.set_page_config(page_title="Mon Magasin Plus", layout="centered")

if "clients" not in st.session_state:
    st.session_state.clients = charger_donnees()

# CSS pour le look "App Mobile"
st.markdown("""
    <style>
    .stProgress > div > div > div > div { background-color: #0050aa; }
    .coupon-card {
        padding: 15px;
        border-radius: 10px;
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------- FONCTIONS MÉTIER ---------------- #

def ajouter_points(id_client, montant):
    idx = st.session_state.clients.index[st.session_state.clients["ID"] == id_client]
    if not idx.empty:
        pts = int(montant // 5)
        st.session_state.clients.at[idx[0], "Points"] += pts
        st.session_state.clients.at[idx[0], "Dernier_Achat"] = datetime.date.today()
        sauvegarder_donnees() # Sauvegarde immédiate après achat
        return pts
    return 0

# ---------------- INTERFACE ---------------- #

st.title("💙 Mon Magasin Plus")

tabs = st.tabs(["📱 Ma Carte", "🎟️ Mes Coupons", "🛒 Encaisser", "⚙️ Admin"])

# --- TAB 1 : VUE CLIENT ---
with tabs[0]:
    search_id = st.number_input("Entrez votre ID Client", min_value=0, step=1)
    client_data = st.session_state.clients[st.session_state.clients["ID"] == search_id]
    
    if not client_data.empty:
        row = client_data.iloc[0]
        st.header(f"Ravi de vous revoir, {row['Nom']} !")
        
        # Jauge de progression
        pts = row['Points']
        palier = 50
        progress = min(pts / palier, 1.0)
        st.write(f"**Points cumulés : {pts}**")
        st.progress(progress)
        
        if pts >= palier:
            st.success("🎉 Vous avez débloqué un bon d'achat !")
        else:
            st.info(f"Encore {palier - pts} points pour votre prochain cadeau.")
    else:
        st.caption("Entrez votre identifiant pour voir vos points.")

# --- TAB 2 : COUPONS ---
with tabs[1]:
    st.subheader("Mes avantages")
    coupons = [
        {"nom": "Coupons Fruits & Légumes", "desc": "-15% dès 10 pts", "req": 10},
        {"nom": "Offre Boulangerie", "desc": "3 achetés + 1 offert", "req": 0},
        {"nom": "Bon de 5€", "desc": "Réduction immédiate", "req": 50}
    ]
    
    for c in coupons:
        st.markdown(f"""<div class="coupon-card">
            <strong>{c['nom']}</strong><br>{c['desc']}
        </div>""", unsafe_allow_html=True)
        st.button(f"Activer l'offre", key=c['nom'])

# --- TAB 3 : CAISSE ---
with tabs[2]:
    st.subheader("Enregistrement Achat")
    c_id = st.number_input("Scanner ID", min_value=0, key="caisse_id")
    montant = st.number_input("Montant (€)", min_value=0.0)
    
    if st.button("Valider la transaction"):
        pts_gagnes = ajouter_points(c_id, montant)
        if pts_gagnes > 0:
            st.success(f"Bravo ! +{pts_gagnes} points ajoutés.")
            st.balloons()
        else:
            st.error("ID Client inconnu.")

# --- TAB 4 : ADMIN ---
with tabs[3]:
    st.subheader("Paramètres & Base de données")
    
    if st.checkbox("Afficher la liste des clients"):
        st.dataframe(st.session_state.clients)
    
    with st.expander("Inscrire un nouveau client"):
        with st.form("inscription"):
            n_id = st.number_input("ID unique", min_value=1)
            n_nom = st.text_input("Nom")
            n_mail = st.text_input("Email")
            if st.form_submit_button("Enregistrer"):
                new_data = pd.DataFrame([{"ID": n_id, "Nom": n_nom, "Points": 0, "Dernier_Achat": datetime.date.today(), "Email": n_mail, "Segment": "Nouveau"}])
                st.session_state.clients = pd.concat([st.session_state.clients, new_data], ignore_index=True)
                sauvegarder_donnees()
                st.success("Client créé avec succès !")
