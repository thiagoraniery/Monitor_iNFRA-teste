import streamlit as st
import pandas as pd
import plotly.express as px
import unicodedata
from supabase import create_client
from datetime import datetime, date, timedelta
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# ==============================================================================
# 1. DESIGN & IDENTIDADE VISUAL (CSS PREMIUM FINAL)
# ==============================================================================
st.set_page_config(page_title="Monitor iNFRA", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #000000; }
    
    section[data-testid="stSidebar"] { background-color: #0e1117; border-right: 1px solid #262730; }
    .sidebar-label { color: #F75D00; font-size: 0.9rem; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; margin-top: 12px; border-bottom: 1px solid #262730; padding-bottom: 5px; }

    /* Padronização Total de Botões de Navegação e Filtros */
    div.stButton > button {
        height: 4.2rem !important;
        font-size: 1.1rem !important;
        background-color: #F75D00 !important;
        color: #ffffff !important;
        border-radius: 12px !important;
        border: none !important;
        font-weight: 700 !important;
        transition: 0.3s ease;
        margin-bottom: 10px !important;
        width: 100% !important;
        display: block !important;
        letter-spacing: 0.5px;
    }
    div.stButton > button:hover { background-color: #ff7a29 !important; transform: scale(1.02); box-shadow: 0 6px 20px rgba(247, 93, 0, 0.4); }

    div[data-baseweb="input"], div[data-baseweb="select"] {
        background-color: #1c1f26 !important;
        border-radius: 8px !important;
        border: 1px solid #2d303e !important;
    }

    div[data-testid="metric-container"] {
        background-color: #1c1f26; border: 1px solid #2d303e; padding: 20px;
        border-radius: 12px; border-left: 5px solid #F75D00;
    }
    
    .main-title-container { display: flex; align-items: flex-end; justify-content: center; margin-bottom: 3rem; margin-top: 1rem; }
    .title-monitor { font-weight: 700; font-size: 3.5rem; color: #ffffff; margin-right: 1.2rem; line-height: 1; }
    .infra-i-wrapper { display: flex; flex-direction: column; align-items: center; justify-content: flex-end; height: 3.5rem; margin-right: 0.1rem; }
    .infra-i-dot { width: 0.6rem; height: 0.6rem; background-color: #F75D00; border-radius: 50%; margin-bottom: 0.3rem; }
    .infra-i-body { width: 0.6rem; height: 2.4rem; background-color: #ffffff; border-radius: 0.05rem; }
    .title-nfra { font-weight: 700; font-size: 3.5rem; color: #F75D00; line-height: 1; }
    
    .narrative-box { 
        font-size: 1.25rem !important; 
        line-height: 1.9 !important; 
        color: #e0e0e0; 
        background: linear-gradient(145deg, #1c1f26, #16191f);
        padding: 30px; 
        border-radius: 15px; 
        border: 1px solid #2d303e;
        border-left: 4px solid #F75D00;
        text-align: justify;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .highlight-sector { color: #F75D00; font-weight: 800; text-transform: uppercase; }
    .news-link { color: #F75D00; text-decoration: none; font-size: 1.3rem; margin-left: 5px; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. SISTEMA DE ESTADO E LIMPEZA
# ==============================================================================
if 'pagina_ativa' not in st.session_state: st.session_state.pagina_ativa = "noticias"
if 'limit' not in st.session_state: st.session_state.limit = 100

def reset_filtros():
    """Limpa as chaves de estado sem disparar mensagens visuais"""
    st.session_state["busca_input"] = ""
    st.session_state["setores_input"] = []
    st.session_state["data_ini_input"] = date(2026, 1, 1)

def set_pag(name): st.session_state.pagina_ativa = name

def limpar_titulo(titulo):
    if not isinstance(titulo, str): return titulo
    termos = ["Agência iNFRA", "AGÊNCIA INFRA", "Agencia iNFRA", "Agencia Infra", "iNFRA"]
    for t in termos: titulo = titulo.replace(t, "").strip()
    return titulo.lstrip(" -|: ")

@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

@st.cache_data(ttl=300)
def carregar_dados():
    supabase = init_connection()
    res = supabase.table("noticias_infra").select("*").order("data_noticia", desc=True).limit(6000).execute()
    df = pd.DataFrame(res.data)
    if not df.empty:
        df['data_noticia'] = pd.to_datetime(df['data_noticia'])
        df['titulo_limpo'] = df['titulo'].apply(limpar_titulo)
    return df

df_bruto = carregar_dados()

# ==============================================================================
# 3. SIDEBAR (FILTROS E NAVEGAÇÃO PADRONIZADA)
# ==============================================================================
with st.sidebar:
    st.markdown('<p class="sidebar-label">Navegação</p>', unsafe_allow_html=True)
    st.button("🗞️ NOTÍCIAS RECENTES", on_click=lambda: set_pag("noticias"))
    st.button("📊 PAINEL DE INSIGHTS", on_click=lambda: set_pag("insights"))
    st.button("📋 BOLETIM SEMANAL", on_click=lambda: set_pag("resumo"))
    
    st.divider()
    
    st.markdown('<p class="sidebar-label">Período</p>', unsafe_allow_html=True)
    max_banco = df_bruto['data_noticia'].max().date() if not df_bruto.empty else date.today()
    
    d_inicio = st.date_input("Início", key="data_ini_input", value=date(2026, 1, 1), 
                            min_value=date(2025, 1, 1), max_value=date(2026, 12, 31), format="DD/MM/YYYY")
    d_fim = st.date_input("Fim", value=max_banco, min_value=date(2025, 1, 1), max_value=date(2026, 12, 31), format="DD/MM/YYYY")

    st.markdown('<p class="sidebar-label">Setores</p>', unsafe_allow_html=True)
    cats = sorted(df_bruto['categoria'].unique().tolist()) if not df_bruto.empty else []
    sel_setores = st.multiselect("Setores", key="setores_input", options=cats, placeholder="Todos", label_visibility="collapsed")

    st.markdown('<p class="sidebar-label">Busca</p>', unsafe_allow_html=True)
    busca = st.text_input("Busca", key="busca_input", placeholder="Palavra-chave...", label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.button("🔄 LIMPAR FILTROS", on_click=reset_filtros)

# Filtragem Global
df_f = df_bruto.copy()
if not df_f.empty:
    df_f = df_f[(df_f['data_noticia'].dt.date >= d_inicio) & (df_f['data_noticia'].dt.date <= d_fim)]
    if sel_setores: df_f = df_f[df_f['categoria'].isin(sel_setores)]
    if busca:
        df_f = df_f[df_f['titulo_limpo'].str.contains(busca, case=False, na=False) | 
                    df_f['conteudo'].str.contains(busca, case=False, na=False)]

st.markdown("""
<div class="main-title-container">
    <span class="title-monitor">Monitor</span>
    <div class="infra-i-wrapper">
        <div class="infra-i-dot"></div>
        <div class="infra-i-body"></div>
    </div>
    <span class="title-nfra">NFRA</span>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 4. PÁGINAS
# ==============================================================================

if st.session_state.pagina_ativa == "noticias":
    if not df_f.empty:
        st.markdown(f"### Feed ({len(df_f)} resultados)")
        for _, r in df_f.head(st.session_state.limit).iterrows():
            with st.expander(f"{r['data_noticia'].strftime('%d/%m/%Y')} | {r['titulo_limpo']}"):
                st.markdown(f"<span style='color:#F75D00; font-weight:600;'>Setor: {r['categoria']}</span>", unsafe_allow_html=True)
                st.write(r['conteudo'].replace("$", r"\$").replace("•", "\n\n- "))
                st.link_button("🔗 Ver conteúdo original", r['link'])
        if len(df_f) > st.session_state.limit:
            if st.button("📥 Carregar Mais"): st.session_state.limit += 100; st.rerun()
    else: st.info("Nenhuma notícia encontrada.")

elif st.session_state.pagina_ativa == "insights":
    if not df_f.empty:
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Volume no Período", len(df_f))
        k2.metric("Setor em Destaque", df_f['categoria'].mode()[0])
        k3.metric("Total na Base", len(df_bruto))
        k4.metric("Última Captura", df_f['data_noticia'].max().strftime('%d/%m/%Y'))

        st.divider()
        st.markdown('<p class="chart-title">Evolução Temporal das Publicações</p>', unsafe_allow_html=True)
        modo_evol = st.radio("Filtro:", ["Geral", "Por Setor"], horizontal=True, label_visibility="collapsed")
        
        if modo_evol == "Geral":
            df_t = df_f.groupby(df_f['data_noticia'].dt.date).size().reset_index(name='Qtd')
            fig_evol = px.area(df_t, x='data_noticia', y='Qtd', labels={'data_noticia': 'Data', 'Qtd': 'Notícias'})
            fig_evol.update_traces(line_color='#F75D00', fillcolor='rgba(247, 93, 0, 0.2)')
        else:
            df_t = df_f.groupby([df_f['data_noticia'].dt.date, 'categoria']).size().reset_index(name='Qtd')
            fig_evol = px.line(df_t, x='data_noticia', y='Qtd', color='categoria')
        
        fig_evol.update_layout(
            height=450, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            hovermode="closest",
            hoverlabel=dict(bgcolor="#1c1f26", font_size=14, font_family="Inter", bordercolor="#F75D00"),
            xaxis=dict(title=None, showgrid=False, showspikes=False), 
            yaxis=dict(gridcolor='#262730', title=None, showspikes=False)
        )
        fig_evol.update_traces(hovertemplate="<b>Data:</b> %{x}<br><b>Volume:</b> %{y}<extra></extra>")
        st.plotly_chart(fig_evol, width='stretch')

        st.divider()
        col_bar, col_wc = st.columns([1, 1])
        with col_bar:
            st.markdown('<p class="chart-title">Volume por Categoria</p>', unsafe_allow_html=True)
            cont = df_f['categoria'].value_counts().head(10).sort_values(ascending=True)
            fig_freq = px.bar(x=cont.values, y=cont.index, orientation='h', color_discrete_sequence=['#F75D00'])
            fig_freq.update_traces(texttemplate='%{x}', textposition='outside', textfont_color='white', textfont_size=13)
            fig_freq.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False), yaxis=dict(title=None))
            st.plotly_chart(fig_freq, width='stretch')

        with col_wc:
            st.markdown('<p class="chart-title">Temas em Destaque</p>', unsafe_allow_html=True)
            texto = " ".join(df_f['titulo_limpo'].astype(str)).lower()
            ignore = {"a", "ao", "por", "à", "e", "o", "as", "os", "de", "do", "da", "dos", "das", "em", "no", "na", "nos", "nas", "para", "com", "que", "se", "sobre", "mais", "até", "ate", "foi", "está", "tem", "diz", "nova", "onde", "portanto", "ma", "r", "dia", "não", "cade"}
            if texto.strip():
                wc = WordCloud(width=800, height=400, background_color='#000000', colormap='Oranges', stopwords=ignore, max_words=17, prefer_horizontal=1.0).generate(texto)
                fig_wc, ax = plt.subplots(figsize=(10, 5), facecolor='#000000')
                ax.imshow(wc, interpolation='bilinear'); ax.axis("off")
                st.pyplot(fig_wc, width='stretch')

# --- PÁGINA: BOLETIM SEMANAL (NARRATIVA FINAL) ---
elif st.session_state.pagina_ativa == "resumo":
    referencia = df_bruto['data_noticia'].max().date() if not df_bruto.empty else date.today()
    inicio_semana = referencia - timedelta(days=7)
    df_semana = df_bruto[df_bruto['data_noticia'].dt.date >= inicio_semana]
    
    st.markdown(f"""
    <div class="bulletin-header">
        <h1 style='margin:0; color:#F75D00; font-size:3.2rem;'>📋 Boletim Semanal iNFRA</h1>
        <p style='font-size:1.5rem; color:#e0e0e0; margin-top:15px;'>
            Análise Estratégica: <b>{inicio_semana.strftime('%d/%m/%Y')}</b> a <b>{referencia.strftime('%d/%m/%Y')}</b>
        </p>
    </div>
    """, unsafe_allow_html=True)

    if not df_semana.empty:
        c1, c2 = st.columns([1, 1])
        c1.metric("Volume na Semana", len(df_semana))
        c2.metric("Setor em Evidência", df_semana['categoria'].mode()[0])
        st.divider()

        for cat in sorted(df_semana['categoria'].unique()):
            df_cat = df_semana[df_semana['categoria'] == cat]
            
            with st.expander(f"📂 {cat.replace('_', ' ')} — ({len(df_cat)} notícias)", expanded=True):
                titulos = df_cat['titulo_limpo'].tolist()
                links = df_cat['link'].tolist()
                
                narrativa = f"Nesta última semana, a área de <span class='highlight-sector'>{cat.replace('_', ' ')}</span> concentrou {len(df_cat)} publicações de relevância. "
                narrativa += f"O foco principal recaiu sobre <b>{titulos[0]}</b> <a href='{links[0]}' class='news-link'>🔗</a>. "
                
                if len(titulos) > 1:
                    narrativa += f"Também observou-se repercussão acerca de <b>{titulos[1]}</b> <a href='{links[1]}' class='news-link'>🔗</a>"
                    if len(titulos) > 2:
                        narrativa += f", além de desdobramentos em <b>{titulos[2]}</b> <a href='{links[2]}' class='news-link'>🔗</a>."
                    else:
                        narrativa += "."
                
                st.markdown(f"<div class='narrative-box'>{narrativa}</div>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.warning("Aguardando novas notícias para compilar o boletim.")