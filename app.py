import streamlit as st
import pdfplumber
import re
from datetime import datetime
import time

# --------------------------------------------------
# CONFIGURAÇÃO DE DESIGN (ESTILO DEVTOOLS)
# --------------------------------------------------
st.set_page_config(page_title="Burocrata de Bolso", page_icon="⚖️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .main-title { color: #1e3a8a; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; }
    
    /* Estilização da Coluna Direita (DevTools Style) */
    .devtools-panel {
        background-color: #ffffff;
        border-left: 2px solid #e2e8f0;
        padding: 20px;
        height: 100vh;
        position: sticky;
        top: 0;
    }
    .stChatFloatingInputContainer { bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# LÓGICA DE AUDITORIA
# --------------------------------------------------

def realizar_auditoria(texto):
    problemas = []
    texto_limpo = texto.lower()
    regras = [
        {"id": "guarantee", "regex": r"fiador.*(caução|depósito|seguro|título)|(caução|depósito|seguro|título).*fiador", "nome": "Garantia Dupla", "gravidade": "RED", "emoji": "🚫", "exp": "A lei proíbe exigir mais de uma garantia.", "lei": "Art. 37, Lei 8.245/91"},
        {"id": "fees", "regex": r"taxa.*(elaboração|confecção|contrato|cadastro|adm|reserva)", "nome": "Taxas de Intermediação", "gravidade": "RED", "emoji": "💸", "exp": "Custos de contrato cabem ao locador.", "lei": "Art. 22, VII, Lei 8.245/91"},
        {"id": "proportion", "regex": r"multa.*(3|três).*alugue", "check_not": "proporcional", "nome": "Multa Rescisória", "gravidade": "RED", "emoji": "⚠️", "exp": "A multa deve ser proporcional ao tempo restante.", "lei": "Art. 4º, Lei 8.245/91"},
        {"id": "readjust", "regex": r"(reajuste|aumento|atualização).*trimestral|mensal", "nome": "Reajuste Ilegal", "gravidade": "RED", "emoji": "📉", "exp": "Prazos de reajuste devem ser anuais.", "lei": "Lei 10.192/01"},
        {"id": "visit", "regex": r"(qualquer|a qualquer|sem aviso|independente de).*visita|vistoria|ingressar", "nome": "Invasão de Privacidade", "gravidade": "RED", "emoji": "🏠", "exp": "Exige aviso prévio combinado.", "lei": "Art. 23, IX, Lei 8.245/91"}
    ]
    for r in regras:
        if re.search(r["regex"], texto_limpo, re.DOTALL):
            if "check_not" in r and r["check_not"] in texto_limpo: continue
            problemas.append(r)
    return problemas

# --------------------------------------------------
# INTERFACE PRINCIPAL
# --------------------------------------------------

st.markdown("<h1 class='main-title'>⚖️ Burocrata de Bolso</h1>", unsafe_allow_html=True)
st.write("---")

# Definição das colunas
col_main, col_devtools = st.columns([1.5, 1])

with col_main:
    st.subheader("📂 Upload do Documento")
    uploaded_file = st.file_uploader("Arraste o contrato para inspeção", type=["pdf"])
    
    if uploaded_file:
        with st.spinner("Processando texto..."):
            with pdfplumber.open(uploaded_file) as pdf:
                full_text = "".join([p.extract_text() or "" for p in pdf.pages])
            
            st.success("PDF carregado com sucesso.")
            st.info("Inspeção detalhada disponível no painel à direita →")
            
            # Dashboard de Score
            problemas = realizar_auditoria(full_text)
            score = max(100 - (len(problemas) * 20), 0)
            st.metric("Health Check do Contrato", f"{score}/100")
            
            with st.expander("Ver texto extraído"):
                st.write(full_text[:1000] + "...")

# --------------------------------------------------
# PAINEL DE INSPEÇÃO (LADO DIREITO)
# --------------------------------------------------
with col_devtools:
    if uploaded_file:
        st.markdown("### 🛠️ Inspeção de Cláusulas")
        st.write("---")
        
        # Simulação de Console de Auditoria
        problemas = realizar_auditoria(full_text)
        
        if problemas:
            for p in problemas:
                with st.chat_message("assistant", avatar="🔴"):
                    st.markdown(f"**{p['nome']}**")
                    st.write(p['exp'])
                    st.caption(f"Referência: {p['lei']}")
            
            # Campo de entrada no estilo chat de suporte
            if prompt := st.chat_input("Dúvida sobre uma cláusula?"):
                st.toast(f"Analisando: {prompt}")
                # Aqui você pode conectar a lógica de resposta futura
        else:
            st.balloons()
            st.success("Console: Nenhuma vulnerabilidade encontrada.")
    else:
        # Estado vazio antes do upload
        st.markdown("<div style='text-align: center; margin-top: 50px; color: #94a3b8;'>", unsafe_allow_html=True)
        st.write("### 🖥️ Console de Auditoria")
        st.write("Aguardando upload de arquivo para iniciar o debugger jurídico...")
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br><p style='text-align: center; color: #94a3b8;'>Burocrata de Bolso | DevMode v1.0</p>", unsafe_allow_html=True)
