import streamlit as st
import pandas as pd
import datetime
import os

# ---------------- CONFIGURATION & BDD ---------------- #
DB_FILE = "clients_db.csv"
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/3724/3724720.png"

def charger_donnees():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        return df
    return pd.DataFrame(columns=["Nom", "Prenom", "Age", "Email", "Password", "Points", "Statut"])

def sauvegarder_donnees(df):
    df.to_csv(DB_FILE, index=False)

if "clients" not in st.session_state:
    st.session_state.clients = charger_donnees()
if "user_connected" not in st.session_state:
    st.session_state.user_connected = None
if "show_signup" not in st.session_state:
    st.session_state.show_signup = False

# ---------------- STYLE VM MAGASIN ---------------- #
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    [data-testid="stSidebar"] { background-color: #343a40; color: white; }
    .offer-card { background-color: white; padding: 15px; border-radius: 12px; border: 2px solid #28a745; margin-bottom: 10px; text-align: center; }
    .new-price { color: #28a745; font-weight: bold; font-size: 1.3em; }
    .old-price { text-decoration: line-through; color: #dc3545; }
    </style>
    """, unsafe_allow_html=True)

# ---------------- SIDEBAR (LOGO & CONNEXION) ---------------- #
with st.sidebar:
    st.image(LOGO_URL, width=80)
    st.markdown("<h2 style='color:white;'>VM Magasin</h2>", unsafe_allow_html=True)
    
    if st.session_state.user_connected is None:
        st.subheader("🔑 Connexion")
        email_log = st.text_input("Email")
        pass_log = st.text_input("Mot de passe", type="password")
        
        if st.button("Se connecter"):
            user = st.session_state.clients[(st.session_state.clients["Email"] == email_log) & (st.session_state.clients["Password"] == pass_log)]
            if not user.empty:
                st.session_state.user_connected = user.iloc[0].to_dict()
                st.session_state.show_signup = False # Ferme l'inscription si elle était ouverte
                st.rerun()
            else:
                st.error("Identifiants incorrects")
        
        st.write("---")
        if st.button("🆕 Créer un compte"):
            st.session_state.show_signup = True
            st.rerun()
    else:
        st.success(f"Salut, {st.session_state.user_connected['Prenom']} !")
        st.metric("Mes Points", f"{st.session_state.user_connected['Points']} pts")
        if st.button("Se déconnecter"):
            st.session_state.user_connected = None
            st.rerun()

# ---------------- FORMULAIRE D'INSCRIPTION (S'affiche en haut si activé) ---------------- #
if st.session_state.show_signup and st.session_state.user_connected is None:
    with st.expander("📝 FORMULAIRE D'INSCRIPTION - VM MAGASIN", expanded=True):
        with st.form("inscription"):
            c1, c2 = st.columns(2)
            nom = c1.text_input("Nom")
            prenom = c2.text_input("Prénom")
            age = st.number_input("Âge", min_value=12)
            email = st.text_input("Email de contact")
            mdp = st.text_input("Mot de passe", type="password")
            
            if st.form_submit_button("Valider la création"):
                if not email or not mdp:
                    st.error("Email et Mot de passe obligatoires")
                else:
                    new_user = pd.DataFrame([{"Nom": nom, "Prenom": prenom, "Age": age, "Email": email, "Password": mdp, "Points": 0, "Statut": "Actif"}])
                    st.session_state.clients = pd.concat([st.session_state.clients, new_user], ignore_index=True)
                    sauvegarder_donnees(st.session_state.clients)
                    st.success(f"✅ Compte créé ! Un email a été envoyé à {email} (simulation).")
                    st.session_state.show_signup = False # On ferme le formulaire
                    # st.rerun() # Optionnel : relance pour mettre à jour l'affichage

# ---------------- INTERFACE DU MAGASIN (Toujours accessible) ---------------- #
st.title("🛒 Notre Magasin")

tabs = st.tabs(["🔥 Offres Spéciales", "📖 Catalogue", "💎 Ma Fidélité"])

with tabs[0]:
    st.subheader("Les promos VM")
    colA, colB = st.columns(2)
    with colA:
        st.markdown('<div class="offer-card"><b>Boucherie</b><br>Escalope dinde (1kg)<br><span class="old-price">9,59€</span> <span class="new-price">8,59€</span></div>', unsafe_allow_html=True)
    with colB:
        st.markdown('<div class="offer-card"><b>Fidélité</b><br>Bonus Nouveau Client<br><span class="new-price">+10 Points offerts</span></div>', unsafe_allow_html=True)

with tabs[1]:
    st.subheader("Rechercher un produit")
    search = st.text_input("🔍 Tapez le nom d'un article...")
    # Simulation de données
    df_prod = pd.DataFrame({"Article": ["Lait", "Pain", "Pommes", "Escalope"], "Prix": ["1.20€", "0.90€", "2.50€", "8.59€"], "Stock": ["Oui", "Oui", "Oui", "Oui"]})
    st.table(df_prod)

with tabs[2]:
    st.subheader("Mon Espace Fidélité")
    if st.session_state.user_connected:
        st.write(f"Titulaire : **{st.session_state.user_connected['Prenom']} {st.session_state.user_connected['Nom']}**")
        st.progress(min(int(st.session_state.user_connected['Points'])/100, 1.0))
        st.write("Prochain coupon : 100 points")
    else:
        st.info("Connectez-vous pour voir vos avantages personnalisés.")
