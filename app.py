import streamlit as st
import pdfplumber
import re
import pandas as pd
from datetime import datetime

# --------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# --------------------------------------------------
st.set_page_config(
    page_title="Burocrata de Bolso",
    page_icon="📄",
    layout="wide"
)

st.markdown("""
    <style>
    .stExpander { border: 1px solid #f0f2f6; border-radius: 10px; }
    .main-score { font-size: 24px; font-weight: bold; color: #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

st.title("📄 Burocrata de Bolso")
st.caption("O Conciliador: Transformando contratos complexos em acordos justos.")

# --------------------------------------------------
# MOTOR DE ANÁLISE (CÉREBRO DO APP)
# --------------------------------------------------

def buscar_padroes(texto):
    problemas = []
    texto = texto.lower()

    # 1. Garantia Dupla
    if re.search(r"fiador.*(caução|depósito|seguro|título)", texto, re.DOTALL) or \
       re.search(r"(caução|depósito|seguro|título).*fiador", texto, re.DOTALL):
        problemas.append({
            "nome": "Garantia Dupla",
            "gravidade": "RED",
            "emoji": "🚫",
            "explicacao": "A lei proíbe exigir mais de uma garantia (ex: Fiador + Caução).",
            "lei": "Art. 37, Parágrafo Único, Lei 8.245/91"
        })

    # 2. Taxas Administrativas
    if re.search(r"taxa.*(elaboração|confecção|contrato|cadastro|adm|reserva)", texto):
        problemas.append({
            "nome": "Taxas de Intermediação",
            "gravidade": "RED",
            "emoji": "💸",
            "explicacao": "Taxas de elaboração de contrato e cadastro devem ser pagas pelo proprietário.",
            "lei": "Art. 22, VII, Lei 8.245/91"
        })

    # 3. Multa Rescisória Sem Proporcionalidade
    if re.search(r"multa.*(3|três).*alugue", texto) and not re.search(r"proporcional", texto):
        problemas.append({
            "nome": "Multa Rescisória sem Proporcionalidade",
            "gravidade": "RED",
            "emoji": "⚠️",
            "explicacao": "A multa rescisória deve ser sempre proporcional ao tempo restante do contrato.",
            "lei": "Art. 4º da Lei 8.245/91"
        })

    # 4. Fundo de Reserva
    if re.search(r"fundo.*reserva|despesas.*extraordinária", texto):
        problemas.append({
            "nome": "Fundo de Reserva / Despesas Extraordinárias",
            "gravidade": "YELLOW",
            "emoji": "🏢",
            "explicacao": "O fundo de reserva e obras estruturais são obrigações do locador.",
            "lei": "Art. 22, Parágrafo Único, Lei 8.245/91"
        })

    return problemas

def calcular_score(problemas):
    score = 100
    for p in problemas:
        if p["gravidade"] == "RED": score -= 25
        elif p["gravidade"] == "YELLOW": score -= 10
    return max(score, 0)

def gerar_contraproposta(problemas):
    data_atual = datetime.now().strftime("%d/%m/%Y")
    texto = f"À IMOBILIÁRIA / AO PROPRIETÁRIO\n\nAssunto: Solicitação de Revisão de Cláusulas Contratuais\nData: {data_atual}\n\nPrezados,\n\nApós análise minuciosa da minuta do contrato de locação, gostaria de solicitar a revisão de alguns pontos que divergem da Lei do Inquilinato (Lei 8.245/91), visando garantir o equilíbrio jurídico da relação:\n\n"
    
    for p in problemas:
        texto += f"• {p['nome']}: Identifiquei previsão contrária ao {p['lei']}. {p['explicacao']}\n"
    
    texto += "\nCerto da vossa compreensão e buscando uma resolução amigável para procedermos com a assinatura, aguardo o envio da minuta retificada.\n\nAtenciosamente,\n[Seu Nome]"
    return texto

# --------------------------------------------------
# UI PRINCIPAL
# --------------------------------------------------
col_main, col_info = st.columns([2, 1])

with col_main:
    uploaded_file = st.file_uploader("📎 Faça upload do contrato (PDF)", type=["pdf"])

    if uploaded_file:
        with st.spinner("Analisando..."):
            with pdfplumber.open(uploaded_file) as pdf:
                texto_contrato = "".join([p.extract_text() or "" for p in pdf.pages]).lower()
            
            problemas = buscar_padroes(texto_contrato)
            score = calcular_score(problemas)

            st.subheader(f"📊 Score de Saúde: {score}/100")
            st.progress(score / 100)

            if problemas:
                st.write("### Itens detectados:")
                for idx, p in enumerate(problemas):
                    with st.expander(f"{p['emoji']} {p['nome']}"):
                        st.write(p['explicacao'])
                        st.caption(f"Base: {p['lei']}")
                
                # NOVIDADE: GERADOR DE CONTRAPROPOSTA
                st.markdown("---")
                st.subheader("📝 Resolver de Vez")
                if st.button("Gerar Contraproposta Formal"):
                    texto_final = gerar_contraproposta(problemas)
                    st.text_area("Copie o texto abaixo para enviar por e-mail:", texto_final, height=300)
                    st.download_button("Baixar como Arquivo de Texto", texto_final, file_name="contraproposta.txt")
            else:
                st.success("Nenhum problema comum encontrado!")

with col_info:
    st.sidebar.header("🛌 Modo Sono")
    data_inicio = st.sidebar.date_input("Início do Contrato", datetime.now())
    if st.sidebar.button("Ativar Guardião"):
        st.sidebar.success("Guardado! Te aviso no reajuste.")
    
    st.info("O Burocrata foca em conciliação. Use os textos gerados para negociar sem stress.")

st.markdown("---")
st.caption("Burocrata de Bolso 2026 - O seu direito, simplificado.")