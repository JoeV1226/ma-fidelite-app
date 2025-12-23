import streamlit as st
import pandas as pd
import datetime
import os

# ---------------- CONFIGURATION ---------------- #
DB_FILE = "clients_db.csv"
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/3724/3724720.png" # Remplace par l'URL de ton logo VM

def charger_donnees():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        return df
    return pd.DataFrame(columns=["Email", "Password", "Nom", "Points", "Dernier_Achat"])

def sauvegarder_donnees(df):
    df.to_csv(DB_FILE, index=False)

if "clients" not in st.session_state:
    st.session_state.clients = charger_donnees()
if "user_connected" not in st.session_state:
    st.session_state.user_connected = None

# ---------------- STYLE PERSONNALISÉ (Couleurs de l'image) ---------------- #
st.markdown(f"""
    <style>
    /* Fond de l'application */
    .stApp {{ background-color: #f8f9fa; }}
    
    /* Sidebar - Gris Anthracite */
    [data-testid="stSidebar"] {{
        background-color: #343a40;
        color: white;
    }}
    
    /* Titres et boutons */
    h1, h2, h3 {{ color: #1e7e34; font-family: 'Arial'; }}
    
    .stButton>button {{
        background-color: #28a745;
        color: white;
        border-radius: 10px;
        border: none;
        width: 100%;
    }}

    /* Cartes des offres */
    .offer-card {{
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #28a745;
        box-shadow: 2px 2px 12px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 15px;
    }}
    .old-price {{ text-decoration: line-through; color: #dc3545; font-size: 1em; }}
    .new-price {{ color: #28a745; font-weight: bold; font-size: 1.5em; }}
    .badge {{ background-color: #ffc107; padding: 5px 10px; border-radius: 5px; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

# ---------------- SIDEBAR (Connexion & Logo) ---------------- #
with st.sidebar:
    st.image(LOGO_URL, width=100)
    st.markdown("<h2 style='color:white; text-align:center;'>VM Magasin</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-style:italic;'>La qualité, le prix pour tous</p>", unsafe_allow_html=True)
    
    st.divider()
    
    if st.session_state.user_connected is None:
        st.subheader("🔑 Accès Client")
        email_log = st.text_input("Email")
        pass_log = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            user = st.session_state.clients[(st.session_state.clients["Email"] == email_log) & (st.session_state.clients["Password"] == pass_log)]
            if not user.empty:
                st.session_state.user_connected = user.iloc[0].to_dict()
                st.rerun()
            else:
                st.error("Identifiants incorrects")
    else:
        st.success(f"Bienvenue, {st.session_state.user_connected['Nom']}")
        if st.button("Se déconnecter"):
            st.session_state.user_connected = None
            st.rerun()

# ---------------- CONTENU PRINCIPAL ---------------- #
tabs = st.tabs(["⭐ Nos Offres", "📋 Catalogue", "💰 Mes Points", "⚙️ Gestion"])

# --- TAB 1 : OFFRES SPÉCIALES ---
with tabs[0]:
    st.markdown("## 🏷️ Offres Spéciales")
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("""
        <div class="offer-card">
            <span class="badge">BOUCHERIE</span>
            <h4>Escalopes de dinde (1kg)</h4>
            <span class="old-price">9,59€</span> <span style='font-size:1.5em;'>➡️</span> <span class="new-price">8,59€</span>
            <p style='color:gray; font-size:0.8em;'>Valable jusqu'au 31/12</p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="offer-card">
            <span class="badge">RAYON FRAIS</span>
            <h4>Filet de pommes (2kg)</h4>
            <span class="old-price">3,50€</span> <span style='font-size:1.5em;'>➡️</span> <span class="new-price">2,49€</span>
            <p style='color:gray; font-size:0.8em;'>Offre limitée</p>
        </div>
        """, unsafe_allow_html=True)

# --- TAB 2 : CATALOGUE ---
with tabs[1]:
    st.markdown("## 📖 Catalogue Produits")
    search = st.text_input("🔍 Rechercher un article dans le magasin...")
    
    catalogue_data = [
        {"Produit": "Lait Demi-écrémé", "Prix": "1.10€", "Rayon": "Frais", "État": "En stock"},
        {"Produit": "Pain de mie", "Prix": "0.95€", "Rayon": "Boulangerie", "État": "En stock"},
        {"Produit": "Huile de Tournesol", "Prix": "2.50€", "Rayon": "Épicerie", "État": "Rupture de stock"},
        {"Produit": "Escalope de dinde", "Prix": "8.59€", "Rayon": "Boucherie", "État": "En stock"},
    ]
    df_cat = pd.DataFrame(catalogue_data)
    
    if search:
        df_cat = df_cat[df_cat["Produit"].str.contains(search, case=False)]
    
    st.dataframe(df_cat, use_container_width=True, hide_index=True)

# --- TAB 3 : MES POINTS ---
with tabs[2]:
    st.markdown("## 💎 Espace Fidélité")
    if st.session_state.user_connected:
        # On récupère les points à jour
        email = st.session_state.user_connected['Email']
        user_data = st.session_state.clients[st.session_state.clients["Email"] == email].iloc[0]
        
        col_pts, col_info = st.columns(2)
        col_pts.metric("Solde actuel", f"{user_data['Points']} Points")
        
        pts_manquants = 100 - int(user_data['Points'])
        if pts_manquants > 0:
            st.info(f"Il vous manque **{pts_manquants} points** pour obtenir votre bon d'achat de 5€ !")
        else:
            st.success("🎁 Vous avez un bon d'achat disponible !")
            
        st.progress(min(int(user_data['Points']) / 100, 1.0))
    else:
        st.warning("Veuillez vous connecter pour voir vos points de fidélité.")

# --- TAB 4 : ADMIN ---
with tabs[3]:
    st.markdown("## ⚙️ Administration")
    
    with st.expander("➕ Créer un nouveau compte client"):
        with st.form("new_user"):
            nom = st.text_input("Nom Complet")
            email = st.text_input("Adresse Email")
            mdp = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Créer le compte"):
                if email in st.session_state.clients["Email"].values:
                    st.error("Cet email existe déjà !")
                else:
                    new_line = pd.DataFrame([{"Email": email, "Password": mdp, "Nom": nom, "Points": 0, "Dernier_Achat": datetime.date.today()}])
                    st.session_state.clients = pd.concat([st.session_state.clients, new_line], ignore_index=True)
                    sauvegarder_donnees(st.session_state.clients)
                    st.success("Compte créé avec succès !")

    if st.checkbox("Afficher la base clients"):
        st.write(st.session_state.clients)
