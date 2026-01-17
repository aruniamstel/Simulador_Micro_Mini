import os
import time
import keyboard
from datetime import datetime

class MessageManager:
    def __init__(self):
        # Pasta onde as mensagens serão salvas
        self.diretorio_sms = os.path.join(os.getcwd(), "Telefone", "SMS")
        if not os.path.exists(self.diretorio_sms):
            os.makedirs(self.diretorio_sms)

    def quebrar_texto(self, texto, largura=20):
        """Quebra o texto em linhas conforme a largura da tela."""
        linhas = []
        for i in range(0, len(texto), largura):
            linhas.append(texto[i:i+largura])
        return linhas

    def escrever_mensagem(self):
        import SYSTEM
        mensagem = ""
        cursor_visivel = True
        ultimo_pisca = time.time()
        
        while True:
            # Lógica do cursor piscando
            if time.time() - ultimo_pisca > 0.5:
                cursor_visivel = not cursor_visivel
                ultimo_pisca = time.time()

            # Prepara as linhas para exibição
            texto_exibicao = mensagem + ("|" if cursor_visivel else " ")
            linhas_corpo = self.quebrar_texto(texto_exibicao)
            
            # Garante que sempre tenha 9 linhas para a renderização não quebrar
            while len(linhas_corpo) < 9:
                linhas_corpo.append("")
            
            # Limite de segurança (9 linhas de 20 caracteres = 180 chars)
            if len(mensagem) >= 180:
                mensagem = mensagem[:180]

            SYSTEM.renderizar_tela_fixa("NOVA MSG", linhas_corpo, barra_status_esq="Enviar", barra_status_dir="Apagar")
            
            # Captura de entrada (usando keyboard.read_event para pegar caracteres direto)
            evento = keyboard.read_event(suppress=True)
            if evento.event_type == keyboard.KEY_DOWN:
                tecla = evento.name
                
                # Enviar (Page Up)
                if tecla == "page up":
                    if len(mensagem.strip()) > 0:
                        self.salvar_mensagem(mensagem)
                        SYSTEM.renderizar_tela_fixa("SMS", ["", "", SYSTEM.centralizar("Enviando..."), "", ""], barra_status_esq="", barra_status_dir="")
                        time.sleep(1.5)
                        return "MENU_PRINCIPAL"
                    
                # Apagar (Backspace ou Page Down para sair)
                elif tecla == "backspace":
                    mensagem = mensagem[:-1]
                elif tecla == "page down":
                    if mensagem == "": return "MENU_PRINCIPAL"
                    mensagem = "" # Limpa se houver texto, sai se estiver vazio
                
                # Digitação de caracteres (letras, números, espaço)
                elif len(tecla) == 1: # Evita capturar "shift", "ctrl", etc
                    mensagem += tecla
                elif tecla == "space":
                    mensagem += " "

    def salvar_mensagem(self):
        # Nome do arquivo baseado na data/hora
        nome_arq = datetime.now().strftime("SMS_%Y%m%d_%H%M%S.txt")
        caminho = os.path.join(self.diretorio_sms, nome_arq)
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
            f.write("-" * 10 + "\n")
            f.write(texto)

    def listar_enviadas(self):
        import SYSTEM
        while True:
            arquivos = sorted([f for f in os.listdir(self.diretorio_sms) if f.endswith('.txt')], reverse=True)
            
            if not arquivos:
                SYSTEM.renderizar_tela_fixa("ENVIADAS", ["", SYSTEM.centralizar("Caixa vazia")], barra_status_dir="Voltar")
                if SYSTEM.obter_entrada_tecla() == "aux_dir": return "MENU_PRINCIPAL"
                continue

            conteudo_tela = []
            for i, arq in enumerate(arquivos[:9]): # Mostra as 9 últimas
                data_str = arq.replace("SMS_", "").replace(".txt", "")
                conteudo_tela.append(f"{i+1}. {data_str[:8]} {data_str[9:13]}")

            SYSTEM.renderizar_tela_fixa("ENVIADAS", conteudo_tela, barra_status_esq="Abrir", barra_status_dir="Voltar")
            
            tecla = SYSTEM.obter_entrada_tecla()
            if tecla == "aux_dir": return "MENU_PRINCIPAL"
            if tecla.isdigit() and int(tecla) <= len(arquivos):
                self.ler_mensagem(arquivos[int(tecla)-1])

    def ler_mensagem(self, nome_arquivo):
        import SYSTEM
        caminho = os.path.join(self.diretorio_sms, nome_arquivo)
        with open(caminho, "r", encoding="utf-8") as f:
            linhas = [l.strip() for l in f.readlines()]
            
        while True:
            SYSTEM.renderizar_tela_fixa("MENSAGEM", linhas, barra_status_esq="", barra_status_dir="Sair")
            if SYSTEM.obter_entrada_tecla() == "aux_dir": break

# Instância global para facilitar o acesso
msg_manager = MessageManager()

def nova_mensagem():
    return msg_manager.escrever_mensagem()

def mensagens_enviadas():
    return msg_manager.listar_enviadas()