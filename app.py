import streamlit as st
import pdfplumber
import re
import unicodedata
from datetime import datetime
import pandas as pd
import io

# --------------------------------------------------
# CONFIGURAÇÃO DE LAYOUT PROFISSIONAL
# --------------------------------------------------
st.set_page_config(
    page_title="Burocrata de Bolso - Análise Jurídica de Documentos",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# ESTILOS CSS PERSONALIZADOS
# --------------------------------------------------
st.markdown("""
<style>
    /* Estilos gerais */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Cabeçalho profissional */
    .header-title {
        font-family: 'Georgia', serif;
        font-weight: 600;
        color: #1a365d;
        border-bottom: 2px solid #c9a96e;
        padding-bottom: 10px;
        margin-bottom: 30px;
    }
    
    .header-subtitle {
        font-family: 'Helvetica', sans-serif;
        color: #4a5568;
        font-size: 16px;
        margin-top: -15px;
        margin-bottom: 30px;
    }
    
    /* Cards e containers */
    .analysis-card {
        background-color: white;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 4px solid #2c5282;
        margin-bottom: 15px;
    }
    
    .info-card {
        background-color: #f7fafc;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 15px;
        margin-bottom: 10px;
    }
    
    /* Métricas e indicadores */
    .metric-container {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
    
    .score-excellent {
        color: #276749;
        font-weight: 700;
    }
    
    .score-moderate {
        color: #d69e2e;
        font-weight: 700;
    }
    
    .score-critical {
        color: #c53030;
        font-weight: 700;
    }
    
    /* Botões */
    .stButton button {
        background-color: #2c5282;
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 4px;
        font-weight: 500;
        transition: background-color 0.3s;
    }
    
    .stButton button:hover {
        background-color: #1a365d;
    }
    
    /* Tags de tipo de problema */
    .tag-critico {
        background-color: #fed7d7;
        color: #9b2c2c;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
    }
    
    .tag-medio {
        background-color: #feebc8;
        color: #9c4221;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
    }
    
    .tag-leve {
        background-color: #c6f6d5;
        color: #276749;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SISTEMA DE DETECÇÃO DE TIPO DE DOCUMENTO
# --------------------------------------------------

class DocumentTypeDetector:
    """Detecta automaticamente o tipo de documento"""
    
    @staticmethod
    def detectar_tipo(texto):
        if not texto or len(texto.strip()) < 50:
            return 'desconhecido'
            
        texto_lower = texto.lower()
        
        # Palavras-chave para cada tipo de documento
        locacao_palavras = ['contrato de locação', 'locador', 'locatário', 'aluguel', 'imóvel', 
                           'vigência', 'fiador', 'caução', 'valor do aluguel', 'reajuste']
        
        nfe_palavras = ['nota fiscal', 'nfe', 'nf-e', 'chave de acesso', 'emitente', 'destinatário',
                       'cnpj', 'icms', 'ipi', 'danfe', 'número da nota']
        
        servico_palavras = ['contrato de prestação de serviços', 'contratante', 'contratada', 
                           'objeto do contrato', 'prestador de serviços', 'tomador de serviços']
        
        compra_venda_palavras = ['contrato de compra e venda', 'vendedor', 'comprador', 
                                'imóvel objeto', 'matrícula', 'preço total', 'sinal']
        
        # Contar ocorrências
        contagem_locacao = sum(1 for palavra in locacao_palavras if palavra in texto_lower)
        contagem_nfe = sum(1 for palavra in nfe_palavras if palavra in texto_lower)
        contagem_servico = sum(1 for palavra in servico_palavras if palavra in texto_lower)
        contagem_cv = sum(1 for palavra in compra_venda_palavras if palavra in texto_lower)
        
        # Determinar tipo
        contagens = {
            'contrato_locacao': contagem_locacao,
            'nota_fiscal': contagem_nfe,
            'contrato_servico': contagem_servico,
            'contrato_compra_venda': contagem_cv
        }
        
        tipo_detectado = max(contagens.items(), key=lambda x: x[1])
        
        if tipo_detectado[1] < 2:
            return 'desconhecido'
        
        return tipo_detectado[0]

# --------------------------------------------------
# LÓGICA DE AUDITORIA PARA CONTRATO DE LOCAÇÃO
# --------------------------------------------------

def normalizar_texto(t):
    if t:
        t = "".join(ch for ch in unicodedata.normalize('NFKD', t) if not unicodedata.combining(ch))
        return " ".join(t.lower().split())
    return ""

def realizar_auditoria_contrato_locacao(arquivo_pdf):
    problemas_detectados = []
    
    # Regras específicas para contrato de locação - MAIS FLEXÍVEIS
    regras = [
        {
            "id": "readjust", 
            "regex": r"reajuste.*?(trimestral|mensal|semestral|3|tres|6|seis|bianual|bimestral|4|quarto|quatro)", 
            "nome": "Reajuste Ilegal", 
            "gravidade": "critico",
            "exp": "O reajuste de aluguel deve ser ANUAL (12 meses). Períodos menores são ilegais.", 
            "lei": "Lei 10.192/01"
        },
        {
            "id": "improvements", 
            "regex": r"(renuncia|nao indeniza|sem direito|nao tem direito|nao recebera).*?(benfeitoria|reforma|obra|melhoria|investimento)", 
            "nome": "Cláusula de Benfeitorias", 
            "gravidade": "critico",
            "exp": "O inquilino tem direito a indenização por reformas necessárias. Cláusula de renúncia é nula.", 
            "lei": "Art. 35, Lei 8.245/91"
        },
        {
            "id": "proportion", 
            "regex": r"(multa.*?(12|doze|integral|total|cheia|completa).*?(aluguel|meses))|(pagar.*?(12|doze).*?meses.*?multa)", 
            "nome": "Multa s/ Proporcionalidade", 
            "gravidade": "critico",
            "exp": "A multa deve ser proporcional ao tempo que resta de contrato. Multa integral de 12 meses é abusiva.", 
            "lei": "Art. 4º, Lei 8.245/91 e Art. 51, CDC"
        },
        {
            "id": "privacy", 
            "regex": r"(qualquer|sem aviso|independente|livre|a qualquer).*?(visita|vistoria|ingresso|entrar|acesso|inspecao)", 
            "nome": "Violação de Privacidade", 
            "gravidade": "medio",
            "exp": "O locador não pode entrar no imóvel sem aviso prévio e hora combinada.", 
            "lei": "Art. 23, IX, Lei 8.245/91"
        },
        {
            "id": "guarantee_dupla", 
            "regex": r"(fiador.*?(caucao|deposito|seguro|aval))|((caucao|deposito|seguro|aval).*?fiador)|(exige.*?(fiador.*?caucao|caucao.*?fiador))", 
            "nome": "Garantia Dupla Ilegal", 
            "gravidade": "critico",
            "exp": "É proibido exigir mais de uma garantia no mesmo contrato (ex: fiador E caução).", 
            "lei": "Art. 37, Lei 8.245/91"
        },
        {
            "id": "summary_eviction", 
            "regex": r"(despejo|desocupacao).*?(imediata|sumario|automatico|sem notificacao)", 
            "nome": "Despejo Sumário Ilegal", 
            "gravidade": "critico",
            "exp": "O despejo requer processo judicial e não pode ser automático por cláusula contratual.", 
            "lei": "Art. 9º, Lei 8.245/91"
        },
        {
            "id": "sale_eviction", 
            "regex": r"(venda|alienacao).*?(rescindir|terminar|desocupar|despejo)", 
            "nome": "Cláusula 'Venda Despeja'", 
            "gravidade": "medio",
            "exp": "A venda do imóvel não rescinde automaticamente o contrato. Inquilino tem preferência.", 
            "lei": "Art. 27, Lei 8.245/91"
        },
        {
            "id": "no_pets", 
            "regex": r"(proibido|nao permitido|vedado).*?(animais|pet|cao|gato|animal)", 
            "nome": "Proibição Total de Animais", 
            "gravidade": "leve",
            "exp": "Cláusula que proíbe qualquer animal pode ser considerada abusiva, exceto por justa causa.", 
            "lei": "Art. 51, CDC e Súmula 482 STJ"
        },
    ]

    try:
        with pdfplumber.open(arquivo_pdf) as pdf:
            texto_completo = ""
            
            for i, pagina in enumerate(pdf.pages):
                try:
                    texto_pag = pagina.extract_text() or ""
                    texto_completo += texto_pag + "\n"
                except:
                    continue
            
            texto_normalizado = normalizar_texto(texto_completo)
            
            # Verificar cada regra
            for regra in regras:
                try:
                    # Usar search ao invés de finditer para primeira ocorrência
                    match = re.search(regra["regex"], texto_normalizado, re.IGNORECASE)
                    
                    if match:
                        inicio = max(0, match.start() - 100)
                        fim = min(len(texto_normalizado), match.end() + 100)
                        contexto = texto_normalizado[inicio:fim]
                        
                        problemas_detectados.append({
                            "id": regra["id"],
                            "nome": regra["nome"],
                            "gravidade": regra["gravidade"],
                            "exp": regra["exp"],
                            "lei": regra["lei"],
                            "contexto": f"...{contexto}..." if contexto else "",
                            "pagina": 1
                        })
                        
                except Exception as e:
                    continue
        
        # Remover duplicatas baseadas no ID
        problemas_unicos = []
        ids_vistos = set()
        for problema in problemas_detectados:
            if problema['id'] not in ids_vistos:
                problemas_unicos.append(problema)
                ids_vistos.add(problema['id'])
        
        # Ordenar por gravidade
        ordem_gravidade = {'critico': 0, 'medio': 1, 'leve': 2}
        problemas_unicos.sort(key=lambda x: ordem_gravidade.get(x.get('gravidade', 'leve'), 2))
        
        return problemas_unicos
        
    except Exception as e:
        st.error(f"Erro ao processar PDF: {str(e)}")
        return []

# --------------------------------------------------
# FUNÇÃO PRINCIPAL DE AUDITORIA
# --------------------------------------------------

def realizar_auditoria_total(arquivo_pdf):
    try:
        # Ler o arquivo PDF
        arquivo_bytes = arquivo_pdf.read()
        
        # Usar io.BytesIO para abrir o PDF
        with pdfplumber.open(io.BytesIO(arquivo_bytes)) as pdf:
            texto_completo = ""
            for pagina in pdf.pages:
                try:
                    texto = pagina.extract_text() or ""
                    texto_completo += texto + "\n"
                except:
                    continue
        
        if not texto_completo.strip():
            st.warning("Não foi possível extrair texto do PDF. O documento pode estar escaneado como imagem.")
            return [], 'desconhecido'
        
        # Detectar tipo de documento
        detector = DocumentTypeDetector()
        tipo_documento = detector.detectar_tipo(texto_completo)
        
        # Realizar auditoria específica
        if tipo_documento == 'contrato_locacao':
            # Voltar para o início do arquivo
            arquivo_pdf.seek(0)
            problemas = realizar_auditoria_contrato_locacao(io.BytesIO(arquivo_bytes))
            return problemas, tipo_documento
        
        # Para outros tipos, retorna lista vazia
        return [], tipo_documento
        
    except Exception as e:
        st.error(f"Erro ao processar documento: {str(e)}")
        return [], 'desconhecido'

# --------------------------------------------------
# FUNÇÕES AUXILIARES
# --------------------------------------------------

def obter_tag_html(gravidade):
    if gravidade == 'critico':
        return '<span class="tag-critico">CRÍTICO</span>'
    elif gravidade == 'medio':
        return '<span class="tag-medio">MÉDIO</span>'
    elif gravidade == 'leve':
        return '<span class="tag-leve">LEVE</span>'
    else:
        return ''

def obter_icone_documento(tipo_doc):
    icones = {
        'contrato_locacao': '🏠',
        'nota_fiscal': '🧾',
        'contrato_servico': '⚖️',
        'contrato_compra_venda': '💰',
        'desconhecido': '📄'
    }
    return icones.get(tipo_doc, '📄')

# --------------------------------------------------
# INTERFACE DO USUÁRIO
# --------------------------------------------------

st.markdown('<h1 class="header-title">Burocrata de Bolso</h1>', unsafe_allow_html=True)
st.markdown('<p class="header-subtitle">Sistema de Análise Jurídica de Documentos</p>', unsafe_allow_html=True)

# --------------------------------------------------
# LAYOUT PRINCIPAL
# --------------------------------------------------
col_upload, col_status = st.columns([2, 1])

with col_upload:
    st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
    st.subheader("Análise de Documento")
    
    arquivo = st.file_uploader(
        "Selecione um documento em formato PDF",
        type=["pdf"],
        help="Documentos suportados: Contratos de locação, Notas Fiscais, Contratos de Serviços, Contratos de Compra e Venda"
    )
    
    if arquivo:
        if st.button("Iniciar Análise Jurídica", type="primary", use_container_width=True):
            with st.spinner("Realizando análise técnica..."):
                achados, tipo_doc = realizar_auditoria_total(arquivo)
                
                st.session_state['achados'] = achados
                st.session_state['tipo_doc'] = tipo_doc
                st.session_state['analisado'] = True
                st.session_state['arquivo_nome'] = arquivo.name
    
    st.markdown('</div>', unsafe_allow_html=True)

with col_status:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    
    if st.session_state.get('analisado', False):
        achados = st.session_state.get('achados', [])
        tipo_doc = st.session_state.get('tipo_doc', 'desconhecido')
        
        # Cálculo de score
        penalidade_critico = sum(1 for a in achados if a.get('gravidade') == 'critico') * 25
        penalidade_medio = sum(1 for a in achados if a.get('gravidade') == 'medio') * 15
        penalidade_leve = sum(1 for a in achados if a.get('gravidade') == 'leve') * 5
        penalidade = min(penalidade_critico + penalidade_medio + penalidade_leve, 100)
        
        score = max(100 - penalidade, 0)
        
        st.markdown("**Índice de Conformidade**")
        
        if score >= 80:
            st.markdown(f'<h2 class="score-excellent">{score}/100</h2>', unsafe_allow_html=True)
            st.markdown("**Status:** Conforme")
        elif score >= 60:
            st.markdown(f'<h2 class="score-moderate">{score}/100</h2>', unsafe_allow_html=True)
            st.markdown("**Status:** Atenção Necessária")
        else:
            st.markdown(f'<h2 class="score-critical">{score}/100</h2>', unsafe_allow_html=True)
            st.markdown("**Status:** Não Conforme")
        
        st.progress(score / 100)
        
        icone = obter_icone_documento(tipo_doc)
        st.markdown(f"**Documento:** {icone} {tipo_doc.replace('_', ' ').title()}")
        st.markdown(f"**Problemas:** {len(achados)}")
    else:
        st.markdown("**Índice de Conformidade**")
        st.markdown('<h2>--/100</h2>', unsafe_allow_html=True)
        st.markdown("**Status:** Aguardando análise")
        st.progress(0)
        st.markdown("**Documento:** Não analisado")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# RESULTADOS DA ANÁLISE
# --------------------------------------------------
if st.session_state.get('analisado', False):
    achados = st.session_state.get('achados', [])
    tipo_doc = st.session_state.get('tipo_doc', 'desconhecido')
    
    if achados:
        st.markdown("---")
        st.subheader("Resultados da Auditoria")
        
        # Sumário executivo
        col_summary, col_details = st.columns([1, 2])
        
        with col_summary:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.markdown("**Sumário Executivo**")
            
            icone = obter_icone_documento(tipo_doc)
            st.markdown(f"- Tipo: {icone} {tipo_doc.replace('_', ' ').title()}")
            st.markdown(f"- Total de problemas: {len(achados)}")
            
            if tipo_doc == 'contrato_locacao':
                st.markdown("- Área: Direito Imobiliário")
                st.markdown("- Legislação: Lei 8.245/91 (Lei do Inquilinato)")
            
            # Estatísticas por gravidade
            criticos = sum(1 for a in achados if a.get('gravidade') == 'critico')
            medios = sum(1 for a in achados if a.get('gravidade') == 'medio')
            leves = sum(1 for a in achados if a.get('gravidade') == 'leve')
            
            if criticos > 0:
                st.markdown(f"- <span style='color: #c53030;'>Críticos: {criticos}</span>", unsafe_allow_html=True)
            if medios > 0:
                st.markdown(f"- <span style='color: #d69e2e;'>Médios: {medios}</span>", unsafe_allow_html=True)
            if leves > 0:
                st.markdown(f"- <span style='color: #38a169;'>Leves: {leves}</span>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col_details:
            for a in achados:
                # Determinar estilo baseado na gravidade
                if a.get('gravidade') == 'critico':
                    border_color = '#c53030'
                    gravidade_texto = "CRÍTICO"
                elif a.get('gravidade') == 'medio':
                    border_color = '#d69e2e'
                    gravidade_texto = "MÉDIO"
                elif a.get('gravidade') == 'leve':
                    border_color = '#38a169'
                    gravidade_texto = "LEVE"
                else:
                    border_color = '#2c5282'
                    gravidade_texto = ""
                
                # Criar título do expander SEM unsafe_allow_html
                if gravidade_texto:
                    titulo = f"{a['nome']} ({gravidade_texto})"
                else:
                    titulo = f"{a['nome']}"
                
                with st.expander(titulo):
                    st.markdown(f"**Descrição:** {a.get('exp', 'Descrição não disponível')}")
                    st.markdown(f"**Fundamento Legal:** {a.get('lei', 'Não especificado')}")
                    
                    if a.get('contexto'):
                        st.markdown("**Contexto Encontrado:**")
                        st.markdown(f'<div style="background-color: #f7fafc; padding: 10px; border-radius: 4px; border-left: 3px solid {border_color}; font-size: 14px; font-family: monospace;">{a["contexto"]}</div>', unsafe_allow_html=True)
                    
                    st.markdown(f"**Localização:** Página {a.get('pagina', 1)}")
    
    else:
        st.markdown("---")
        st.markdown('<div class="analysis-card" style="border-left-color: #38a169;">', unsafe_allow_html=True)
        st.markdown("**Resultado da Análise**")
        
        if tipo_doc == 'contrato_locacao':
            st.markdown("✅ O contrato de locação analisado não apresenta irregularidades nas cláusulas verificadas.")
            st.markdown("""
            **Cláusulas verificadas:**
            - Reajuste (deve ser anual)
            - Benfeitorias (não pode haver renúncia)
            - Multas (devem ser proporcionais)
            - Privacidade (visitas com aviso)
            - Garantias (não pode exigir dupla garantia)
            - Despejo (não pode ser sumário)
            - Venda (não rescinde automaticamente)
            - Animais (proibição total pode ser abusiva)
            """)
        else:
            st.markdown(f"✅ O documento analisado ({tipo_doc.replace('_', ' ').title()}) não apresenta irregularidades nos padrões verificados.")
        
        st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# BOTÃO PARA BAIXAR CONTRATO DE TESTE
# --------------------------------------------------
st.markdown("---")
st.subheader("📄 Contrato de Teste")

# Criar um contrato de teste em memória
from fpdf import FPDF
import base64

def criar_pdf_contrato_teste():
    pdf = FPDF()
    pdf.add_page()
    
    # Título
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="CONTRATO DE LOCAÇÃO RESIDENCIAL", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", size=12)
    
    # Texto do contrato COM ARMAZILHAS
    texto = """CONTRATO DE LOCAÇÃO RESIDENCIAL

Pelo presente instrumento particular de locação, de um lado, MARIA DA SILVA SANTOS, 
doravante denominada LOCADORA; e de outro lado, JOÃO PEREIRA OLIVEIRA, 
doravante denominado LOCATÁRIO, têm entre si justo e acertado o presente 
contrato de locação:

CLÁUSULA 1 - DO OBJETO
A LOCADORA dá em locação ao LOCATÁRIO o imóvel residencial situado à 
Avenida Paulista, 1000, apartamento 101, São Paulo-SP.

CLÁUSULA 2 - DO PRAZO
Contrato com vigência de 30 meses.

CLÁUSULA 3 - DO VALOR DO ALUGUEL
O aluguel mensal será de R$ 3.000,00. O reajuste será trimestral. 
[ARMADILHA 1: Reajuste trimestral é ilegal - deve ser anual]

CLÁUSULA 4 - DAS GARANTIAS
O LOCATÁRIO deverá apresentar fiadores E depósito caução.
[ARMADILHA 2: Garantia dupla é ilegal - escolha apenas uma]

CLÁUSULA 5 - DAS BENFEITORIAS
O LOCATÁRIO renuncia a qualquer indenização por benfeitorias necessárias.
[ARMADILHA 3: Renúncia a benfeitorias é nula]

CLÁUSULA 6 - DAS VISITAS
A LOCADORA poderá visitar o imóvel a qualquer tempo sem aviso prévio.
[ARMADILHA 4: Violação de privacidade]

CLÁUSULA 7 - DA MULTA
Multa de 12 meses de aluguel em caso de rescisão.

CLÁUSULA 8 - DOS ANIMAIS
Proibida a permanência de animais.

CLÁUSULA 9 - DA VENDA
Em caso de venda, contrato rescindido automaticamente.

CLÁUSULA 10 - DO FORO
Foro da Comarca de São Paulo.

São Paulo, 15/12/2023

___________________________
LOCADORA

___________________________
LOCATÁRIO"""
    
    for linha in texto.split('\n'):
        pdf.multi_cell(0, 10, txt=linha)
    
    return pdf.output(dest='S').encode('latin1')

# Botão para download do contrato de teste
if st.button("📥 Baixar Contrato de Locação para Teste (com 4 armadilhas)"):
    pdf_bytes = criar_pdf_contrato_teste()
    
    st.download_button(
        label="Clique para baixar",
        data=pdf_bytes,
        file_name="contrato_locacao_teste.pdf",
        mime="application/pdf",
        help="Contrato com 4 armadilhas para testar o sistema"
    )

# --------------------------------------------------
# BARRA LATERAL
# --------------------------------------------------
with st.sidebar:
    st.markdown('<p class="sidebar-title">Módulos Disponíveis</p>', unsafe_allow_html=True)
    
    modulos = {
        "🏠 Contratos de Locação": {
            "status": "ativo",
            "desc": "Análise de 8 cláusulas problemáticas",
            "clausulas": "Reajuste, Benfeitorias, Multa, Privacidade, Garantia, Despejo, Venda, Animais"
        },
        "🧾 Notas Fiscais": {
            "status": "em_breve", 
            "desc": "Validação de dados fiscais",
            "clausulas": "Chave de acesso, CNPJ, Data, Valores"
        },
        "⚖️ Contratos de Serviços": {
            "status": "em_breve",
            "desc": "Análise de cláusulas críticas",
            "clausulas": "Prazo, Multas, Juros, Responsabilidade"
        },
        "💰 Contratos de Compra e Venda": {
            "status": "em_breve",
            "desc": "Análise de cláusulas críticas",
            "clausulas": "Matrícula, Preço, Multa, Tributos"
        }
    }
    
    for modulo, info in modulos.items():
        status_icon = "🟢" if info["status"] == "ativo" else "🟡"
        st.markdown(f"{status_icon} **{modulo}**")
        st.markdown(f'<div style="font-size: 12px; color: #4a5568; margin-bottom: 10px;">{info["desc"]}</div>', unsafe_allow_html=True)
        
        if info.get("clausulas"):
            with st.expander(f"Cláusulas analisadas"):
                st.markdown(f'<div style="font-size: 11px; color: #718096;">{info["clausulas"]}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("**Legenda de Gravidade**")
    st.markdown("""
    <div style="font-size: 12px;">
    <span style="color: #c53030; font-weight: bold;">● Crítico:</span> Cláusula nula ou ilegal<br>
    <span style="color: #d69e2e; font-weight: bold;">● Médio:</span> Cláusula potencialmente abusiva<br>
    <span style="color: #38a169; font-weight: bold;">● Leve:</span> Recomendação de ajuste
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("**Aviso Legal**")
    st.markdown("""
    <div style="font-size: 11px; color: #718096;">
    Este sistema fornece análise automática com base em padrões predefinidos. 
    Não substitui a consulta a profissional qualificado. 
    Os resultados são informativos e não constituem orientação jurídica formal.
    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# RODAPÉ
# --------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #718096; font-size: 12px; padding: 20px;">
    Burocrata de Bolso | Sistema de Análise Jurídica de Documentos © 2024<br>
    Todos os direitos reservados | Processamento realizado localmente
</div>
""", unsafe_allow_html=True)
