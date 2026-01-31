import streamlit as st
import pdfplumber
import re
import unicodedata
from datetime import datetime
import pandas as pd
import io

# --------------------------------------------------
# CONFIGURAÇÃO
# --------------------------------------------------
st.set_page_config(
    page_title="Burocrata de Bolso - Auditor Jurídico",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --------------------------------------------------
# ESTILOS PROFISSIONAIS - TEMA ESCURO COM DOURADO
# --------------------------------------------------
st.markdown("""
<style>
    /* Fundo preto e texto branco */
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    
    /* Títulos e texto geral */
    h1, h2, h3, h4, h5, h6, p, span, div {
        color: #ffffff !important;
    }
    
    /* Cabeçalho principal */
    .main-header {
        text-align: center;
        padding: 30px;
        background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
        color: #ffffff;
        border-radius: 15px;
        margin-bottom: 40px;
        box-shadow: 0 10px 30px rgba(212, 175, 55, 0.2);
        border: 2px solid #d4af37;
    }
    
    /* Cartões de métricas */
    .metric-card {
        background: rgba(26, 26, 26, 0.9);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        text-align: center;
        border-top: 4px solid;
        border-left: 1px solid #d4af37;
        border-right: 1px solid #d4af37;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(212, 175, 55, 0.3);
    }
    
    /* Container de ícones de problemas */
    .problems-icons-container {
        background: rgba(20, 20, 20, 0.9);
        padding: 30px;
        border-radius: 15px;
        margin: 30px 0;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(212, 175, 55, 0.3);
        text-align: center;
    }
    
    /* Ícones de problemas */
    .problem-icon {
        display: inline-block;
        margin: 15px;
        padding: 20px;
        border-radius: 15px;
        background: rgba(30, 30, 30, 0.9);
        transition: all 0.3s ease;
        cursor: pointer;
        position: relative;
        min-width: 100px;
        border: 2px solid transparent;
    }
    
    .problem-icon:hover {
        transform: translateY(-5px) scale(1.05);
        box-shadow: 0 10px 25px rgba(212, 175, 55, 0.3);
    }
    
    .critical-icon {
        border-color: #ff4444;
        background: rgba(255, 68, 68, 0.1);
    }
    
    .medium-icon {
        border-color: #ffaa44;
        background: rgba(255, 170, 68, 0.1);
    }
    
    .low-icon {
        border-color: #44aaff;
        background: rgba(68, 170, 255, 0.1);
    }
    
    .icon-emoji {
        font-size: 2.5em;
        margin-bottom: 10px;
        display: block;
    }
    
    .icon-title {
        font-size: 0.9em;
        font-weight: bold;
        color: #ffffff;
        margin: 5px 0;
    }
    
    .icon-severity {
        font-size: 0.75em;
        padding: 3px 10px;
        border-radius: 12px;
        display: inline-block;
        font-weight: bold;
    }
    
    .severity-critical {
        background: #ff4444;
        color: white;
    }
    
    .severity-medium {
        background: #ffaa44;
        color: white;
    }
    
    .severity-low {
        background: #44aaff;
        color: white;
    }
    
    /* Tooltip para ícones */
    .problem-tooltip {
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(0, 0, 0, 0.9);
        color: white;
        padding: 15px;
        border-radius: 10px;
        width: 300px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        border: 1px solid #d4af37;
        z-index: 1000;
        opacity: 0;
        visibility: hidden;
        transition: opacity 0.3s, visibility 0.3s;
        text-align: left;
    }
    
    .problem-icon:hover .problem-tooltip {
        opacity: 1;
        visibility: visible;
    }
    
    .tooltip-section {
        margin: 10px 0;
        padding: 10px;
        border-radius: 8px;
    }
    
    .tooltip-violation {
        background: rgba(255, 68, 68, 0.1);
        border-left: 3px solid #ff4444;
    }
    
    .tooltip-law {
        background: rgba(212, 175, 55, 0.1);
        border-left: 3px solid #d4af37;
    }
    
    .tooltip-solution {
        background: rgba(0, 255, 0, 0.1);
        border-left: 3px solid #00ff00;
    }
    
    /* Container de upload */
    .upload-container {
        border: 3px dashed #d4af37;
        border-radius: 20px;
        padding: 60px 40px;
        text-align: center;
        background: rgba(26, 26, 26, 0.7);
        margin: 30px 0;
        transition: all 0.3s;
        backdrop-filter: blur(10px);
    }
    
    .upload-container:hover {
        background: rgba(40, 40, 40, 0.7);
        border-color: #e6c158;
    }
    
    /* Botões dourados */
    .gold-button {
        background: linear-gradient(135deg, #d4af37, #b8941f);
        color: #000000 !important;
        border: none;
        padding: 12px 30px;
        border-radius: 25px;
        font-weight: 700;
        font-size: 1em;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .gold-button:hover {
        background: linear-gradient(135deg, #e6c158, #d4af37);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(212, 175, 55, 0.4);
    }
    
    /* Linhas divisorias douradas */
    .gold-divider {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #d4af37, transparent);
        margin: 40px 0;
    }
    
    /* Status do sistema */
    .system-status {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8em;
        font-weight: 600;
        background: rgba(0, 255, 0, 0.1);
        color: #00ff00;
        border: 1px solid rgba(0, 255, 0, 0.3);
    }
    
    /* Responsividade */
    @media (max-width: 768px) {
        .metric-card {
            margin-bottom: 20px;
        }
        .problem-icon {
            margin: 10px;
            padding: 15px;
            min-width: 80px;
        }
        .icon-emoji {
            font-size: 2em;
        }
    }
    
    /* Animação de entrada */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.6s ease-out;
    }
    
    /* Scrollbar customizada */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1a1a1a;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #d4af37;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #e6c158;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SISTEMA DE AUDITORIA COM ALTA PRECISÃO
# --------------------------------------------------

class SistemaAuditoriaAltaPrecisao:
    def __init__(self):
        # Dicionário de sinônimos para melhor detecção
        self.sinonimos = {
            'trimestral': ['trimestral', 'a cada 3 meses', '3 meses', 'trimestre', 'trimestralmente'],
            'mensal': ['mensal', 'a cada mês', 'mensalmente', 'por mês', 'mês a mês'],
            'semestral': ['semestral', 'a cada 6 meses', '6 meses', 'semestralmente'],
            'fiador': ['fiador', 'fiadores', 'garantidor', 'avalista', 'fiança'],
            'caucao': ['caução', 'depósito', 'garantia', 'seguro-fiança', 'caução bancária'],
            'benfeitoria': ['benfeitoria', 'benfeitorias', 'melhoria', 'reforma', 'obra', 'investimento'],
            'renuncia': ['renuncia', 'renúncia', 'abdica', 'abre mão', 'desiste', 'desistência'],
            'visita': ['visita', 'vistoria', 'inspeção', 'verificação', 'fiscalização'],
            'multa': ['multa', 'penalidade', 'indenização', 'compensação', 'sanção'],
            'proibido': ['proibido', 'vedado', 'não permitido', 'interditado', 'impedido']
        }
        
        # Configurações de detecção por tipo de problema
        self.padroes_avancados = {
            'reajuste_ilegal': {
                'nome': 'REAJUSTE ILEGAL',
                'gravidade': 'critical',
                'descricao_curta': 'Reajuste rápido que 12 meses',
                'descricao_detalhada': 'Reajuste deve ser ANUAL (12 meses). Trimestral/semestral é ilegal.',
                'lei': 'Lei 10.192/01',
                'icone': '📅',
                'contestacao': 'Exija reajuste anual com índice oficial.',
                'cor': '#ff4444'
            },
            'garantia_dupla': {
                'nome': 'GARANTIA DUPLA',
                'gravidade': 'critical',
                'descricao_curta': 'Fiador + caução juntos',
                'descricao_detalhada': 'Não pode exigir fiador E caução simultaneamente.',
                'lei': 'Art. 37, Lei 8.245/91',
                'icone': '🔒',
                'contestacao': 'Escolha apenas uma garantia.',
                'cor': '#ff4444'
            },
            'benfeitorias_ilegal': {
                'nome': 'BENFEITORIAS',
                'gravidade': 'critical',
                'descricao_curta': 'Renúncia a consertos',
                'descricao_detalhada': 'Não pode abrir mão de receber por melhorias necessárias.',
                'lei': 'Art. 35, Lei 8.245/91',
                'icone': '🏗️',
                'contestacao': 'Guarde notas fiscais de consertos.',
                'cor': '#ff4444'
            },
            'privacidade_violada': {
                'nome': 'PRIVACIDADE',
                'gravidade': 'medium',
                'descricao_curta': 'Visitas sem aviso',
                'descricao_detalhada': 'Proprietário não pode entrar sem aviso prévio combinado.',
                'lei': 'Art. 23, IX, Lei 8.245/91',
                'icone': '👁️',
                'contestacao': 'Exija visitas agendadas com 24h de antecedência.',
                'cor': '#ffaa44'
            },
            'multa_abusiva': {
                'nome': 'MULTA ABUSIVA',
                'gravidade': 'critical',
                'descricao_curta': 'Multa de 12 meses',
                'descricao_detalhada': 'Multa integral de 12 meses é considerada abusiva.',
                'lei': 'Art. 4º, Lei 8.245/91 e CDC',
                'icone': '💰',
                'contestacao': 'Negocie multa proporcional.',
                'cor': '#ff4444'
            },
            'venda_despeja': {
                'nome': 'VENDA DO IMÓVEL',
                'gravidade': 'medium',
                'descricao_curta': 'Venda não cancela contrato',
                'descricao_detalhada': 'Venda não rescinde automaticamente o contrato.',
                'lei': 'Art. 27, Lei 8.245/91',
                'icone': '🏠',
                'contestacao': 'Você tem 90 dias para se organizar.',
                'cor': '#ffaa44'
            },
            'proibicao_animais': {
                'nome': 'ANIMAIS',
                'gravidade': 'low',
                'descricao_curta': 'Proibição total ilegal',
                'descricao_detalhada': 'Proibição total de animais pode ser abusiva.',
                'lei': 'Art. 51, CDC e Súmula 482 STJ',
                'icone': '🐕',
                'contestacao': 'Negocie com garantias de bom comportamento.',
                'cor': '#44aaff'
            }
        }
        
        # Palavras-chave para verificação de contexto
        self.palavras_chave_contrato = [
            'contrato', 'locação', 'locador', 'locatário', 'aluguel', 'imóvel',
            'cláusula', 'vigência', 'obrigações', 'direitos', 'deveres'
        ]
    
    def preparar_texto_avancado(self, texto):
        """Prepara texto com técnicas avançadas de normalização"""
        if not texto:
            return ""
        
        # 1. Remove acentos e caracteres especiais
        texto = unicodedata.normalize('NFKD', texto)
        texto = ''.join([c for c in texto if not unicodedata.combining(c)])
        
        # 2. Padroniza espaços e quebras de linha
        texto = re.sub(r'\s+', ' ', texto)
        
        # 3. Converte para minúsculas
        texto = texto.lower()
        
        # 4. Expande sinônimos para melhor detecção
        for palavra, sinonimos in self.sinonimos.items():
            for sinonimo in sinonimos:
                texto = texto.replace(sinonimo, palavra)
        
        # 5. Remove pontuação excessiva
        texto = re.sub(r'[^\w\s]', ' ', texto)
        texto = re.sub(r'\s+', ' ', texto)
        
        return texto.strip()
    
    def verificar_contexto(self, texto, palavras_contexto, posicao):
        """Verifica se o contexto ao redor da detecção é relevante"""
        if not palavras_contexto:
            return True
        
        # Extrair contexto (200 caracteres antes e depois)
        inicio = max(0, posicao - 200)
        fim = min(len(texto), posicao + 200)
        contexto = texto[inicio:fim].lower()
        
        # Contar palavras de contexto presentes
        palavras_encontradas = sum(1 for palavra in palavras_contexto if palavra in contexto)
        
        # Retorna True se pelo menos 60% das palavras de contexto estiverem presentes
        return (palavras_encontradas / len(palavras_contexto)) >= 0.6
    
    def calcular_confianca(self, match, contexto_relevante, palavras_chave_encontradas):
        """Calcula nível de confiança da detecção"""
        confianca = 0.5  # Base
        
        # 1. Comprimento do match (mais longo = mais específico)
        if len(match.group()) > 15:
            confianca += 0.2
        
        # 2. Contexto relevante
        if contexto_relevante:
            confianca += 0.15
        
        # 3. Palavras-chave do contrato presentes
        if palavras_chave_encontradas >= 3:
            confianca += 0.1
        elif palavras_chave_encontradas >= 5:
            confianca += 0.2
        
        # 4. Localização no texto (primeiras 1000 palavras = mais importante)
        if match.start() < 1000:
            confianca += 0.05
        
        return min(confianca, 1.0)
    
    def obter_nivel_confianca(self, valor):
        """Converte valor numérico em nível de confiança"""
        if valor >= 0.8:
            return "ALTA", "#00ff00"
        elif valor >= 0.6:
            return "MÉDIA", "#ffff00"
        else:
            return "BAIXA", "#ff4444"
    
    def analisar_documento_avancado(self, texto):
        """Análise avançada com múltiplas camadas de verificação"""
        texto_preparado = self.preparar_texto_avancado(texto)
        texto_original = texto.lower()
        
        # Verificar se é realmente um contrato de locação
        palavras_contrato_encontradas = sum(1 for palavra in self.palavras_chave_contrato 
                                          if palavra in texto_original)
        
        if palavras_contrato_encontradas < 3:
            return []  # Provavelmente não é um contrato de locação
        
        problemas_detectados = []
        
        for chave, config in self.padroes_avancados.items():
            melhor_match = None
            melhor_confianca = 0
            melhor_contexto = ""
            
            # Padrões específicos para cada tipo
            padroes = []
            if chave == 'reajuste_ilegal':
                padroes = [
                    r'reajuste.*?(trimestral|mensal|semestral|bianual|bimestral)',
                    r'reajuste.*?(a cada|cada).*?(3|4|6).*?(mes|mês)'
                ]
            elif chave == 'garantia_dupla':
                padroes = [
                    r'(fiador|fiadores).*?(e|mais|alem|com|juntamente).*?(caucao|deposito|seguro|garantia)',
                    r'(caucao|deposito|seguro|garantia).*?(e|mais|alem|com|juntamente).*?(fiador|fiadores)'
                ]
            elif chave == 'benfeitorias_ilegal':
                padroes = [
                    r'renuncia.*?(benfeitoria|reforma|obra|melhoria)',
                    r'(nao|não).*?(indeniza|recebe|tem direito|ressarce).*?(benfeitoria|reforma|obra)'
                ]
            elif chave == 'privacidade_violada':
                padroes = [
                    r'(qualquer|a qualquer|livre).*?(visita|vistoria|ingresso|acesso)',
                    r'(sem|dispensa|dispensado).*?(aviso|notificação|comunicação).*?(visita|vistoria|entrar)'
                ]
            elif chave == 'multa_abusiva':
                padroes = [
                    r'multa.*?(12|doze).*?meses',
                    r'(12|doze).*?meses.*?multa'
                ]
            elif chave == 'venda_despeja':
                padroes = [
                    r'venda.*?(rescindido|rescisão|terminado|extinto).*?automaticamente',
                    r'alienação.*?rescindir.*?contrato'
                ]
            elif chave == 'proibicao_animais':
                padroes = [
                    r'proibido.*?animais',
                    r'vedado.*?animais'
                ]
            
            for padrao in padroes:
                try:
                    matches = list(re.finditer(padrao, texto_preparado, re.IGNORECASE))
                    
                    for match in matches:
                        # Verificar contexto
                        contexto_relevante = self.verificar_contexto(
                            texto_preparado, 
                            ['contrato', 'aluguel', 'locação'], 
                            match.start()
                        )
                        
                        # Calcular confiança
                        confianca = self.calcular_confianca(
                            match, 
                            contexto_relevante, 
                            palavras_contrato_encontradas
                        )
                        
                        # Manter apenas o match com maior confiança
                        if confianca > melhor_confianca and confianca >= 0.5:
                            melhor_match = match
                            melhor_confianca = confianca
                            
                            # Extrair contexto
                            inicio = max(0, match.start() - 100)
                            fim = min(len(texto_preparado), match.end() + 100)
                            melhor_contexto = texto_preparado[inicio:fim]
                
                except Exception as e:
                    continue
            
            if melhor_match and melhor_confianca >= 0.5:
                nivel_confianca, cor_confianca = self.obter_nivel_confianca(melhor_confianca)
                
                problemas_detectados.append({
                    'id': chave,
                    'nome': config['nome'],
                    'gravidade': config['gravidade'],
                    'descricao_curta': config['descricao_curta'],
                    'descricao_detalhada': config['descricao_detalhada'],
                    'lei': config['lei'],
                    'icone': config['icone'],
                    'contestacao': config['contestacao'],
                    'contexto': f"...{melhor_contexto}..." if melhor_contexto else "",
                    'confianca': melhor_confianca,
                    'nivel_confianca': nivel_confianca,
                    'cor_confianca': cor_confianca,
                    'cor_gravidade': config['cor'],
                    'posicao': melhor_match.start()
                })
        
        # Ordenar por gravidade e depois por confiança
        ordem_gravidade = {'critical': 0, 'medium': 1, 'low': 2}
        problemas_detectados.sort(key=lambda x: (
            ordem_gravidade.get(x['gravidade'], 3),
            -x['confianca']  # Confiança decrescente
        ))
        
        return problemas_detectados
    
    def gerar_metricas_detalhadas(self, problemas):
        """Gera métricas detalhadas com estatísticas avançadas"""
        total_problemas = len(problemas)
        
        # Contagem por gravidade
        criticos = sum(1 for p in problemas if p['gravidade'] == 'critical')
        medios = sum(1 for p in problemas if p['gravidade'] == 'medium')
        leves = sum(1 for p in problemas if p['gravidade'] == 'low')
        
        # Média de confiança
        media_confianca = sum(p['confianca'] for p in problemas) / total_problemas if total_problemas > 0 else 0
        
        # Score de conformidade ponderado por confiança
        penalidade = 0
        for problema in problemas:
            peso = problema['confianca']  # Ponderar pela confiança
            
            if problema['gravidade'] == 'critical':
                penalidade += 25 * peso
            elif problema['gravidade'] == 'medium':
                penalidade += 15 * peso
            else:
                penalidade += 5 * peso
        
        score = max(100 - penalidade, 0)
        
        # Nível de risco ajustado
        if criticos > 0:
            nivel_risco = 'ALTO RISCO'
        elif medios > 0:
            nivel_risco = 'ATENÇÃO'
        else:
            nivel_risco = 'BAIXO RISCO'
        
        return {
            'total_problemas': total_problemas,
            'criticos': criticos,
            'medios': medios,
            'leves': leves,
            'score_conformidade': score,
            'media_confianca': media_confianca,
            'nivel_risco': nivel_risco
        }

# --------------------------------------------------
# FUNÇÕES AUXILIARES
# --------------------------------------------------

def extrair_texto_pdf_completo(arquivo):
    """Extrai texto de PDF com tratamento de erros"""
    try:
        with pdfplumber.open(arquivo) as pdf:
            texto_completo = ""
            
            for i, pagina in enumerate(pdf.pages):
                try:
                    conteudo = pagina.extract_text() or ""
                    
                    # Adiciona marcador de página
                    if conteudo.strip():
                        texto_completo += f"\n[PÁGINA {i+1}]\n{conteudo}\n"
                except:
                    continue
            
            if not texto_completo.strip():
                st.error("❌ O PDF não contém texto extraível. Pode ser uma imagem ou documento protegido.")
                return None
            
            return texto_completo
    except Exception as e:
        st.error(f"❌ Erro ao processar PDF: {str(e)}")
        return None

# --------------------------------------------------
# INTERFACE PRINCIPAL
# --------------------------------------------------

def main():
    # Cabeçalho profissional com tema escuro e dourado
    st.markdown("""
    <div class="main-header fade-in">
        <h1 style="margin: 0; font-size: 3em; color: #d4af37; text-shadow: 0 0 20px rgba(212, 175, 55, 0.5);">⚖️ BUROCRATA DE BOLSO</h1>
        <p style="margin: 10px 0 0 0; font-size: 1.3em; color: #ffffff; opacity: 0.9;">Auditoria Jurídica Inteligente</p>
        <p style="margin: 5px 0 0 0; font-size: 0.9em; color: #d4af37; opacity: 0.7;">
            <span class="system-status">SISTEMA ATIVO</span> • Versão 10.0
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializar sistema
    auditoria = SistemaAuditoriaAltaPrecisao()
    
    # Área de upload centralizada
    st.markdown("""
    <div style="text-align: center; margin: 40px 0;">
        <h2 style="color: #d4af37; font-size: 2em;">📤 ENVIE SEU CONTRATO</h2>
        <p style="color: #cccccc; margin-bottom: 20px; font-size: 1.1em;">
            Analise seu contrato de aluguel em segundos
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_upload = st.columns([1, 2, 1])[1]
    
    with col_upload:
        arquivo = st.file_uploader(
            "",
            type=["pdf"],
            label_visibility="collapsed",
            help="Arraste ou clique para selecionar um arquivo PDF"
        )
    
    # Processar se arquivo carregado
    if arquivo:
        with st.spinner("🔍 Analisando seu contrato..."):
            # Extrair texto
            texto = extrair_texto_pdf_completo(arquivo)
            
            if texto:
                # Analisar documento com sistema avançado
                problemas = auditoria.analisar_documento_avancado(texto)
                metricas = auditoria.gerar_metricas_detalhadas(problemas)
                
                # Divisor dourado
                st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)
                
                # Título dos resultados
                st.markdown(f"""
                <div style="text-align: center; margin: 40px 0;">
                    <h2 style="color: #d4af37; font-size: 2.2em;">📊 RESULTADO DA ANÁLISE</h2>
                    <p style="color: #cccccc; font-size: 1.1em;">
                        Documento: <span style="color: #d4af37; font-weight: bold;">{arquivo.name}</span>
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Painel de métricas principal - SIMPLIFICADO
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card" style="border-top-color: #d4af37;">
                        <h3 style="margin: 0; font-size: 2.5em; color: #d4af37;">{metricas['total_problemas']}</h3>
                        <p style="margin: 10px 0 0 0; font-weight: 600; font-size: 1.1em;">PROBLEMAS</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    cor_score = "#00ff00" if metricas['score_conformidade'] >= 80 else "#ffaa44" if metricas['score_conformidade'] >= 60 else "#ff4444"
                    st.markdown(f"""
                    <div class="metric-card" style="border-top-color: {cor_score};">
                        <h3 style="margin: 0; font-size: 2.5em; color: {cor_score};">{metricas['score_conformidade']:.0f}</h3>
                        <p style="margin: 10px 0 0 0; font-weight: 600; font-size: 1.1em;">SCORE</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    cor_risco = "#ff4444" if metricas['nivel_risco'] == 'ALTO RISCO' else "#ffaa44" if metricas['nivel_risco'] == 'ATENÇÃO' else "#00ff00"
                    st.markdown(f"""
                    <div class="metric-card" style="border-top-color: {cor_risco};">
                        <h3 style="margin: 0; font-size: 1.8em; color: {cor_risco};">{metricas['nivel_risco']}</h3>
                        <p style="margin: 10px 0 0 0; font-weight: 600; font-size: 1.1em;">RISCO</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Divisor
                st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)
                
                # ÍCONES DOS PROBLEMAS - DESIGN MINIMALISTA
                if problemas:
                    st.markdown(f"""
                    <div style="text-align: center; margin: 30px 0;">
                        <h3 style="color: #d4af37; font-size: 1.8em;">🔍 CLÁUSULAS PROBLEMÁTICAS</h3>
                        <p style="color: #cccccc; font-size: 1em;">
                            Passe o mouse sobre os ícones para detalhes
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown('<div class="problems-icons-container fade-in">', unsafe_allow_html=True)
                    
                    # Mostrar ícones em linha
                    col_count = min(len(problemas), 4)
                    cols = st.columns(col_count)
                    
                    for idx, problema in enumerate(problemas):
                        with cols[idx % col_count]:
                            # Determinar classe CSS baseado na gravidade
                            classe_css = {
                                'critical': 'critical-icon',
                                'medium': 'medium-icon',
                                'low': 'low-icon'
                            }.get(problema['gravidade'], 'low-icon')
                            
                            # Determinar classe de severidade
                            severidade_css = {
                                'critical': 'severity-critical',
                                'medium': 'severity-medium',
                                'low': 'severity-low'
                            }.get(problema['gravidade'], 'severity-low')
                            
                            # Texto da severidade
                            texto_severidade = {
                                'critical': 'CRÍTICO',
                                'medium': 'MÉDIO',
                                'low': 'BAIXO'
                            }.get(problema['gravidade'], 'BAIXO')
                            
                            st.markdown(f"""
                            <div class="problem-icon {classe_css}">
                                <span class="icon-emoji">{problema['icone']}</span>
                                <div class="icon-title">{problema['nome']}</div>
                                <span class="icon-severity {severidade_css}">{texto_severidade}</span>
                                
                                <div class="problem-tooltip">
                                    <div class="tooltip-section tooltip-violation">
                                        <strong>❌ Problema:</strong><br>
                                        {problema['descricao_detalhada']}
                                    </div>
                                    
                                    <div class="tooltip-section tooltip-law">
                                        <strong>⚖️ Lei:</strong><br>
                                        {problema['lei']}
                                    </div>
                                    
                                    <div class="tooltip-section tooltip-solution">
                                        <strong>✅ Solução:</strong><br>
                                        {problema['contestacao']}
                                    </div>
                                    
                                    <div style="margin-top: 10px; font-size: 0.8em; color: #d4af37;">
                                        Confiança: {problema['nivel_confianca']} ({problema['confianca']:.0%})
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    # Mensagem quando nenhum problema é encontrado
                    st.markdown("""
                    <div style="text-align: center; padding: 40px; background: rgba(0, 100, 0, 0.2); border-radius: 15px; margin: 40px 0; border: 2px solid #00ff00;">
                        <div style="font-size: 4em; color: #00ff00;">✅</div>
                        <h3 style="color: #00ff00; margin: 20px 0; font-size: 1.8em;">CONTRATO REGULAR!</h3>
                        <p style="color: #cccccc; font-size: 1.1em;">
                            Seu contrato está em conformidade com a legislação.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Botão para exportar relatório
                if problemas:
                    st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)
                    
                    # Criar DataFrame para exportação
                    dados_exportar = []
                    for p in problemas:
                        dados_exportar.append({
                            'Problema': p['nome'],
                            'Gravidade': p['gravidade'].upper(),
                            'Descrição': p['descricao_detalhada'],
                            'Artigo da Lei': p['lei'],
                            'Como Contestar': p['contestacao'],
                            'Confiança': f"{p['confianca']:.1%}"
                        })
                    
                    df_relatorio = pd.DataFrame(dados_exportar)
                    
                    # Converter para CSV
                    csv_buffer = io.StringIO()
                    df_relatorio.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
                    csv_str = csv_buffer.getvalue()
                    
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        st.download_button(
                            label="📥 BAIXAR RELATÓRIO",
                            data=csv_str,
                            file_name=f"relatorio_contrato_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            use_container_width=True,
                            type="primary"
                        )
    else:
        # Mensagem inicial quando nenhum arquivo foi carregado
        st.markdown("""
        <div class="upload-container fade-in">
            <div style="font-size: 5em; color: #d4af37; margin-bottom: 20px;">📄</div>
            <h3 style="color: #ffffff; margin: 20px 0; font-size: 1.8em;">ENVIE SEU CONTRATO</h3>
            <p style="color: #cccccc; font-size: 1.1em; max-width: 600px; margin: 0 auto 30px auto;">
                Analise cláusulas abusivas em contratos de aluguel
            </p>
            <div style="background: rgba(212, 175, 55, 0.1); padding: 20px; border-radius: 10px; display: inline-block;">
                <p style="margin: 0; color: #d4af37; font-weight: bold;">
                    🔒 100% SEGURO
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
