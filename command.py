import tkinter as tk
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

class CommandRecorder:
    def __init__(self, root, gui, main):
        self.root = root
        self.main = main
        self.gui = gui

    def save_macros(self):
        """Salva a lista de ações em um arquivo."""
        if not self.main.actions:
            messagebox.showwarning("Aviso", "Nenhuma ação para salvar!")
            return

        file_path = tk.filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    json.dump(self.main.actions, file)
                messagebox.showinfo("Sucesso", "Macros salvos com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar macros: {e}")

    def load_macros(self):
        """Carrega a lista de ações de um arquivo."""
        file_path = tk.filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    self.main.actions = json.load(file)
                self.gui.update_listbox()  # Atualiza a Listbox com as ações carregadas
                messagebox.showinfo("Sucesso", "Macros carregados com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar macros: {e}")

    #list_commands
    def remove_item(self):
        """Remove itens selecionados, considerando grupos."""
        selected_indices = list(self.gui.actions_listbox.curselection())[::-1]
        
        for index in selected_indices:
            if 0 <= index < len(self.main.actions):
                if self.main.actions[index][0] == "group_start":
                    # Remover tudo até encontrar "group_end"
                    group_name = self.main.actions[index][1]
                    while index < len(self.main.actions) and self.main.actions[index] != ["group_end", group_name]:
                        self.main.actions.pop(index)
                    self.main.actions.pop(index)  # Remove também "group_end"
                else:
                    self.main.actions.pop(index)
        self.gui.update_listbox()
    
    def reset_macro(self):
        """Reseta todos os dados do macro."""
        try:
            # Limpa a lista de ações
            self.main.actions.clear()

            # Limpa a lista de ações exibida na interface
            self.gui.actions_listbox.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao resetar o macro: {e}")

    def move_up(self):
        """Move ações ou grupos selecionados para cima."""
        selected_indices = list(self.gui.actions_listbox.curselection())
        if not selected_indices or selected_indices[0] == 0:
            return
        
        for index in selected_indices:
            if 0 < index < len(self.main.actions):
                self.main.actions[index - 1], self.main.actions[index] = self.main.actions[index], self.main.actions[index - 1]
        
        self.gui.update_listbox()

        # Atualiza a seleção após mover
        self.gui.actions_listbox.selection_clear(0, tk.END)
        for index in selected_indices:
            self.gui.actions_listbox.select_set(index - 1)

    def move_down(self):
        """Move ações ou grupos selecionados para baixo."""
        selected_indices = list(self.gui.actions_listbox.curselection())[::-1]
        if not selected_indices or selected_indices[-1] == len(self.main.actions) - 1:
            return
        
        for index in selected_indices:
            if index < len(self.main.actions) - 1:
                self.main.actions[index + 1], self.main.actions[index] = self.main.actions[index], self.main.actions[index + 1]
        
        self.gui.update_listbox()

        # Atualiza a seleção após mover
        self.gui.actions_listbox.selection_clear(0, tk.END)
        for index in selected_indices:
            self.gui.actions_listbox.select_set(index + 1)

    def duplicate_items(self):
        """Duplica os itens selecionados e adiciona ao final da lista."""
        selected_indices = list(self.gui.actions_listbox.curselection())
        if not selected_indices:
            return

        new_items = []
        i = 0

        while i < len(selected_indices):
            index = selected_indices[i]
            action = self.main.actions[index]

            if action[0] == "group_start":
                # Encontrar o índice correspondente do "group_end"
                group_name = action[1]
                end_index = index + 1

                while end_index < len(self.main.actions) and self.main.actions[end_index] != ["group_end", group_name]:
                    end_index += 1

                if end_index < len(self.main.actions):
                    end_index += 1  # Incluir o "group_end" na cópia

                new_items.extend(self.main.actions[index:end_index])  # Copia o grupo inteiro
                i = selected_indices.index(end_index - 1) + 1 if end_index - 1 in selected_indices else i + 1
            else:
                new_items.append(action)
                i += 1

        self.main.actions.extend(new_items)
        self.gui.update_listbox()
