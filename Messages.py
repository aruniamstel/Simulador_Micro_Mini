import os
import time
import keyboard
from datetime import datetime

class MessageManager:
    def __init__(self):
        # Cria a pasta de destino se não existir
        self.diretorio_sms = os.path.join(os.getcwd(), "Telefone", "SMS")
        if not os.path.exists(self.diretorio_sms):
            os.makedirs(self.diretorio_sms, exist_ok=True)

    def quebrar_texto(self, texto, largura=20):
        """Divide o texto em linhas de 20 caracteres para caber na tela."""
        return [texto[i:i+largura] for i in range(0, len(texto), largura)]

    def escrever_mensagem(self):
        import SYSTEM
        mensagem = ""
        cursor_visivel = True
        ultimo_pisca = time.time()
        
        while True:
            # Lógica do cursor piscando
            if time.time() - ultimo_pisca > 0.4:
                cursor_visivel = not cursor_visivel
                ultimo_pisca = time.time()

            # Prepara o conteúdo visual
            # A primeira linha exibe a instrução, as outras o texto digitado
            texto_exibicao = mensagem + ("|" if cursor_visivel else " ")
            linhas_digitadas = self.quebrar_texto(texto_exibicao)
            
            conteudo_tela = ["digite a sua mensagem:"] + linhas_digitadas
            
            # Garante preenchimento de 9 linhas para manter a moldura estável
            while len(conteudo_tela) < 9:
                conteudo_tela.append("")

            SYSTEM.renderizar_tela_fixa("NOVA MSG", conteudo_tela[:9], barra_status_esq="Enviar", barra_status_dir="Apagar")
            
            # Captura de entrada
            evento = keyboard.read_event(suppress=True)
            if evento.event_type == keyboard.KEY_DOWN:
                tecla = evento.name.lower()
                
                # Enviar (Page Up / aux_esq)
                if tecla == "page up":
                    if mensagem.strip():
                        self.salvar_mensagem(mensagem) # Correção do TypeError aqui
                        SYSTEM.renderizar_tela_fixa("SMS", ["", "", SYSTEM.centralizar("Mensagem"), SYSTEM.centralizar("Enviada!"), ""], barra_status_esq="", barra_status_dir="")
                        time.sleep(2)
                        return "MENU_PRINCIPAL"
                
                # Sair/Apagar tudo (Page Down / aux_dir)
                elif tecla == "page down":
                    if mensagem == "": return "MENU_PRINCIPAL"
                    mensagem = "" # Limpa o texto primeiro
                
                # Apagar caractere (Backspace)
                elif tecla == "backspace":
                    mensagem = mensagem[:-1]
                
                # Espaço
                elif tecla == "space":
                    if len(mensagem) < 160: mensagem += " "
                
                # Letras e Números (PC Keyboard)
                elif len(tecla) == 1:
                    if len(mensagem) < 160: # Limite para caber na tela (aprox 8 linhas x 20 colunas)
                        # Mantém a caixa alta/baixa original do teclado
                        mensagem += evento.name 

    def salvar_mensagem(self, texto):
        """Grava a mensagem em um arquivo .txt com timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arq = f"SMS_{timestamp}.txt"
        caminho = os.path.join(self.diretorio_sms, nome_arq)
        
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
            f.write("-" * 15 + "\n")
            f.write(texto)

    def listar_enviadas(self):
        import SYSTEM
        while True:
            arquivos = sorted([f for f in os.listdir(self.diretorio_sms) if f.endswith('.txt')], reverse=True)
            
            if not arquivos:
                SYSTEM.renderizar_tela_fixa("ENVIADAS", ["", "", SYSTEM.centralizar("Caixa vazia"), "", ""], barra_status_dir="Voltar")
                if SYSTEM.obter_entrada_tecla() == "aux_dir": return "MENU_PRINCIPAL"
                continue

            conteudo_tela = []
            for i, arq in enumerate(arquivos[:9]):
                # Formata a exibição: "1. 15/01 22:30"
                partes = arq.replace("SMS_", "").replace(".txt", "").split("_")
                data, hora = partes[0], partes[1]
                conteudo_tela.append(f"{i+1}. {data[6:8]}/{data[4:6]} {hora[:2]}:{hora[2:4]}")

            SYSTEM.renderizar_tela_fixa("ENVIADAS", conteudo_tela, barra_status_esq="Abrir", barra_status_dir="Voltar")
            
            tecla = SYSTEM.obter_entrada_tecla()
            if tecla == "aux_dir": return "MENU_PRINCIPAL"
            if tecla.isdigit() and 0 < int(tecla) <= len(arquivos):
                self.ler_mensagem(arquivos[int(tecla)-1])

    def ler_mensagem(self, nome_arquivo):
        import SYSTEM
        caminho = os.path.join(self.diretorio_sms, nome_arquivo)
        with open(caminho, "r", encoding="utf-8") as f:
            linhas = [l.strip() for l in f.readlines()]
            
        while True:
            SYSTEM.renderizar_tela_fixa("MENSAGEM", linhas, barra_status_esq="", barra_status_dir="Voltar")
            if SYSTEM.obter_entrada_tecla() == "aux_dir": break

# Instâncias globais para o SYSTEM.py
msg_manager = MessageManager()

def nova_mensagem():
    return msg_manager.escrever_mensagem()

def mensagens_enviadas():
    return msg_manager.listar_enviadas()