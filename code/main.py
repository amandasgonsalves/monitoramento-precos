import time
import re
import os
import random
import difflib
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class GoogleShoppingScraper:
    """Classe para raspar dados do Google Shopping com Selenium."""
    
    # Inicializa o scraper com configurações anti-detecção para o navegador Chrome
    def __init__(self):
        """Inicializa o scraper com configurações anti-detecção para o navegador Chrome"""
        # Setup Chrome options com configurações para evitar detecção de automação
        self.options = Options()
        
        # Configurações para evitar detecção como bot
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_argument("--disable-infobars")
        self.options.add_argument("--window-size=1920,1080")  # Tamanho de janela comum
        self.options.add_argument("--start-maximized")
        
        # User agent de um navegador comum
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        self.options.add_argument(f"user-agent={user_agent}")
        
        # Evitar sinais de automação
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option("useAutomationExtension", False)
        
        # Inicializar o driver com as opções configuradas
        self.driver = webdriver.Chrome(options=self.options)
        
        # Modificar o navigator.webdriver para evitar detecção
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    # Simula digitação humana com pausas aleatórias entre caracteres
    def human_like_typing(self, element, text):
        """Simula digitação humana com pausas aleatórias entre caracteres"""
        for char in text:
            element.send_keys(char)
            # Pausa aleatória entre 0.05 e 0.2 segundos
            time.sleep(random.uniform(0.05, 0.2))
    
    # Pausa a execução por um tempo aleatório para simular comportamento humano
    def random_sleep(self, min_seconds=2, max_seconds=5):
        """Pausa a execução por um tempo aleatório para simular comportamento humano"""
        time.sleep(random.uniform(min_seconds, max_seconds))
    
    # Pesquisa um produto no Google Shopping e retorna os resultados da pesquisa
    def search_product(self, product_name):
        """Pesquisa um produto no Google Shopping e retorna os resultados da pesquisa"""
        try:
            # Abrir o Google diretamente, não o Google Shopping (menos suspeito)
            print("Navegando até o Google...")
            self.driver.get("https://www.google.com.br")
            
            self.random_sleep(2, 4)
            
            # Verificar se há um botão de aceitar cookies e clicar nele
            try:
                accept_buttons = self.driver.find_elements(By.XPATH, 
                    "//button[contains(text(), 'Aceito') or contains(text(), 'Aceitar') or contains(text(), 'Concordo')]")
                if accept_buttons:
                    accept_buttons[0].click()
                    self.random_sleep(1, 2)
            except:
                print("Não foi necessário aceitar cookies.")
            
            # Mexer o mouse aleatoriamente para simular comportamento humano
            self.random_sleep(1, 3)
            
            # Encontrar o campo de busca do Google
            print("Procurando campo de busca...")
            search_box = None
            
            # Tentar múltiplos seletores para o campo de busca
            selectors = ["input[name='q']", ".gLFyf", "#APjFqb", "input[title='Pesquisar']", "textarea[name='q']"]
            for selector in selectors:
                try:
                    search_box = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    print(f"Campo de busca encontrado com seletor: {selector}")
                    break
                except:
                    continue
            
            if not search_box:
                raise Exception("Não foi possível encontrar o campo de busca")
            
            # Clicar no campo de busca como um humano faria
            search_box.click()
            self.random_sleep(0.5, 1.5)
            
            # Limpar qualquer texto existente
            search_box.clear()
            self.random_sleep(0.5, 1)
            
            # Usar apenas o nome do produto como termo de busca
            search_term = product_name
            print(f"Digitando o termo de busca: {search_term}")
            
            # Digitar como humano, com pausas entre caracteres
            self.human_like_typing(search_box, search_term)
            
            self.random_sleep(0.8, 2)
            
            # Pressionar Enter para pesquisar
            search_box.send_keys(Keys.RETURN)
            
            # Esperar que os resultados carreguem
            print("Aguardando carregamento dos resultados...")
            self.random_sleep(3, 5)
            
            # Salvar screenshot para debug
            self.driver.save_screenshot("google_results.png")
            print("Screenshot salvo como google_results.png")
            
            # Clicar na aba Shopping usando o seletor específico
            print("Tentando clicar na aba Shopping com o seletor específico...")
            try:
                # Primeiro tentar o seletor específico fornecido
                shopping_tab = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "#hdtb-sc > div > div > div.crJ18e > div > div:nth-child(3) > a > div"))
                )
                print("Aba Shopping encontrada com o seletor específico!")
                shopping_tab.click()
            except Exception as e:
                print(f"Não foi possível encontrar a aba Shopping com o seletor específico: {e}")
                print("Tentando seletores alternativos...")
                
                # Lista de seletores alternativos para a aba Shopping
                alternative_selectors = [
                    "a[href*='tbm=shop']",
                    ".hdtb-mitem a[data-sc='shop']",
                    "div[jsname='BgbAdf'] a[data-sc='shop']",
                    "//a[contains(text(), 'Shopping')]",
                    "//div[contains(@class, 'hdtb-mitem')]//a[contains(text(), 'Shopping')]"
                ]
                
                found = False
                for selector in alternative_selectors:
                    try:
                        if selector.startswith("//"):
                            # Usando XPath
                            element = WebDriverWait(self.driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, selector))
                            )
                        else:
                            # Usando CSS Selector
                            element = WebDriverWait(self.driver, 5).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                            )
                        print(f"Aba Shopping encontrada com seletor alternativo: {selector}")
                        element.click()
                        found = True
                        break
                    except:
                        continue
                
                if not found:
                    print("Não foi possível encontrar a aba Shopping. Tentando continuar com os resultados atuais.")
            
            # Esperar que a página do Shopping carregue
            self.random_sleep(3, 5)
            
            # Salvar screenshot dos resultados
            self.driver.save_screenshot("shopping_results.png")
            print("Screenshot dos resultados do Shopping salvo como shopping_results.png")
            
            # Se ainda precisar verificar CAPTCHA, pausar para interação manual
            if "captcha" in self.driver.page_source.lower() or "não sou um robô" in self.driver.page_source.lower():
                print("\n======== ATENÇÃO! ========")
                print("CAPTCHA detectado! Por favor, complete manualmente o CAPTCHA na janela do navegador.")
                print("Após completar o CAPTCHA, pressione ENTER neste console para continuar.")
                self.driver.save_screenshot("captcha_detected.png")
                input("Pressione ENTER após completar o CAPTCHA: ")
                self.random_sleep(2, 3)
            
            # Extrair informações dos produtos
            return self.extract_product_info()
            
        except Exception as e:
            print(f"Erro durante a busca: {e}")
            self.driver.save_screenshot("error_screenshot.png")
            print("Screenshot do erro salvo como error_screenshot.png")
            return []
    
    # Extrai informações de produtos a partir dos resultados de pesquisa do Google Shopping
    def extract_product_info(self):
        """Extrai informações de produtos a partir dos resultados de pesquisa do Google Shopping"""
        try:
            print("Extraindo informações dos produtos...")
            
            # Esperar que a página carregue completamente
            print("Aguardando carregamento completo da página de resultados...")
            self.random_sleep(4, 6)
            
            # Salvar screenshot atual para verificar o estado da página
            self.driver.save_screenshot("before_extraction.png")
            print("Screenshot atual salvo como before_extraction.png")
            
            # Salvar HTML para análise detalhada
            with open("shopping_page.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            print("HTML da página salvo como shopping_page.html para análise")
            
            # Começar com o seletor específico mencionado
            print("Tentando o seletor específico #bGmlqc > div > div > div > div")
            results = []
            
            try:
                # Esperar explicitamente que os elementos apareçam
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#bGmlqc > div > div > div > div"))
                )
                
                elements = self.driver.find_elements(By.CSS_SELECTOR, "#bGmlqc > div > div > div > div")
                if elements:
                    print(f"Encontrados {len(elements)} elementos com o seletor específico")
                    for element in elements:
                        try:
                            text_content = element.text.strip()
                            if text_content:
                                results.append(text_content)
                                print(f"Conteúdo encontrado: {text_content[:50]}...")
                        except Exception as e:
                            print(f"Erro ao extrair texto: {e}")
                            continue
            except Exception as e:
                print(f"Erro ao usar o seletor específico: {e}")
            
            # Tentar o seletor vplap mais específico se solicitado
            if not results:
                try:
                    print("Tentando o seletor #vplap...")
                    vplap_elements = self.driver.find_elements(By.CSS_SELECTOR, "[id^='vplap_']")
                    for element in vplap_elements:
                        text_content = element.text.strip()
                        if text_content:
                            results.append(text_content)
                            print(f"Conteúdo encontrado em vplap: {text_content[:50]}...")
                except Exception as e:
                    print(f"Erro ao usar o seletor vplap: {e}")
            
            # Seletores mais específicos para Google Shopping
            if not results:
                print("Tentando seletores específicos para Google Shopping...")
                shopping_selectors = [
                    ".sh-dlr__list-result",
                    ".sh-dgr__grid-result",
                    ".sh-pr__product-result",
                    ".F4eCab",
                    ".dXQqNb",
                    ".jBQqof",
                    ".gm8XGd",
                    "div[data-pl]",
                    ".ZGFjDb",
                    ".i0X6df"
                ]
                
                for selector in shopping_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            print(f"Encontrados {len(elements)} elementos com o seletor: {selector}")
                            for element in elements:
                                text_content = element.text.strip()
                                if text_content:
                                    results.append(text_content)
                                    print(f"Conteúdo encontrado: {text_content[:50]}...")
                    except Exception as e:
                        print(f"Erro ao usar seletor {selector}: {e}")
                        continue
            
            # Tentar capturar elementos de produto usando XPath mais genérico
            if not results:
                print("Tentando XPath para encontrar elementos de produto...")
                try:
                    # XPath para elementos que parecem ser itens de produto
                    product_elements = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'sh-') and .//a[contains(@href, '/shopping/product')]]")
                    for element in product_elements:
                        text_content = element.text.strip()
                        if text_content:
                            results.append(text_content)
                            print(f"Conteúdo encontrado via XPath: {text_content[:50]}...")
                except Exception as e:
                    print(f"Erro ao usar XPath: {e}")
            
            # Tentar método de scrolling para garantir que todos os elementos estejam carregados
            if not results or len(results) < 3:  # Se encontramos poucos resultados
                print("Tentando scroll para carregar mais conteúdo...")
                try:
                    # Rolar a página para baixo para carregar elementos dinâmicos
                    for _ in range(3):
                        self.driver.execute_script("window.scrollBy(0, 500)")
                        self.random_sleep(1, 2)
                    
                    # Tentar novamente após rolagem
                    elements = self.driver.find_elements(By.CSS_SELECTOR, "#bGmlqc > div > div > div > div")
                    if elements:
                        for element in elements:
                            text_content = element.text.strip()
                            if text_content and text_content not in results:
                                results.append(text_content)
                                print(f"Após scroll, conteúdo encontrado: {text_content[:50]}...")
                except Exception as e:
                    print(f"Erro durante scrolling: {e}")
            
            # Estratégia final: Coletar todos os textos visíveis
            if not results:
                print("Última tentativa: coletando todos os textos visíveis na página")
                try:
                    # Obter todos os elementos com texto
                    all_elements = self.driver.find_elements(By.XPATH, "//*[not(self::script or self::style)][string-length(normalize-space(text())) > 10]")
                    for element in all_elements:
                        if element.is_displayed():
                            text = element.text.strip()
                            if text and len(text) > 15:  # Textos significativos
                                results.append(text)
                                print(f"Texto visível encontrado: {text[:50]}...")
                except Exception as e:
                    print(f"Erro na coleta final de textos: {e}")
            
            # Se ainda não temos resultados, tentar acessar diretamente o primeiro produto
            if not results:
                print("Tentando clicar no primeiro produto para obter detalhes...")
                try:
                    # Tentar clicar no primeiro produto
                    product_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/shopping/product']")
                    if product_links:
                        product_links[0].click()
                        self.random_sleep(3, 5)
                        
                        # Salvar screenshot da página de detalhes
                        self.driver.save_screenshot("product_details.png")
                        
                        # Extrair informações da página de detalhes
                        details = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'product-')]")
                        for detail in details:
                            text = detail.text.strip()
                            if text:
                                results.append(text)
                                print(f"Detalhe de produto: {text[:50]}...")
                except Exception as e:
                    print(f"Erro ao acessar detalhes do produto: {e}")
            
            # Remover duplicatas e textos muito curtos
            cleaned_results = []
            seen = set()
            for result in results:
                if result not in seen and len(result) > 15:
                    cleaned_results.append(result)
                    seen.add(result)
            
            return cleaned_results
            
        except Exception as e:
            print(f"Erro ao extrair informações dos produtos: {e}")
            self.driver.save_screenshot("extraction_error.png")
            print("Screenshot do erro salvo como extraction_error.png")
            return []
    
    # Calcula a similaridade entre o termo de busca e o título do produto
    def calculate_similarity(self, search_term, product_title):
        """Calcula a similaridade entre o termo de busca e o título do produto usando múltiplos métodos"""
        # Normalizar os textos para comparação
        s_term = search_term.lower()
        p_title = product_title.lower()
        
        # Método 1: Usando difflib sequence matcher
        similarity_ratio = difflib.SequenceMatcher(None, s_term, p_title).ratio()
        
        # Método 2: Verificar se todas as palavras-chave importantes estão presentes
        # Para produtos como pneus, verificar se as especificações exatas estão presentes
        palavras_chave = []
        
        # Identificar números/códigos específicos, como dimensões de produtos
        codigos = re.findall(r'\d+/\d+[rR]\d+', s_term)  # Formato tipo 175/65R14
        if codigos:
            palavras_chave.extend(codigos)
        
        # Identificar códigos alfanuméricos - algo como "SP Touring R1"
        alfanumericos = re.findall(r'[A-Za-z]+\s+[A-Za-z]+\s+[A-Za-z0-9]+', s_term)
        if alfanumericos:
            palavras_chave.extend(alfanumericos)
        
        # Identificar especificações numéricas
        especificacoes = re.findall(r'\b\d+[a-zA-Z]+\b', s_term)  # Como "82T"
        if especificacoes:
            palavras_chave.extend(especificacoes)
        
        # Se não encontramos palavras-chave específicas, usar as palavras principais
        if not palavras_chave:
            # Remover palavras muito comuns/pouco significativas
            stop_words = ['de', 'em', 'e', 'com', 'para', 'o', 'a', 'os', 'as', 'um', 'uma']
            palavras_significativas = [p for p in s_term.split() if p.lower() not in stop_words and len(p) > 2]
            palavras_chave = palavras_significativas
        
        # Verificar presença das palavras-chave
        palavras_encontradas = sum(1 for palavra in palavras_chave if palavra.lower() in p_title)
        taxa_palavras = palavras_encontradas / len(palavras_chave) if palavras_chave else 0
        
        # Método 3: Para produtos com especificações exatas como pneus, verificar se os números principais correspondem
        numeros_search = re.findall(r'\d+', s_term)
        numeros_title = re.findall(r'\d+', p_title)
        
        # Verificar correspondência de números
        correspondencia_numeros = 0
        if numeros_search and numeros_title:
            correspondencia_numeros = sum(1 for num in numeros_search if num in numeros_title) / len(numeros_search)
        
        # Combinar os métodos com pesos
        similaridade_final = (similarity_ratio * 0.4) + (taxa_palavras * 0.4) + (correspondencia_numeros * 0.2)
        
        # Bonus: Se contém exatamente as especificações principais do produto
        for codigo in codigos:
            if codigo.lower() in p_title:
                similaridade_final += 0.2
                break
        
        # Normalizar para não ultrapassar 1
        return min(similaridade_final, 1.0)
    
    # Verifica se um produto corresponde ao item buscado usando a API do OpenAI ou método alternativo
    def verify_product_with_openai(self, search_term, product_title, api_key=None):
        """Verifica se um produto corresponde ao item buscado usando a API do OpenAI ou método alternativo"""
        # Se não tiver uma API key, usar uma verificação baseada em especificações
        if not api_key or api_key == "sua-chave-api-aqui":
            print("API Key não fornecida ou inválida. Usando verificação avançada de especificações.")
            return self.advanced_specification_match(search_term, product_title)
        
        # Preparar mensagem para a API do OpenAI
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            # Mensagem para a API
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "Você é um assistente especializado em identificar se dois produtos são exatamente o mesmo modelo."},
                    {"role": "user", "content": f"""
Analise se estes dois produtos são EXATAMENTE o mesmo modelo, especificação e variante:

Produto buscado: {search_term}
Produto encontrado: {product_title}

Seja EXTREMAMENTE RIGOROSO na comparação. Um produto só deve ser considerado o mesmo se todas as especificações técnicas relevantes forem idênticas:
- Mesma marca/fabricante
- Mesmo modelo exato (incluindo códigos de modelo)
- Mesma capacidade/tamanho/BTUs/polegadas/dimensões
- Mesmas funcionalidades (ex: se o produto buscado é quente/frio, o encontrado também deve ser)

ATENÇÃO: Diferenças em modelo, capacidade ou especificações técnicas principais significam produtos diferentes!
Exemplos claros de produtos diferentes:
- Um ar-condicionado de 9000 BTUs vs. 12000 BTUs
- Um pneu 175/65R14 vs. 185/65R14
- Um modelo NEO vs. LIV da mesma marca

Responda apenas com um JSON contendo:
1. is_same_product: false (se qualquer especificação técnica relevante for diferente) ou true (se forem o mesmo produto)
2. confidence: valor entre 0 e 1 indicando sua confiança
3. explanation: explicação breve da sua decisão, destacando diferenças encontradas
"""}
                ],
                "temperature": 0.1
            }
            
            # Fazer a chamada à API
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                data=json.dumps(data)
            )
            
            # Verificar se há erro na resposta
            if response.status_code != 200:
                print(f"Erro na chamada à API: {response.status_code}")
                print(response.text)
                return self.advanced_specification_match(search_term, product_title)
            
            # Extrair a resposta
            try:
                response_data = response.json()
                content = response_data["choices"][0]["message"]["content"]
                
                # Extrair o JSON da resposta
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    json_content = json_match.group(0)
                    result = json.loads(json_content)
                    return result
                else:
                    # Tentar encontrar valores diretos no texto
                    is_same = "true" in content.lower() and "false" not in content.lower()
                    confidence = 0.5  # Valor padrão se não for encontrado
                    explanation = content
                    
                    return {
                        "is_same_product": is_same,
                        "confidence": confidence,
                        "explanation": explanation
                    }
                
            except Exception as e:
                print(f"Erro ao processar resposta da API: {e}")
                return self.advanced_specification_match(search_term, product_title)
                
        except Exception as e:
            print(f"Erro ao chamar a API: {e}")
            return self.advanced_specification_match(search_term, product_title)
    
    # Compara especificações técnicas entre produtos para determinar se são o mesmo item
    def advanced_specification_match(self, search_term, product_title):
        """Compara especificações técnicas entre produtos para determinar se são o mesmo item"""
        # Normalizar textos para comparação
        search_term_lower = search_term.lower()
        product_title_lower = product_title.lower()
        
        # Inicializar variáveis
        is_match = True
        confidence = 1.0
        reasons = []
        
        # Para pneus: Verificar se a dimensão principal é a mesma
        if "pneu" in search_term_lower or "pneu" in product_title_lower:
            # Extrair dimensões como 185/65r14
            # Normalizar "R" para "r" para facilitar a comparação
            search_term_norm = search_term_lower.replace('R', 'r')
            product_title_norm = product_title_lower.replace('R', 'r')
            
            # Padrão de dimensão para pneus (ex: 185/65r14)
            dim_pattern = r'(\d+/\d+r\d+)'
            search_dims = re.findall(dim_pattern, search_term_norm)
            product_dims = re.findall(dim_pattern, product_title_norm)
            
            # Se ambos têm dimensões, comparar
            if search_dims and product_dims:
                if search_dims[0] != product_dims[0]:
                    is_match = False
                    reasons.append(f"Dimensões diferentes: {search_dims[0]} vs {product_dims[0]}")
                    confidence -= 0.5
                else:
                    # Se a dimensão principal é igual, é provavelmente o mesmo pneu
                    # Verificar código da série também (ex: SP Touring R1)
                    if "sp touring r1" in search_term_lower and "sp touring r1" in product_title_lower:
                        # Verificar código de carga/velocidade (ex: 86T)
                        load_speed_pattern = r'\b(\d{2}[a-zA-Z])\b'
                        search_codes = re.findall(load_speed_pattern, search_term_lower)
                        product_codes = re.findall(load_speed_pattern, product_title_lower)
                        
                        if search_codes and product_codes:
                            if search_codes[0].lower() != product_codes[0].lower():
                                # Diferença no código de carga/velocidade não é tão crítica
                                confidence -= 0.2
                                reasons.append(f"Códigos diferentes: {search_codes[0]} vs {product_codes[0]}")
                    
                    # Se é um pneu Dunlop com mesma dimensão e mesma série, é o mesmo produto
                    if "dunlop" in search_term_lower and "dunlop" in product_title_lower:
                        if confidence > 0.7:
                            is_match = True
            # Se um tem dimensão e o outro não, não é o mesmo produto
            elif search_dims and not product_dims:
                is_match = False
                reasons.append(f"Produto encontrado não especifica a dimensão {search_dims[0]}")
                confidence -= 0.5
        else:
            # Para outros tipos de produtos (não pneus)
            # Extrair especificações numéricas (como dimensões, capacidades, etc.)
            
            # 1. BTUs em ar condicionados
            btu_pattern = r'(\d+)\s*(?:btus?|btu)'
            search_btus = re.findall(btu_pattern, search_term_lower)
            product_btus = re.findall(btu_pattern, product_title_lower)
            
            if search_btus and product_btus:
                if search_btus[0] != product_btus[0]:
                    is_match = False
                    reasons.append(f"BTUs diferentes: {search_btus[0]} vs {product_btus[0]}")
                    confidence -= 0.5
            
            # 3. Códigos de modelo específicos (ex: ICS9QF)
            # Buscar padrões que parecem ser códigos de modelo (letra seguida de números e letras)
            model_pattern = r'\b([a-zA-Z]{2,}[0-9]+[a-zA-Z0-9]*)\b'
            search_models = re.findall(model_pattern, search_term_lower)
            product_models = re.findall(model_pattern, product_title_lower)
            
            # Se encontramos códigos de modelo no termo de busca, verificar se estão no produto
            if search_models:
                model_found = False
                for model in search_models:
                    if any(model.lower() == m.lower() for m in product_models):
                        model_found = True
                        break
                
                if not model_found:
                    is_match = False
                    reasons.append(f"Código de modelo não encontrado: {', '.join(search_models)}")
                    confidence -= 0.4
            
            # 4. Características específicas (Inverter, Split, etc.)
            key_features = ["inverter", "split", "quente/frio", "q/f", "qf", "neo"]
            for feature in key_features:
                if feature in search_term_lower and feature not in product_title_lower:
                    # Se for "q/f" ou "qf", verificar também "quente/frio" e vice-versa
                    if feature in ["q/f", "qf"] and "quente" in product_title_lower and "frio" in product_title_lower:
                        continue
                    if feature == "quente/frio" and ("q/f" in product_title_lower or "qf" in product_title_lower):
                        continue
                    
                    is_match = False
                    reasons.append(f"Característica ausente: {feature}")
                    confidence -= 0.3
            
            # 5. Verificar diferenças nos principais números do produto
            numbers_search = set(re.findall(r'\d+', search_term_lower))
            numbers_product = set(re.findall(r'\d+', product_title_lower))
            
            # Ignorar números comuns de voltagem
            voltages = {"110", "127", "220", "240", "380"}
            critical_numbers_search = numbers_search - voltages
            critical_numbers_product = numbers_product - voltages
            
            # Se o produto buscado tem números críticos que não aparecem no produto encontrado
            missing_numbers = critical_numbers_search - critical_numbers_product
            if missing_numbers and critical_numbers_search:
                major_numbers_missing = False
                for num in missing_numbers:
                    # Verificar se é um número significativo (não apenas um código)
                    if len(num) >= 2 and num.isdigit() and int(num) > 10:
                        major_numbers_missing = True
                        break
                
                if major_numbers_missing:
                    is_match = False
                    reasons.append(f"Números críticos ausentes: {', '.join(missing_numbers)}")
                    confidence -= 0.3
            
            # 6. Verificar se há modelos diferentes explicitamente mencionados
            # Ex: "NEO" vs "LIV", "TOURING" vs "SPORT"
            model_terms = []
            for term in search_term_lower.split():
                if term.isalpha() and len(term) >= 3 and term not in ["para", "com", "the", "por", "dos", "das"]:
                    model_terms.append(term)
            
            for term in model_terms:
                # Ignorar termos muito comuns
                common_terms = ["tipo", "para", "com", "novo", "frio", "marca"]
                if term in common_terms:
                    continue
                    
                if term not in product_title_lower:
                    is_match = False
                    reasons.append(f"Termo de modelo ausente: {term}")
                    confidence -= 0.2
        
        # Ajustar confiança para não ficar negativa
        confidence = max(0.0, confidence)
        
        # Se a confiança for muito baixa, considerar como não sendo o mesmo produto
        if confidence < 0.4:  # Reduzido de 0.5 para 0.4 para ser menos rigoroso
            is_match = False
        
        # Para pneus, se é da mesma dimensão e marca, considerar match mesmo com confiança mais baixa
        if "pneu" in search_term_lower and "pneu" in product_title_lower:
            # Verificar se é o mesmo fabricante
            fabricantes = ["dunlop", "pirelli", "michelin", "goodyear", "continental", "bridgestone", "firestone"]
            for fab in fabricantes:
                if fab in search_term_lower and fab in product_title_lower:
                    # Se tem a mesma dimensão e é do mesmo fabricante, aumentar a confiança
                    confidence = max(confidence, 0.6)
                    if confidence >= 0.6:
                        is_match = True
                    break
        
        explanation = "Este é exatamente o mesmo produto." if is_match else "Produto diferente: " + "; ".join(reasons)
        
        return {
            "is_same_product": is_match,
            "confidence": confidence,
            "explanation": explanation
        }
    
    # Salva os resultados em formatos JSON e TXT, processando e filtrando os produtos encontrados
    def save_to_file(self, product_name, results):
        """Salva os resultados em formatos JSON e TXT, processando e filtrando os produtos encontrados"""
        if not os.path.exists("results"):
            os.makedirs("results")
            
        # Limpa o nome do produto para usar como nome de arquivo
        clean_name = re.sub(r'[\\/*?:"<>|]', "", product_name)
        clean_name = clean_name.replace(" ", "_")
        
        # Caminhos para os arquivos de saída
        txt_filename = f"results/{clean_name}_results.txt"
        json_filename = f"results/{clean_name}_results.json"
        
        # Processar os resultados para extrair produtos com preços
        produtos_processados = []
        
        print("Processando resultados para extrair informações de preço...")
        
        # Primeiro, vamos processar todo o texto bruto para encontrar padrões de preço
        texto_completo = "\n".join(results)
        
        # Encontrar todos os padrões de preço no texto completo
        # Buscar padrões como "R$ 123,45" ou mesmo "R$123.45"
        todos_precos = re.findall(r'R\$\s*(\d+[,.]\d+)', texto_completo)
        print(f"Encontrados {len(todos_precos)} padrões de preço no texto completo")
        
        # Tentar obter a OpenAI API key do ambiente ou arquivo de configuração
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            try:
                # Tentar ler de um arquivo config.json na pasta atual
                if os.path.exists("config.json"):
                    with open("config.json", "r") as f:
                        config = json.load(f)
                        api_key = config.get("openai_api_key")
            except:
                pass
        
        if not api_key:
            print("Atenção: Chave API OpenAI não encontrada. Usando método alternativo de similaridade.")
        else:
            print("Usando API do OpenAI para verificação de produtos.")
        
        # Processar cada bloco de resultado separadamente
        for result in results:
            try:
                # Dividir o texto em linhas
                linhas = result.strip().split('\n')
                
                # Se o bloco tiver menos de 2 linhas, é provavelmente um fragmento e não um produto completo
                if len(linhas) < 2:
                    continue
                
                # Inicializar variáveis
                nome_produto = ""
                preco = ""
                valor_numerico = 9999999  # Valor alto para caso não encontre preço
                loja = ""
                
                # Primeira linha geralmente é o nome do produto (exceto se for "Patrocinado")
                if not linhas[0].startswith("Patrocinado"):
                    nome_produto = linhas[0]
                elif len(linhas) > 1:
                    nome_produto = linhas[1]
                
                # Verificar com a API do OpenAI se o produto é o mesmo que estamos buscando
                verification_result = self.verify_product_with_openai(product_name, nome_produto, api_key)
                
                # Verificar se o produto é o mesmo com base na resposta da API
                if not verification_result["is_same_product"]:
                    print(f"Produto rejeitado pela verificação: {nome_produto}")
                    print(f"Razão: {verification_result['explanation']}")
                    continue
                
                # Se chegou aqui, o produto foi aprovado pela verificação
                print(f"Produto aceito pela verificação (confiança: {verification_result['confidence']:.2f}): {nome_produto}")
                print(f"Explicação: {verification_result['explanation']}")
                
                # Procurar por todas as linhas com preço
                precos_encontrados = []
                indices_precos = []
                
                for i, linha in enumerate(linhas):
                    # Buscar padrão de preço na linha
                    if "R$" in linha:
                        preco_match = re.search(r'R\$\s*(\d+[,.]\d+)', linha)
                        if preco_match:
                            # Extrair o valor numérico
                            valor_texto = preco_match.group(1)
                            # Converter para float (substituindo , por .)
                            valor = float(valor_texto.replace('.', '').replace(',', '.'))
                            
                            precos_encontrados.append({
                                'texto': linha.strip(),
                                'valor': valor,
                                'indice': i
                            })
                            indices_precos.append(i)
                
                # Se não encontrou preços, pular para o próximo resultado
                if not precos_encontrados:
                    continue
                
                # Usar o menor preço encontrado
                menor_preco = min(precos_encontrados, key=lambda x: x['valor'])
                preco = menor_preco['texto']
                valor_numerico = menor_preco['valor']
                indice_preco = menor_preco['indice']
                
                # Tentar encontrar a loja (geralmente é a linha após o preço)
                if indice_preco + 1 < len(linhas) and "R$" not in linhas[indice_preco + 1]:
                    loja = linhas[indice_preco + 1]
                
                # Se ainda não temos uma loja, procurar em outras linhas
                if not loja:
                    for i, linha in enumerate(linhas):
                        if i not in indices_precos and not linha.startswith("R$") and i > 0:
                            # Excluir linhas que parecem ser informações do produto
                            if not any(palavra in linha.lower() for palavra in ["promoção", "patrocinado", "frete"]):
                                loja = linha
                                break
                
                # Se encontramos as informações mínimas necessárias
                if nome_produto and preco:
                    produto = {
                        'produto': nome_produto,
                        'valor': preco,
                        'loja': loja
                    }
                    produtos_processados.append(produto)
                    print(f"Produto processado: {nome_produto} - {preco}")
            except Exception as e:
                print(f"Erro ao processar um resultado: {e}")
                continue
        
        # Depuração: mostrar produtos processados
        print(f"Total de produtos processados: {len(produtos_processados)}")
        
        # Ordenar produtos pelo preço (estimativa numérica extraída)
        produtos_ordenados = sorted(produtos_processados, 
                                   key=lambda x: float(re.search(r'R\$\s*(\d+[,.]\d+)', x['valor']).group(1).replace('.', '').replace(',', '.')))
        
        # Pegar os 4 melhores preços (ou menos se não houver 4)
        melhores_produtos = produtos_ordenados[:min(4, len(produtos_ordenados))]
        
        # Salvar resultados em JSON no formato simples solicitado
        with open(json_filename, "w", encoding="utf-8") as json_file:
            # Se não houver produtos, criar um arquivo JSON vazio mas válido
            if not melhores_produtos:
                json_file.write("[]")  # Array vazio
            else:
                # Abrir com um colchete para criar um array JSON
                json_file.write("[\n")
                
                # Adicionar cada produto
                for i, produto in enumerate(melhores_produtos):
                    json_file.write(json.dumps(produto, ensure_ascii=False, indent=4))
                    # Adicionar vírgula após cada produto exceto o último
                    if i < len(melhores_produtos) - 1:
                        json_file.write(",\n")
                    else:
                        json_file.write("\n")
                
                # Fechar o array
                json_file.write("]")
        
        # Também manter o formato TXT para compatibilidade
        with open(txt_filename, "w", encoding="utf-8") as txt_file:
            txt_file.write(f"Resultados da busca por: {product_name}\n")
            txt_file.write("=" * 50 + "\n\n")
            txt_file.write("MELHORES OFERTAS ENCONTRADAS:\n\n")
            
            if not melhores_produtos:
                txt_file.write("Não foi possível identificar ofertas com preços.\n\n")
            else:
                for i, produto in enumerate(melhores_produtos, 1):
                    txt_file.write(f"OFERTA {i}:\n")
                    txt_file.write(f"Produto: {produto['produto']}\n")
                    txt_file.write(f"Preço: {produto['valor']}\n")
                    if produto['loja']:
                        txt_file.write(f"Loja: {produto['loja']}\n")
                    txt_file.write("\n" + "-" * 40 + "\n\n")
            
            # Incluir todos os dados brutos no final do arquivo para referência
            txt_file.write("\nDADOS BRUTOS DE TODOS OS PRODUTOS ENCONTRADOS:\n")
            txt_file.write("-" * 50 + "\n\n")
            
            for i, result in enumerate(results, 1):
                txt_file.write(f"Item {i}:\n{result}\n\n")
                txt_file.write("-" * 30 + "\n")
        
        print(f"Resultados salvos em formato JSON: {json_filename}")
        print(f"Resultados salvos em formato TXT: {txt_filename}")
        
        return json_filename
    # Fecha o navegador e libera recursos utilizados pelo scraper
    def close(self):
        """Fecha o navegador e libera recursos utilizados pelo scraper"""
        if self.driver:
            self.driver.quit()


# Função principal que obtém o produto a ser pesquisado e executa o scraper
def main():
    """Função principal que obtém o produto a ser pesquisado e executa o scraper"""
    # Get product name from user
    product_name = input("Enter the product name to search: ")
    
    if not product_name.strip():
        print("Product name cannot be empty.")
        return
    
    # Initialize the scraper
    scraper = GoogleShoppingScraper()
    
    try:
        print(f"Searching for: {product_name}")
        results = scraper.search_product(product_name)
        
        if results:
            print(f"Found {len(results)} results.")
            filename = scraper.save_to_file(product_name, results)
            print(f"Results saved to: {filename}")
        else:
            print("No results found.")
    finally:
        # Always close the browser
        scraper.close()


if __name__ == "__main__":
    main()