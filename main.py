from gui import GuiRecorder
from tkinter import messagebox, simpledialog, filedialog, PhotoImage
from ttkbootstrap.constants import *
from pynput import mouse
from PIL import Image, ImageTk
import tkinter as tk
import ttkbootstrap as ttk
import pyautogui
import keyboard
import threading
import time
import json
import os
import cv2
import numpy as np

class MacroRecorder:
    def __init__(self, root):
        self.root = root
        self.is_running = False
        self.actions = []
        self.loop_var = tk.BooleanVar(value=False)
        self.gui = GuiRecorder(root, self)
        self.current_index = 0

    def toggle_macro(self):
        """Alterna entre iniciar e parar o macro."""
        if not self.is_running:
            self.start_macro()
        else:
            self.stop_macro()

    def start_macro(self):
        """Inicia o macro a partir da ação selecionada na Listbox."""
        if not self.actions:
            return

        selected_indices = self.gui.actions_listbox.curselection()
        self.current_index = min(selected_indices) if selected_indices else 0

        self.is_running = True
        self.gui.toggle_btn.config(image=self.gui.stop_icon)  # Muda o ícone para Stop
        self.execute_next_action()

    def stop_macro(self):
        """Para a execução do macro."""
        self.is_running = False
        self.gui.toggle_btn.config(image=self.gui.play_icon)  # Muda o ícone para Play

    def find_image_with_opencv(self, template_path, screenshot=None, threshold=0.8):
        """
        Encontra uma imagem na tela usando OpenCV.
        :param template_path: Caminho da imagem de referência.
        :param screenshot: Captura de tela (opcional).
        :param threshold: Limiar de correspondência (0 a 1).
        :return: Coordenadas da imagem encontrada ou None.
        """
        try:
            # Normaliza o caminho do arquivo
            template_path = os.path.normpath(template_path)

            # Verifica se o arquivo existe
            if not os.path.exists(template_path):
                raise FileNotFoundError(f"Arquivo não encontrado: {template_path}")

            # Carrega a imagem de referência
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            if template is None:
                raise ValueError(f"Não foi possível carregar a imagem: {template_path}")

            # Captura a tela se não for fornecida
            if screenshot is None:
                screenshot = pyautogui.screenshot()
                screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

            # Realiza a correspondência de template
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            # Verifica se a correspondência é maior que o limiar
            if max_val >= threshold:
                return max_loc  # Retorna a posição da imagem encontrada
            return None
        except Exception as e:
            print(f"Erro ao buscar imagem com OpenCV: {e}")
            return None

    def run_macro(self):
        """Executa as ações do macro com suporte a pausa, retomada e início de posição selecionada."""
        if not self.actions:
            return

        selected_indices = self.gui.actions_listbox.curselection()
        start_index = min(selected_indices) if selected_indices else 0

        self.is_running = True
        self.current_index = start_index
        self.execute_next_action()

    def execute_next_action(self):
        """Executa a ação atual e avança para a próxima, garantindo que a UI continue responsiva."""
        if not self.is_running:
            self.stop_macro()
            return

        if self.current_index >= len(self.actions):
            if self.loop_var.get():
                self.current_index = 0
            else:
                self.stop_macro()
                return

        action, value = self.actions[self.current_index]

        self.gui.actions_listbox.selection_clear(0, tk.END)
        self.gui.actions_listbox.select_set(self.current_index)
        self.gui.actions_listbox.see(self.current_index)

        should_skip_next = False

        if action == "key":
            keys = value.split('+')
            pyautogui.hotkey(*keys)

        elif action == "press_key":
            key, press_time = value
            start_time = time.time()
            while time.time() - start_time < press_time / 1000:
                pyautogui.press(key)
                time.sleep(0.05)

        elif action == "wait":
            self.current_index += 1
            self.root.after(int(value), self.execute_next_action)
            return

        elif action == "click":
            pyautogui.click(button=value)

        elif action == "move":
            pyautogui.moveTo(*value)

        elif action == "image_check":
            image_path = os.path.normpath(value)
            
            if os.path.exists(image_path) and os.access(image_path, os.R_OK):
                found = False
                
                for _ in range(3):  # Tenta até 3 vezes
                    location = self.find_image_with_opencv(image_path, threshold=0.9) if hasattr(self, "find_image_with_opencv") else None
                    if location:
                        found = True
                        time.sleep(0.5)  # Pequena espera antes de clicar
                        pyautogui.moveTo(location[0] + 10, location[1] + 10)
                        break  # Sai do loop se encontrar a imagem
                    
                    time.sleep(0.2)  # Aguarda 200ms antes da próxima tentativa
                
                if not found:
                    should_skip_next = True  # Se não encontrou, pula a próxima ação/grupo

        self.current_index += 1

        # Se o `image_check` falhou, pula a próxima linha ou grupo inteiro
        if should_skip_next and self.current_index < len(self.actions):
            next_action, next_value = self.actions[self.current_index]

            if next_action == "group_start":
                # Pular o grupo inteiro
                group_name = next_value
                while self.current_index < len(self.actions) and self.actions[self.current_index] != ["group_end", group_name]:
                    self.current_index += 1
                self.current_index += 1  # Pula também o `group_end`
            else:
                self.current_index += 1  # Apenas pula a próxima linha se não for um grupo

        self.root.after(200, self.execute_next_action)  # Agenda a próxima ação


if __name__ == "__main__":
    root = tk.Tk()
    app = MacroRecorder(root)
    root.mainloop()
