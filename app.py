import streamlit as st
import pdfplumber
import re
import unicodedata
from datetime import datetime
import pandas as pd

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
    
    /* Tabelas e expanders */
    .stExpander {
        border: 1px solid #e2e8f0;
        border-radius: 6px;
    }
    
    .stExpander > div:first-child {
        background-color: #f7fafc;
        padding: 12px 15px;
        font-weight: 500;
        color: #2d3748;
    }
    
    /* Console profissional */
    .console-header {
        background-color: #2d3748;
        color: white;
        padding: 12px 15px;
        border-radius: 6px 6px 0 0;
        font-family: 'Monaco', 'Courier New', monospace;
        font-size: 14px;
    }
    
    .console-body {
        background-color: #1a202c;
        color: #a0aec0;
        padding: 15px;
        border-radius: 0 0 6px 6px;
        font-family: 'Monaco', 'Courier New', monospace;
        font-size: 13px;
        border: 1px solid #2d3748;
    }
    
    /* Sidebar profissional */
    .sidebar-title {
        color: #2c5282;
        font-weight: 600;
        margin-bottom: 20px;
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-active {
        background-color: #38a169;
    }
    
    .status-inactive {
        background-color: #cbd5e0;
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
        texto_lower = texto.lower()
        
        indicadores = {
            'contrato_locacao': ['contrato de locação', 'locador', 'locatário', 'aluguel', 'imóvel', 
                                 'termos de locação', 'cláusula', 'vigência', 'fiador', 'caução'],
            'nota_fiscal': ['nota fiscal', 'nfe', 'nf-e', 'chave de acesso', 'emitente', 'destinatário',
                           'cnpj', 'icms', 'ipi', 'danfe', 'número da nota', 'modelo 55'],
            'contrato_servico': ['contrato de prestação de serviços', 'contratante', 'contratada', 
                                'objeto do contrato', 'escopo dos serviços', 'fornecimento de serviços'],
            'contrato_compra_venda': ['contrato de compra e venda', 'vendedor', 'comprador', 
                                     'alienante', 'adquirente', 'imóvel objeto', 'preço total']
        }
        
        contagem = {tipo: 0 for tipo in indicadores.keys()}
        
        for tipo, palavras in indicadores.items():
            for palavra in palavras:
                if palavra in texto_lower:
                    contagem[tipo] += 1
        
        tipo_detectado = max(contagem.items(), key=lambda x: x[1])
        
        if tipo_detectado[1] < 2:
            return 'desconhecido'
        
        return tipo_detectado[0]

# --------------------------------------------------
# LEITORES DE DOCUMENTOS ESPECÍFICOS
# --------------------------------------------------

class NotaFiscalReader:
    """Lê e analisa Notas Fiscais Eletrônicas"""
    
    def __init__(self):
        self.tipo = "nota_fiscal"
        self.padroes = {
            'numero': r'N[º°]\s*[:]?\s*(\d+)',
            'serie': r'S[ÉE]RIE\s*[:]?\s*(\d+)',
            'chave_acesso': r'CHAVE\s+DE\s+ACESSO\s*[:]?\s*([0-9]{44})',
            'cnpj_emitente': r'CNPJ\s*[:]?\s*(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})',
            'nome_emitente': r'EMITENTE\s*(?:.*?\n)?(?:RAZÃO SOCIAL|NOME)?\s*[:]?\s*(.+)',
            'cnpj_destinatario': r'DESTINATÁRIO.*?CNPJ\s*[:]?\s*(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})',
            'valor_total': r'VALOR\s+TOTAL\s+(?:R\$|\$)?\s*([\d.,]+)',
            'data_emissao': r'DATA\s+(?:DA\s+)?EMISSÃO\s*[:]?\s*(\d{2}/\d{2}/\d{4})',
            'valor_icms': r'VALOR\s+DO\s+ICMS\s*(?:R\$|\$)?\s*([\d.,]+)',
            'valor_ipi': r'VALOR\s+DO\s+IPI\s*(?:R\$|\$)?\s*([\d.,]+)',
            'cfop': r'CFOP\s*[:]?\s*(\d{4})',
            'natureza_operacao': r'NATUREZA\s+DA\s+OPERAÇÃO\s*[:]?\s*(.+)',
            'protocolo_autorizacao': r'PROTOCOLO\s+DE\s+AUTORIZAÇÃO\s*[:]?\s*(\d+)'
        }
        
        self.padroes_auditoria = [
            {
                "id": "nfe_chave_invalida",
                "regex": r"CHAVE\s+DE\s+ACESSO\s*[:]?\s*([0-9]{43}|[0-9]{45})",
                "nome": "Chave de Acesso Inválida",
                "exp": "A chave de acesso deve conter exatamente 44 dígitos.",
                "lei": "Portaria CAT 142/2018"
            },
            {
                "id": "nfe_data_vencida",
                "regex": r"DATA\s+DE\s+EMISSÃO.*?(\d{2}/\d{2}/\d{4})",
                "nome": "Nota Fiscal Vencida",
                "exp": "Verifique se a data de emissão não ultrapassa 5 anos para fins fiscais.",
                "lei": "Art. 198, RICMS/SP"
            },
            {
                "id": "nfe_cnpj_invalido",
                "regex": r"CNPJ\s*[:]?\s*(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{1}|\d{2}\.\d{3}\.\d{3}/\d{3}-\d{2})",
                "nome": "CNPJ com Formato Inválido",
                "exp": "Formato de CNPJ incorreto. Deve seguir o padrão XX.XXX.XXX/XXXX-XX.",
                "lei": "Instrução Normativa RFB 1.863/2018"
            }
        ]
    
    def extrair_informacoes(self, texto):
        resultados = {}
        for campo, padrao in self.padroes.items():
            match = re.search(padrao, texto, re.IGNORECASE | re.MULTILINE)
            if match:
                resultados[campo] = match.group(1)
            else:
                padrao_flex = padrao.replace(r'\s*[:]?\s*', r'.*?')
                match_flex = re.search(padrao_flex, texto, re.IGNORECASE | re.MULTILINE)
                resultados[campo] = match_flex.group(1) if match_flex else None
        return resultados
    
    def auditoria_nfe(self, texto):
        problemas = []
        texto_normalizado = normalizar_texto(texto)
        
        for regra in self.padroes_auditoria:
            matches = list(re.finditer(regra["regex"], texto, re.IGNORECASE | re.MULTILINE))
            
            if matches:
                for match in matches:
                    inicio = max(0, match.start() - 50)
                    fim = min(len(texto_normalizado), match.end() + 50)
                    contexto = texto_normalizado[inicio:fim]
                    
                    problemas.append({
                        **regra,
                        "contexto": f"...{contexto}..." if contexto else "",
                        "pagina": 1
                    })
        
        info = self.extrair_informacoes(texto)
        
        if info.get('chave_acesso'):
            chave = info['chave_acesso']
            if len(chave) != 44 or not chave.isdigit():
                problemas.append({
                    "id": "nfe_chave_erro",
                    "nome": "Chave de Acesso com Erro",
                    "exp": f"Chave '{chave}' não possui 44 dígitos numéricos.",
                    "lei": "Portaria CAT 142/2018",
                    "contexto": f"Chave encontrada: {chave}",
                    "pagina": 1
                })
        
        if info.get('data_emissao'):
            try:
                data_emissao = datetime.strptime(info['data_emissao'], '%d/%m/%Y')
                if (datetime.now() - data_emissao).days > 365 * 5:
                    problemas.append({
                        "id": "nfe_muito_antiga",
                        "nome": "Nota Fiscal Muito Antiga",
                        "exp": f"Nota emitida em {info['data_emissao']} - pode estar prescrita para créditos fiscais.",
                        "lei": "Art. 198, RICMS/SP",
                        "contexto": f"Data de emissão: {info['data_emissao']}",
                        "pagina": 1
                    })
            except:
                pass
        
        return problemas, info

# --------------------------------------------------
# FUNÇÕES AUXILIARES
# --------------------------------------------------

def normalizar_texto(t):
    if t:
        t = "".join(ch for ch in unicodedata.normalize('NFKD', t) if not unicodedata.combining(ch))
        return " ".join(t.lower().split())
    return ""

# --------------------------------------------------
# LÓGICA DE AUDITORIA PARA CONTRATO DE LOCAÇÃO
# --------------------------------------------------

def realizar_auditoria_contrato_locacao(arquivo_pdf):
    problemas_detectados = []
    problemas_ja_encontrados = set()
    
    regras = [
        {"id": "readjust", "regex": r"reajuste.*?(trimestral|mensal|semestral|3|tres|6|seis|bianual|bimestral|4|quatro)", 
         "nome": "Reajuste Ilegal", 
         "exp": "O reajuste de aluguel deve ser ANUAL (12 meses). Períodos menores são ilegais.", 
         "lei": "Lei 10.192/01"},
        
        {"id": "improvements", "regex": r"(renuncia|nao indeniza|sem direito|nao tem direito|nao recebera).*?(benfeitoria|reforma|obra|melhoria|investimento)", 
         "nome": "Cláusula de Benfeitorias", 
         "exp": "O inquilino tem direito a indenização por reformas necessárias. Cláusula de renúncia é nula.", 
         "lei": "Art. 35, Lei 8.245/91"},
        
        {"id": "proportion", "regex": r"(multa.*?(12|doze|integral|total|cheia|completa).*?(aluguel|meses))|(pagar.*?(12|doze).*?meses.*?multa)", 
         "nome": "Multa s/ Proporcionalidade", 
         "exp": "A multa deve ser proporcional ao tempo que resta de contrato. Multa integral de 12 meses é abusiva.", 
         "lei": "Art. 4º, Lei 8.245/91 e Art. 51, CDC"},
        
        {"id": "privacy", "regex": r"(qualquer|sem aviso|independente|livre|a qualquer).*?(visita|vistoria|ingresso|entrar|acesso|inspecao)", 
         "nome": "Violação de Privacidade", 
         "exp": "O locador não pode entrar no imóvel sem aviso prévio e hora combinada.", 
         "lei": "Art. 23, IX, Lei 8.245/91"},
        
        {"id": "guarantee_dupla", "regex": r"(fiador.*?(caucao|deposito|seguro|aval))|((caucao|deposito|seguro|aval).*?fiador)|(exige.*?(fiador.*?caucao|caucao.*?fiador))", 
         "nome": "Garantia Dupla Ilegal", 
         "exp": "É proibido exigir mais de uma garantia no mesmo contrato (ex: fiador E caução).", 
         "lei": "Art. 37, Lei 8.245/91"},
        
        {"id": "summary_eviction", "regex": r"(despejo|desocupacao).*?(imediata|sumario|automatico|sem notificacao)", 
         "nome": "Despejo Sumário Ilegal", 
         "exp": "O despejo requer processo judicial e não pode ser automático por cláusula contratual.", 
         "lei": "Art. 9º, Lei 8.245/91"},
        
        {"id": "sale_eviction", "regex": r"(venda|alienacao).*?(rescindir|terminar|desocupar|despejo)", 
         "nome": "Cláusula 'Venda Despeja'", 
         "exp": "A venda do imóvel não rescinde automaticamente o contrato. Inquilino tem preferência.", 
         "lei": "Art. 27, Lei 8.245/91"},
        
        {"id": "no_pets", "regex": r"(proibido|nao permitido|vedado).*?(animais|pet|cao|gato|animal)", 
         "nome": "Proibição Total de Animais", 
         "exp": "Cláusula que proíbe qualquer animal pode ser considerada abusiva, exceto por justa causa.", 
         "lei": "Art. 51, CDC e Súmula 482 STJ"},
    ]

    with pdfplumber.open(arquivo_pdf) as pdf:
        texto_completo = ""
        
        for i, pagina in enumerate(pdf.pages):
            texto_pag = pagina.extract_text() or ""
            texto_completo += texto_pag + "\n"
        
        texto_normalizado = normalizar_texto(texto_completo)
        
        for i, pagina in enumerate(pdf.pages):
            texto_pag = pagina.extract_text() or ""
            texto_limpo = normalizar_texto(texto_pag)
            
            for r in regras:
                matches_pagina = list(re.finditer(r["regex"], texto_limpo, re.IGNORECASE))
                
                if matches_pagina:
                    for match in matches_pagina:
                        chave_duplicata = f"{r['id']}_{i+1}_{match.start()}"
                        if chave_duplicata not in problemas_ja_encontrados:
                            inicio = max(0, match.start() - 50)
                            fim = min(len(texto_limpo), match.end() + 50)
                            contexto = texto_limpo[inicio:fim]
                            
                            problemas_detectados.append({
                                **r, 
                                "pagina": i + 1,
                                "contexto": f"...{contexto}..." if contexto else "",
                                "posicao": match.start()
                            })
                            problemas_ja_encontrados.add(chave_duplicata)
    
    problemas_detectados.sort(key=lambda x: (x['pagina'], x.get('posicao', 0)))
    return problemas_detectados

# --------------------------------------------------
# FUNÇÃO PRINCIPAL DE AUDITORIA
# --------------------------------------------------

def realizar_auditoria_total(arquivo_pdf):
    with pdfplumber.open(arquivo_pdf) as pdf:
        texto_completo = ""
        for pagina in pdf.pages:
            texto = pagina.extract_text() or ""
            texto_completo += texto + "\n"
    
    detector = DocumentTypeDetector()
    tipo_documento = detector.detectar_tipo(texto_completo)
    
    st.session_state['tipo_documento'] = tipo_documento
    st.session_state['texto_completo'] = texto_completo[:1000] + "..."
    
    if tipo_documento == 'contrato_locacao':
        return realizar_auditoria_contrato_locacao(arquivo_pdf), tipo_documento
    
    elif tipo_documento == 'nota_fiscal':
        leitor_nf = NotaFiscalReader()
        problemas, informacoes = leitor_nf.auditoria_nfe(texto_completo)
        st.session_state['informacoes_nf'] = informacoes
        return problemas, tipo_documento
    
    elif tipo_documento == 'desconhecido':
        return [], tipo_documento
    
    else:
        return [], tipo_documento

# --------------------------------------------------
# CABEÇALHO PROFISSIONAL
# --------------------------------------------------
st.markdown('<h1 class="header-title">Burocrata de Bolso</h1>', unsafe_allow_html=True)
st.markdown('<p class="header-subtitle">Sistema de Análise Jurídica e Fiscal de Documentos</p>', unsafe_allow_html=True)

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
        help="Documentos suportados: Contratos de locação, Notas Fiscais Eletrônicas"
    )
    
    if arquivo:
        if st.button("Iniciar Análise Jurídica", type="primary", use_container_width=True):
            with st.spinner("Realizando análise técnica..."):
                achados, tipo_doc = realizar_auditoria_total(arquivo)
                
                st.session_state['achados'] = achados
                st.session_state['tipo_doc'] = tipo_doc
                st.session_state['analisado'] = True
    
    st.markdown('</div>', unsafe_allow_html=True)

with col_status:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    
    if st.session_state.get('analisado', False):
        achados = st.session_state.get('achados', [])
        tipo_doc = st.session_state.get('tipo_doc', 'desconhecido')
        
        penalidade = min(len(achados) * 15, 100)
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
        
        st.markdown(f"**Documento:** {tipo_doc.replace('_', ' ').title()}")
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
            st.markdown(f"- Tipo: {tipo_doc.replace('_', ' ').title()}")
            st.markdown(f"- Total de problemas: {len(achados)}")
            
            if tipo_doc == 'contrato_locacao':
                st.markdown("- Área: Direito Imobiliário")
            elif tipo_doc == 'nota_fiscal':
                st.markdown("- Área: Direito Tributário")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col_details:
            for a in achados:
                with st.expander(f"{a['nome']}"):
                    st.markdown(f"**Descrição:** {a['exp']}")
                    st.markdown(f"**Fundamento Legal:** {a.get('lei', 'Não especificado')}")
                    
                    if a.get('contexto'):
                        st.markdown("**Contexto Encontrado:**")
                        st.markdown(f'<div style="background-color: #f7fafc; padding: 10px; border-radius: 4px; border-left: 3px solid #2c5282; font-size: 14px;">{a["contexto"]}</div>', unsafe_allow_html=True)
                    
                    st.markdown(f"**Localização:** Página {a.get('pagina', 1)}")
    
    else:
        st.markdown("---")
        st.markdown('<div class="analysis-card" style="border-left-color: #38a169;">', unsafe_allow_html=True)
        st.markdown("**Resultado da Análise**")
        
        if tipo_doc == 'nota_fiscal':
            st.markdown("✅ A nota fiscal analisada está conforme os padrões verificados.")
            
            if 'informacoes_nf' in st.session_state:
                info = st.session_state['informacoes_nf']
                with st.expander("Informações da Nota Fiscal"):
                    cols = st.columns(2)
                    with cols[0]:
                        if info.get('numero'):
                            st.markdown(f"**Número:** {info.get('numero')}")
                        if info.get('data_emissao'):
                            st.markdown(f"**Data de Emissão:** {info.get('data_emissao')}")
                    with cols[1]:
                        if info.get('valor_total'):
                            st.markdown(f"**Valor Total:** R$ {info.get('valor_total')}")
                        if info.get('chave_acesso'):
                            st.markdown(f"**Chave de Acesso:**")
                            st.code(info.get('chave_acesso'), language="text")
        
        elif tipo_doc == 'contrato_locacao':
            st.markdown("✅ O contrato de locação analisado não apresenta irregularidades nas cláusulas verificadas.")
        
        else:
            st.markdown("✅ O documento analisado não apresenta irregularidades nos padrões verificados.")
        
        st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# CONSOLE TÉCNICO
# --------------------------------------------------
st.markdown("---")
st.subheader("Console Técnico")

col_console, col_assist = st.columns([2, 1])

with col_console:
    st.markdown('<div class="console-header">Log da Análise</div>', unsafe_allow_html=True)
    st.markdown('<div class="console-body">', unsafe_allow_html=True)
    
    if st.session_state.get('analisado', False):
        achados = st.session_state.get('achados', [])
        tipo_doc = st.session_state.get('tipo_doc', 'desconhecido')
        
        st.markdown(f"[INFO] Tipo de documento: {tipo_doc}")
        st.markdown(f"[INFO] Problemas encontrados: {len(achados)}")
        
        if achados:
            for a in achados:
                st.markdown(f"[ALERTA] {a['nome']} - Página {a.get('pagina', 1)}")
                st.markdown(f"       Lei: {a.get('lei', 'N/A')}")
        else:
            st.markdown("[INFO] Auditoria concluída sem alertas")
        
        st.markdown(f"[STATUS] Análise concluída às {datetime.now().strftime('%H:%M:%S')}")
    
    else:
        st.markdown("[INFO] Sistema inicializado")
        st.markdown("[INFO] Aguardando upload de documento")
        st.markdown("[STATUS] Pronto para análise")
    
    st.markdown('</div>', unsafe_allow_html=True)

with col_assist:
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown("**Assistente Jurídico**")
    
    if prompt := st.text_input("Consultar orientação:", placeholder="Digite sua dúvida sobre o documento..."):
        with st.spinner("Analisando consulta..."):
            st.markdown("---")
            
            if st.session_state.get('tipo_doc'):
                tipo_doc = st.session_state.get('tipo_doc')
                
                if tipo_doc == 'nota_fiscal':
                    if any(termo in prompt.lower() for termo in ['chave', 'acesso', 'validação']):
                        st.markdown("**Orientação:** A chave de acesso da NF-e possui 44 dígitos e pode ser validada no portal da Receita Federal através do DANFE.")
                    elif any(termo in prompt.lower() for termo in ['validade', 'prescrição', 'prazo']):
                        st.markdown("**Orientação:** Notas fiscais devem ser arquivadas por 5 anos para fins fiscais. Para créditos de ICMS, o prazo prescricional é de 5 anos.")
                    else:
                        st.markdown("**Orientação:** Para dúvidas específicas sobre NF-e, consulte a legislação tributária aplicável ou contate um contador especializado.")
                
                elif tipo_doc == 'contrato_locacao':
                    if any(termo in prompt.lower() for termo in ['reajuste', 'aumento']):
                        st.markdown("**Orientação:** Reajustes de aluguel em contratos residenciais devem ser anuais, conforme Lei do Inquilinato (Lei 8.245/91).")
                    elif any(termo in prompt.lower() for termo in ['multa', 'rescisão']):
                        st.markdown("**Orientação:** Multas rescisórias devem ser proporcionais ao tempo restante de contrato. Multas integrais são consideradas abusivas.")
                    else:
                        st.markdown("**Orientação:** Para questões contratuais complexas, recomenda-se consulta a advogado especializado em direito imobiliário.")
                
                else:
                    st.markdown("**Orientação:** Recomenda-se análise jurídica especializada para este tipo de documento.")
            else:
                st.markdown("**Orientação:** Faça o upload e análise do documento para obter orientações específicas.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# BARRA LATERAL
# --------------------------------------------------
with st.sidebar:
    st.markdown('<p class="sidebar-title">Módulos Disponíveis</p>', unsafe_allow_html=True)
    
    modulos = {
        "📑 Contratos de Locação": "Análise de 8 cláusulas problemáticas com base na Lei do Inquilinato",
        "🧾 Notas Fiscais": "Validação de dados fiscais e conformidade tributária",
        "⚖️ Contratos de Serviços": "Em desenvolvimento",
        "🏠 Contratos de Compra e Venda": "Em desenvolvimento"
    }
    
    for modulo, descricao in modulos.items():
        st.markdown(f"**{modulo}**")
        st.markdown(f'<div style="font-size: 12px; color: #4a5568; margin-bottom: 15px;">{descricao}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("**Informações do Sistema**")
    st.markdown(f'<div style="font-size: 12px; color: #4a5568;">Versão: 8.0</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size: 12px; color: #4a5568;">Última atualização: {datetime.now().strftime("%d/%m/%Y")}</div>', unsafe_allow_html=True)
    
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
