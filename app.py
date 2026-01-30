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
# ESTILOS PROFISSIONAIS
# --------------------------------------------------
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        text-align: center;
        border-top: 4px solid;
    }
    
    .issue-card {
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 5px solid;
    }
    
    .critical-card { border-left-color: #ef4444; }
    .medium-card { border-left-color: #f59e0b; }
    .low-card { border-left-color: #10b981; }
    
    .confidence-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75em;
        font-weight: 600;
        margin-left: 8px;
    }
    
    .confidence-high { background: #d1fae5; color: #065f46; }
    .confidence-medium { background: #fef3c7; color: #92400e; }
    .confidence-low { background: #fee2e2; color: #991b1b; }
    
    .upload-container {
        border: 2px dashed #d1d5db;
        border-radius: 12px;
        padding: 40px;
        text-align: center;
        background: #f8fafc;
        margin: 20px 0;
        transition: all 0.3s;
    }
    
    .stat-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: 600;
        margin: 2px;
    }
    
    .badge-critical { background: #fee2e2; color: #dc2626; }
    .badge-medium { background: #fef3c7; color: #d97706; }
    .badge-low { background: #d1fae5; color: #059669; }
    
    .progress-bar-container {
        height: 20px;
        background: #e5e7eb;
        border-radius: 10px;
        margin: 10px 0;
        overflow: hidden;
    }
    
    .progress-bar-fill {
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s ease;
    }
    
    .score-excellent { background: linear-gradient(90deg, #10b981, #34d399); }
    .score-medium { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
    .score-poor { background: linear-gradient(90deg, #ef4444, #f87171); }
    
    .title-with-outline {
        color: white;
        text-shadow: 
            2px 2px 0 #000,
            -2px -2px 0 #000,
            2px -2px 0 #000,
            -2px 2px 0 #000,
            0px 2px 0 #000,
            2px 0px 0 #000,
            0px -2px 0 #000,
            -2px 0px 0 #000,
            2px 2px 5px rgba(0,0,0,0.3);
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
                'nome': 'Reajuste Ilegal',
                'gravidade': 'critical',
                'descricao': 'O reajuste de aluguel deve ser ANUAL (12 meses). Períodos menores são ilegais.',
                'lei': 'Lei 10.192/01',
                'icone': '📅',
                'padroes_exatos': [
                    r'reajuste.*?(trimestral|mensal|semestral|bianual|bimestral)',
                    r'reajuste.*?(a cada|cada).*?(3|4|6).*?(mes|mês)',
                    r'reajuste.*?(periodicidade|periodo).*?(3|4|6).*?meses',
                    r'(trimestral|mensal|semestral).*?reajuste',
                    r'calculo.*?reajuste.*?(3|4|6).*?meses'
                ],
                'contexto_minimo': ['reajuste', 'aluguel', 'valor', 'atualização'],
                'confianca_minima': 0.7
            },
            'garantia_dupla': {
                'nome': 'Garantia Dupla Ilegal',
                'gravidade': 'critical',
                'descricao': 'É proibido exigir mais de uma garantia no mesmo contrato (ex: fiador E caução).',
                'lei': 'Art. 37, Lei 8.245/91',
                'icone': '🔒',
                'padroes_exatos': [
                    r'(fiador|fiadores).*?(e|mais|alem|com|juntamente).*?(caucao|deposito|seguro|garantia)',
                    r'(caucao|deposito|seguro|garantia).*?(e|mais|alem|com|juntamente).*?(fiador|fiadores)',
                    r'(exige|requer|necessita).*?(fiador|fiadores).*?(caucao|deposito)',
                    r'(exige|requer|necessita).*?(caucao|deposito).*?(fiador|fiadores)',
                    r'dupla.*?garantia.*?(fiador|caucao)',
                    r'(fiador|fiadores).*?e.*?(caucao|deposito).*?simultaneamente',
                    r'(fiador|fiadores).*?acompanhado.*?(caucao|deposito)'
                ],
                'contexto_minimo': ['garantia', 'fiador', 'caução', 'depósito', 'seguro'],
                'confianca_minima': 0.8
            },
            'benfeitorias_ilegal': {
                'nome': 'Renúncia Ilegal a Benfeitorias',
                'gravidade': 'critical',
                'descricao': 'O inquilino tem direito a indenização por benfeitorias necessárias.',
                'lei': 'Art. 35, Lei 8.245/91',
                'icone': '🏗️',
                'padroes_exatos': [
                    r'renuncia.*?(benfeitoria|reforma|obra|melhoria)',
                    r'(nao|não).*?(indeniza|recebe|tem direito|ressarce).*?(benfeitoria|reforma|obra)',
                    r'(sem|isento|isenção).*?(direito|indenização).*?(benfeitoria|reforma|obra)',
                    r'abre.*?mao.*?(benfeitoria|reforma|obra)',
                    r'renuncia.*?expressamente.*?(benfeitoria|reforma)',
                    r'(nao|não).*?(haverá|existira).*?indenizacao.*?(benfeitoria|reforma)'
                ],
                'contexto_minimo': ['benfeitoria', 'reforma', 'obra', 'indenização', 'direito'],
                'confianca_minima': 0.75
            },
            'privacidade_violada': {
                'nome': 'Violação de Privacidade',
                'gravidade': 'medium',
                'descricao': 'O locador não pode entrar no imóvel sem aviso prévio e hora combinada.',
                'lei': 'Art. 23, IX, Lei 8.245/91',
                'icone': '👁️',
                'padroes_exatos': [
                    r'(qualquer|a qualquer|livre).*?(visita|vistoria|ingresso|acesso)',
                    r'(sem|dispensa|dispensado).*?(aviso|notificação|comunicação).*?(visita|vistoria|entrar)',
                    r'visita.*?(sem|dispensa).*?aviso',
                    r'vistoria.*?(sem|dispensa).*?aviso',
                    r'(qualquer|a qualquer).*?momento.*?(visita|vistoria)',
                    r'(livre|irrestrito).*?acesso.*?(visita|vistoria)'
                ],
                'contexto_minimo': ['visita', 'vistoria', 'aviso', 'locador', 'entrar'],
                'confianca_minima': 0.6
            },
            'multa_abusiva': {
                'nome': 'Multa Abusiva',
                'gravidade': 'critical',
                'descricao': 'A multa deve ser proporcional ao tempo restante. Multa integral de 12 meses é abusiva.',
                'lei': 'Art. 4º, Lei 8.245/91 e CDC',
                'icone': '💰',
                'padroes_exatos': [
                    r'multa.*?(12|doze).*?meses',
                    r'(12|doze).*?meses.*?multa',
                    r'multa.*?integral.*?(aluguel|valor)',
                    r'multa.*?total.*?(aluguel|valor)',
                    r'multa.*?correspondente.*?(12|doze|integral|total)',
                    r'pagar.*?(12|doze).*?meses.*?multa',
                    r'multa.*?equivalente.*?(12|doze).*?meses',
                    r'(indenizar|compensar).*?(12|doze).*?meses.*?aluguel'
                ],
                'contexto_minimo': ['multa', 'rescisão', 'aluguel', 'meses', 'valor'],
                'confianca_minima': 0.85
            },
            'venda_despeja': {
                'nome': 'Venda Despeja Inquilino',
                'gravidade': 'medium',
                'descricao': 'A venda do imóvel não rescinde automaticamente o contrato. Inquilino tem preferência.',
                'lei': 'Art. 27, Lei 8.245/91',
                'icone': '🏠',
                'padroes_exatos': [
                    r'venda.*?(rescindido|rescisão|terminado|extinto).*?automaticamente',
                    r'alienação.*?rescindir.*?contrato',
                    r'venda.*?imovel.*?(rescisão|rescindido).*?automatica',
                    r'(alienação|transferência).*?determina.*?rescisão',
                    r'venda.*?acarreta.*?rescisão.*?automatica'
                ],
                'contexto_minimo': ['venda', 'alienação', 'rescisão', 'contrato', 'automático'],
                'confianca_minima': 0.65
            },
            'proibicao_animais': {
                'nome': 'Proibição Total de Animais',
                'gravidade': 'low',
                'descricao': 'A proibição total de animais pode ser abusiva. Apenas por justa causa.',
                'lei': 'Art. 51, CDC e Súmula 482 STJ',
                'icone': '🐕',
                'padroes_exatos': [
                    r'proibido.*?animais',
                    r'vedado.*?animais',
                    r'(nao|não).*?permitido.*?animais',
                    r'proibição.*?total.*?animais',
                    r'(nao|não).*?animais.*?estimação',
                    r'interdita.*?presença.*?animais'
                ],
                'contexto_minimo': ['animais', 'proibido', 'vedado', 'permitido', 'pet'],
                'confianca_minima': 0.5
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
            return "alta", "confidence-high"
        elif valor >= 0.6:
            return "média", "confidence-medium"
        else:
            return "baixa", "confidence-low"
    
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
            
            for padrao in config['padroes_exatos']:
                try:
                    matches = list(re.finditer(padrao, texto_preparado, re.IGNORECASE))
                    
                    for match in matches:
                        # Verificar contexto
                        contexto_relevante = self.verificar_contexto(
                            texto_preparado, 
                            config['contexto_minimo'], 
                            match.start()
                        )
                        
                        # Calcular confiança
                        confianca = self.calcular_confianca(
                            match, 
                            contexto_relevante, 
                            palavras_contrato_encontradas
                        )
                        
                        # Manter apenas o match com maior confiança
                        if confianca > melhor_confianca and confianca >= config['confianca_minima']:
                            melhor_match = match
                            melhor_confianca = confianca
                            
                            # Extrair contexto
                            inicio = max(0, match.start() - 100)
                            fim = min(len(texto_preparado), match.end() + 100)
                            melhor_contexto = texto_preparado[inicio:fim]
                
                except Exception as e:
                    continue
            
            if melhor_match and melhor_confianca >= config['confianca_minima']:
                nivel_confianca, classe_confianca = self.obter_nivel_confianca(melhor_confianca)
                
                problemas_detectados.append({
                    'id': chave,
                    'nome': config['nome'],
                    'gravidade': config['gravidade'],
                    'descricao': config['descricao'],
                    'lei': config['lei'],
                    'icone': config['icone'],
                    'contexto': f"...{melhor_contexto}..." if melhor_contexto else "",
                    'confianca': melhor_confianca,
                    'nivel_confianca': nivel_confianca,
                    'classe_confianca': classe_confianca,
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
        
        # Distribuição por confiança
        alta_confianca = sum(1 for p in problemas if p['confianca'] >= 0.8)
        media_confianca_count = sum(1 for p in problemas if 0.6 <= p['confianca'] < 0.8)
        baixa_confianca = sum(1 for p in problemas if p['confianca'] < 0.6)
        
        # Score de conformidade ponderado por confiança
        penalidade = 0
        for problema in problemas:
            peso = problema['confianca']  # Ponderar pela confiança
            
            if problema['gravidade'] == 'critical':
                penalidade += 20 * peso
            elif problema['gravidade'] == 'medium':
                penalidade += 10 * peso
            else:
                penalidade += 5 * peso
        
        score = max(100 - penalidade, 0)
        
        # Nível de risco ajustado
        if criticos > 0:
            if media_confianca > 0.7:
                nivel_risco = 'ALTO'
            else:
                nivel_risco = 'ALTO (confiança moderada)'
        elif medios > 0:
            nivel_risco = 'MÉDIO'
        else:
            nivel_risco = 'BAIXO'
        
        return {
            'total_problemas': total_problemas,
            'criticos': criticos,
            'medios': medios,
            'leves': leves,
            'score_conformidade': score,
            'media_confianca': media_confianca,
            'alta_confianca': alta_confianca,
            'media_confianca_count': media_confianca_count,
            'baixa_confianca': baixa_confianca,
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

def criar_grafico_distribuicao_html(metricas):
    """Cria gráfico de distribuição usando HTML/CSS"""
    if metricas['total_problemas'] == 0:
        return None
    
    total = metricas['total_problemas']
    crit_percent = (metricas['criticos'] / total) * 100 if total > 0 else 0
    med_percent = (metricas['medios'] / total) * 100 if total > 0 else 0
    lev_percent = (metricas['leves'] / total) * 100 if total > 0 else 0
    
    html = f"""
    <div style="margin: 20px 0;">
        <h4 style="margin-bottom: 15px; color: #1e3a8a;">📊 Distribuição por Gravidade</h4>
        <div style="display: flex; height: 40px; border-radius: 8px; overflow: hidden; margin-bottom: 10px;">
            <div style="flex: {metricas['criticos']}; background: #ef4444; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                {metricas['criticos']}
            </div>
            <div style="flex: {metricas['medios']}; background: #f59e0b; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                {metricas['medios']}
            </div>
            <div style="flex: {metricas['leves']}; background: #10b981; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                {metricas['leves']}
            </div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.9em; color: #6b7280;">
            <div>🚨 Críticos: {crit_percent:.1f}%</div>
            <div>⚠️ Médios: {med_percent:.1f}%</div>
            <div>ℹ️ Leves: {lev_percent:.1f}%</div>
        </div>
    </div>
    """
    return html

def criar_grafico_score_html(score):
    """Cria gráfico de score usando HTML/CSS"""
    if score >= 80:
        score_class = "score-excellent"
        status = "EXCELENTE"
        color = "#10b981"
    elif score >= 60:
        score_class = "score-medium"
        status = "ATENÇÃO"
        color = "#f59e0b"
    else:
        score_class = "score-poor"
        status = "CRÍTICO"
        color = "#ef4444"
    
    html = f"""
    <div style="text-align: center; margin: 20px 0;">
        <h4 style="margin-bottom: 15px; color: #1e3a8a;">🎯 Índice de Conformidade</h4>
        <div style="position: relative; margin: 0 auto; width: 200px; height: 200px;">
            <div style="position: absolute; top: 0; left: 0; width: 200px; height: 200px; border-radius: 50%; background: conic-gradient(
                {color} 0% {score}%,
                #e5e7eb {score}% 100%
            );"></div>
            <div style="position: absolute; top: 20px; left: 20px; width: 160px; height: 160px; border-radius: 50%; background: white; display: flex; align-items: center; justify-content: center; flex-direction: column;">
                <div style="font-size: 2.5em; font-weight: bold; color: {color};">{int(score)}</div>
                <div style="font-size: 1.1em; color: {color}; font-weight: bold;">{status}</div>
                <div style="font-size: 0.9em; color: #6b7280;">de 100</div>
            </div>
        </div>
    </div>
    """
    return html

def criar_grafico_confianca_html(metricas):
    """Cria gráfico de distribuição de confiança"""
    if metricas['total_problemas'] == 0:
        return None
    
    total = metricas['total_problemas']
    alta_percent = (metricas['alta_confianca'] / total) * 100 if total > 0 else 0
    media_percent = (metricas['media_confianca_count'] / total) * 100 if total > 0 else 0
    baixa_percent = (metricas['baixa_confianca'] / total) * 100 if total > 0 else 0
    
    html = f"""
    <div style="margin: 20px 0;">
        <h4 style="margin-bottom: 15px; color: #1e3a8a;">📈 Qualidade das Detecções</h4>
        <div style="display: flex; height: 30px; border-radius: 8px; overflow: hidden; margin-bottom: 10px;">
            <div style="flex: {metricas['alta_confianca']}; background: #10b981; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 0.9em;">
                {metricas['alta_confianca']}
            </div>
            <div style="flex: {metricas['media_confianca_count']}; background: #f59e0b; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 0.9em;">
                {metricas['media_confianca_count']}
            </div>
            <div style="flex: {metricas['baixa_confianca']}; background: #ef4444; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 0.9em;">
                {metricas['baixa_confianca']}
            </div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.9em; color: #6b7280;">
            <div>✅ Alta: {alta_percent:.1f}%</div>
            <div>⚠️ Média: {media_percent:.1f}%</div>
            <div>❌ Baixa: {baixa_percent:.1f}%</div>
        </div>
        <div style="margin-top: 10px; font-size: 0.85em; color: #6b7280; text-align: center;">
            Confiança média: <strong>{metricas['media_confianca']:.1%}</strong>
        </div>
    </div>
    """
    return html

# --------------------------------------------------
# INTERFACE PRINCIPAL
# --------------------------------------------------

def main():
    # Cabeçalho profissional com contorno branco
    st.markdown("""
    <div class="main-header">
        <h1 class="title-with-outline" style="margin: 0; font-size: 2.5em;">⚖️ BUROCRATA DE BOLSO</h1>
        <p style="margin: 10px 0 0 0; font-size: 1.2em; opacity: 0.9; color: white;">Sistema Inteligente de Auditoria Jurídica</p>
        <p style="margin: 5px 0 0 0; font-size: 0.9em; opacity: 0.7; color: white;">Versão 9.0 - Detecção de Alta Precisão</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializar sistema
    auditoria = SistemaAuditoriaAltaPrecisao()
    
    # Área de upload centralizada
    st.markdown("""
    <div style="text-align: center; margin: 40px 0;">
        <h2 style="color: #1e3a8a;">📤 UPLOAD DO DOCUMENTO</h2>
        <p style="color: #6b7280; margin-bottom: 20px;">Carregue seu contrato em PDF para análise avançada</p>
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
        with st.spinner("🔍 Analisando documento com sistema de alta precisão..."):
            # Extrair texto
            texto = extrair_texto_pdf_completo(arquivo)
            
            if texto:
                # Analisar documento com sistema avançado
                problemas = auditoria.analisar_documento_avancado(texto)
                metricas = auditoria.gerar_metricas_detalhadas(problemas)
                
                # Área de resultados
                st.markdown("---")
                
                # Título dos resultados
                st.markdown(f"""
                <div style="text-align: center; margin: 30px 0;">
                    <h2 style="color: #1e3a8a;">📊 RESULTADOS DA ANÁLISE AVANÇADA</h2>
                    <p style="color: #6b7280;">Documento: <strong>{arquivo.name}</strong> | {len(texto):,} caracteres analisados</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Painel de métricas principal
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card" style="border-top-color: #3b82f6;">
                        <h3 style="margin: 0; color: #1e3a8a;">{metricas['total_problemas']}</h3>
                        <p style="margin: 5px 0 0 0; font-weight: 600;">Total de Problemas</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-card" style="border-top-color: #ef4444;">
                        <h3 style="margin: 0; color: #1e3a8a;">{metricas['criticos']}</h3>
                        <p style="margin: 5px 0 0 0; font-weight: 600;">Problemas Críticos</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="metric-card" style="border-top-color: #f59e0b;">
                        <h3 style="margin: 0; color: #1e3a8a;">{metricas['score_conformidade']:.0f}</h3>
                        <p style="margin: 5px 0 0 0; font-weight: 600;">Score de Conformidade</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""
                    <div class="metric-card" style="border-top-color: #10b981;">
                        <h3 style="margin: 0; color: #1e3a8a;">{metricas['nivel_risco']}</h3>
                        <p style="margin: 5px 0 0 0; font-weight: 600;">Nível de Risco</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Gráficos e visualizações
                col_left, col_right = st.columns([1, 1])
                
                with col_left:
                    # Gráfico de distribuição
                    html_dist = criar_grafico_distribuicao_html(metricas)
                    if html_dist:
                        st.markdown(html_dist, unsafe_allow_html=True)
                    
                    # Gráfico de confiança
                    html_conf = criar_grafico_confianca_html(metricas)
                    if html_conf:
                        st.markdown(html_conf, unsafe_allow_html=True)
                
                with col_right:
                    # Gráfico de score
                    html_score = criar_grafico_score_html(metricas['score_conformidade'])
                    if html_score:
                        st.markdown(html_score, unsafe_allow_html=True)
                
                # Lista de problemas detectados
                st.markdown("---")
                st.markdown(f"""
                <div style="margin: 30px 0;">
                    <h2 style="color: #1e3a8a;">🔍 PROBLEMAS DETECTADOS</h2>
                    <p style="color: #6b7280;">
                        {len(problemas)} problema(s) encontrado(s) com sistema de detecção avançado
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                if problemas:
                    for i, problema in enumerate(problemas, 1):
                        # Determinar classe CSS baseado na gravidade
                        classe_gravidade = {
                            'critical': 'critical-card',
                            'medium': 'medium-card',
                            'low': 'low-card'
                        }.get(problema['gravidade'], 'low-card')
                        
                        # Determinar cor do ícone
                        cor_icone = {
                            'critical': '#ef4444',
                            'medium': '#f59e0b',
                            'low': '#10b981'
                        }.get(problema['gravidade'], '#10b981')
                        
                        # Determinar cor da gravidade
                        cor_gravidade = {
                            'critical': 'Crítico',
                            'medium': 'Médio',
                            'low': 'Leve'
                        }.get(problema['gravidade'], 'Leve')
                        
                        cor_texto_gravidade = {
                            'critical': '#dc2626',
                            'medium': '#d97706',
                            'low': '#059669'
                        }.get(problema['gravidade'], '#059669')
                        
                        st.markdown(f"""
                        <div class="issue-card {classe_gravidade}">
                            <div style="display: flex; align-items: center; justify-content: space-between;">
                                <div style="display: flex; align-items: center; gap: 10px;">
                                    <div style="font-size: 1.5em;">{problema['icone']}</div>
                                    <div>
                                        <h4 style="margin: 0; color: #1e3a8a;">#{i}: {problema['nome']}</h4>
                                        <div style="display: flex; gap: 15px; margin-top: 5px;">
                                            <span style="color: {cor_texto_gravidade}; font-weight: 600;">
                                                🔴 Gravidade: {cor_gravidade}
                                            </span>
                                            <span style="color: #6b7280;">
                                                📚 Base Legal: {problema['lei']}
                                            </span>
                                            <span class="confidence-badge {problema['classe_confianca']}">
                                                Confiança: {problema['nivel_confianca']} ({problema['confianca']:.0%})
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div style="margin-top: 15px;">
                                <p style="margin: 0 0 10px 0; color: #374151;">
                                    {problema['descricao']}
                                </p>
                                <div style="background: #f9fafb; padding: 12px; border-radius: 6px; margin-top: 10px;">
                                    <p style="margin: 0; font-size: 0.9em; color: #6b7280; font-style: italic;">
                                        <strong>Contexto encontrado:</strong> {problema['contexto']}
                                    </p>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="text-align: center; padding: 50px; background: #f0fdf4; border-radius: 10px; margin: 20px 0;">
                        <div style="font-size: 4em; color: #10b981;">✅</div>
                        <h3 style="color: #065f46; margin: 10px 0;">Nenhum problema detectado!</h3>
                        <p style="color: #059669;">Este contrato parece estar em conformidade com a legislação brasileira.</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Botão para exportar relatório
                st.markdown("---")
                st.markdown("""
                <div style="text-align: center; margin: 30px 0;">
                    <h3 style="color: #1e3a8a;">📥 EXPORTAR RELATÓRIO</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Criar DataFrame para exportação
                if problemas:
                    dados_exportar = []
                    for p in problemas:
                        dados_exportar.append({
                            'Problema': p['nome'],
                            'Gravidade': p['gravidade'].capitalize(),
                            'Descrição': p['descricao'],
                            'Base Legal': p['lei'],
                            'Confiança (%)': f"{p['confianca']:.1%}",
                            'Contexto': p['contexto'][:200] + "..." if len(p['contexto']) > 200 else p['contexto']
                        })
                    
                    df_relatorio = pd.DataFrame(dados_exportar)
                    
                    # Converter para CSV
                    csv_buffer = io.StringIO()
                    df_relatorio.to_csv(csv_buffer, index=False)
                    csv_str = csv_buffer.getvalue()
                    
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        st.download_button(
                            label="📊 Baixar Relatório em CSV",
                            data=csv_str,
                            file_name=f"relatorio_auditoria_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
    else:
        # Mensagem inicial quando nenhum arquivo foi carregado
        st.markdown("""
        <div class="upload-container">
            <div style="font-size: 4em; color: #9ca3af;">📄</div>
            <h3 style="color: #4b5563; margin: 20px 0;">Arraste seu contrato em PDF aqui</h3>
            <p style="color: #6b7280;">Ou clique para selecionar um arquivo</p>
            <p style="color: #9ca3af; font-size: 0.9em; margin-top: 30px;">
                🔒 Seus dados são processados localmente e não são armazenados
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Informações sobre o sistema
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; margin: 40px 0;">
            <h3 style="color: #1e3a8a;">🎯 O QUE NOSSO SISTEMA DETECTA</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="padding: 20px; background: white; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <div style="font-size: 2em; text-align: center; margin-bottom: 10px;">📅</div>
                <h4 style="text-align: center; color: #1e3a8a;">Reajuste Ilegal</h4>
                <p style="text-align: center; color: #6b7280; font-size: 0.9em;">
                    Reajuste trimestral, mensal ou semestral
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="padding: 20px; background: white; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <div style="font-size: 2em; text-align: center; margin-bottom: 10px;">🔒</div>
                <h4 style="text-align: center; color: #1e3a8a;">Garantia Dupla</h4>
                <p style="text-align: center; color: #6b7280; font-size: 0.9em;">
                    Exigência de fiador E caução simultaneamente
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="padding: 20px; background: white; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <div style="font-size: 2em; text-align: center; margin-bottom: 10px;">🏗️</div>
                <h4 style="text-align: center; color: #1e3a8a;">Benfeitorias</h4>
                <p style="text-align: center; color: #6b7280; font-size: 0.9em;">
                    Renúncia ilegal a direito de indenização
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; margin: 40px 0; padding: 20px; background: #eff6ff; border-radius: 10px;">
            <h4 style="color: #1e40af;">⚖️ Base Legal</h4>
            <p style="color: #4b5563;">
                Nosso sistema utiliza a Lei 8.245/91 (Lei do Inquilinato), 
                Lei 10.192/01 e o Código de Defesa do Consumidor para identificar
                cláusulas abusivas e ilegais.
            </p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
