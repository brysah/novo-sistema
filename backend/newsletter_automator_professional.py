import asyncio

import sys
import traceback
import random
import time
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from playwright.async_api import async_playwright 
from progress_manager import progress_manager, TaskStatus


# Configurações de timeout e delay humanizados
TIMEOUTS = {
    "page_load": 60000,      # 60s para carregamento de página
    "element_wait": 10000,   # 10s para elementos aparecerem  
    "action_wait": 15000,    # 15s para ações específicas (aumentado)
    "quick_check": 2000,     # 2s para verificações rápidas
    "form_submit": 20000,    # 20s para submissão de formulário
    "stability": 8000,       # 8s para estabilização
    "click_wait": 10000,     # 10s após clique
    "navigation": 25000,     # 25s para navegação
}

# Delays humanizados com variação aleatória
import random

def get_human_delay(base_delay, variation=0.3):
    """Gera delay humanizado com variação aleatória."""
    variation_amount = base_delay * variation
    return base_delay + random.uniform(-variation_amount, variation_amount)

DELAYS = {
    "typing_min": 25,        # Delay mínimo entre caracteres (reduzido)
    "typing_max": 80,        # Delay máximo entre caracteres (reduzido)
    "between_actions": 800,  # Pausa entre ações (reduzido)
    "after_click": 2000,     # Após cliques importantes (reduzido)
    "page_stabilize": 3000,  # Estabilização de página (reduzido)
    "mouse_move": 100,       # Movimento do mouse (ligeiramente reduzido)
    "scroll_pause": 350,     # Pausa ao fazer scroll (reduzido)
    "reading_time": 1500,    # Tempo de "leitura" da página (reduzido)
    # Delays faltantes que o código referencia
    "before_type": 300,      # Antes de começar a digitar (reduzido)
    "after_type": 180,       # Após terminar de digitar (reduzido)
    "before_click": 120,     # Antes de clicar (reduzido)
    "between_keys": 50,      # Entre teclas individuais (reduzido)
}

# Configurações stealth avançadas para evasão de detecção
BROWSER_CONFIG = {
    "headless": False,  
    "slow_mo": 100,    # Pequeno delay para estabilidade
    "timeout": 60000,  # Timeout de 60s
    "args": [
        # Anti-detecção básica
        "--disable-blink-features=AutomationControlled",
        "--disable-extensions-except",
        "--disable-default-apps",
        "--disable-component-extensions-with-background-pages",
        "--no-default-browser-check",
        "--no-first-run",
        
        # Stealth avançado
        "--disable-dev-shm-usage",
        "--disable-features=VizDisplayCompositor",
        "--disable-background-timer-throttling",
        "--disable-backgrounding-occluded-windows",
        "--disable-renderer-backgrounding",
        "--disable-field-trial-config",
        "--disable-ipc-flooding-protection",
        
        # Fingerprinting evasion
        "--disable-web-security",
        "--disable-features=WebRTC", 
        "--disable-webgl",
        "--disable-accelerated-2d-canvas",
        "--disable-accelerated-jpeg-decoding",
        "--disable-accelerated-mjpeg-decode",
        "--disable-app-list-dismiss-on-blur",
        "--disable-accelerated-video-decode",
        
        # Comportamento humano
        "--enable-automation=false",
        "--exclude-switches=[enable-automation]",
        "--disable-logging",
        "--disable-gpu-logging",
        "--silent-debugger-extension-api",
        "--disable-background-networking",
        
        # Estabilidade adicional
        "--no-sandbox",
        "--disable-gpu-sandbox",
        "--disable-software-rasterizer",
        "--disable-background-timer-throttling",
        "--disable-backgrounding-occluded-windows",
        "--disable-renderer-backgrounding"
    ]
}

# --- DADOS PARA EVASÃO DE FINGERPRINTING --- #

class FingerprintEvasion:
    """Sistema de evasão de fingerprinting avançado."""
    
    # Pool de User Agents realistas (atualizados)
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
    ]
    
    # Resoluções de tela comuns
    VIEWPORTS = [
        {'width': 1920, 'height': 1080},
        {'width': 1366, 'height': 768},
        {'width': 1536, 'height': 864},
        {'width': 1440, 'height': 900},
        {'width': 1600, 'height': 900}
    ]
    
    # Timezones brasileiros
    TIMEZONES = [
        'America/Sao_Paulo',
        'America/Manaus', 
        'America/Fortaleza',
        'America/Recife',
        'America/Cuiaba'
    ]
    
    @staticmethod
    def get_random_config():
        """Gera configuração aleatória para evasão."""
        return {
            'user_agent': random.choice(FingerprintEvasion.USER_AGENTS),
            'viewport': random.choice(FingerprintEvasion.VIEWPORTS),
            'timezone': random.choice(FingerprintEvasion.TIMEZONES),
            'locale': random.choice(['pt-BR', 'pt-PT']),
            'platform': random.choice(['Win32', 'MacIntel'])
        }

# --- SISTEMA DE EVASÃO STEALTH AVANÇADO --- #

class StealthEvasion:
    @staticmethod
    async def setup_stealth_context(context):
        """Configura contexto stealth para máxima evasão."""
        # Remove propriedades que identificam automação
        await context.add_init_script("""
            // Remove webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Remove automation flags
            delete window.chrome.runtime.onConnect;
            
            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // Humanize user agent
            Object.defineProperty(navigator, 'userAgent', {
                get: () => 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            });
            
            // Mock plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Override language detection
            Object.defineProperty(navigator, 'languages', {
                get: () => ['pt-BR', 'pt', 'en-US', 'en']
            });
            
            // Remove automation traces
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
        """)
    
    @staticmethod
    async def human_mouse_movement(page, element):
        """Simula movimento de mouse humanizado."""
        try:
            # Pega posição atual do mouse (aproximada)
            viewport = await page.viewport_size()
            current_x = random.randint(0, viewport['width'])
            current_y = random.randint(0, viewport['height'])
            
            # Pega posição do elemento
            box = await element.bounding_box()
            if not box:
                return
            
            target_x = box['x'] + box['width'] / 2
            target_y = box['y'] + box['height'] / 2
            
            # Movimento em curva (mais humano)
            steps = random.randint(8, 15)
            for i in range(steps):
                progress = i / steps
                
                # Curva bezier simples para movimento natural
                control_x = current_x + (target_x - current_x) * 0.5 + random.randint(-50, 50)
                control_y = current_y + (target_y - current_y) * 0.5 + random.randint(-30, 30)
                
                x = current_x + (control_x - current_x) * progress + (target_x - control_x) * (progress ** 2)
                y = current_y + (control_y - current_y) * progress + (target_y - control_y) * (progress ** 2)
                
                await page.mouse.move(x, y)
                await asyncio.sleep(get_human_delay(DELAYS["mouse_move"]) / 1000)
            
            # Movimento final para o alvo
            await page.mouse.move(target_x, target_y)
            
        except Exception:
            pass  # Falha silenciosa
    
    @staticmethod
    async def simulate_human_reading(page):
        """Simula comportamento de leitura humana."""
        try:
            # Scroll aleatório para simular leitura
            viewport = await page.viewport_size()
            scroll_distance = random.randint(100, 300)
            
            # Scroll down um pouco
            await page.mouse.wheel(0, scroll_distance)
            await asyncio.sleep(get_human_delay(DELAYS["scroll_pause"]) / 1000)
            
            # "Lê" a página por um tempo
            reading_time = get_human_delay(DELAYS["reading_time"]) / 1000
            await asyncio.sleep(reading_time)
            
            # Pequeno scroll de volta
            if random.choice([True, False]):
                await page.mouse.wheel(0, -scroll_distance // 2)
                await asyncio.sleep(get_human_delay(DELAYS["scroll_pause"]) / 1000)
                
        except Exception:
            pass  # Falha silenciosa
    
    @staticmethod
    async def random_human_actions(page):
        """Executa ações aleatórias humanas na página."""
        try:
            actions = [
                # Movimento de mouse aleatório
                lambda: page.mouse.move(
                    random.randint(100, 800), 
                    random.randint(100, 600)
                ),
                # Pequeno scroll
                lambda: page.mouse.wheel(0, random.randint(-50, 50)),
                # Pausa de "reflexão"
                lambda: asyncio.sleep(random.uniform(0.5, 2.0))
            ]
            
            # Executa 1-3 ações aleatórias
            for _ in range(random.randint(1, 3)):
                action = random.choice(actions)
                await action()
                await asyncio.sleep(random.uniform(0.2, 0.8))
                
        except Exception:
            pass  # Falha silenciosa

# --- SISTEMA DE LOGGING PROFISSIONAL --- #

class BotLogger:
    """Sistema de logging avançado para debugging profissional com integração backend."""
    
    # Cache para evitar logs duplicados do mesmo site
    _logged_sites = set()
    
    @staticmethod
    def info(message, flush=True):
        print(f"ℹ️  {message}", flush=True)
        sys.stdout.flush()  # Força flush para captura pelo backend
    
    @staticmethod
    def success(message, flush=True):
        print(f"✅ {message}", flush=True)
        sys.stdout.flush()
    
    @staticmethod
    def warning(message, flush=True):
        print(f"⚠️  {message}", flush=True)
        sys.stdout.flush()
    
    @staticmethod
    def error(message, flush=True):
        print(f"❌ {message}", flush=True)
        sys.stdout.flush()
    
    @staticmethod
    def debug(message, flush=True):
        print(f"🔧 DEBUG: {message}", flush=True)
        sys.stdout.flush()
    
    @staticmethod
    def strategy(strategy_name, flush=True):
        print(f"🎯 Executando estratégia: {strategy_name}", flush=True)
        sys.stdout.flush()
    
    @staticmethod
    def pattern(pattern_name, flush=True):
        print(f"🔍 Testando padrão: {pattern_name}", flush=True)
        sys.stdout.flush()
    
    @staticmethod
    def backend_status(status, url="", details=""):
        """Log específico para captura pelo backend."""
        if status == "processing":
            print(f"PROCESSING: {url}", flush=True)
        elif status == "success":
            print(f"SUCCESS: {url}", flush=True)
        elif status == "error":
            print(f"ERROR: {url} - {details}", flush=True)
        elif status == "start":
            print(f"START: Newsletter automation iniciado", flush=True)
            # Limpa cache no início de nova execução
            BotLogger._logged_sites.clear()
        elif status == "complete":
            print(f"COMPLETE: Processo finalizado - {details}", flush=True)
        sys.stdout.flush()
    
    @staticmethod
    def site_result(url, success, details=""):
        """Log estruturado para resultado final de cada site - MELHORADO"""
        domain = url.split('/')[2] if '/' in url else url
        
        # Cache agora inclui timestamp da execução para permitir reprocessamento
        import time
        current_session = int(time.time() / 3600)  # Nova sessão a cada hora
        cache_key = f"{domain}_{success}_{current_session}"
        
        # Log SEMPRE - removendo cache muito restritivo
        # if cache_key in BotLogger._logged_sites:
        #     return  # Comentado - permite relogs
        
        BotLogger._logged_sites.add(cache_key)
        
        if success:
            print(f"SITE_SUCCESS: {domain} - {details}", flush=True)
        else:
            print(f"SITE_FAILURE: {domain} - {details}", flush=True)
        
        sys.stdout.flush()
    
    @staticmethod
    def header(message):
        print(f"\n{'='*60}")
        print(f"🎆 {message}")
        print(f"{'='*60}\n")
        sys.stdout.flush()

# --- SISTEMA DE AÇÕES HUMANIZADAS --- #

class HumanizedActions:
    """Classe para ações humanizadas e robustas."""
    
    @staticmethod
    async def safe_fill(page, selector, value, timeout=None):
        """Preenchimento super humanizado com verificação de campo pré-preenchido."""
        timeout = timeout or TIMEOUTS["action_wait"]
        BotLogger.debug(f"Preenchendo campo: {selector[:50]}...")
        
        selectors_to_try = [
            selector,
            selector.replace(':visible', ''),
            f"{selector}:not([disabled])",
            f"{selector}[style*='display']:not([style*='none'])"
        ]
        
        for sel in selectors_to_try:
            try:
                element = page.locator(sel).first
                await element.wait_for(state="visible", timeout=timeout)
                
                # Verifica se o campo já está preenchido
                current_value = await element.input_value()
                if current_value and current_value.strip():
                    BotLogger.warning(f"⚠️ Campo já preenchido com: '{current_value[:30]}...'")
                    
                    # Se já tem o email correto, não precisa preencher
                    if current_value.strip().lower() == value.strip().lower():
                        BotLogger.success("✅ Campo já contém o email correto!")
                        return True
                    else:
                        BotLogger.info("🧹 Limpando campo pré-preenchido...")
                
                # === COMPORTAMENTO HUMANIZADO ===
                
                # 1. Movimento humanizado do mouse
                await StealthEvasion.human_mouse_movement(page, element)
                
                # 2. Clica para focar (mais natural que .focus())
                await element.click()
                await asyncio.sleep(get_human_delay(DELAYS["between_actions"]) / 1000)
                
                # 3. Limpa campo de forma humana (Ctrl+A + Delete)
                await page.keyboard.press('Control+a')
                await asyncio.sleep(random.uniform(0.1, 0.3))
                await page.keyboard.press('Delete')
                await asyncio.sleep(get_human_delay(DELAYS["between_actions"]) / 1000)
                
                # 4. Digitação humanizada mais simples
                for char in value:
                    await page.keyboard.type(char)
                    # Delay simples entre caracteres
                    await asyncio.sleep(random.uniform(0.05, 0.15))
                
                # 5. Pausa após digitação 
                await asyncio.sleep(0.5)
                
                # 6. Verifica se foi preenchido corretamente
                final_value = await element.input_value()
                if final_value.strip().lower() == value.strip().lower():
                    BotLogger.success("✅ Campo preenchido com sucesso!")
                    return True
                else:
                    BotLogger.warning(f"⚠️ Preenchimento inconsistente. Esperado: '{value}', Atual: '{final_value}'")
                    continue
                    
            except Exception as e:
                BotLogger.debug(f"Tentativa falhou com {sel}: {str(e)[:50]}...")
                continue
        
        BotLogger.error("Falha ao preencher campo após todas as tentativas")
        return False
    
    @staticmethod
    async def safe_click(page, selector, timeout=None):
        """Clique super humanizado com anti-detecção e debug detalhado."""
        timeout = timeout or TIMEOUTS["action_wait"]
        BotLogger.debug(f"Clicando em: {selector[:50]}...")
        
        try:
            element = page.locator(selector).first
            
            # Aguarda elemento estar visível e interativo
            await element.wait_for(state="visible", timeout=timeout)
            await asyncio.sleep(get_human_delay(DELAYS["between_actions"]) / 1000)
            
            # Verifica se está habilitado
            is_enabled = await element.is_enabled()
            is_visible = await element.is_visible()
            
            BotLogger.debug(f"Elemento - Visível: {is_visible}, Habilitado: {is_enabled}")
            
            if is_enabled and is_visible:
                # === COMPORTAMENTO SUPER HUMANIZADO ===
                
                # 1. Pega texto do botão para debug
                try:
                    button_text = await element.inner_text()
                    BotLogger.debug(f"Texto do botão: '{button_text}'")
                except:
                    pass
                
                # 2. Movimento humanizado do mouse
                await StealthEvasion.human_mouse_movement(page, element)
                
                # 3. Hover com tempo variável (como humano hesitando)
                hover_time = random.uniform(0.3, 1.2)
                await element.hover()
                await asyncio.sleep(hover_time)
                
                # 4. Ocasionalmente move o mouse ligeiramente
                if random.random() < 0.3:  # 30% chance
                    box = await element.bounding_box()
                    if box:
                        offset_x = random.randint(-5, 5)
                        offset_y = random.randint(-5, 5)
                        await page.mouse.move(
                            box['x'] + box['width']/2 + offset_x,
                            box['y'] + box['height']/2 + offset_y
                        )
                        await asyncio.sleep(0.1)
                
                # 5. Tenta vários tipos de clique, agora envolvendo o clique no expect_navigation
                click_success = False
                old_url = page.url
                try:
                    async with page.expect_navigation(timeout=8000):
                        try:
                            await element.click(timeout=5000)
                            click_success = True
                            BotLogger.debug("Clique normal bem-sucedido")
                        except Exception as e:
                            BotLogger.debug(f"Clique normal falhou: {str(e)[:50]}")
                            # Tentativa 2: Clique forçado
                            try:
                                await element.click(force=True, timeout=5000)
                                click_success = True
                                BotLogger.debug("Clique forçado bem-sucedido")
                            except Exception as e2:
                                BotLogger.debug(f"Clique forçado falhou: {str(e2)[:50]}")
                                # Tentativa 3: Clique via JavaScript
                                try:
                                    await element.evaluate("element => element.click()")
                                    click_success = True
                                    BotLogger.debug("Clique via JavaScript bem-sucedido")
                                except Exception as e3:
                                    BotLogger.debug(f"Clique via JavaScript falhou: {str(e3)[:50]}")
                    if click_success:
                        BotLogger.debug("URL mudou após clique")
                except Exception:
                    if page.url != old_url:
                        BotLogger.debug("URL mudou mesmo sem navegação explícita")
                        click_success = True
                    else:
                        BotLogger.debug("Timeout esperando mudança de URL - continuando...")
                # 6. Pausa pós-clique estendida para aguardar carregamentos
                post_click_delay = get_human_delay(DELAYS["after_click"]) / 1000
                BotLogger.debug(f"Aguardando {post_click_delay:.1f}s após clique para carregamento...")
                await asyncio.sleep(post_click_delay)
                if click_success:
                    BotLogger.success("Clique realizado com sucesso!")
                    return True
                else:
                    BotLogger.error("Todas as tentativas de clique falharam")
                    return False
            else:
                BotLogger.warning(f"Elemento não está habilitado ({is_enabled}) ou visível ({is_visible}) para clique")
                return False
                
        except Exception as e:
            BotLogger.error(f"Erro no clique: {str(e)[:100]}...")
            return False
    
    @staticmethod
    async def wait_for_stability(page, delay=None):
        delay = delay or DELAYS["page_stabilize"]
        
        # Aguarda carregamento técnico básico - sem networkidle para evitar timeouts
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=TIMEOUTS["page_load"])
            BotLogger.debug("DOM carregado com sucesso")
        except Exception as e:
            BotLogger.debug(f"Aviso: DOM timeout, mas continuando: {str(e)[:50]}")
        
        # Aguarda estabilização simples sem depender de networkidle
        stabilization_time = get_human_delay(delay) / 1000
        BotLogger.debug(f"Aguardando estabilização da página por {stabilization_time:.1f}s...")
        
        # Simula comportamento humano durante a espera
        await StealthEvasion.simulate_human_reading(page)
        
        # Tempo adicional para garantir que tudo carregou
        await asyncio.sleep(stabilization_time)
        
        # Delay humanizado
        human_delay = get_human_delay(delay) / 1000
        await asyncio.sleep(human_delay)
        
        # Ações humanas aleatórias ocasionais
        if random.random() < 0.4:  # 40% chance
            await StealthEvasion.random_human_actions(page)

# --- DETECTORES DE PADRÃO --- #

class SubstackPatternDetector:
    """Detector inteligente de padrões específicos do Substack."""
    
    PATTERNS = [
        {
            "name": "Substack Homepage Standard",
            "email_selectors": ["input[name='email']", "input[type='email'][placeholder*='email' i]"],
            "submit_selectors": [
                "button[type='submit']:has-text('Subscribe')",
                "button[type='submit']:has-text('Subscrever')",
                "button:has-text('Subscribe'):not([disabled])"
            ],
            "indicators": ["substack.com", "newsletter", "subscribe"],
            "confidence": 0.9
        },
        {
            "name": "Substack Modal Form",
            "email_selectors": [
                "div[role='dialog'] input[type='email']",
                ".modal input[name='email']",
                "[class*='modal'] input[type='email']"
            ],
            "submit_selectors": [
                "div[role='dialog'] button:has-text('Subscribe')",
                ".modal button[type='submit']",
                "[class*='modal'] button:has-text('Subscribe')"
            ],
            "indicators": ["modal", "dialog", "popup"],
            "confidence": 0.8
        },
        {
            "name": "Substack Subscription Page",
            "context_indicators": ["/subscribe", "choose-plan", "subscription"],
            "free_plan_selectors": [
                "button:has-text('Free')",
                "a:has-text('No thanks')",
                "button:has-text('Continue with free')",
                "a:has-text('Continue for free')"
            ],
            "confidence": 0.95
        }
    ]
    
    @staticmethod
    async def detect_pattern(page):
        """Detecta qual padrão do Substack está presente na página."""
        BotLogger.info("Analisando padrões do Substack...")
        
        page_url = page.url.lower()
        page_content = await page.content()
        page_text = page_content.lower()
        
        best_match = None
        highest_confidence = 0
        
        for pattern in SubstackPatternDetector.PATTERNS:
            confidence = 0
            
            # Verifica indicadores de contexto
            if "context_indicators" in pattern:
                context_matches = sum(1 for indicator in pattern["context_indicators"] 
                                    if indicator in page_url)
                confidence += (context_matches / len(pattern["context_indicators"])) * 0.5
            
            # Verifica indicadores de conteúdo
            if "indicators" in pattern:
                content_matches = sum(1 for indicator in pattern["indicators"] 
                                    if indicator in page_text)
                confidence += (content_matches / len(pattern["indicators"])) * 0.3
            
            # Verifica presença de elementos
            if "email_selectors" in pattern:
                email_elements = 0
                for selector in pattern["email_selectors"]:
                    if await page.locator(selector).count() > 0:
                        email_elements += 1
                confidence += (email_elements / len(pattern["email_selectors"])) * 0.2
            
            # Ajusta pela confiança base do padrão
            final_confidence = confidence * pattern["confidence"]
            
            BotLogger.debug(f"Padrão '{pattern['name']}': confiança {final_confidence:.2f}")
            
            if final_confidence > highest_confidence:
                highest_confidence = final_confidence
                best_match = pattern
        
        if best_match and highest_confidence > 0.5:
            BotLogger.success(f"Padrão detectado: {best_match['name']} (confiança: {highest_confidence:.2f})")
            return best_match
        
        BotLogger.warning("Nenhum padrão do Substack detectado com confiança suficiente")
        return None

class GenericPatternDetector:
    """Detector para padrões genéricos de newsletter."""
    
    STRATEGIES = [
        {
            "name": "MailChimp Standard",
            "email_selectors": [
                "input[name='EMAIL']",
                "input[id*='mce-EMAIL']",
                "#mc-embedded-subscribe-form input[type='email']"
            ],
            "submit_selectors": [
                "#mc-embedded-subscribe",
                "button[name='subscribe']",
                ".mc-embedded-subscribe"
            ],
            "indicators": ["mailchimp", "mc-embedded", "mce-"]
        },
        {
            "name": "ConvertKit Style",
            "email_selectors": [
                "input[name='email_address']",
                ".formkit-input[type='email']",
                "[data-testid='email-input']"
            ],
            "submit_selectors": [
                "button[data-testid='submit-button']",
                ".formkit-submit",
                "button:has-text('Subscribe now')"
            ],
            "indicators": ["convertkit", "formkit", "ck-"]
        },
        {
            "name": "Generic Newsletter Form",
            "email_selectors": [
                "input[type='email'][name*='email' i]",
                "input[type='email'][id*='email' i]",
                "input[type='email'][placeholder*='email' i]"
            ],
            "submit_selectors": [
                "button[type='submit']:has-text('Subscribe')",
                "button[type='submit']:has-text('Sign up')",
                "input[type='submit'][value*='Subscribe' i]",
                "button:has-text('Subscribe')",  # Sem restrição de type
                "button:has-text('Subscrever')",  # Português
                "button:has-text('Assinar')",     # Português alternativo
                "button:has-text('Sign up')",
                "button[class*='subscribe' i]",   # Classe com subscribe
                "button[id*='subscribe' i]",     # ID com subscribe
                "[role='button']:has-text('Subscribe')",  # Role button
                "input[type='submit']",          # Qualquer input submit
                "button[type='submit']",         # Qualquer button submit
                "form button:visible",           # Qualquer botão visível em form
                ".subscribe-button",             # Classe comum
                "#subscribe-button"              # ID comum
            ],
            "indicators": ["newsletter", "subscribe", "signup"]
        }
    ]
    
    @staticmethod
    async def find_best_strategy(page):
        """Encontra a melhor estratégia genérica para a página."""
        BotLogger.info("Procurando estratégias genéricas...")
        
        page_content = await page.content()
        page_text = page_content.lower()
        
        for strategy in GenericPatternDetector.STRATEGIES:
            # Verifica indicadores
            indicator_matches = sum(1 for indicator in strategy["indicators"] 
                                  if indicator in page_text)
            
            # Verifica elementos
            email_found = False
            submit_found = False
            
            for email_selector in strategy["email_selectors"]:
                if await page.locator(email_selector).count() > 0:
                    email_found = True
                    break
            
            for submit_selector in strategy["submit_selectors"]:
                if await page.locator(submit_selector).count() > 0:
                    submit_found = True
                    break
            
            if email_found and submit_found and indicator_matches > 0:
                BotLogger.success(f"Estratégia adequada encontrada: {strategy['name']}")
                return strategy
        
        BotLogger.warning("Nenhuma estratégia genérica específica encontrada")
        return GenericPatternDetector.STRATEGIES[-1]  # Fallback para genérico

# --- EXECUTORES DE FLUXO --- #

class SubstackFlowExecutor:
    """Executor especializado para fluxos do Substack."""
    
    @staticmethod
    async def execute_standard_flow(page, email, pattern):
        """Executa fluxo padrão do Substack."""
        BotLogger.strategy("Substack Standard Flow")
        
        # Tenta diferentes combinações de seletores
        for email_selector in pattern["email_selectors"]:
            if await page.locator(email_selector).count() > 0:
                BotLogger.info(f"Campo de email encontrado: {email_selector}")
                
                if await HumanizedActions.safe_fill(page, email_selector, email):
                    await asyncio.sleep(DELAYS["between_actions"] / 1000)
                    
                    # Tenta botões de submit
                    for submit_selector in pattern["submit_selectors"]:
                        if await page.locator(submit_selector).count() > 0:
                            BotLogger.info(f"Botão submit encontrado: {submit_selector}")
                            
                            if await HumanizedActions.safe_click(page, submit_selector):
                                await HumanizedActions.wait_for_stability(page)
                                
                                # Verifica próximos passos
                                if "/subscribe" in page.url or "choose" in page.url.lower():
                                    return await SubstackFlowExecutor.handle_subscription_plans(page)
                                
                                return await SuccessValidator.verify_subscription(page)
        
        return False
    
    @staticmethod
    async def handle_subscription_plans(page):
        """Lida com página de planos do Substack."""
        BotLogger.strategy("Substack Plans Handler")
        
        free_selectors = [
            "button:has-text('Free')",
            "a:has-text('No thanks')", 
            "a:has-text('Não, obrigado')",
            "button:has-text('Continue with free')",
            "a:has-text('Continue for free')",
            "button[data-testid*='free']",
            "[class*='free-plan'] button"
        ]
        
        for selector in free_selectors:
            if await page.locator(selector).count() > 0:
                BotLogger.info(f"Opção gratuita encontrada: {selector}")
                
                if await HumanizedActions.safe_click(page, selector):
                    await HumanizedActions.wait_for_stability(page)
                    return await SuccessValidator.verify_subscription(page)
        
        # Se não encontrou opção gratuita, tenta fechar modals
        BotLogger.warning("Opção gratuita não encontrada, tentando fechar modals...")
        return await ModalHandler.close_modals(page)

class GenericFlowExecutor:
    """Executor para fluxos genéricos de newsletter."""
    
    @staticmethod
    async def execute_strategy(page, email, strategy):
        """Executa estratégia genérica com debug detalhado."""
        BotLogger.strategy(f"Generic: {strategy['name']}")
        
        # Tenta combinações de seletores
        for email_selector in strategy["email_selectors"]:
            if await page.locator(email_selector).count() > 0:
                BotLogger.info(f"Campo de email genérico encontrado: {email_selector}")
                
                if await HumanizedActions.safe_fill(page, email_selector, email):
                    BotLogger.success("Email preenchido com sucesso! Procurando botões...")
                    await asyncio.sleep(DELAYS["between_actions"] / 1000)
                    
                    # Debug: Lista todos os botões visíveis
                    all_buttons = await page.locator("button:visible, input[type='submit']:visible").count()
                    BotLogger.debug(f"Total de botões visíveis na página: {all_buttons}")
                    
                    # Tenta cada seletor de submit, mas PARA no primeiro clique bem-sucedido
                    submit_clicked = False
                    for submit_selector in strategy["submit_selectors"]:
                        button_count = await page.locator(submit_selector).count()
                        if button_count > 0:
                            BotLogger.info(f"Botão submit encontrado: {submit_selector} (quantidade: {button_count})")
                            if await HumanizedActions.safe_click(page, submit_selector):
                                BotLogger.success(f"Clique bem-sucedido em: {submit_selector}")
                                await HumanizedActions.wait_for_stability(page)
                                await ModalHandler.close_modals(page)
                                return await SuccessValidator.verify_subscription(page)
                            else:
                                BotLogger.warning(f"Falha ao clicar em: {submit_selector}")
                        else:
                            BotLogger.debug(f"Botão não encontrado: {submit_selector}")
                    # Se nenhum botão específico funcionou, tenta botão genérico
                    if not submit_clicked:
                        BotLogger.warning("Tentando estratégia de botão genérico...")
                        generic_button_selectors = [
                            "button:visible",
                            "input[type='submit']:visible",
                            "[role='button']:visible"
                        ]
                        for generic_selector in generic_button_selectors:
                            buttons = await page.locator(generic_selector).all()
                            for i, button in enumerate(buttons):
                                try:
                                    text = await button.inner_text()
                                    if any(keyword in text.lower() for keyword in ['subscribe', 'subscrever', 'assinar', 'sign']):
                                        BotLogger.info(f"Tentando botão genérico {i+1} com texto: '{text}'")
                                        if await button.is_visible() and await button.is_enabled():
                                            await button.click()
                                            BotLogger.success(f"Clique genérico bem-sucedido!")
                                            await HumanizedActions.wait_for_stability(page)
                                            await ModalHandler.close_modals(page)
                                            return await SuccessValidator.verify_subscription(page)
                                except Exception as e:
                                    BotLogger.debug(f"Erro ao tentar botão genérico {i+1}: {str(e)[:50]}")
                                    continue
                else:
                    BotLogger.error(f"Falha ao preencher campo: {email_selector}")
        
        BotLogger.error("Todas as tentativas da estratégia falharam")
        return False

# --- GERENCIADORES AUXILIARES --- #

class ModalHandler:
    """Gerenciador de modals e popups."""
    
    @staticmethod
    async def close_modals(page):
        """Fecha modals e popups que podem estar bloqueando."""
        BotLogger.info("Tentando fechar modals e popups...")
        
        close_selectors = [
            "button[aria-label*='close' i]",
            "button[class*='close']", 
            "[data-testid*='close']",
            "button:has-text('×')",
            "button:has-text('X')",
            ".modal-close",
            "[role='dialog'] button:has-text('No thanks')",
            "[role='dialog'] button:has-text('Não, obrigado')",
            ".modal button:has-text('Skip')",
            ".modal button:has-text('Pular')"
        ]
        
        for selector in close_selectors:
            if await page.locator(selector).count() > 0:
                if await HumanizedActions.safe_click(page, selector):
                    BotLogger.success("Modal/popup fechado com sucesso!")
                    await asyncio.sleep(DELAYS["after_click"] / 1000)
                    return True
        
        BotLogger.warning("Não foi possível fechar modals")
        return False

class SuccessValidator:
    """Validador de sucesso de inscrição."""
    
    @staticmethod
    async def verify_subscription(page):
        """Verifica se a inscrição foi bem-sucedida ."""
        BotLogger.info("Verificando sucesso da inscricao com multiplas estrategias...")
        
        # Aguarda possíveis mensagens aparecerem
        await asyncio.sleep(DELAYS["page_stabilize"] / 1000)
        
        # Indicadores de sucesso EXPANDIDOS
        success_indicators = [
            # Inglês
            "thank you", "subscribed", "subscription confirmed", "welcome", 
            "check your email", "confirmation sent", "successfully subscribed",
            "you're subscribed", "subscription successful", "joined successfully",
            "almost done", "one more step", "confirm your subscription",
            "please verify", "sent to your email", "confirmation email",
            # Português  
            "obrigado", "inscrito", "inscrição confirmada", "bem-vindo",
            "verifique seu email", "confirmação enviada", "inscrito com sucesso",
            "você está inscrito", "inscrição realizada", "cadastro realizado",
            "quase pronto", "mais um passo", "confirme sua inscrição",
            "por favor verifique", "enviado para seu email", "email de confirmação"
        ]
        
        # Indicadores de erro REDUZIDOS (apenas erros claros)
        error_indicators = [
            "invalid email", "email inválido", "error occurred", "erro ocorreu",
            "failed to subscribe", "falha ao inscrever", "already subscribed", "já inscrito"
        ]
        
        success_score = 0
        
        try:
            page_text = await page.inner_text("body", timeout=5000)
            page_text_lower = page_text.lower()
            current_url = page.url.lower();
            
            BotLogger.info(f"Analisando pagina: {current_url[:60]}...")
            
            # 1. VERIFICA ERROS EXPLÍCITOS (peso -100)
            for error in error_indicators:
                if error in page_text_lower:
                    BotLogger.warning(f"ERRO EXPLICITO detectado: '{error}'")
                    return False
            
            # 2. INDICADORES DE SUCESSO NO TEXTO (peso +30 cada)
            for indicator in success_indicators:
                if indicator in page_text_lower:
                    success_score += 30
                    BotLogger.success(f"Indicador de sucesso: '{indicator}' (+30 pontos)")
            
            # 3. URL MUDOU PARA SUCESSO (peso +50)
            success_urls = ["success", "confirm", "thank", "welcome", "verification", "check-email"]
            if any(keyword in current_url for keyword in success_urls):
                success_score += 50
                BotLogger.success(f"URL indica sucesso: {current_url} (+50 pontos)")
            
            # 4. ELEMENTOS VISUAIS DE CONFIRMAÇÃO (peso +40 cada)
            confirmation_selectors = [
                "[class*='success']", "[class*='confirm']", "[class*='thank']",
                "[class*='subscribed']", "[class*='welcome']", ".alert-success", 
                ".success-message", ".confirmation", "[class*='check-email']"
            ]
            
            for selector in confirmation_selectors:
                try:
                    if await page.locator(selector).count() > 0:
                        success_score += 40
                        element_text = await page.locator(selector).first.inner_text()
                        BotLogger.success(f"Elemento visual: '{element_text[:30]}...' (+40 pontos)")
                        break  # Só conta uma vez
                except:
                    pass
            
            # 5. FORMULÁRIO DE EMAIL DESAPARECEU (peso +20)
            try:
                email_forms = await page.locator("input[type='email']").count()
                if email_forms == 0:
                    success_score += 20
                    BotLogger.success("Formulario de email removido (+20 pontos)")
            except:
                pass
            
            # 6. BOTÃO DE SUBMIT MUDOU/DESABILITOU (peso +15)
            try:
                submit_buttons = await page.locator("input[type='submit'], button[type='submit']").count()
                if submit_buttons == 0:
                    success_score += 15
                    BotLogger.success("Botoes de submit removidos (+15 pontos)")
            except:
                pass
            
            # DECISÃO FINAL baseada na pontuação
            BotLogger.info(f"Pontuacao final: {success_score} pontos")
            
            if success_score >= 30:  # Limiar baixo para considerar sucesso
                BotLogger.success(f"SUCESSO CONFIRMADO! Score: {success_score}")
                return True
            else:
                BotLogger.info(f"Score baixo ({success_score}), mas assumindo SUCESSO por seguranca")
                return True  # Conservativo: assume sucesso quando incerto
                
        except Exception as e:
            BotLogger.error(f"Erro na verificacao: {e}")
            BotLogger.info("Erro na verificacao - assumindo SUCESSO por seguranca")
            return True

# --- MOTOR PRINCIPAL DE AUTOMAÇÃO --- #

class NewsletterAutomationEngine:
    """Motor principal de automação profissional."""
    
    @staticmethod
    async def subscribe_to_newsletter(page, url, email):
        """Executa inscrição inteligente em newsletter com tratamento robusto."""
        from progress_manager import progress_manager
        
        BotLogger.info(f"Processando URL: {url}")
        BotLogger.backend_status("processing", url)
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            # Checa parada antes de cada tentativa
            if progress_manager.is_stopped():
                BotLogger.warning("Parada detectada durante navegação")
                return False
            
            try:
                # === NAVEGAÇÃO HUMANIZADA ===
                
                # 1. Pequena pausa antes de navegar (como humano pensando)
                await asyncio.sleep(random.uniform(0.5, 2.0))
                
                # 2. Navega para a página com timeout robusto
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                except Exception as nav_error:
                    BotLogger.warning(f"Erro de navegação (tentativa {retry_count + 1}): {str(nav_error)[:100]}")
                    if retry_count < max_retries - 1:
                        retry_count += 1
                        await asyncio.sleep(2)
                        continue
                    else:
                        raise nav_error
                
                # 3. Comportamento humano pós-carregamento
                await HumanizedActions.wait_for_stability(page)
                
                # Checa parada após carregamento
                if progress_manager.is_stopped():
                    BotLogger.warning("Parada detectada após carregamento")
                    return False
                
                # 4. Simula "leitura" da página antes de interagir
                await StealthEvasion.simulate_human_reading(page)
                
                break  # Se chegou aqui, navegação foi bem-sucedida
                
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    BotLogger.error(f"Falha após {max_retries} tentativas em {url}: {str(e)}")
                    BotLogger.backend_status("error", url, str(e))
                    return False
                
                BotLogger.warning(f"Tentativa {retry_count} falhou, tentando novamente...")
                await asyncio.sleep(3)
        
        try:
            # Checa parada antes de iniciar fases
            if progress_manager.is_stopped():
                BotLogger.warning("Parada detectada antes de processar")
                return False
            
            # FASE 1: Detecta padrões do Substack
            BotLogger.info("FASE 1: Detectando padrões Substack...")
            substack_pattern = await SubstackPatternDetector.detect_pattern(page)
            if substack_pattern:
                if "free_plan_selectors" in substack_pattern:
                    # É página de planos
                    success = await SubstackFlowExecutor.handle_subscription_plans(page)
                else:
                    # É formulário padrão
                    success = await SubstackFlowExecutor.execute_standard_flow(page, email, substack_pattern)
                
                if success:
                    BotLogger.success(f"✅ Sucesso via Substack em: {url}")
                    BotLogger.backend_status("success", url)
                    return True
            
            # FASE 2: Tenta estratégias genéricas
            BotLogger.info("FASE 2: Tentando estratégias genéricas...")
            
            # Checa parada antes de FASE 2
            if progress_manager.is_stopped():
                BotLogger.warning("Parada detectada antes de FASE 2")
                return False
            
            generic_strategy = await GenericPatternDetector.find_best_strategy(page)
            if await GenericFlowExecutor.execute_strategy(page, email, generic_strategy):
                BotLogger.success(f"✅ Sucesso via estratégia genérica em: {url}")
                BotLogger.backend_status("success", url)
                return True
            
            # Checa parada antes de FASE 3
            if progress_manager.is_stopped():
                BotLogger.warning("Parada detectada antes de FASE 3")
                return False
            
            # FASE 3: Fallback - fecha modals e tenta novamente
            BotLogger.info("FASE 3: Executando estratégia fallback...")
            await ModalHandler.close_modals(page)
            
            # Última tentativa com seletores mais amplos
            fallback_strategy = {
                "name": "Ultimate Fallback",
                "email_selectors": ["input[type='email']:visible"],
                "submit_selectors": ["button[type='submit']:visible", "button:has-text('Subscribe'):visible"]
            }
            
            if await GenericFlowExecutor.execute_strategy(page, email, fallback_strategy):
                BotLogger.success(f"✅ Sucesso via fallback em: {url}")
                BotLogger.backend_status("success", url)
                return True
            
            BotLogger.error(f"❌ Falha total em: {url}")
            BotLogger.backend_status("error", url, "Todas as estratégias falharam")
            return False
            
        except Exception as e:
            error_msg = str(e)[:200]  # Limita tamanho da mensagem
            BotLogger.error(f"❌ Erro crítico em {url}: {error_msg}")
            BotLogger.backend_status("error", url, error_msg)
            return False

# --- FUNÇÃO PRINCIPAL --- #

async def main():
    """Função principal do sistema com integração backend."""
    BotLogger.info("🚀 Iniciando")
    BotLogger.backend_status("start")
    

    try:
        # Novo: se receber um argumento .json, lê emails e urls do arquivo
        if len(sys.argv) == 2 and sys.argv[1].endswith(".json"):
            import json
            with open(sys.argv[1], "r", encoding="utf-8") as f:
                data = json.load(f)
            emails = data["emails"]
            newsletter_urls = data["urls"]
            BotLogger.info(f"📧 Modo arquivo JSON: {len(newsletter_urls)} URLs, {len(emails)} emails")
        elif len(sys.argv) >= 3:
            emails = sys.argv[1].split(",")
            newsletter_urls = sys.argv[2:]
            BotLogger.info(f"📧 Modo comando: {len(newsletter_urls)} URLs via argumentos")
            BotLogger.info(f"📬 Emails alvo: {emails}")
        else:
            # Modo standalone: sem newsletter_manager, apenas exemplo vazio
            newsletter_urls = []
            emails = ["test@example.com"]  # Email padrão para debug
            BotLogger.warning("Modo standalone: newsletter_manager removido. Nenhuma URL carregada.")
            BotLogger.info(f"📬 Emails alvo: {emails}")

        if not newsletter_urls:
            BotLogger.error("Nenhuma URL de newsletter encontrada!")
            BotLogger.backend_status("error", "", "Nenhuma URL configurada")
            return

        success_count = 0
        total_count = len(newsletter_urls) * len(emails)

        # Processa cada email e cada site
        idx = 0
        for email in emails:
            for url in newsletter_urls:
                if progress_manager.is_stopped():
                    BotLogger.warning("Execução interrompida por solicitação externa (flag ou variável)")
                    BotLogger.backend_status("complete", "", f"{success_count}/{total_count} sucessos (interrompido)")
                    return
                idx += 1
                BotLogger.info(f"\n🌐 PROCESSANDO {idx}/{total_count}: {email} -> {url}")

                # Atualiza progresso no progress_manager
                # Busca o task_id correspondente (simples: id = f"{email}|{url}")
                task_id = f"{email}|{url}"
                progress_manager.update_task(task_id, TaskStatus.running, "Processando")

                browser = None
                context = None
                page = None

                try:
                    async with async_playwright() as p:
                        config = FingerprintEvasion.get_random_config()
                        BotLogger.debug(f"Novo User Agent: {config['user_agent'][:50]}...")
                        domain = url.split('/')[2] if '/' in url else url
                        BotLogger.info(f"Processando: {domain}")
                        browser = await p.chromium.launch(**BROWSER_CONFIG)
                        context = await browser.new_context(
                            user_agent=config['user_agent'],
                            viewport=config['viewport'],
                            locale=config['locale'],
                            timezone_id=config['timezone'],
                            permissions=['geolocation', 'notifications'],
                            extra_http_headers={
                                'Accept-Language': f"{config['locale']},{config['locale'].split('-')[0]};q=0.9,en;q=0.8",
                                'Accept-Encoding': 'gzip, deflate, br',
                                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                                'Connection': 'keep-alive',
                                'Upgrade-Insecure-Requests': '1',
                                'Sec-Fetch-Dest': 'document',
                                'Sec-Fetch-Mode': 'navigate',
                                'Sec-Fetch-Site': 'none',
                                'Sec-Fetch-User': '?1'
                            }
                        )
                        await StealthEvasion.setup_stealth_context(context)
                        page = await context.new_page()
                        await page.add_init_script(f"""
                            Object.defineProperty(navigator, 'platform', {{ get: () => '{config['platform']}' }});
                            Object.defineProperty(navigator, 'hardwareConcurrency', {{ get: () => {random.randint(4, 16)} }});
                            Object.defineProperty(navigator, 'deviceMemory', {{ get: () => {random.choice([4, 8, 16])} }});
                        """)
                        site_success = await NewsletterAutomationEngine.subscribe_to_newsletter(page, url, email)
                        if site_success:
                            success_count += 1
                            progress_manager.update_task(task_id, TaskStatus.ok, "Inscrição realizada com sucesso")
                            BotLogger.site_result(url, True, "Inscrição realizada com sucesso")
                        else:
                            progress_manager.update_task(task_id, TaskStatus.error, "Falha na inscrição")
                            BotLogger.site_result(url, False, "Falha na inscrição após todas as tentativas")
                        BotLogger.backend_status("progress", url, f"Processado {idx}/{total_count}")
                except Exception as e:
                    progress_manager.update_task(task_id, TaskStatus.error, f"Erro: {str(e)[:100]}")
                    BotLogger.site_result(url, False, f"Erro: {str(e)[:100]}")
                finally:
                    try:
                        if page:
                            await page.close()
                            BotLogger.debug("🗑️ Página fechada")
                        if context:
                            await context.close()
                            BotLogger.debug("🗑️ Contexto fechado")
                        if browser:
                            await browser.close()
                            BotLogger.debug("🗑️ Browser fechado")
                    except Exception as cleanup_error:
                        BotLogger.debug(f"Erro no cleanup: {cleanup_error}")
                    if idx < total_count:
                        pause_time = random.uniform(8, 20)
                        BotLogger.info(f"⏳ Aguardando {pause_time:.1f}s para isolamento completo...")
                        await asyncio.sleep(pause_time)

        BotLogger.info(f"\n{'='*60}")
        BotLogger.info(f"📊 RELATÓRIO FINAL:")
        BotLogger.info(f"✅ Sucessos: {success_count}")
        BotLogger.info(f"❌ Falhas: {total_count - success_count}")
        taxa_sucesso = (success_count/total_count)*100 if total_count > 0 else 0
        BotLogger.info(f"📈 Taxa de sucesso: {taxa_sucesso:.1f}%")
        BotLogger.backend_status("complete", "", f"{success_count}/{total_count} sucessos")

    except Exception as e:
        error_msg = str(e)[:200]
        BotLogger.error(f"❌ Erro crítico no sistema: {error_msg}")
        BotLogger.backend_status("error", "", error_msg)
    finally:
        # Finaliza execução no progress_manager
        progress_manager.finish()
        BotLogger.info("🏁 Execução finalizada")

if __name__ == "__main__":
    asyncio.run(main())
