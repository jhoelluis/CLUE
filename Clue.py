import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random
from PIL import Image, ImageTk

class ClueGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Clue - Juego de Misterio")
        self.master.geometry("1200x800")
        self.master.configure(bg="#F0F0F0")  # Light gray background

        self.players = ["Rojo", "Morado", "Verde", "Azul", "Blanco", "Amarillo"]
        self.suspects = ["Luis", "Pablo", "Jhoel", "White", "Dennis", "Jean"]
        self.weapons = ["Cuchillo", "Candelabro", "Revolver", "Cuerda", "Tuberia", "Llave Inglesa"]
        self.rooms = ["Biblioteca", "Cocina", "Salon de Baile", "Estudio", "Sala", "Comedor", "Invernadero", "Salon de Billar", "Vestibulo"]

        self.num_players = 0
        self.current_player = 0
        self.player_positions = {}
        self.player_cards = []

        self.prepositions = ["con", "en", "por", "mediante", "utilizando"]
        self.knowledge_base = {
            "suspects": {},
            "weapons": {},
            "rooms": {}
        }

        self.load_images()
        self.create_styles()
        self.create_start_screen()

    def load_images(self):
        self.images = {}
        for item in self.suspects + self.weapons + self.rooms:
            try:
                image = Image.open(f"images/{item.lower().replace(' ', '_')}.png")
                image = image.resize((50, 50), Image.LANCZOS)
                self.images[item] = ImageTk.PhotoImage(image)
            except FileNotFoundError:
                print(f"Image not found for {item}")

    def create_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=("Arial", 14), background="#F0F0F0")
        style.configure("TButton", font=("Arial", 12), padding=5)
        style.configure("TFrame", background="#F0F0F0")
        style.configure("Header.TLabel", font=("Arial", 28, "bold"), background="#F0F0F0")
        style.configure("Action.TButton", font=("Arial", 12, "bold"), padding=10)

    def create_start_screen(self):
        self.start_frame = ttk.Frame(self.master, style="TFrame")
        self.start_frame.pack(expand=True, fill="both")

        ttk.Label(self.start_frame, text="Bienvenido a Clue", style="Header.TLabel").pack(pady=20)
        ttk.Label(self.start_frame, text="Selecciona el número de jugadores:").pack()

        self.player_var = tk.StringVar(value="3")
        player_combo = ttk.Combobox(self.start_frame, textvariable=self.player_var, values=["3", "4", "5", "6"], font=("Arial", 12), width=5)
        player_combo.pack(pady=10)

        ttk.Button(self.start_frame, text="Comenzar Juego", command=self.start_game, style="TButton").pack(pady=20)
        ttk.Button(self.start_frame, text="Reglas del Juego", command=self.show_rules, style="TButton").pack()

    def show_rules(self):
        rules = """
        Reglas del Juego Clue:

        1. Objetivo: Descubrir quién cometió el asesinato, con qué arma y en qué habitación.
        2. Al inicio, se seleccionan al azar una carta de cada categoría (sospechoso, arma, habitación) como solución.
        3. El resto de las cartas se reparten entre los jugadores.
        4. En tu turno:
           - Mueve tu ficha a una habitación.
           - Si estás en una habitación, puedes hacer una sugerencia.
           - Los otros jugadores deben mostrar una carta que refute tu sugerencia si pueden.
        5. Cuando creas saber la solución, haz una acusación.
        6. Si tu acusación es correcta, ¡ganas! Si no, quedas eliminado.
        7. El juego continúa hasta que alguien haga la acusación correcta o todos sean eliminados.

        ¡Buena suerte, detective!
        """
        messagebox.showinfo("Reglas del Juego", rules)

    def start_game(self):
        self.num_players = int(self.player_var.get())
        self.start_frame.destroy()
        
        self.solution = self.generate_solution()
        self.player_cards = self.deal_cards()
        self.initialize_player_positions()
        self.initialize_knowledge_base()

        self.create_gui()
        self.print_solution()
        self.print_knowledge_base()

    def generate_solution(self):
        return {
            "suspect": random.choice(self.suspects),
            "weapon": random.choice(self.weapons),
            "room": random.choice(self.rooms)
        }

    def deal_cards(self):
        all_cards = self.suspects + self.weapons + self.rooms
        all_cards = [card for card in all_cards if card not in self.solution.values()]
        random.shuffle(all_cards)
        
        player_cards = [[] for _ in range(self.num_players)]
        for i, card in enumerate(all_cards):
            player_cards[i % self.num_players].append(card)
        
        return player_cards

    def initialize_player_positions(self):
        center_x, center_y = 12, 12  # Center of the board
        radius = 3  # Distance from center
        angle_step = 2 * 3.14159 / self.num_players

        for i in range(self.num_players):
            angle = i * angle_step
            x = center_x + radius * 3.14159 * (angle - 1.5)
            y = center_y + radius * 3.14159 * (angle - 1.5)
            self.player_positions[i] = (x, y)

    def initialize_knowledge_base(self):
        for suspect in self.suspects:
            self.knowledge_base["suspects"][suspect] = "Desconocido"
        for weapon in self.weapons:
            self.knowledge_base["weapons"][weapon] = "Desconocido"
        for room in self.rooms:
            self.knowledge_base["rooms"][room] = "Desconocido"

    def create_gui(self):
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(expand=1, fill="both")

        self.game_frame = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(self.game_frame, text="Tablero")

        self.notes_frame = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(self.notes_frame, text="Notas")

        self.create_game_board()
        self.create_player_info()
        self.create_action_buttons()
        self.create_notes_section()
        self.create_card_display()

    def create_game_board(self):
        self.board_canvas = tk.Canvas(self.game_frame, width=800, height=800, bg="#E6E6FA")  # Light lavender background
        self.board_canvas.pack(side=tk.LEFT, padx=10, pady=10)

        self.draw_rooms()
        self.draw_hallways()
        self.draw_player_tokens()

    def draw_rooms(self):
        room_coords = {
            "Estudio": (0, 0, 6, 4),
            "Vestibulo": (9, 0, 15, 6),
            "Biblioteca": (18, 0, 24, 5),
            "Sala": (0, 6, 7, 11),
            "Salon de Billar": (18, 7, 24, 12),
            "Invernadero": (0, 19, 5, 24),
            "Comedor": (9, 18, 15, 24),
            "Salon de Baile": (17, 19, 24, 24),
            "Cocina": (0, 13, 6, 17)
        }

        colors = ["#FFE4E1", "#E0FFFF", "#F0FFF0", "#FFF0F5", "#F0F8FF", "#FFF5E6", "#F5F5DC", "#F0E68C", "#E6E6FA"]
        for i, (room, coords) in enumerate(room_coords.items()):
            x1, y1, x2, y2 = coords
            self.board_canvas.create_rectangle(x1*30, y1*30, x2*30, y2*30, fill=colors[i], outline="black")
            self.board_canvas.create_text((x1+x2)*15, (y1+y2)*15, text=room, font=("Arial", 8, "bold"))
            if room in self.images:
                self.board_canvas.create_image((x1+x2)*15, (y1+y2)*15 + 30, image=self.images[room])


    def draw_hallways(self):
        for x in range(25):
            for y in range(25):
                if (6 <= x <= 18 and y in [5, 18]) or (x in [7, 17] and 6 <= y <= 17):
                    self.board_canvas.create_rectangle(x*30, y*30, (x+1)*30, (y+1)*30, fill="#F5F5F5", outline="black")

    def draw_player_tokens(self):
        colors = ["red", "purple", "green", "blue", "white", "yellow"]
        for i, (x, y) in self.player_positions.items():
            token = self.board_canvas.create_oval(x*30-10, y*30-10, x*30+10, y*30+10, fill=colors[i], tags=f"player_{i}")
            self.board_canvas.tag_bind(token, '<Button-1>', lambda e, p=i: self.show_player_info(p))

    def show_player_info(self, player):
        info = f"Jugador: {self.players[player]}\nPosición: {self.player_positions[player]}"
        messagebox.showinfo(f"Información del Jugador {player+1}", info)

    def create_player_info(self):
        self.player_frame = ttk.Frame(self.game_frame, style="TFrame")
        self.player_frame.pack(side=tk.TOP, pady=10)

        ttk.Label(self.player_frame, text="Turno del Jugador:", font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        self.player_label = ttk.Label(self.player_frame, text=f"{self.players[0]}", font=("Arial", 14, "bold"))
        self.player_label.pack(side=tk.LEFT)

    def create_action_buttons(self):
        self.button_frame = ttk.Frame(self.game_frame, style="TFrame")
        self.button_frame.pack(side=tk.TOP, pady=10)

        ttk.Button(self.button_frame, text="Mover", command=self.move_player, style="Action.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Hacer Sugerencia", command=self.make_suggestion, style="Action.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Hacer Acusación", command=self.make_accusation, style="Action.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Terminar Turno", command=self.end_turn, style="Action.TButton").pack(side=tk.LEFT, padx=5)

    def create_notes_section(self):
        self.notes_text = tk.Text(self.notes_frame, height=30, width=40, font=("Arial", 12))
        self.notes_text.pack(padx=10, pady=10, side=tk.LEFT)
        self.notes_text.insert(tk.END, "Tus notas del juego:\n\n")

        self.checklist_frame = ttk.Frame(self.notes_frame, style="TFrame")
        self.checklist_frame.pack(padx=10, pady=10, side=tk.LEFT, fill=tk.Y)
        
        ttk.Label(self.checklist_frame, text="Lista de Verificación", font=("Arial", 14, "bold")).pack()
        
        self.checkbuttons = {}
        for category, items in [("Sospechosos", self.suspects), ("Armas", self.weapons), ("Habitaciones", self.rooms)]:
            ttk.Label(self.checklist_frame, text=category, font=("Arial", 12, "bold")).pack(pady=(10,0))
            for item in items:
                var = tk.BooleanVar()
                cb = ttk.Checkbutton(self.checklist_frame, text=item, variable=var, style="TCheckbutton")
                cb.pack(anchor=tk.W)
                self.checkbuttons[item] = var

    def create_card_display(self):
        self.card_frame = ttk.Frame(self.game_frame, style="TFrame")
        self.card_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

        ttk.Label(self.card_frame, text="Tus Cartas", font=("Arial", 14, "bold")).pack()

        self.card_listbox = tk.Listbox(self.card_frame, height=10, width=30, font=("Arial", 12))
        self.card_listbox.pack(pady=10)
        self.card_listbox.bind('<<ListboxSelect>>', self.show_card_image)

        self.card_image_label = ttk.Label(self.card_frame)
        self.card_image_label.pack(pady=10)

        self.update_card_display()

    def show_card_image(self, event):
        selection = event.widget.curselection()
        if selection:
            card = event.widget.get(selection[0])
            if card in self.images:
                self.card_image_label.config(image=self.images[card])
            else:
                self.card_image_label.config(image='')

    def move_player(self):
        room = simpledialog.askstring("Mover", "¿A qué habitación quieres moverte?")
        if room in self.rooms:
            self.player_positions[self.current_player] = self.get_room_center(room)
            self.update_player_position(self.current_player)
            self.ask_for_suggestion(room)
        else:
            messagebox.showerror("Error", "Habitación no válida")

    def get_room_center(self, room):
        room_coords = {
            "Estudio": (3, 2),
            "Vestibulo": (12, 3),
            "Biblioteca": (21, 2),
            "Sala": (3, 8),
            "Salon de Billar": (21, 9),
            "Invernadero": (2, 21),
            "Comedor": (12, 21),
            "Salon de Baile": (20, 21),
            "Cocina": (3, 15)
        }
        return room_coords.get(room, (0, 0))

    def update_player_position(self, player):
        x, y = self.player_positions[player]
        self.board_canvas.coords(f"player_{player}", x*30-10, y*30-10, x*30+10, y*30+10)

    def ask_for_suggestion(self, room):
        response = messagebox.askyesno("Sugerencia", f"Has entrado en {room}. ¿Quieres hacer una sugerencia?")
        if response:
            self.make_suggestion(room)

    def make_suggestion(self, room=None):
        if not room:
            room = simpledialog.askstring("Sugerencia", "¿En qué habitación sugieres?")
        suspect = simpledialog.askstring("Sugerencia", "¿Qué sospechoso sugieres?")
        weapon = simpledialog.askstring("Sugerencia", "¿Qué arma sugieres?")
        
        if suspect and weapon and room:
            messagebox.showinfo("Sugerencia", f"Sugieres que {suspect} cometió el crimen en {room} con {weapon}")
            self.check_suggestion(suspect, weapon, room)
        else:
            messagebox.showerror("Error", "Por favor, completa todos los campos para hacer una sugerencia.")

    def check_suggestion(self, suspect, weapon, room):
        for i in range(1, self.num_players):
            player = (self.current_player + i) % self.num_players
            matching_cards = [card for card in self.player_cards[player] if card in [suspect, weapon, room]]
            if matching_cards:
                card_to_show = random.choice(matching_cards)
                messagebox.showinfo("Sugerencia Refutada", f"El Jugador {self.players[player]} te muestra la carta: {card_to_show}")
                
                # Actualizar la base de conocimiento
                if card_to_show in self.suspects:
                    self.knowledge_base["suspects"][card_to_show] = "No es el asesino"
                elif card_to_show in self.weapons:
                    self.knowledge_base["weapons"][card_to_show] = "No es el arma"
                elif card_to_show in self.rooms:
                    self.knowledge_base["rooms"][card_to_show] = "No es la habitación del crimen"
                
                self.print_knowledge_base()
                return
        messagebox.showinfo("Sugerencia No Refutada", "Nadie pudo refutar tu sugerencia.")
        self.print_knowledge_base()

    def make_accusation(self):
        suspect = simpledialog.askstring("Acusación", "¿Quién es el asesino?")
        weapon = simpledialog.askstring("Acusación", "¿Qué arma se usó?")
        room = simpledialog.askstring("Acusación", "¿Dónde ocurrió el crimen?")
        
        if suspect and weapon and room:
            if (suspect == self.solution["suspect"] and
                weapon == self.solution["weapon"] and
                room == self.solution["room"]):
                messagebox.showinfo("¡Correcto!", f"¡Felicidades! Has resuelto el misterio. {suspect} cometió el crimen en {room} con {weapon}.")
                self.end_game(winner=self.current_player)
            else:
                messagebox.showerror("Incorrecto", "Tu acusación es incorrecta. Estás eliminado del juego.")
                self.eliminate_player()
        else:
            messagebox.showerror("Error", "Por favor, completa todos los campos para hacer una acusación.")

    def eliminate_player(self):
        eliminated_player = self.current_player
        self.player_cards[eliminated_player] = []
        self.board_canvas.itemconfig(f"player_{eliminated_player}", state="hidden")
        
        active_players = [i for i in range(self.num_players) if self.player_cards[i]]
        if len(active_players) == 1:
            messagebox.showinfo("Fin del Juego", f"¡{self.players[active_players[0]]} gana por eliminación!")
            self.end_game(winner=active_players[0])
        else:
            self.end_turn()

    def end_turn(self):
        self.current_player = (self.current_player + 1) % self.num_players
        while not self.player_cards[self.current_player]:  # Saltar jugadores eliminados
            self.current_player = (self.current_player + 1) % self.num_players
        self.player_label.config(text=f"{self.players[self.current_player]}")
        self.update_card_display()

    def update_card_display(self):
        self.card_listbox.delete(0, tk.END)
        for card in self.player_cards[self.current_player]:
            self.card_listbox.insert(tk.END, card)

    def end_game(self, winner):
        for widget in self.master.winfo_children():
            widget.destroy()
        
        end_frame = ttk.Frame(self.master, style="TFrame")
        end_frame.pack(expand=True, fill="both")
        
        ttk.Label(end_frame, text=f"¡Fin del Juego!", font=("Arial", 24, "bold")).pack(pady=20)
        ttk.Label(end_frame, text=f"Ganador: {self.players[winner]}", font=("Arial", 18)).pack(pady=10)
        ttk.Label(end_frame, text=f"Solución:", font=("Arial", 16, "bold")).pack(pady=10)
        ttk.Label(end_frame, text=f"Asesino: {self.solution['suspect']}", font=("Arial", 14)).pack()
        ttk.Label(end_frame, text=f"Arma: {self.solution['weapon']}", font=("Arial", 14)).pack()
        ttk.Label(end_frame, text=f"Habitación: {self.solution['room']}", font=("Arial", 14)).pack()
        
        ttk.Button(end_frame, text="Jugar de Nuevo", command=self.restart_game, style="Action.TButton").pack(pady=20)

    def restart_game(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        self.__init__(self.master)

    def update_notes(self, text):
        self.notes_text.insert(tk.END, text + "\n")
        self.notes_text.see(tk.END)

    def toggle_checklist_item(self, item):
        self.checkbuttons[item].set(not self.checkbuttons[item].get())

    def print_solution(self):
        print("\n=== SOLUCION DEL JUEGO ===")
        print(f"Asesino: {self.solution['suspect']}")
        print(f"Arma: {self.solution['weapon']}")
        print(f"Habitacion: {self.solution['room']}")
        print("==========================")
        
        # Imprimir una frase completa con preposiciones aleatorias
        suspect_prep = random.choice(self.prepositions)
        weapon_prep = random.choice(self.prepositions)
        room_prep = random.choice(self.prepositions)
        
        print(f"\nEl crimen fue cometido {suspect_prep} {self.solution['suspect']}, " 
              f"{weapon_prep} {self.solution['weapon']}, "
              f"{room_prep} {self.solution['room']}.")
        print("==========================\n")

    def print_knowledge_base(self):
        print("\n=== BASE DE CONOCIMIENTO (KB) ===")
        print("Sospechosos:")
        for suspect, status in self.knowledge_base["suspects"].items():
            print(f"  - {suspect}: {status}")
        print("\nArmas:")
        for weapon, status in self.knowledge_base["weapons"].items():
            print(f"  - {weapon}: {status}")
        print("\nHabitaciones:")
        for room, status in self.knowledge_base["rooms"].items():
            print(f"  - {room}: {status}")
        print("================================\n")

if __name__ == "__main__":
    root = tk.Tk()
    game = ClueGame(root)
    root.mainloop()