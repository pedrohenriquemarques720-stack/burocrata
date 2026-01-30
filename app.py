import streamlit as st
import pdfplumber
import re
from datetime import datetime

# --------------------------------------------------
# CONFIGURAÇÃO DE LAYOUT
# --------------------------------------------------
st.set_page_config(page_title="Burocrata de Bolso", page_icon="⚖️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stColumn > div { padding: 10px; }
    .console-box {
        background-color: #1e1e1e;
        color: #d4d4d4;
        padding: 15px;
        border-radius: 10px;
        font-family: 'Courier New', Courier, monospace;
    }
    </style>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# LÓGICA DE ANÁLISE REFINADA COM LOCALIZAÇÃO DE PÁGINA
# --------------------------------------------------

def realizar_auditoria_detalhada(arquivo_pdf):
    problemas_detectados = []
    
    # Regras de detecção (Padrões mais flexíveis para evitar erros de leitura)
    regras = [
        {"id": "guarantee", "keywords": ["fiador", "caução", "depósito", "seguro"], "min_matches": 2, "nome": "Garantia Dupla", "exp": "A lei proíbe exigir mais de uma garantia (ex: Fiador + Caução).", "lei": "Art. 37, Lei 8.245/91"},
        {"id": "fees", "keywords": ["taxa", "elaboração", "contrato", "cadastro", "adm"], "min_matches": 2, "nome": "Taxas Indevidas", "exp": "Taxas de confecção de contrato são obrigação do locador.", "lei": "Art. 22, VII, Lei 8.245/91"},
        {"id": "proportion", "keywords": ["multa", "aluguel", "integral", "restante"], "not_word": "proporcional", "nome": "Multa s/ Proporcionalidade", "exp": "A multa rescisória deve ser sempre proporcional ao tempo restante.", "lei": "Art. 4º, Lei 8.245/91"},
        {"id": "readjust", "keywords": ["reajuste", "trimestral", "mensal", "semestral"], "min_matches": 2, "nome": "Reajuste Ilegal", "exp": "O reajuste só pode ocorrer após 12 meses de contrato.", "lei": "Lei 10.192/01"},
        {"id": "visit", "keywords": ["visita", "vistoria", "qualquer hora", "sem aviso"], "min_matches": 2, "nome": "Invasão de Privacidade", "exp": "O locador não pode entrar no imóvel sem aviso e horário combinado.", "lei": "Art. 23, IX, Lei 8.245/91"}
    ]

    with pdfplumber.open(arquivo_pdf) as pdf:
        for i, pagina in enumerate(pdf.pages):
            texto_pag = pagina.extract_text()
            if not texto_pag: continue
            
            # Limpeza para análise: remove quebras de linha e espaços duplos
            texto_analise = " ".join(texto_pag.lower().split())
            
            for r in regras:
                # Contagem de palavras-chave na mesma página
                matches = sum(1 for word in r["keywords"] if word in texto_analise)
                
                # Lógica específica para Multa (Proporcionalidade)
                if r["id"] == "proportion":
                    if "multa" in texto_analise and "aluguel" in texto_analise and r["not_word"] not in texto_analise:
                        problemas_detectados.append({**r, "pagina": i + 1})
                        continue

                # Lógica para as demais regras (Mínimo de palavras-chave próximas)
                if matches >= r.get("min_matches", 2):
                    # Evita duplicar o mesmo erro na mesma página
                    if not any(p['id'] == r['id'] and p['pagina'] == i+1 for p in problemas_detectados):
                        problemas_detectados.append({**r, "pagina": i + 1})
                        
    return problemas_detectados

# --------------------------------------------------
# INTERFACE
# --------------------------------------------------

st.title("⚖️ Burocrata de Bolso v3.0")
st.write("---")

col_esquerda, col_direita = st.columns([1.5, 1])

with col_esquerda:
    st.subheader("📄 Analisador de Contratos")
    arquivo = st.file_uploader("Suba o PDF do contrato", type=["pdf"])
    
    if arquivo:
        achados = realizar_auditoria_detalhada(arquivo)
        
        score = max(100 - (len(achados) * 20), 0)
        st.metric("Score de Proteção", f"{score}/100")
        st.progress(score / 100)
        
        if achados:
            st.error(f"⚠️ {len(achados)} irregularidades encontradas!")
            for a in achados:
                with st.expander(f"📍 Página {a['pagina']}: {a['nome']}"):
                    st.write(f"**O que o Burocrata diz:** {a['exp']}")
                    st.caption(f"Referência: {a['lei']}")
        else:
            st.success("Nenhum erro detectado nos padrões de teste.")

# --------------------------------------------------
# CONSOLE DE AUDITORIA À DIREITA
# --------------------------------------------------
with col_direita:
    st.subheader("🖥️ Auditoria em Tempo Real")
    
    if arquivo:
        for a in achados:
            with st.chat_message("assistant", avatar="⚖️"):
                st.markdown(f"**[PAG {a['pagina']}] DETECTADO:** `{a['nome']}`")
                st.info(f"Violação provável do {a['lei']}")
                st.divider()
        
        if prompt := st.chat_input("Dúvidas sobre os erros?"):
            with st.chat_message("user"):
                st.write(prompt)
            with st.chat_message("assistant"):
                st.write("Analisando sua dúvida... Como Burocrata, recomendo focar na correção da Cláusula de " + 
                         (achados[0]['nome'] if achados else "Contrato") + " primeiro.")
    else:
        st.info("Aguardando arquivo para processamento...")

st.markdown("---")
st.caption("Burocrata de Bolso © 2026 - Analisando página por página.")
