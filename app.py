import streamlit as st
import pdfplumber
import re
from datetime import datetime

# --------------------------------------------------
# CONFIGURAÇÃO DE LAYOUT
# --------------------------------------------------
st.set_page_config(page_title="Burocrata de Bolso", page_icon="⚖️", layout="wide")

# CSS para garantir que a coluna da direita pareça um painel de debug
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stColumn > div { 
        padding: 10px; 
    }
    .console-box {
        background-color: #1e1e1e;
        color: #d4d4d4;
        padding: 15px;
        border-radius: 10px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.8em;
    }
    </style>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# LÓGICA DE ANÁLISE REFINADA (O CÉREBRO)
# --------------------------------------------------

def realizar_auditoria_completa(texto):
    problemas = []
    
    # Lista de regras com Regex otimizado para PDFs (usa .*? para pular quebras de linha)
    regras = [
        {
            "id": "guarantee", 
            "regex": r"fiador.*?(?=caução|depósito|seguro|título)|(caução|depósito|seguro|título).*?fiador", 
            "nome": "Garantia Dupla", 
            "exp": "A lei proíbe mais de uma garantia. Isso é nulidade absoluta.", 
            "lei": "Art. 37, Lei 8.245/91"
        },
        {
            "id": "fees", 
            "regex": r"taxa.*?(elaboração|confecção|contrato|cadastro|adm|reserva)", 
            "nome": "Taxas de Intermediação", 
            "exp": "Cobrar taxa de contrato do inquilino é ilegal.", 
            "lei": "Art. 22, VII, Lei 8.245/91"
        },
        {
            "id": "proportion", 
            "regex": r"multa.*?(3|três).*?alugue", 
            "check_not": "proporcional", 
            "nome": "Multa Rescisória Abusiva", 
            "exp": "A multa deve ser proporcional ao tempo restante, nunca integral.", 
            "lei": "Art. 4º, Lei 8.245/91"
        },
        {
            "id": "readjust", 
            "regex": r"(reajuste|aumento|atualização).*?(trimestral|mensal|semestral)", 
            "nome": "Periodicidade Ilegal", 
            "exp": "Reajustes de aluguel só podem ocorrer a cada 12 meses.", 
            "lei": "Lei 10.192/01"
        },
        {
            "id": "visit", 
            "regex": r"(qualquer|sem aviso|independente de).*?(visita|vistoria|ingresso)", 
            "nome": "Violação de Privacidade", 
            "exp": "O locador deve agendar visitas com antecedência mínima.", 
            "lei": "Art. 23, IX, Lei 8.245/91"
        }
    ]

    for r in regras:
        # IGNORECASE: ignora maiúsculas | DOTALL: faz o '.' pegar quebras de linha (\n)
        if re.search(r["regex"], texto, re.IGNORECASE | re.DOTALL):
            # Se a regra diz que NÃO pode ter a palavra "proporcional"
            if "check_not" in r and r["check_not"].lower() in texto.lower():
                continue
            problemas.append(r)
            
    return problemas

# --------------------------------------------------
# INTERFACE EM COLUNAS
# --------------------------------------------------

st.title("⚖️ Burocrata de Bolso v2.0")
st.write("---")

col_esquerda, col_direita = st.columns([1.5, 1])

with col_esquerda:
    st.subheader("📄 Upload e Resultado")
    arquivo = st.file_uploader("Suba o contrato em PDF", type=["pdf"])
    
    if arquivo:
        with pdfplumber.open(arquivo) as pdf:
            texto_bruto = "".join([p.extract_text() or "" for p in pdf.pages])
        
        # Dispara a análise
        achados = realizar_auditoria_completa(texto_bruto)
        
        # Exibição do Score
        score = max(100 - (len(achados) * 20), 0)
        st.metric("Nível de Segurança Jurídica", f"{score}/100")
        st.progress(score / 100)
        
        if achados:
            st.error(f"Atenção: Encontramos {len(achados)} irregularidades potenciais.")
            for a in achados:
                with st.expander(f"📌 {a['nome']}"):
                    st.write(a['exp'])
                    st.caption(f"Base: {a['lei']}")
        else:
            st.success("Nenhuma irregularidade detectada nos padrões configurados.")

# --------------------------------------------------
# PAINEL DE CONSOLE À DIREITA (A MUDANÇA QUE VOCÊ PEDIU)
# --------------------------------------------------
with col_direita:
    st.subheader("🖥️ Auditoria em Tempo Real (Console)")
    
    if arquivo:
        # Bloco de mensagens estilo Chat/Console
        for a in achados:
            with st.chat_message("assistant", avatar="⚖️"):
                st.markdown(f"**LOG_ERROR:** Cláusula de `{a['nome']}` detectada.")
                st.markdown(f"**Ação:** Recomendar revisão baseada no `{a['lei']}`.")
                st.divider()
        
        # Campo de Chat Externo posicionado aqui
        if prompt := st.chat_input("Pergunte ao Burocrata..."):
            with st.chat_message("user"):
                st.write(prompt)
            with st.chat_message("assistant"):
                st.write("Como seu Burocrata, analiso que essa dúvida se refere à validade jurídica. Recomendo confrontar o locador com os artigos citados no log acima.")
    else:
        st.info("Aguardando upload para iniciar o console de depuração...")

st.markdown("---")
st.caption("Burocrata de Bolso - Focado em Taxas e Cobranças Indevidas © 2026")
