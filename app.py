import streamlit as st
import pandas as pd
import datetime
import os

# ---------------- CONFIGURATION ---------------- #
DB_FILE = "clients_db.csv"

def charger_donnees():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        return df
    return pd.DataFrame(columns=["Email", "Password", "Nom", "Points", "Dernier_Achat"])

def sauvegarder_donnees(df):
    df.to_csv(DB_FILE, index=False)

# Initialisation des données
if "clients" not in st.session_state:
    st.session_state.clients = charger_donnees()
if "user_connected" not in st.session_state:
    st.session_state.user_connected = None

# ---------------- STYLE ---------------- #
st.markdown("""
    <style>
    .offer-card { background-color: #fff3cd; padding: 15px; border-radius: 10px; border-left: 5px solid #ffc107; margin-bottom: 10px; }
    .old-price { text-decoration: line-through; color: red; font-size: 0.9em; }
    .new-price { color: green; font-weight: bold; font-size: 1.2em; }
    </style>
    """, unsafe_allow_html=True)

# ---------------- INTERFACE ---------------- #
st.title("🛒 Mon Magasin Pro")

# Barre latérale pour la connexion
with st.sidebar:
    if st.session_state.user_connected is None:
        st.subheader("Connexion")
        email_log = st.text_input("Email")
        pass_log = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            user = st.session_state.clients[(st.session_state.clients["Email"] == email_log) & (st.session_state.clients["Password"] == pass_log)]
            if not user.empty:
                st.session_state.user_connected = user.iloc[0].to_dict()
                st.rerun()
            else:
                st.error("Identifiants incorrects")
        
        st.divider()
        st.subheader("Pas encore de compte ?")
        if st.button("Créer un compte"):
            st.session_state.page = "Inscription"
    else:
        st.success(f"Connecté : {st.session_state.user_connected['Nom']}")
        if st.button("Se déconnecter"):
            st.session_state.user_connected = None
            st.rerun()

# Menu principal
tabs = st.tabs(["🔥 Offres Spéciales", "📖 Catalogue", "💎 Mes Points", "⚙️ Admin"])

# --- TAB 1 : OFFRES SPÉCIALES ---
with tabs[0]:
    st.header("Promotions de la semaine")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="offer-card">
            <h4>🥩 Boucherie</h4>
            <p>1kg d'escalopes de dinde</p>
            <span class="old-price">9,59€</span> ➡️ <span class="new-price">8,59€</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="offer-card">
            <h4>🍎 Rayon Frais</h4>
            <p>Filet de pommes 2kg</p>
            <span class="old-price">3,50€</span> ➡️ <span class="new-price">2,49€</span>
        </div>
        """, unsafe_allow_html=True)

# --- TAB 2 : CATALOGUE ---
with tabs[1]:
    st.header("Catalogue Produits")
    # Simulation d'un stock
    catalogue = pd.DataFrame({
        "Produit": ["Lait", "Pain", "Escalope dinde", "Pâtes", "Café", "Yaourts"],
        "Prix": ["1,20€", "0,90€", "8,59€", "1,50€", "4,20€", "2,10€"],
        "Stock": ["En stock", "En stock", "En stock", "Rupture", "En stock", "En stock"]
    })
    
    search = st.text_input("🔍 Chercher un produit...")
    if search:
        catalogue = catalogue[catalogue["Produit"].str.contains(search, case=False)]
    
    st.table(catalogue)

# --- TAB 3 : MES POINTS (AVEC CONNEXION) ---
with tabs[2]:
    st.header("Espace Fidélité")
    if st.session_state.user_connected:
        user_email = st.session_state.user_connected['Email']
        # Rafraîchir les points depuis la base
        current_user_data = st.session_state.clients[st.session_state.clients["Email"] == user_email].iloc[0]
        
        st.metric("Mon solde de points", f"{current_user_data['Points']} pts")
        st.progress(min(int(current_user_data['Points']) / 100, 1.0))
        st.write("Cadeau à 100 points !")
    else:
        st.warning("Veuillez vous connecter dans la barre latérale pour voir vos points.")

# --- TAB 4 : ADMIN (POUR CRÉER LES COMPTES) ---
with tabs[3]:
    st.header("Administration")
    with st.expander("Enregistrer un nouveau client"):
        with st.form("inscription_form"):
            new_nom = st.text_input("Nom")
            new_email = st.text_input("Email")
            new_pass = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Créer le compte"):
                new_user = pd.DataFrame([{"Email": new_email, "Password": new_pass, "Nom": new_nom, "Points": 0, "Dernier_Achat": datetime.date.today()}])
                st.session_state.clients = pd.concat([st.session_state.clients, new_user], ignore_index=True)
                sauvegarder_donnees(st.session_state.clients)
                st.success("Compte créé ! Connectez-vous à gauche.")

    if st.checkbox("Voir tous les clients (Debug)"):
        st.dataframe(st.session_state.clients)
