import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from pynput import mouse
import pyautogui
import keyboard
import threading
import time
from tkinter import PhotoImage
import json
import os
import cv2
import numpy as np

class MacroRecorder:
    def __init__(self, root):
        self.root = root
        self.root.title("Macro Recorder")
        self.root.geometry("1000x600")
        self.root.configure(bg="#f0f0f0")

        self.is_running = False  # Estado do macro
        self.actions = []  # Lista de ações

        # Cria a barra de menu
        self.create_menu()

        # Frame principal
        self.main_frame = tk.Frame(root, bg="#f0f0f0", padx=20, pady=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        self.title_label = tk.Label(self.main_frame, text="Macro Recorder", font=("Helvetica", 16, "bold"), bg="#f0f0f0", fg="#333333")
        self.title_label.pack(pady=10)

        # Frame para os botões de controle de macro no topo
        self.control_buttons_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.control_buttons_frame.pack(fill=tk.X, pady=10)

        # Botões de controle com ícones de Play e Stop
        button_style = {
            "bg": "#0078d7",
            "fg": "white",
            "font": ("Helvetica", 10),
            "border": 0,
            "activebackground": "#005bb5",
            "activeforeground": "white",
            "padx": 10,
            "pady": 5,
        }

        button_main_style = {
            "bg": "#f0f0f0",
            "border": 0,
        }

        # Carregando ícones para Play e Stop
        self.play_icon = PhotoImage(file="play_icon.png").subsample(16, 16)
        self.stop_icon = PhotoImage(file="stop_icon.png").subsample(16, 16)

        # Botão único para Play/Stop
        self.toggle_btn = tk.Button(self.control_buttons_frame, image=self.play_icon, command=self.toggle_macro, **button_main_style)
        self.toggle_btn.pack(side=tk.LEFT, padx=5, expand=True)

        self.loop_var = tk.BooleanVar(value=False)  # Variável do checkbox
        self.loop_checkbox = tk.Checkbutton(self.control_buttons_frame, text="Loo Infinito", variable=self.loop_var)
        self.loop_checkbox.pack()

        # Frame para botões de ação
        self.action_buttons_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.action_buttons_frame.pack(fill=tk.X, pady=10)

        # Botões de ação
        self.add_key_btn = tk.Button(self.action_buttons_frame, text="Clicar Tecla", command=self.add_key, **button_style)
        self.add_key_btn.pack(side=tk.LEFT, padx=5, expand=True)

        self.press_key_btn = tk.Button(self.action_buttons_frame, text="Pressionar Tecla", command=self.add_press_key, **button_style)
        self.press_key_btn.pack(side=tk.LEFT, padx=5, expand=True)

        self.wait_btn = tk.Button(self.action_buttons_frame, text="Adicionar Espera", command=self.add_wait, **button_style)
        self.wait_btn.pack(side=tk.LEFT, padx=5, expand=True)

        self.add_click_btn = tk.Button(self.action_buttons_frame, text="Adicionar Clique", command=self.add_click, **button_style)
        self.add_click_btn.pack(side=tk.LEFT, padx=5, expand=True)

        self.move_mouse_btn = tk.Button(self.action_buttons_frame, text="Mover Mouse", command=self.move_mouse, **button_style)
        self.move_mouse_btn.pack(side=tk.LEFT, padx=5, expand=True)

        self.add_image_btn = tk.Button(self.action_buttons_frame, text="Verificar Imagem", command=self.add_image_check, **button_style)
        self.add_image_btn.pack(side=tk.LEFT, padx=5, expand=True)

        # Novos botões para grupos
        self.add_group_btn = tk.Button(self.action_buttons_frame, text="Adicionar Grupo", command=lambda: self.add_group(), **button_style)
        self.add_group_btn.pack(side=tk.LEFT, padx=5, expand=True)

        # Lista de ações
        self.actions_listbox = tk.Listbox(self.main_frame, height=12, width=60, font=("Helvetica", 10), bg="white", fg="black", selectmode=tk.EXTENDED)
        self.actions_listbox.pack(fill=tk.BOTH, pady=10, expand=True)

        # Frame para botões de controle de movimentação
        self.move_buttons_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.move_buttons_frame.pack(fill=tk.X, pady=10)

        # Botões de controle
        self.remove_btn = tk.Button(self.move_buttons_frame, text="Remover Item", command=self.remove_item, **button_style)
        self.remove_btn.pack(side=tk.LEFT, padx=5, expand=True)

        self.move_up_btn = tk.Button(self.move_buttons_frame, text="Mover para Cima", command=self.move_up, **button_style)
        self.move_up_btn.pack(side=tk.LEFT, padx=5, expand=True)

        self.move_down_btn = tk.Button(self.move_buttons_frame, text="Mover para Baixo", command=self.move_down, **button_style)
        self.move_down_btn.pack(side=tk.LEFT, padx=5, expand=True)

        self.duplicate_btn = tk.Button(self.move_buttons_frame, text="Duplicar Itens", command=self.duplicate_items, **button_style)
        self.duplicate_btn.pack(side=tk.LEFT, padx=5, expand=True)

        self.reset_btn = tk.Button(self.move_buttons_frame, text="Resetar", command=self.reset_macro, **button_style)
        self.reset_btn.pack(side=tk.LEFT, padx=5, expand=True)


    def create_menu(self):
        """Cria a barra de menu com as opções Save e Load."""
        menubar = tk.Menu(self.root)

        # Menu "Arquivo"
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Salvar Macros", command=self.save_macros)
        file_menu.add_command(label="Carregar Macros", command=self.load_macros)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)

        # Adiciona o menu "Arquivo" à barra de menus
        menubar.add_cascade(label="Arquivo", menu=file_menu)

        # Configura a barra de menus na janela principal
        self.root.config(menu=menubar)

    def save_macros(self):
        """Salva a lista de ações em um arquivo."""
        if not self.actions:
            messagebox.showwarning("Aviso", "Nenhuma ação para salvar!")
            return

        file_path = tk.filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    json.dump(self.actions, file)
                messagebox.showinfo("Sucesso", "Macros salvos com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar macros: {e}")

    def load_macros(self):
        """Carrega a lista de ações de um arquivo."""
        file_path = tk.filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    self.actions = json.load(file)
                self.update_listbox()  # Atualiza a Listbox com as ações carregadas
                messagebox.showinfo("Sucesso", "Macros carregados com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar macros: {e}")

    def add_key(self):
        """Captura combinações de teclas, agora com a opção de pressionar a tecla por um tempo."""
        # Mudar o texto do botão para "Gravando..." e ajustar as cores
        self.add_key_btn.config(text="Gravando...", state=tk.DISABLED, bg="#f44336", fg="white")

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
                self.actions.append(("key", hotkey))
                self.actions_listbox.insert(tk.END, f"Pressionar: {hotkey}")
            
            # Depois de capturar as teclas, retorna o texto do botão e habilita novamente, com as cores padrão
            self.add_key_btn.config(text="Clicar Tecla", state=tk.NORMAL, bg="#0078d7", fg="white")
        threading.Thread(target=capture_keys, daemon=True).start()

    def add_press_key(self):
        """Captura a tecla a ser pressionada e por quanto tempo em milissegundos."""
        press_time = simpledialog.askinteger("Tempo de Pressão", "Digite o tempo em milissegundos que a tecla ficará pressionada:")

        if press_time is not None:
            def capture_keys():
                recorded_keys = []  # Lista para manter a ordem
                pressed_keys = set()  # Controla teclas pressionadas
                self.press_key_btn.config(text="Gravando...", state=tk.DISABLED, bg="#f44336", fg="white")

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
                    self.actions.append(("press_key", (hotkey, press_time)))
                    self.actions_listbox.insert(tk.END, f"Pressionar {hotkey} por {press_time} ms")
                
                # Depois de capturar as teclas, retorna o texto do botão e habilita novamente, com as cores padrão
                self.press_key_btn.config(text="Pressionar Tecla", state=tk.NORMAL, bg="#0078d7", fg="white")
            threading.Thread(target=capture_keys, daemon=True).start()

    def add_wait(self):
        """Adiciona um tempo de espera em milissegundos."""
        wait_time = simpledialog.askinteger("Adicionar Espera", "Digite o tempo em milissegundos:")
        if wait_time:
            self.actions.append(("wait", wait_time))
            self.actions_listbox.insert(tk.END, f"Esperar {wait_time} ms")

    def add_click(self):
        """Adiciona um clique do mouse."""
        click_type = simpledialog.askstring("Adicionar Clique", "Digite 'left' para clique esquerdo ou 'right' para direito:")
        if click_type in ["left", "right"]:
            self.actions.append(("click", click_type))
            self.actions_listbox.insert(tk.END, f"Clique {click_type}")
    
    def move_mouse(self):
        """Aguarda um clique do usuário e captura a posição do mouse."""
        self.move_mouse_btn.config(text="Clique para gravar", state=tk.DISABLED, bg="#f44336", fg="white")

        def on_click(x, y, button, pressed):
            if pressed and button == mouse.Button.left:  # Captura apenas o clique esquerdo
                self.actions.append(("move", (x, y)))
                self.actions_listbox.insert(tk.END, f"Mover mouse para ({x}, {y})")
                self.move_mouse_btn.config(text="Mover Mouse", state=tk.NORMAL, bg="#0078d7", fg="white")
                listener.stop()  # Para o listener após capturar o clique

        # Executa o listener em uma thread separada
        listener = mouse.Listener(on_click=on_click)
        listener.start()

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

        selected_indices = self.actions_listbox.curselection()
        self.current_index = min(selected_indices) if selected_indices else 0

        self.is_running = True
        self.toggle_btn.config(image=self.stop_icon)  # Muda o ícone para Stop
        self.execute_next_action()

    def stop_macro(self):
        """Para a execução do macro."""
        self.is_running = False
        self.toggle_btn.config(image=self.play_icon)  # Muda o ícone para Play

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

        self.actions.append(("image_check", image_path))
        self.actions_listbox.insert(tk.END, f"Verificar Imagem: {os.path.basename(image_path)}")

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

        selected_indices = self.actions_listbox.curselection()
        start_index = min(selected_indices) if selected_indices else 0

        self.is_running = True
        self.current_index = start_index  # Armazena a posição atual para retomar corretamente

        self.execute_next_action()

    def execute_next_action(self):
        """Executa a ação atual e avança para a próxima, com suporte para pular ações após um image_check falho e loop infinito."""
        if not self.is_running:
            self.stop_macro()
            return

        # Se atingiu o fim da lista
        if self.current_index >= len(self.actions):
            if self.loop_var.get():  # Se o loop infinito estiver ativado
                self.current_index = 0  # Reinicia do começo
            else:
                self.stop_macro()
                return

        action, value = self.actions[self.current_index]

        # Atualiza visualmente a ação em execução
        self.actions_listbox.selection_clear(0, tk.END)
        self.actions_listbox.select_set(self.current_index)
        self.actions_listbox.see(self.current_index)

        should_skip_next = False

        # Executa a ação correspondente
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
            time.sleep(value / 1000)

        elif action == "click":
            pyautogui.click(button=value)

        elif action == "move":
            pyautogui.moveTo(*value)

        elif action == "image_check":
            image_path = os.path.normpath(value)
            if os.path.exists(image_path) and os.access(image_path, os.R_OK):
                location = self.find_image_with_opencv(image_path, threshold=0.8) if hasattr(self, "find_image_with_opencv") else None
                if location:
                    time.sleep(0.5)
                    pyautogui.click(location[0] + 10, location[1] + 10)
                else:
                    should_skip_next = True  # Ativa a flag para pular a próxima ação/grupo

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

    def remove_item(self):
        """Remove itens selecionados, considerando grupos."""
        selected_indices = list(self.actions_listbox.curselection())[::-1]
        
        for index in selected_indices:
            if 0 <= index < len(self.actions):
                if self.actions[index][0] == "group_start":
                    # Remover tudo até encontrar "group_end"
                    group_name = self.actions[index][1]
                    while index < len(self.actions) and self.actions[index] != ["group_end", group_name]:
                        self.actions.pop(index)
                    self.actions.pop(index)  # Remove também "group_end"
                else:
                    self.actions.pop(index)
        self.update_listbox()
    
    def reset_macro(self):
        """Reseta todos os dados do macro."""
        try:
            # Limpa a lista de ações
            self.actions.clear()

            # Limpa a lista de ações exibida na interface
            self.actions_listbox.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao resetar o macro: {e}")

    def move_up(self):
        """Move ações ou grupos selecionados para cima."""
        selected_indices = list(self.actions_listbox.curselection())
        if not selected_indices or selected_indices[0] == 0:
            return
        
        for index in selected_indices:
            if 0 < index < len(self.actions):
                self.actions[index - 1], self.actions[index] = self.actions[index], self.actions[index - 1]
        
        self.update_listbox()

        # Atualiza a seleção após mover
        self.actions_listbox.selection_clear(0, tk.END)
        for index in selected_indices:
            self.actions_listbox.select_set(index - 1)

    def move_down(self):
        """Move ações ou grupos selecionados para baixo."""
        selected_indices = list(self.actions_listbox.curselection())[::-1]
        if not selected_indices or selected_indices[-1] == len(self.actions) - 1:
            return
        
        for index in selected_indices:
            if index < len(self.actions) - 1:
                self.actions[index + 1], self.actions[index] = self.actions[index], self.actions[index + 1]
        
        self.update_listbox()

        # Atualiza a seleção após mover
        self.actions_listbox.selection_clear(0, tk.END)
        for index in selected_indices:
            self.actions_listbox.select_set(index + 1)

    def duplicate_items(self):
        """Duplica os itens selecionados e adiciona ao final da lista."""
        selected_indices = list(self.actions_listbox.curselection())
        if not selected_indices:
            return

        new_items = []
        i = 0

        while i < len(selected_indices):
            index = selected_indices[i]
            action = self.actions[index]

            if action[0] == "group_start":
                # Encontrar o índice correspondente do "group_end"
                group_name = action[1]
                end_index = index + 1

                while end_index < len(self.actions) and self.actions[end_index] != ["group_end", group_name]:
                    end_index += 1

                if end_index < len(self.actions):
                    end_index += 1  # Incluir o "group_end" na cópia

                new_items.extend(self.actions[index:end_index])  # Copia o grupo inteiro
                i = selected_indices.index(end_index - 1) + 1 if end_index - 1 in selected_indices else i + 1
            else:
                new_items.append(action)
                i += 1

        self.actions.extend(new_items)
        self.update_listbox()

    def add_group(self):
        """Adiciona um novo grupo em torno dos itens selecionados ou ao final da lista."""
        group_name = simpledialog.askstring("Nome do Grupo", "Digite o nome do grupo:")
        if not group_name:
            return  # Se o usuário cancelar ou não digitar nada, não faz nada.

        selected_indices = list(self.actions_listbox.curselection())

        if selected_indices:
            # Se houver itens selecionados, encapsula em um grupo
            start_index = selected_indices[0]
            end_index = selected_indices[-1] + 1  # Ajusta para incluir o último item

            self.actions.insert(start_index, ["group_start", group_name])
            self.actions.insert(end_index + 1, ["group_end", group_name])
        else:
            # Caso contrário, adiciona um grupo vazio no final
            self.actions.append(["group_start", group_name])
            self.actions.append(["group_end", group_name])

        self.update_listbox()

    def update_listbox(self):
        """Atualiza a lista de ações na interface, garantindo que os dados estejam sincronizados."""
        self.actions_listbox.delete(0, tk.END)  # Limpa a Listbox

        for action, value in self.actions:
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
                    self.actions_listbox.insert(tk.END, f"📂 Grupo: {value}")  # Ícone para representar grupo
                case "group_end":
                    self.actions_listbox.insert(tk.END, f"📁 Fim do Grupo: {value}")  # Ícone para representar fechamento do grupo


if __name__ == "__main__":
    root = tk.Tk()
    app = MacroRecorder(root)
    root.mainloop()
