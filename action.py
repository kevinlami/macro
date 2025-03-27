import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, Toplevel, Button, StringVar
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from pynput import mouse
from PIL import Image, ImageTk
import pyautogui
import keyboard
import threading
import time
import json
import os
import cv2
import numpy as np

class ActionRecorder:
    def __init__(self, root, gui, main):
        self.root = root
        self.gui = gui
        self.main = main

    #list_commands
    def add_key(self):
        """Captura combinações de teclas, agora com a opção de pressionar a tecla por um tempo."""
        # Mudar o texto do botão para "Gravando..." e ajustar as cores
        self.gui.add_key_btn.config(text="Gravando...", state=tk.DISABLED, bootstyle="warning")

        def capture_keys():
            recorded_keys = []  # Lista para manter a ordem
            pressed_keys = set()  # Controla teclas pressionadas

            while True:
                event = keyboard.read_event()

                if event.event_type == "down":
                    if event.name not in pressed_keys:
                        recorded_keys.append(event.name)  # Adiciona na ordem
                        pressed_keys.add(event.name)
                elif event.event_type == "up":
                    if event.name in pressed_keys:
                        pressed_keys.remove(event.name)

                # Sai quando todas as teclas forem soltas
                if not pressed_keys:
                    break

            hotkey = "+".join(recorded_keys)
            if hotkey:
                self.main.actions.append(("key", hotkey))
                self.gui.update_listbox()
            
            # Depois de capturar as teclas, retorna o texto do botão e habilita novamente, com as cores padrão
            self.gui.add_key_btn.config(text="Clicar Tecla", state=tk.NORMAL, bootstyle="secondary")
        threading.Thread(target=capture_keys, daemon=True).start()

    def add_press_key(self):
        """Captura a tecla a ser pressionada e por quanto tempo em milissegundos."""
        press_time = simpledialog.askinteger("Tempo de Pressão", "Digite o tempo em milissegundos que a tecla ficará pressionada:")

        if press_time is not None:
            def capture_keys():
                recorded_keys = []  # Lista para manter a ordem
                pressed_keys = set()  # Controla teclas pressionadas
                self.gui.press_key_btn.config(text="Gravando...", state=tk.DISABLED, bootstyle="warning")

                while True:
                    event = keyboard.read_event()

                    if event.event_type == "down":
                        if event.name not in pressed_keys:
                            recorded_keys.append(event.name)  # Adiciona na ordem
                            pressed_keys.add(event.name)
                    elif event.event_type == "up":
                        if event.name in pressed_keys:
                            pressed_keys.remove(event.name)

                    # Sai quando todas as teclas forem soltas
                    if not pressed_keys:
                        break

                hotkey = "+".join(recorded_keys)
                if hotkey:
                    self.main.actions.append(("press_key", (hotkey, press_time)))
                    self.gui.update_listbox()
                
                # Depois de capturar as teclas, retorna o texto do botão e habilita novamente, com as cores padrão
                self.gui.press_key_btn.config(text="Pressionar Tecla", state=tk.NORMAL, bootstyle="secondary")
            threading.Thread(target=capture_keys, daemon=True).start()

    def add_wait(self):
        """Adiciona um tempo de espera em milissegundos."""
        wait_time = simpledialog.askinteger("Adicionar Espera", "Digite o tempo em milissegundos:")
        if wait_time:
            self.main.actions.append(("wait", wait_time))
            self.gui.update_listbox()

    def add_click(self):
        """Adiciona um clique do mouse usando botões em vez de input, com janela centralizada."""
        top = Toplevel(self.root)
        top.title("Adicionar Clique")

        # Dimensões da janela principal
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()

        # Dimensões da janela do diálogo
        dialog_width = 250
        dialog_height = 100

        # Calcula posição centralizada
        pos_x = root_x + (root_width - dialog_width) // 2
        pos_y = root_y + (root_height - dialog_height) // 2

        # Define posição e tamanho
        top.geometry(f"{dialog_width}x{dialog_height}+{pos_x}+{pos_y}")

        selected_button = StringVar()

        def set_click(value):
            selected_button.set(value)
            top.destroy()  # Fecha a janela ao escolher

        # Criando botões para seleção
        Button(top, text="Left", command=lambda: set_click("left"), width=10).pack(pady=5)
        Button(top, text="Middle", command=lambda: set_click("middle"), width=10).pack(pady=5)
        Button(top, text="Right", command=lambda: set_click("right"), width=10).pack(pady=5)

        top.wait_window()  # Aguarda a escolha do usuário

        # Adiciona o clique à lista de ações se for válido
        click_type = selected_button.get()
        if click_type in ["left", "middle", "right"]:
            self.main.actions.append(("click", click_type))
            self.gui.update_listbox()
    
    def move_mouse(self):
        """Aguarda um clique do usuário e captura a posição do mouse."""
        self.gui.move_mouse_btn.config(text="Clique para gravar", state=tk.DISABLED, bootstyle="warning")

        def on_click(x, y, button, pressed):
            if pressed and button == mouse.Button.left:  # Captura apenas o clique esquerdo
                self.main.actions.append(("move", (x, y)))
                self.gui.update_listbox()
                self.gui.move_mouse_btn.config(text="Mover Mouse", state=tk.NORMAL, bootstyle="secondary")
                listener.stop()  # Para o listener após capturar o clique

        # Executa o listener em uma thread separada
        listener = mouse.Listener(on_click=on_click)
        listener.start()
    
    def start_mouse_listener(self):
        """Inicia o listener do mouse para capturar cliques e movimentos."""
        self.mouse_listener = mouse.Listener(on_click=self.on_click, on_move=self.on_move)
        self.mouse_listener.start()  # Apenas inicia, sem join()

    def add_image_check(self):
        """Adiciona uma verificação de imagem à lista de ações."""
        try:
            # Informa o usuário sobre a captura de região
            messagebox.showinfo("Capturar Imagem", "Clique e arraste para selecionar uma região da tela.")

            # Cria uma janela transparente para desenhar o retângulo
            self.overlay = tk.Toplevel(self.root)
            self.overlay.attributes("-fullscreen", True)
            self.overlay.attributes("-alpha", 0.1)
            self.overlay.attributes("-topmost", True)

            self.canvas = tk.Canvas(self.overlay, bg="black", highlightthickness=0)
            self.canvas.pack(fill=tk.BOTH, expand=True)

            # Reseta as coordenadas
            self.start_x, self.start_y = None, None
            self.end_x, self.end_y = None, None

            # Inicia o listener do mouse em uma thread separada
            self.listener_thread = threading.Thread(target=self.start_mouse_listener, daemon=True)
            self.listener_thread.start()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao capturar imagem: {e}")

    def on_click(self, x, y, button, pressed):
        """Captura os eventos de clique e soltura do mouse."""
        if pressed:
            self.start_x, self.start_y = x, y
        else:
            self.end_x, self.end_y = x, y

            # Calcula a região selecionada
            width = abs(self.end_x - self.start_x)
            height = abs(self.end_y - self.start_y)

            # Garante que a região tenha pelo menos 1x1 pixel
            if width == 0 or height == 0:
                messagebox.showwarning("Aviso", "A região selecionada é muito pequena. Tente novamente.")

                # Para o listener do mouse se ainda estiver ativo
                if hasattr(self, 'mouse_listener') and self.mouse_listener.is_alive():
                    self.mouse_listener.stop()

                # Fecha a janela de overlay para evitar múltiplas execuções
                if hasattr(self, 'overlay') and self.overlay:
                    self.overlay.destroy()
                return  # Sai da função para evitar travamento

            # Para o listener do mouse
            if hasattr(self, 'mouse_listener') and self.mouse_listener.is_alive():
                self.mouse_listener.stop()

            # Fecha a janela de overlay
            if hasattr(self, 'overlay') and self.overlay:
                self.overlay.destroy()

            # Captura a região da tela
            region = (min(self.start_x, self.end_x), min(self.start_y, self.end_y), width, height)
            image = pyautogui.screenshot(region=region)

            # Move o salvamento da imagem para uma thread separada
            threading.Thread(target=self.save_image, args=(image,), daemon=True).start()

    def on_move(self, x, y):
        """Atualiza o retângulo enquanto o usuário arrasta o mouse."""
        if hasattr(self, 'canvas') and self.canvas.winfo_exists():
            if self.start_x is not None and self.start_y is not None:
                # Limpa o canvas e desenha um novo retângulo
                self.canvas.delete("rect")
                self.canvas.create_rectangle(
                    self.start_x, self.start_y, x, y,
                    outline="red", width=2, tags="rect"
                )

    def save_image(self, image):
        """Salva a imagem capturada em uma thread separada."""
        try:
            # Abre a janela de diálogo para salvar o arquivo
            image_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])

            if not image_path:
                print("Nenhum caminho de imagem foi selecionado.")
                return

            # Salva a imagem
            image.save(image_path)

            # Atualiza a interface na thread principal
            self.root.after(0, self.add_image_to_list, image_path)
        except Exception as e:
            print(f"Erro ao salvar imagem: {e}")

    def add_image_to_list(self, image_path):
        """Adiciona a imagem à lista de ações na interface."""
        if not isinstance(image_path, str):
            print(f"ERRO: Caminho da imagem inválido! Tipo recebido: {type(image_path)}")
            return  # Não adiciona à lista se for inválido

        self.main.actions.append(("image_check", image_path))
        self.gui.update_listbox()
    
    def add_group(self):
        """Adiciona um novo grupo em torno dos itens selecionados ou ao final da lista."""
        group_name = simpledialog.askstring("Nome do Grupo", "Digite o nome do grupo:")
        if not group_name:
            return  # Se o usuário cancelar ou não digitar nada, não faz nada.

        selected_indices = list(self.gui.actions_listbox.curselection())

        if selected_indices:
            # Se houver itens selecionados, encapsula em um grupo
            start_index = selected_indices[0]
            end_index = selected_indices[-1] + 1  # Ajusta para incluir o último item

            self.main.actions.insert(start_index, ["group_start", group_name])
            self.main.actions.insert(end_index + 1, ["group_end", group_name])
        else:
            # Caso contrário, adiciona um grupo vazio no final
            self.main.actions.append(["group_start", group_name])
            self.main.actions.append(["group_end", group_name])

        self.gui.update_listbox()

