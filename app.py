import streamlit as st
import pdfplumber
import re
from datetime import datetime
import time

# --------------------------------------------------
# CONFIGURAÇÃO DE DESIGN PREMIUM
# --------------------------------------------------
st.set_page_config(page_title="Burocrata de Bolso", page_icon="⚖️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .main-title { color: #1e3a8a; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; letter-spacing: -1px; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #1e3a8a; color: white; border: none; }
    .stButton>button:hover { background-color: #2563eb; color: white; }
    [data-testid="stExpander"] { border-radius: 10px; border: 1px solid #e2e8f0; }
    </style>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# LÓGICA DE AUDITORIA (REGRAS)
# --------------------------------------------------

def realizar_auditoria(texto):
    problemas = []
    texto_limpo = texto.lower()
    
    regras = [
        {"id": "guarantee", "regex": r"fiador.*(caução|depósito|seguro|título)|(caução|depósito|seguro|título).*fiador", "nome": "Garantia Dupla", "gravidade": "RED", "emoji": "🚫", "exp": "A lei proíbe exigir mais de uma garantia. Isso anula a cláusula.", "lei": "Art. 37, Lei 8.245/91"},
        {"id": "fees", "regex": r"taxa.*(elaboração|confecção|contrato|cadastro|adm|reserva)", "nome": "Taxas de Intermediação", "gravidade": "RED", "emoji": "💸", "exp": "Taxas de contrato são custos do proprietário, não do inquilino.", "lei": "Art. 22, VII, Lei 8.245/91"},
        {"id": "proportion", "regex": r"multa.*(3|três).*alugue", "check_not": "proporcional", "nome": "Multa Rescisória sem Proporção", "gravidade": "RED", "emoji": "⚠️", "exp": "A multa deve ser proporcional ao tempo que falta.", "lei": "Art. 4º da Lei 8.245/91"},
        {"id": "readjust", "regex": r"(reajuste|aumento|atualização).*trimestral|mensal", "nome": "Reajuste Ilegal", "gravidade": "RED", "emoji": "📉", "exp": "O reajuste só pode ocorrer a cada 12 meses.", "lei": "Lei 10.192/01"},
        {"id": "visit", "regex": r"(qualquer|a qualquer|sem aviso|independente de).*visita|vistoria|ingressar", "nome": "Invasão de Privacidade", "gravidade": "RED", "emoji": "🏠", "exp": "O locador não pode entrar sem aviso prévio.", "lei": "Art. 23, IX, Lei 8.245/91"},
        {"id": "structure", "regex": r"responsabilidade.*(telhado|estrutural|vício oculto|tubulação)", "nome": "Manutenção Estrutural", "gravidade": "RED", "emoji": "🛠️", "exp": "Problemas na estrutura cabem ao locador.", "lei": "Art. 22, I e IV, Lei 8.245/91"}
    ]
    
    for r in regras:
        if re.search(r["regex"], texto_limpo, re.DOTALL):
            if "check_not" in r and r["check_not"] in texto_limpo: continue
            problemas.append(r)
    return problemas

# --------------------------------------------------
# ESTADO DO CHAT
# --------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# --------------------------------------------------
# INTERFACE EM DUAS COLUNAS
# --------------------------------------------------
st.markdown("<h1 class='main-title'>⚖️ Burocrata de Bolso</h1>", unsafe_allow_html=True)
st.write("---")

col_l, col_r = st.columns([1.2, 1])

with col_l:
    st.subheader("📄 Upload do Contrato")
    uploaded_file = st.file_uploader("Arraste o PDF para análise", type=["pdf"])
    
    if uploaded_file:
        with st.spinner("Analisando cláusulas..."):
            with pdfplumber.open(uploaded_file) as pdf:
                text = "".join([p.extract_text() or "" for p in pdf.pages])
            
            problemas_encontrados = realizar_auditoria(text)
            
            # Dashboard de Resultados
            st.success("Análise concluída!")
            score = max(100 - (len(problemas_encontrados) * 20), 0)
            st.metric("Índice de Segurança", f"{score}/100")
            
            # Atualiza o Chatbot automaticamente se for o primeiro processamento
            if not st.session_state.messages:
                st.session_state.messages.append({"role": "assistant", "content": "Olá! Sou seu Burocrata de Bolso. Acabei de ler seu contrato. 👋"})
                
                if problemas_encontrados:
                    st.session_state.messages.append({"role": "assistant", "content": f"Encontrei **{len(problemas_encontrados)} irregularidades** que podem te dar prejuízo. Veja os detalhes abaixo:"})
                    for p in problemas_encontrados:
                        msg = f"❌ **{p['nome']}**\n{p['exp']}\n📍 *Base Legal: {p['lei']}*"
                        st.session_state.messages.append({"role": "assistant", "content": msg})
                else:
                    st.session_state.messages.append({"role": "assistant", "content": "Excelente notícia! Não detectei nenhuma das abusividades comuns no meu banco de dados. ✅"})

            # Botão de Contraproposta
            if problemas_encontrados:
                with st.expander("📝 Gerar Contraproposta"):
                    email_text = f"Olá,\n\nApós análise, solicito a correção dos seguintes pontos no contrato:\n"
                    for p in problemas_encontrados: email_text += f"- {p['nome']} ({p['lei']})\n"
                    st.text_area("Copie o texto:", email_text, height=150)

with col_r:
    st.subheader("🤖 Assistente de Auditoria")
    
    # Área de Chat
    chat_placeholder = st.container(height=450)
    with chat_placeholder:
        for m in st.session_state.messages:
            with st.chat_message(m["role"], avatar="⚖️" if m["role"] == "assistant" else "👤"):
                st.markdown(m["content"])

    # Entrada do Usuário para Perguntas Extras
    if prompt := st.chat_input("Pergunte algo sobre o contrato..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_placeholder:
            with st.chat_message("user", avatar="👤"):
                st.markdown(prompt)
            
            with st.chat_message("assistant", avatar="⚖️"):
                # Simulação de resposta inteligente baseada no contexto
                response = "Como sou um protótipo, analiso padrões específicos. Se você está perguntando sobre taxas, lembre-se que o Art. 22 da Lei do Inquilinato proíbe cobranças de elaboração de contrato pelo inquilino."
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

st.markdown("<br><p style='text-align: center; color: #94a3b8;'>Burocrata de Bolso © 2026 | Teste de IA em Real-Time</p>", unsafe_allow_html=True)
