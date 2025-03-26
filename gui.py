import tkinter as tk
from command import CommandRecorder
from action import ActionRecorder
from tkinter import messagebox, simpledialog, filedialog, PhotoImage
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

class GuiRecorder:
    def __init__(self, root, main):
        self.root = root
        self.main = main
        self.command = CommandRecorder(root, self, main)
        self.action = ActionRecorder(root, self, main)
        self.root.title("K Recorder")
        self.root.geometry("700x600")
        self.root.configure(bg="#f0f0f0")
        ttk.Style(theme="superhero")

        # Frame principal
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.create_menu()
        self.create_header()
        self.create_list_commands()
        self.create_actions()

        # Lista de ações (Listbox)
        self.actions_listbox = tk.Listbox(self.main_frame, height=12, width=60, selectmode=tk.EXTENDED)
        self.actions_listbox.pack(fill=tk.BOTH, pady=10, padx=10, expand=True)

        # Eventos para drag and drop
        self.actions_listbox.bind("<ButtonPress-1>", self.on_start_drag)
        self.actions_listbox.bind("<B1-Motion>", self.on_drag)
        self.actions_listbox.bind("<ButtonRelease-1>", self.on_drop)

        # Dados de arrasto
        self.drag_data = {"index": None}
    
    def create_menu(self):
        """Cria a barra de menu com as opções de salvar, carregar, rodar e parar macro."""
        menubar = tk.Menu(self.root)

        # Menu "Arquivo"
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Salvar Macros", command=self.command.save_macros)
        file_menu.add_command(label="Carregar Macros", command=self.command.load_macros)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)
        menubar.add_cascade(label="Arquivo", menu=file_menu)

        # Menu "Macro" com opções de iniciar e parar
        macro_menu = tk.Menu(menubar, tearoff=0)
        macro_menu.add_command(label="▶ Rodar Macro (F5)", command=self.main.start_macro)
        macro_menu.add_command(label="■ Parar Macro (F6)", command=self.main.stop_macro)
        menubar.add_cascade(label="Macro", menu=macro_menu)

        # Configura a barra de menus na janela principal
        self.root.config(menu=menubar)

    def create_header(self):
        """Cria o cabeçalho."""
        # Título
        self.title_label = ttk.Label(self.main_frame, text="K Recorder", font=("Helvetica", 18, "bold"), bootstyle="light")
        self.title_label.pack(pady=10)

        # Frame para os botões de controle de macro no topo
        self.control_buttons_frame = ttk.Frame(self.main_frame)
        self.control_buttons_frame.pack(fill=tk.X, pady=10)

        imagePlay = Image.open("play_icon.png")
        imagePlay = imagePlay.resize((64, 64), Image.LANCZOS)

        imageStop = Image.open("stop_icon.png")
        imageStop = imageStop.resize((64, 64), Image.LANCZOS)

        # Carregando ícones para Play e Stop
        self.play_icon = ImageTk.PhotoImage(imagePlay)
        self.stop_icon = ImageTk.PhotoImage(imageStop)

        self.toggle_btn = tk.Label(
            self.control_buttons_frame, 
            image=self.play_icon, 
            background="white"  # Pode ajustar para a cor desejada
        )
        self.toggle_btn.pack(side=tk.LEFT, padx=5, expand=True)

        # Adiciona evento de clique
        self.toggle_btn.bind("<Button-1>", lambda event: self.main.toggle_macro())

        # Frame para os botões de controle de macro no topo
        self.control_check_frame = ttk.Frame(self.main_frame)
        self.control_check_frame.pack(fill=tk.X, pady=10)

        self.loop_checkbox = ttk.Checkbutton(self.control_check_frame, bootstyle="success-round-toggle", text="Loop Infinito", variable=self.main.loop_var)
        self.loop_checkbox.pack(side=tk.RIGHT, pady=10, padx=10)

    def create_list_commands(self):
        """Cria area de comandos para a lista."""
                # Frame para botões de controle de movimentação
        self.move_buttons_frame = tk.Frame(self.main_frame)
        self.move_buttons_frame.pack(fill=tk.X, pady=10)

        # Botões de controle
        self.remove_btn = ttk.Button(self.move_buttons_frame, text="Remover Item", command=self.command.remove_item, bootstyle="primary")
        self.remove_btn.pack(side=tk.RIGHT, padx=5)

        self.move_up_btn = ttk.Button(self.move_buttons_frame, text="Mover para Cima", command=self.command.move_up, bootstyle="primary")
        self.move_up_btn.pack(side=tk.RIGHT, padx=5)

        self.move_down_btn = ttk.Button(self.move_buttons_frame, text="Mover para Baixo", command=self.command.move_down, bootstyle="primary")
        self.move_down_btn.pack(side=tk.RIGHT, padx=5)

        self.duplicate_btn = ttk.Button(self.move_buttons_frame, text="Duplicar Itens", command=self.command.duplicate_items, bootstyle="primary")
        self.duplicate_btn.pack(side=tk.RIGHT, padx=5)

        self.reset_btn = ttk.Button(self.move_buttons_frame, text="Resetar", command=self.command.reset_macro, bootstyle="primary")
        self.reset_btn.pack(side=tk.RIGHT, padx=5)

    def create_actions(self):
        """Cria area de acções."""
        # Frame para botões de ação
        self.action_buttons_frame = ttk.Frame(self.main_frame)
        self.action_buttons_frame.pack(side=tk.LEFT, pady=10)

        # Botões de ação
        self.add_key_btn = ttk.Button(self.action_buttons_frame, text="Clicar Tecla", command=self.action.add_key, bootstyle="secondary")
        self.add_key_btn.pack(fill=tk.X, padx=10, pady=5)

        self.press_key_btn = ttk.Button(self.action_buttons_frame, text="Pressionar Tecla", command=self.action.add_press_key, bootstyle="secondary")
        self.press_key_btn.pack(fill=tk.X, padx=10, pady=5)

        self.wait_btn = ttk.Button(self.action_buttons_frame, text="Adicionar Espera", command=self.action.add_wait, bootstyle="secondary")
        self.wait_btn.pack(fill=tk.X, padx=10, pady=5)

        self.add_click_btn = ttk.Button(self.action_buttons_frame, text="Adicionar Clique", command=self.action.add_click, bootstyle="secondary")
        self.add_click_btn.pack(fill=tk.X, padx=10, pady=5)

        self.move_mouse_btn = ttk.Button(self.action_buttons_frame, text="Mover Mouse", command=self.action.move_mouse, bootstyle="secondary")
        self.move_mouse_btn.pack(fill=tk.X, padx=10, pady=5)

        self.add_image_btn = ttk.Button(self.action_buttons_frame, text="Verificar Imagem", command=self.action.add_image_check, bootstyle="secondary")
        self.add_image_btn.pack(fill=tk.X, padx=10, pady=5)

        self.add_group_btn = ttk.Button(self.action_buttons_frame, text="Adicionar Grupo", command=lambda: self.action.add_group(), bootstyle="secondary")
        self.add_group_btn.pack(fill=tk.X, padx=10, pady=5)

    def update_listbox(self):
        """Atualiza a Listbox sem perder a posição do scroll."""
        # Salva a posição atual do scroll
        scroll_pos = self.actions_listbox.yview()

        # Atualiza os itens
        self.actions_listbox.delete(0, tk.END)
        for action, value in self.main.actions:
            match action:
                case "key":
                    self.actions_listbox.insert(tk.END, f"Pressionar: {value}")
                case "press_key":
                    key, press_time = value
                    self.actions_listbox.insert(tk.END, f"Pressionar {key} por {press_time} ms")
                case "wait":
                    self.actions_listbox.insert(tk.END, f"Esperar {value} ms")
                case "click":
                    self.actions_listbox.insert(tk.END, f"Clique {value}")
                case "move":
                    self.actions_listbox.insert(tk.END, f"Mover mouse para {value}")
                case "image_check":
                    self.actions_listbox.insert(tk.END, f"Verificar Imagem: {os.path.basename(value)}")
                case "group_start":
                    self.actions_listbox.insert(tk.END, f"📂 Grupo: {value}")
                case "group_end":
                    self.actions_listbox.insert(tk.END, f"📁 Fim do Grupo: {value}")

        # Restaura a posição do scroll
        self.actions_listbox.yview_moveto(scroll_pos[0])
    
    def on_start_drag(self, event):
        """Inicia o processo de arrastar pegando o índice do item clicado."""
        index = self.actions_listbox.nearest(event.y)
        self.drag_data["index"] = index

    def on_drag(self, event):
        """Detecta movimento do item na lista e troca as posições."""
        index = self.actions_listbox.nearest(event.y)
        if index != self.drag_data["index"]:  
            self.swap_items(self.drag_data["index"], index)
            self.drag_data["index"] = index

    def on_drop(self, event):
        """Finaliza o processo de arrastar e soltar."""
        self.drag_data["index"] = None

    def swap_items(self, old_index, new_index):
        """Troca a posição dos itens na Listbox e na lista de ações."""
        if old_index is not None and new_index is not None and old_index != new_index:
            # Troca na lista de ações principal
            self.main.actions.insert(new_index, self.main.actions.pop(old_index))

            # Atualiza a Listbox para refletir a nova ordem
            self.update_listbox()