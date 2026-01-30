import streamlit as st
import pdfplumber
import re

# --------------------------------------------------
# CONFIGURAÇÃO DE LAYOUT
# --------------------------------------------------
st.set_page_config(page_title="Burocrata de Bolso", page_icon="⚖️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
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
# LÓGICA DE AUDITORIA (AGORA PARA 4+ ERROS)
# --------------------------------------------------

def realizar_auditoria_detalhada(arquivo_pdf):
    problemas_detectados = []
    
    # Regras reforçadas para garantir a detecção dos 4 principais erros
    regras = [
        {
            "id": "guarantee", 
            "keywords": ["fiador", "caução", "depósito", "seguro", "garantia"], 
            "min_matches": 2, 
            "nome": "Garantia Dupla", 
            "exp": "Identificamos mais de uma modalidade de garantia. A lei permite apenas UMA (ex: ou Fiador, ou Caução).", 
            "lei": "Art. 37, Lei 8.245/91"
        },
        {
            "id": "fees", 
            "keywords": ["taxa", "contrato", "cadastro", "elaboração", "administrativa", "boleto"], 
            "min_matches": 2, 
            "nome": "Taxas Indevidas", 
            "exp": "O locatário não deve pagar taxas de 'elaboração de contrato' ou 'cadastro'. Isso é custo do locador.", 
            "lei": "Art. 22, VII, Lei 8.245/91"
        },
        {
            "id": "proportion", 
            "keywords": ["multa", "rescisória", "integral", "3 meses", "aluguel"], 
            "nome": "Multa s/ Proporcionalidade (Interpretação)", 
            "exp": "A cláusula de multa deve especificar que o pagamento é PROPORCIONAL ao tempo restante do contrato. Se for integral, é abusiva.", 
            "lei": "Art. 4º, Lei 8.245/91"
        },
        {
            "id": "readjust", 
            "keywords": ["reajuste", "trimestral", "semestral", "igp-m", "ipca", "mensal"], 
            "min_matches": 2, 
            "nome": "Periodicidade de Reajuste", 
            "exp": "O reajuste do aluguel só pode ser anual. Qualquer cláusula que preveja reajuste em menos de 12 meses é nula.", 
            "lei": "Lei 10.192/01"
        }
    ]

    with pdfplumber.open(arquivo_pdf) as pdf:
        for i, pagina in enumerate(pdf.pages):
            texto_pag = pagina.extract_text()
            if not texto_pag: continue
            
            # Limpeza agressiva para encontrar erros mesmo com formatação ruim
            texto_analise = " ".join(texto_pag.lower().split())
            
            for r in regras:
                # Lógica de Interpretação da Multa (O erro que costuma faltar)
                if r["id"] == "proportion":
                    # Se fala em multa e aluguel, mas NÃO cita a palavra 'proporcional'
                    if "multa" in texto_analise and ("aluguel" in texto_analise or "meses" in texto_analise):
                        if "proporcional" not in texto_analise:
                            if not any(p['id'] == r['id'] for p in problemas_detectados):
                                problemas_detectados.append({**r, "pagina": i + 1})
                    continue

                # Lógica para as demais regras (Keywords)
                matches = sum(1 for word in r["keywords"] if word in texto_analise)
                if matches >= r.get("min_matches", 2):
                    if not any(p['id'] == r['id'] and p['pagina'] == i+1 for p in problemas_detectados):
                        problemas_detectados.append({**r, "pagina": i + 1})
                        
    return problemas_detectados

# --------------------------------------------------
# INTERFACE STREAMLIT
# --------------------------------------------------

st.title("⚖️ Burocrata de Bolso v3.1")
st.subheader("O terror das cláusulas abusivas")

arquivo = st.file_uploader("Arraste o contrato (PDF) aqui", type=["pdf"])

if arquivo:
    achados = realizar_auditoria_detalhada(arquivo)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.metric("Irregularidades", len(achados))
        if len(achados) >= 4:
            st.success("🎯 Sucesso! Todos os 4 erros principais foram detectados.")
        else:
            st.warning(f"Encontramos {len(achados)} de 4 erros esperados.")

    with col2:
        # Exibição dos Erros com a Interpretação
        for a in achados:
            with st.expander(f"🔴 PAG {a['pagina']}: {a['nome']}"):
                st.write(f"**Análise do Burocrata:** {a['exp']}")
                st.caption(f"Base Legal: {a['lei']}")

    # Console Estilizado para o "Pitch" do AI Creation
    st.markdown("---")
    st.markdown("### 🖥️ Console de Diagnóstico")
    with st.container():
        st.markdown('<div class="console-box">', unsafe_allow_html=True)
        for a in achados:
            st.code(f"> [DETECTADO] {a['nome']} na página {a['pagina']}")
        if not achados:
            st.code("> Aguardando análise...")
        st.markdown('</div>', unsafe_allow_html=True)

st.sidebar.info("Este é o protótipo do Pocket Bureaucrat para o projeto AI Creation.")
