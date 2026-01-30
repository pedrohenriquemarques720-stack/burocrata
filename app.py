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
    
    /* Cartões de problemas - design simplificado */
    .problem-card {
        background: rgba(20, 20, 20, 0.9);
        padding: 25px;
        border-radius: 15px;
        margin: 20px 0;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.4);
        border-left: 5px solid;
        transition: all 0.3s ease;
    }
    
    .problem-card:hover {
        transform: translateX(5px);
        box-shadow: 0 8px 25px rgba(212, 175, 55, 0.2);
    }
    
    /* Cores dos problemas */
    .critical-problem { border-left-color: #ff4444; }
    .medium-problem { border-left-color: #ffaa44; }
    .low-problem { border-left-color: #44aaff; }
    
    /* Ícones dourados */
    .gold-icon {
        color: #d4af37;
        font-size: 1.8em;
        margin-right: 15px;
        text-shadow: 0 0 10px rgba(212, 175, 55, 0.5);
    }
    
    /* Badges de gravidade */
    .severity-badge {
        display: inline-block;
        padding: 6px 15px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: 700;
        margin: 5px 10px 5px 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .critical-badge {
        background: linear-gradient(135deg, #ff4444, #cc0000);
        color: white;
        border: 1px solid #ff6666;
    }
    
    .medium-badge {
        background: linear-gradient(135deg, #ffaa44, #ff8800);
        color: white;
        border: 1px solid #ffbb66;
    }
    
    .low-badge {
        background: linear-gradient(135deg, #44aaff, #0088ff);
        color: white;
        border: 1px solid #66bbff;
    }
    
    /* Badge de confiança */
    .confidence-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 0.8em;
        font-weight: 600;
        margin-left: 10px;
        background: rgba(212, 175, 55, 0.2);
        color: #d4af37;
        border: 1px solid #d4af37;
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
    
    /* Barra de progresso customizada */
    .progress-bar-container {
        height: 12px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 6px;
        margin: 15px 0;
        overflow: hidden;
        border: 1px solid rgba(212, 175, 55, 0.3);
    }
    
    .progress-bar-fill {
        height: 100%;
        border-radius: 6px;
        transition: width 0.5s ease;
    }
    
    /* Score circular */
    .score-circle {
        position: relative;
        width: 180px;
        height: 180px;
        margin: 0 auto;
    }
    
    .score-fill {
        position: absolute;
        width: 100%;
        height: 100%;
        border-radius: 50%;
        background: conic-gradient(#d4af37 0%, transparent 0%);
        transition: all 1s ease;
    }
    
    .score-inner {
        position: absolute;
        top: 15px;
        left: 15px;
        width: 150px;
        height: 150px;
        border-radius: 50%;
        background: #000000;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        border: 2px solid #d4af37;
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
    
    /* Tooltip legal */
    .law-tooltip {
        background: rgba(212, 175, 55, 0.1);
        border-left: 3px solid #d4af37;
        padding: 15px;
        margin: 15px 0;
        border-radius: 8px;
        font-style: italic;
    }
    
    /* Contexto destacado */
    .context-box {
        background: rgba(40, 40, 40, 0.9);
        border: 1px solid rgba(212, 175, 55, 0.3);
        border-radius: 10px;
        padding: 15px;
        margin: 15px 0;
        font-family: 'Courier New', monospace;
        font-size: 0.9em;
        line-height: 1.5;
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
        .problem-card {
            padding: 20px;
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
                'nome': 'REAJUSTE ILEGAL DE ALUGUEL',
                'gravidade': 'critical',
                'descricao_curta': 'Reajuste mais rápido que 12 meses é ilegal',
                'descricao_detalhada': 'A lei permite reajuste de aluguel apenas uma vez por ano (12 meses). Qualquer período menor como trimestral (3 meses) ou semestral (6 meses) é PROIBIDO.',
                'lei': 'Lei 10.192/01',
                'icone': '📅',
                'explicacao_simples': 'Imagine que seu aluguel sobe a cada 3 meses. Isso é como tomar um choque de realidade todo trimestre! A lei protege você disso.',
                'recomendacao': 'Exija que o reajuste seja ANUAL e baseado em índice oficial como IPCA ou IGP-M.',
                'cor': '#ff4444'
            },
            'garantia_dupla': {
                'nome': 'GARANTIA DUPLA - FIADOR + CAUÇÃO',
                'gravidade': 'critical',
                'descricao_curta': 'Exigir mais de uma garantia é ilegal',
                'descricao_detalhada': 'O proprietário não pode exigir FIADOR e CAUÇÃO ao mesmo tempo. Você escolhe UMA forma de garantia.',
                'lei': 'Art. 37, Lei 8.245/91',
                'icone': '🔒',
                'explicacao_simples': 'É como pedir para você trazer dois guarda-chuvas em um dia de sol. Um já basta! A lei diz que o proprietário deve aceitar apenas UMA garantia.',
                'recomendacao': 'Escolha entre fiador OU caução. Não aceite as duas coisas.',
                'cor': '#ff4444'
            },
            'benfeitorias_ilegal': {
                'nome': 'RENÚNCIA A BENFEITORIAS',
                'gravidade': 'critical',
                'descricao_curta': 'Não pode abrir mão de receber por melhorias',
                'descricao_detalhada': 'Se você pagou um conserto necessário (ex: cano estourado, telhado vazando), tem direito a receber de volta ou descontar do aluguel.',
                'lei': 'Art. 35, Lei 8.245/91',
                'icone': '🏗️',
                'explicacao_simples': 'Você conserta algo quebrado na casa e o dono diz "isso é seu dever". Não é! Gastos necessários devem ser ressarcidos.',
                'recomendacao': 'Nunca assine cláusula que renuncie a este direito. Guarde todas as notas fiscais de consertos.',
                'cor': '#ff4444'
            },
            'privacidade_violada': {
                'nome': 'VIOLAÇÃO DE PRIVACIDADE',
                'gravidade': 'medium',
                'descricao_curta': 'Proprietário não pode entrar sem avisar',
                'descricao_detalhada': 'O dono do imóvel precisa combinar dia e hora para visitas. Não pode entrar "a qualquer momento" ou "sem aviso prévio".',
                'lei': 'Art. 23, IX, Lei 8.245/91',
                'icone': '👁️',
                'explicacao_simples': 'Sua casa é seu castelo! O proprietário não pode aparecer de surpresa como se fosse dono da sua privacidade.',
                'recomendacao': 'Exija que todas as visitas sejam agendadas com pelo menos 24h de antecedência.',
                'cor': '#ffaa44'
            },
            'multa_abusiva': {
                'nome': 'MULTA ABUSIVA DE RESCISÃO',
                'gravidade': 'critical',
                'descricao_curta': 'Multa de 12 meses inteiros é abusiva',
                'descricao_detalhada': 'A multa por quebra de contrato deve ser proporcional ao tempo que falta. Multa integral de 12 meses é considerada ABUSIVA.',
                'lei': 'Art. 4º, Lei 8.245/91 e CDC',
                'icone': '💰',
                'explicacao_simples': 'Pagar 12 meses de aluguel por sair antes é como comprar um carro e ter que pagar por todos os carros da loja! A multa deve ser justa.',
                'recomendacao': 'Negocie multa proporcional: 3 meses se faltar muito tempo, menos se faltar pouco.',
                'cor': '#ff4444'
            },
            'venda_despeja': {
                'nome': 'VENDA NÃO DESPEJA INQUILINO',
                'gravidade': 'medium',
                'descricao_curta': 'Venda do imóvel não termina contrato',
                'descricao_detalhada': 'Se o proprietário vender a casa, você NÃO precisa sair imediatamente. Tem direito a 90 dias para se organizar e preferência na compra.',
                'lei': 'Art. 27, Lei 8.245/91',
                'icone': '🏠',
                'explicacao_simples': 'O dono vendeu? Você não vira sem-teto! O contrato continua válido com o novo dono e você tem tempo para se preparar.',
                'recomendacao': 'Não aceite cláusula que diga que venda automaticamente cancela o contrato.',
                'cor': '#ffaa44'
            },
            'proibicao_animais': {
                'nome': 'PROIBIÇÃO TOTAL DE ANIMAIS',
                'gravidade': 'low',
                'descricao_curta': 'Proibir animais pode ser abusivo',
                'descricao_detalhada': 'Proibição total de animais domésticos pode ser considerada abusiva. Apenas pode proibir se houver justa causa (ex: animal perigoso).',
                'lei': 'Art. 51, CDC e Súmula 482 STJ',
                'icone': '🐕',
                'explicacao_simples': 'Seu pet é da família! Proibir totalmente é como dizer que você não pode ter uma foto da sua mãe na parede.',
                'recomendacao': 'Se tiver animal, negocie essa cláusula. Ofereça garantias de bom comportamento.',
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
                            inicio = max(0, match.start() - 150)
                            fim = min(len(texto_preparado), match.end() + 150)
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
                    'explicacao_simples': config['explicacao_simples'],
                    'recomendacao': config['recomendacao'],
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
        <p style="margin: 10px 0 0 0; font-size: 1.3em; color: #ffffff; opacity: 0.9;">Auditoria Jurídica Inteligente para Contratos</p>
        <p style="margin: 5px 0 0 0; font-size: 0.9em; color: #d4af37; opacity: 0.7;">
            <span class="system-status">SISTEMA ATIVO</span> • Versão 10.0 • Detecção de Alta Precisão
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
            Analise grátis seu contrato de aluguel em menos de 1 minuto
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
        with st.spinner("🔍 Analisando seu contrato com inteligência artificial..."):
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
                        • {len(texto):,} caracteres analisados
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Painel de métricas principal
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card" style="border-top-color: #d4af37;">
                        <h3 style="margin: 0; font-size: 2.5em; color: #d4af37;">{metricas['total_problemas']}</h3>
                        <p style="margin: 10px 0 0 0; font-weight: 600; font-size: 1.1em;">PROBLEMAS ENCONTRADOS</p>
                        <p style="margin: 5px 0 0 0; color: #cccccc; font-size: 0.9em;">Análise completa do documento</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    cor_critico = "#ff4444" if metricas['criticos'] > 0 else "#cccccc"
                    st.markdown(f"""
                    <div class="metric-card" style="border-top-color: {cor_critico};">
                        <h3 style="margin: 0; font-size: 2.5em; color: {cor_critico};">{metricas['criticos']}</h3>
                        <p style="margin: 10px 0 0 0; font-weight: 600; font-size: 1.1em;">🚨 CRÍTICOS</p>
                        <p style="margin: 5px 0 0 0; color: #cccccc; font-size: 0.9em;">Exigem atenção imediata</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    cor_score = "#00ff00" if metricas['score_conformidade'] >= 80 else "#ffaa44" if metricas['score_conformidade'] >= 60 else "#ff4444"
                    st.markdown(f"""
                    <div class="metric-card" style="border-top-color: {cor_score};">
                        <h3 style="margin: 0; font-size: 2.5em; color: {cor_score};">{metricas['score_conformidade']:.0f}</h3>
                        <p style="margin: 10px 0 0 0; font-weight: 600; font-size: 1.1em;">SCORE FINAL</p>
                        <p style="margin: 5px 0 0 0; color: #cccccc; font-size: 0.9em;">de 100 pontos</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    cor_risco = "#ff4444" if metricas['nivel_risco'] == 'ALTO RISCO' else "#ffaa44" if metricas['nivel_risco'] == 'ATENÇÃO' else "#00ff00"
                    st.markdown(f"""
                    <div class="metric-card" style="border-top-color: {cor_risco};">
                        <h3 style="margin: 0; font-size: 2em; color: {cor_risco};">{metricas['nivel_risco']}</h3>
                        <p style="margin: 10px 0 0 0; font-weight: 600; font-size: 1.1em;">NÍVEL DE RISCO</p>
                        <p style="margin: 5px 0 0 0; color: #cccccc; font-size: 0.9em;">Classificação do contrato</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Divisor
                st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)
                
                # Lista de problemas detectados - DESIGN SIMPLIFICADO
                st.markdown(f"""
                <div style="text-align: center; margin: 40px 0;">
                    <h2 style="color: #d4af37; font-size: 2.2em;">🔍 PROBLEMAS IDENTIFICADOS</h2>
                    <p style="color: #cccccc; font-size: 1.1em;">
                        {len(problemas)} problema(s) encontrado(s) no seu contrato
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                if problemas:
                    for i, problema in enumerate(problemas, 1):
                        # Determinar classe CSS baseado na gravidade
                        classe_css = {
                            'critical': 'critical-problem',
                            'medium': 'medium-problem',
                            'low': 'low-problem'
                        }.get(problema['gravidade'], 'low-problem')
                        
                        # Determinar badge de gravidade
                        badge_gravidade = {
                            'critical': 'critical-badge',
                            'medium': 'medium-badge',
                            'low': 'low-badge'
                        }.get(problema['gravidade'], 'low-badge')
                        
                        texto_gravidade = {
                            'critical': '🚨 CRÍTICO',
                            'medium': '⚠️ ATENÇÃO',
                            'low': 'ℹ️ INFORMATIVO'
                        }.get(problema['gravidade'], 'ℹ️ INFORMATIVO')
                        
                        # Exibir problema de forma SIMPLES e DIRETA
                        st.markdown(f"""
                        <div class="problem-card {classe_css} fade-in">
                            <div style="display: flex; align-items: flex-start; margin-bottom: 20px;">
                                <div class="gold-icon">{problema['icone']}</div>
                                <div style="flex: 1;">
                                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
                                        <h3 style="margin: 0; color: #ffffff; font-size: 1.4em;">{problema['nome']}</h3>
                                        <span class="severity-badge {badge_gravidade}">{texto_gravidade}</span>
                                    </div>
                                    
                                    <div style="background: rgba(40, 40, 40, 0.7); padding: 15px; border-radius: 10px; margin: 15px 0;">
                                        <h4 style="margin: 0 0 10px 0; color: #d4af37; font-size: 1.1em;">❌ O QUE ESTÁ ERRADO:</h4>
                                        <p style="margin: 0; color: #ffffff; line-height: 1.6;">
                                            {problema['descricao_detalhada']}
                                        </p>
                                    </div>
                                    
                                    <div style="background: rgba(212, 175, 55, 0.1); padding: 15px; border-radius: 10px; margin: 15px 0; border-left: 3px solid #d4af37;">
                                        <h4 style="margin: 0 0 10px 0; color: #d4af37; font-size: 1.1em;">💡 EM LINGUAGEM SIMPLES:</h4>
                                        <p style="margin: 0; color: #ffffff; line-height: 1.6; font-style: italic;">
                                            "{problema['explicacao_simples']}"
                                        </p>
                                    </div>
                                    
                                    <div style="display: flex; justify-content: space-between; margin-top: 20px;">
                                        <div>
                                            <span style="color: #d4af37; font-weight: bold;">📚 Base Legal:</span>
                                            <span style="color: #ffffff; margin-left: 10px;">{problema['lei']}</span>
                                        </div>
                                        <div>
                                            <span style="color: #d4af37; font-weight: bold;">🎯 Confiança:</span>
                                            <span style="color: {problema['cor_confianca']}; margin-left: 10px; font-weight: bold;">
                                                {problema['nivel_confianca']} ({problema['confianca']:.0%})
                                            </span>
                                        </div>
                                    </div>
                                    
                                    <div style="background: rgba(0, 100, 0, 0.2); padding: 15px; border-radius: 10px; margin-top: 20px; border: 1px solid #00aa00;">
                                        <h4 style="margin: 0 0 10px 0; color: #00ff00; font-size: 1.1em;">✅ O QUE FAZER AGORA:</h4>
                                        <p style="margin: 0; color: #ffffff; line-height: 1.6; font-weight: bold;">
                                            {problema['recomendacao']}
                                        </p>
                                    </div>
                                    
                                    <div style="margin-top: 20px; padding-top: 15px; border-top: 1px dashed rgba(212, 175, 55, 0.3);">
                                        <p style="margin: 0; color: #999999; font-size: 0.9em;">
                                            <strong>Trecho encontrado no contrato:</strong><br>
                                            <span style="color: #cccccc; font-family: monospace; font-size: 0.9em;">
                                                {problema['contexto'][:300]}...
                                            </span>
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    # Mensagem quando nenhum problema é encontrado
                    st.markdown("""
                    <div style="text-align: center; padding: 60px; background: rgba(0, 100, 0, 0.2); border-radius: 20px; margin: 40px 0; border: 2px solid #00ff00;">
                        <div style="font-size: 5em; color: #00ff00;">✅</div>
                        <h3 style="color: #00ff00; margin: 20px 0; font-size: 2em;">CONTRATO REGULAR!</h3>
                        <p style="color: #cccccc; font-size: 1.2em; max-width: 600px; margin: 0 auto;">
                            Parabéns! Seu contrato está em conformidade com a legislação brasileira.
                        </p>
                        <p style="color: #999999; margin-top: 20px;">
                            Se ainda tiver dúvidas, consulte um advogado especializado.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Botão para exportar relatório
                if problemas:
                    st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)
                    
                    st.markdown("""
                    <div style="text-align: center; margin: 40px 0;">
                        <h3 style="color: #d4af37; font-size: 1.8em;">📥 RELATÓRIO COMPLETO</h3>
                        <p style="color: #cccccc; margin-bottom: 30px;">
                            Baixe o relatório detalhado para discutir com seu advogado
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Criar DataFrame para exportação
                    dados_exportar = []
                    for p in problemas:
                        dados_exportar.append({
                            'Problema': p['nome'],
                            'Gravidade': p['gravidade'].upper(),
                            'Descrição': p['descricao_detalhada'],
                            'Recomendação': p['recomendacao'],
                            'Base Legal': p['lei'],
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
                            label="⬇️ BAIXAR RELATÓRIO EM CSV",
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
            <h3 style="color: #ffffff; margin: 20px 0; font-size: 1.8em;">ENVIE SEU CONTRATO DE ALUGUEL</h3>
            <p style="color: #cccccc; font-size: 1.1em; max-width: 600px; margin: 0 auto 30px auto;">
                Nosso sistema analisa automaticamente cláusulas abusivas e ilegais
                em contratos de locação residencial
            </p>
            <div style="background: rgba(212, 175, 55, 0.1); padding: 20px; border-radius: 10px; display: inline-block;">
                <p style="margin: 0; color: #d4af37; font-weight: bold;">
                    🔒 100% SEGURO • Processamento local • Sem armazenamento
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Divisor
        st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)
        
        # O que o sistema detecta
        st.markdown("""
        <div style="text-align: center; margin: 50px 0;">
            <h2 style="color: #d4af37; font-size: 2em;">🎯 O QUE ANALISAMOS?</h2>
            <p style="color: #cccccc; font-size: 1.1em; max-width: 800px; margin: 20px auto;">
                Nosso sistema inteligente identifica automaticamente as cláusulas mais problemáticas
                em contratos de aluguel
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Exemplos de problemas em colunas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="padding: 25px; background: rgba(26, 26, 26, 0.9); border-radius: 15px; text-align: center; height: 100%; border: 1px solid rgba(212, 175, 55, 0.3);">
                <div style="font-size: 2.5em; margin-bottom: 15px;">🚨</div>
                <h4 style="color: #ff4444; margin: 10px 0;">PROBLEMAS CRÍTICOS</h4>
                <ul style="text-align: left; color: #cccccc; padding-left: 20px;">
                    <li>Reajuste ilegal de aluguel</li>
                    <li>Garantia dupla (fiador + caução)</li>
                    <li>Multa abusiva de 12 meses</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="padding: 25px; background: rgba(26, 26, 26, 0.9); border-radius: 15px; text-align: center; height: 100%; border: 1px solid rgba(212, 175, 55, 0.3);">
                <div style="font-size: 2.5em; margin-bottom: 15px;">⚠️</div>
                <h4 style="color: #ffaa44; margin: 10px 0;">ATENÇÃO NECESSÁRIA</h4>
                <ul style="text-align: left; color: #cccccc; padding-left: 20px;">
                    <li>Violacão de privacidade</li>
                    <li>Venda que "despeja" inquilino</li>
                    <li>Visitas sem aviso prévio</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="padding: 25px; background: rgba(26, 26, 26, 0.9); border-radius: 15px; text-align: center; height: 100%; border: 1px solid rgba(212, 175, 55, 0.3);">
                <div style="font-size: 2.5em; margin-bottom: 15px;">ℹ️</div>
                <h4 style="color: #44aaff; margin: 10px 0;">PONTOS IMPORTANTES</h4>
                <ul style="text-align: left; color: #cccccc; padding-left: 20px;">
                    <li>Proibição total de animais</li>
                    <li>Benfeitorias não ressarcidas</li>
                    <li>Cláusulas ambíguas</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # Rodapé informativo
        st.markdown("""
        <div style="text-align: center; margin: 60px 0 30px 0; padding: 30px; background: rgba(26, 26, 26, 0.7); border-radius: 15px; border-top: 2px solid #d4af37;">
            <h4 style="color: #d4af37; margin-bottom: 15px;">⚖️ BASE LEGAL DO SISTEMA</h4>
            <p style="color: #cccccc; max-width: 800px; margin: 0 auto;">
                Utilizamos a <strong style="color: #ffffff;">Lei 8.245/91 (Lei do Inquilinato)</strong>, 
                <strong style="color: #ffffff;">Lei 10.192/01</strong> e o 
                <strong style="color: #ffffff;">Código de Defesa do Consumidor</strong> para identificar 
                cláusulas abusivas e ilegais em contratos de locação.
            </p>
            <p style="color: #999999; margin-top: 20px; font-size: 0.9em;">
                ⚠️ Este sistema oferece orientação jurídica inicial. Para questões específicas, consulte um advogado.
            </p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
