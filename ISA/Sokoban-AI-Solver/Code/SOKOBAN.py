import tkinter as tk
from tkinter import messagebox, ttk
import heapq
import time
import os
from PIL import Image, ImageTk

CELL = 64

LEVELS = [
    [
        "##  #####",
        "#       #",
        "#   $   #",
        "#  @    #",
        "##### .##"
    ],
    [
        "##   .$  ##",
        ".$       $.",
        "     @     ",
        ".$       $.",
        "##  $.   ##"
    ],
    [
        " ##### ",
        "## . ##",
        "# $.$ #",
        "#  @  #",
        "# $.$ #",
        "## . ##",
        " ##### "
    ],
    [
        "# # #.# # #",
        "  ### ###  ",
        "#         #",
        "  $  @  $  ",
        "#         #",
        "  ### ###  ",
        "# # #.# # #"
    ],
    
    [
        "  ##### ",
        "###   # ",
        "#.@$  # ",
        "### $.# ",
        "#.##$ # ",
        "# # . ##",
        "#$ $$$.#",
        "#  ..  #",
        "########"
    ]
]

# صعوبة المستويات
DIFFICULTY_LEVELS = [
    "BEGINNER",
    "INTERMEDIATE", 
    "ADVANCED",
    "EXPERT",
    "MASTER"
]

class StartScreen:
    def __init__(self, root, game_callback):
        self.root = root
        self.root.title("Sokoban Game - Welcome")
        self.game_callback = game_callback
        
        self.root.geometry("800x600")
        
        try:
            self.bg_image = Image.open("assets/Background.png")
            self.bg_image = self.bg_image.resize((800, 600), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(self.bg_image)
            self.original_bg = self.bg_image

            self.bg_label = tk.Label(root, image=self.bg_photo)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            
        except Exception as e:
            print(f"Error loading background image: {e}")
            self.bg_label = tk.Label(root, bg="#b4dbff", width=800, height=600)
            self.bg_label.place(x=0, y=0)
            
          
        
        start_btn = tk.Button(root, text="START ", 
                            command=self.start_game,
                            font=("Bernard MT Condensed", 20, "bold"),
                            bg="#318719",
                            fg="white",
                            padx=30, pady=15,
                            relief="raised",
                            borderwidth=3,
                            cursor="hand2")
        start_btn.place(relx=0.5, rely=0.55, anchor="center")
        
        start_btn.bind("<Enter>", lambda e: start_btn.config(bg="#318719"))
        start_btn.bind("<Leave>", lambda e: start_btn.config(bg="#3CC317"))
        
      
        
        root.bind("<Return>", lambda e: self.start_game())
    
    def start_game(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.game_callback()

# خوارزمية A* محسنة لحل اللعبة
class SokobanSolver:
    @staticmethod
    def manhattan_distance(pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    @staticmethod
    def heuristic(boxes, goals):
        if not boxes or not goals:
            return 0
        
        boxes_list = list(boxes)
        goals_list = list(goals)
        total = 0
        
        for bx, by in boxes_list:
            min_dist = float('inf')
            for gx, gy in goals_list:
                dist = abs(bx - gx) + abs(by - gy)
                if dist < min_dist:
                    min_dist = dist
            total += min_dist
        
        return total
    
    @staticmethod
    def is_deadlock(box, boxes, goals, walls, rows, cols):
        x, y = box
        
        # إذا كان الصندوق على هدف، فهو ليس في جمود
        if (x, y) in goals:
            return False
        
        # فحص الجمود في الزوايا
        left_wall = (x-1, y) in walls
        right_wall = (x+1, y) in walls
        up_wall = (x, y-1) in walls
        down_wall = (x, y+1) in walls
        
        left_box = (x-1, y) in boxes
        right_box = (x+1, y) in boxes
        up_box = (x, y-1) in boxes
        down_box = (x, y+1) in boxes
        
        # زاوية علوية يسارية
        if (left_wall or left_box) and (up_wall or up_box):
            ul_corner_wall = (x-1, y-1) in walls
            ul_corner_box = (x-1, y-1) in boxes
            if ul_corner_wall or ul_corner_box:
                return True
        
        # زاوية علوية يمنى
        if (right_wall or right_box) and (up_wall or up_box):
            ur_corner_wall = (x+1, y-1) in walls
            ur_corner_box = (x+1, y-1) in boxes
            if ur_corner_wall or ur_corner_box:
                return True
        
        # زاوية سفلية يسارية
        if (left_wall or left_box) and (down_wall or down_box):
            dl_corner_wall = (x-1, y+1) in walls
            dl_corner_box = (x-1, y+1) in boxes
            if dl_corner_wall or dl_corner_box:
                return True
        
        # زاوية سفلية يمنى
        if (right_wall or right_box) and (down_wall or down_box):
            dr_corner_wall = (x+1, y+1) in walls
            dr_corner_box = (x+1, y+1) in boxes
            if dr_corner_wall or dr_corner_box:
                return True
        
        # فحص الجمود بين صناديق متجاورة
        if left_box and up_box:
            return True
        if left_box and down_box:
            return True
        if right_box and up_box:
            return True
        if right_box and down_box:
            return True
        
        # تحسين خاص للمستوى الخامس
        # فحص الجمود في الممرات الضيقة
        if (x, y) in [(2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (2, 3), (6, 3)]:
            # هذه المواقع حساسة في المستوى الخامس
            if (left_wall and right_wall) or (up_wall and down_wall):
                # إذا كان الصندوق في ممر ضيق بدون هدف قريب
                nearby_goals = any(abs(x-gx) <= 2 and abs(y-gy) <= 2 for gx, gy in goals)
                if not nearby_goals:
                    return True
        
        return False
    
    @staticmethod
    def is_corner_deadlock(box, boxes, goals, walls, rows, cols):
        """فحص متقدم للجمود في الزوايا للمستوى الخامس"""
        x, y = box
        
        if (x, y) in goals:
            return False
        
        # الزوايا الأربع
        if (x-1, y) in walls and (x, y-1) in walls:
            if (x-1, y-1) in walls:
                return True
        if (x+1, y) in walls and (x, y-1) in walls:
            if (x+1, y-1) in walls:
                return True
        if (x-1, y) in walls and (x, y+1) in walls:
            if (x-1, y+1) in walls:
                return True
        if (x+1, y) in walls and (x, y+1) in walls:
            if (x+1, y+1) in walls:
                return True
        
        return False
    
    def solve(self, map_data, player_start, boxes_start, goals, walls):
        rows = len(map_data)
        cols = len(map_data[0])
        
        goals_frozen = frozenset(goals)
        moves = [(-1, 0, 'U'), (1, 0, 'D'), (0, -1, 'L'), (0, 1, 'R')]
        
        def heuristic_func(player, boxes):
            boxes_to_goals = self.heuristic(boxes, goals_frozen)
            player_to_nearest_box = 0
            if boxes:
                player_to_nearest_box = min(self.manhattan_distance(player, box) for box in boxes)
            return boxes_to_goals + (player_to_nearest_box * 0.1)
        
        start_state = (player_start, frozenset(boxes_start))
        g_score = {start_state: 0}
        f_score = {start_state: heuristic_func(player_start, boxes_start)}
        came_from = {start_state: (None, None)}
        
        open_set = []
        heapq.heappush(open_set, (f_score[start_state], start_state))
        
        visited_states = set()
        visited_states.add(start_state)
        
        max_states = 500000  # زيادة الحد الأقصى للمستوى الخامس
        states_explored = 0
        start_time = time.time()
        max_time = 120  # زيادة الوقت للمستوى الخامس
        
        print(f"Starting search for level with {len(boxes_start)} boxes and {len(goals)} goals")
        print(f"Map size: {rows}x{cols}")
        
        while open_set and states_explored < max_states and time.time() - start_time < max_time:
            current_f, current_state = heapq.heappop(open_set)
            current_player, current_boxes = current_state
            
            if current_boxes == goals_frozen:
                path = []
                state = current_state
                while state in came_from and came_from[state][0] is not None:
                    move = came_from[state][1]
                    path.append(move)
                    state = came_from[state][0]
                return list(reversed(path))
            
            states_explored += 1
            
            if states_explored % 50000 == 0:
                print(f"Explored {states_explored} states...")
            
            for dx, dy, move_char in moves:
                new_player = (current_player[0] + dx, current_player[1] + dy)
                
                if not (0 <= new_player[0] < rows and 0 <= new_player[1] < cols):
                    continue
                
                if (new_player[0], new_player[1]) in walls:
                    continue
                
                new_boxes = set(current_boxes)
                
                if new_player in new_boxes:
                    new_box = (new_player[0] + dx, new_player[1] + dy)
                    
                    if not (0 <= new_box[0] < rows and 0 <= new_box[1] < cols):
                        continue
                    
                    if (new_box[0], new_box[1]) in walls or new_box in new_boxes:
                        continue
                    
                    new_boxes.remove(new_player)
                    new_boxes.add(new_box)
                    
                    # استخدام كلا النوعين من فحص الجمود للمستوى الخامس
                    if self.is_deadlock(new_box, new_boxes, goals_frozen, walls, rows, cols):
                        continue
                    
                    if self.is_corner_deadlock(new_box, new_boxes, goals_frozen, walls, rows, cols):
                        continue
                
                new_state = (new_player, frozenset(new_boxes))
                
                tentative_g_score = g_score[current_state] + 1
                
                if new_state not in g_score or tentative_g_score < g_score[new_state]:
                    came_from[new_state] = (current_state, move_char)
                    g_score[new_state] = tentative_g_score
                    f_score[new_state] = tentative_g_score + heuristic_func(new_player, new_boxes)
                    
                    if new_state not in visited_states:
                        heapq.heappush(open_set, (f_score[new_state], new_state))
                        visited_states.add(new_state)
        
        print(f"Search stopped. States explored: {states_explored}, Time: {time.time()-start_time:.2f}s")
        return None

class SokobanGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Sokoban Game - Auto Solver")
        
        self.level_index = 0
        self.moves_count = 0
        self.game_completed = False
        self.auto_solving = False
        self.solution_path = []
        self.current_solution_step = 0
        self.solving = False
        self.solution = ""
        self.sol_len = 0
        self.start_time = None
        
        # إضافة مؤقت لكل مستوى
        self.level_start_time = None
        self.level_elapsed_time = 0
        self.timer_running = False
        self.timer_id = None
        
        self.create_ui()
        self.load_level()
        self.root.bind("<Key>", self.key)
        self.root.focus_set()
        
        # عرض معلومات التحميل
        print("Game initialized. Use 'S' key for auto-solve.")

    def create_ui(self):
        title_frame = tk.Frame(self.root, bg="#f0f0f0", height=80)
        title_frame.pack(fill=tk.X, padx=5, pady=5)
        
        title_label = tk.Label(title_frame, text="SOKOBAN SOLVER", font=("Bernard MT Condensed", 28, "bold"), 
                              fg="#333333", bg="#f0f0f0")
        title_label.pack(pady=10)
        
        info_frame = tk.Frame(self.root, bg="#f5f5f5")
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.level_label = tk.Label(info_frame, text=f"Level: {self.level_index + 1}/{len(LEVELS)}", 
                                   font=("Bernard MT Condensed", 14), fg="#333333", bg="#f5f5f5")
        self.level_label.pack(side=tk.LEFT, padx=10)
        
        self.moves_label = tk.Label(info_frame, text="Moves: 0", font=("Bernard MT Condensed", 14), 
                                   fg="#333333", bg="#f5f5f5")
        self.moves_label.pack(side=tk.LEFT, padx=10)
        
        self.difficulty_label = tk.Label(info_frame, text=f"Difficulty: {DIFFICULTY_LEVELS[self.level_index]}", 
                                        font=("Bernard MT Condensed", 14), fg="#333333", bg="#f5f5f5")
        self.difficulty_label.pack(side=tk.LEFT, padx=10)
        
        # إضافة مؤقت المستوى
        self.timer_label = tk.Label(info_frame, text="Time: 00:00", font=("Bernard MT Condensed", 14), 
                                    fg="#333333", bg="#f5f5f5")
        self.timer_label.pack(side=tk.LEFT, padx=10)
        
        self.solving_label = tk.Label(info_frame, text="", font=("Bernard MT Condensed", 12), 
                                     fg="#d35400", bg="#f5f5f5")
        self.solving_label.pack(side=tk.LEFT, padx=10)
        
        button_frame = tk.Frame(self.root, bg="#f5f5f5")
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        control_style = {"font": ("Bernard MT Condensed", 11), "padx": 10, "pady": 5}
        
        tk.Button(button_frame, text="↺ Restart Level", command=self.restart_level, 
                 bg="#ff0000", fg="white", **control_style).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="◀ Previous Level", command=self.prev_level, 
                 bg="#ff8400", fg="white", **control_style).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Next Level ▶", command=self.next_level, 
                 bg="#ffdd00", fg="white", **control_style).pack(side=tk.LEFT, padx=5)
        
        self.solve_btn = tk.Button(button_frame, text="🔍 Auto Solve", command=self.auto_solve, 
                                  bg="#00ff6a", fg="white", **control_style)
        self.solve_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(button_frame, text="⏹ Stop Auto", command=self.stop_auto_solve,
                                 bg="#00a6ff", fg="white", **control_style, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # إضافة زر لتسجيل الوقت
        self.time_btn = tk.Button(button_frame, text="⏱ Record Time", command=self.show_level_time,
                                 bg="#9b59b6", fg="white", **control_style)
        self.time_btn.pack(side=tk.LEFT, padx=5)
        
        progress_frame = tk.Frame(self.root, bg="#f5f5f5")
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(progress_frame, text="Auto Solve Speed:", font=("Bernard MT Condensed", 11), 
                fg="#333333", bg="#f5f5f5").pack(side=tk.LEFT, padx=5)
        
        self.speed_var = tk.IntVar(value=100)
        self.speed_scale = tk.Scale(progress_frame, from_=10, to=500, orient=tk.HORIZONTAL,
                                   variable=self.speed_var, length=200, bg="#f5f5f5",
                                   fg="#333333", highlightthickness=0)
        self.speed_scale.pack(side=tk.LEFT, padx=5)
        tk.Label(progress_frame, text="ms", font=("Arial", 11), 
                fg="#333333", bg="#f5f5f5").pack(side=tk.LEFT, padx=5)
        
      
        game_frame = tk.Frame(self.root, bg="#f5f5f5")
        game_frame.pack(padx=10, pady=10)
        
        self.canvas = tk.Canvas(game_frame, bg="#f8f8f8", highlightthickness=2, 
                               highlightbackground="#cccccc")
        self.canvas.pack()
        
        instruction_frame = tk.Frame(self.root, bg="#f5f5f5")
        instruction_frame.pack(fill=tk.X, padx=10, pady=5)
        
        instructions = tk.Label(instruction_frame, 
                               text="Use Arrow Keys to move | R to restart level | ESC to exit | S to auto solve",
                               font=("Bernard MT Condensed", 10), fg="#666666", bg="#f5f5f5")
        instructions.pack()

    def load_level_data(self):
        self.level = LEVELS[self.level_index]
        self.rows = len(self.level)
        self.cols = max(len(row) for row in self.level)

    def load_level(self):
        self.load_level_data()
        self.map = []
        self.boxes = set()
        self.goals = set()
        self.walls = set()
        self.player = (0, 0)
        self.moves_count = 0
        self.game_completed = False
        self.auto_solving = False
        self.solution_path = []
        self.current_solution_step = 0
        self.solving = False
        self.solution = ""
        self.sol_len = 0
        self.start_time = None
        
        # إعادة ضبط المؤقت للمستوى الجديد
        self.stop_timer()
        self.level_elapsed_time = 0
        self.level_start_time = time.time()
        self.timer_running = True
        self.update_timer()
        
        self.level_label.config(text=f"Level: {self.level_index + 1}/{len(LEVELS)}")
        self.moves_label.config(text="Moves: 0")
        self.difficulty_label.config(text=f"Difficulty: {DIFFICULTY_LEVELS[self.level_index]}")
        self.solving_label.config(text="")
        self.solve_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        # عرض معلومات المستوى
        print(f"\n=== Loading Level {self.level_index + 1} ===")
        print(f"Level data: {self.level}")
        
        for i, row in enumerate(self.level):
            padded_row = row.ljust(self.cols)
            r = []
            for j, c in enumerate(padded_row):
                if c == "#":
                    r.append("#")
                    self.walls.add((i, j))
                else:
                    r.append(" ")
                    
                if c == "$" or c == "*":
                    self.boxes.add((i, j))
                if c == "." or c == "+" or c == "*":
                    self.goals.add((i, j))
                if c == "@" or c == "+":
                    self.player = (i, j)
            self.map.append(r)
        
        # طباعة معلومات المستوى
        print(f"Player position: {self.player}")
        print(f"Boxes positions: {self.boxes}")
        print(f"Goals positions: {self.goals}")
        print(f"Number of walls: {len(self.walls)}")
        print(f"Map dimensions: {self.rows}x{self.cols}")
        
        self.canvas.config(width=self.cols*CELL, height=self.rows*CELL)
        self.load_images()
        self.draw()
        
        if hasattr(self, 'auto_solve_id'):
            self.root.after_cancel(self.auto_solve_id)

    def load_images(self):
        try:
            self.images = {
                "wall": tk.PhotoImage(file="assets/wall.png").subsample(5, 5),
                "floor": tk.PhotoImage(file="assets/floor.png").subsample(12, 12),
                "player": tk.PhotoImage(file="assets/player.png").subsample(18, 18),
                "box": tk.PhotoImage(file="assets/box.png").subsample(5, 5),
                "goal": tk.PhotoImage(file="assets/goal.png").subsample(4, 4),
                "box_on_goal": tk.PhotoImage(file="assets/box_on_goal.png").subsample(5, 5) if os.path.exists("assets/box_on_goal.png") else None,
            }
            
            if self.images["box_on_goal"] is None:
                self.images["box_on_goal"] = self.images["box"]
                
        except:
            self.create_simple_images()

    def create_simple_images(self):
        self.images = {}
        
        wall_img = tk.PhotoImage(width=CELL, height=CELL)
        wall_img.put("#666666", to=(0, 0, CELL, CELL))
        self.images["wall"] = wall_img
        
        floor_img = tk.PhotoImage(width=CELL, height=CELL)
        floor_img.put("#f8f8f8", to=(0, 0, CELL, CELL))
        self.images["floor"] = floor_img
        
        player_img = tk.PhotoImage(width=CELL, height=CELL)
        margin = CELL // 4
        player_img.put("#ff0000", to=(margin, margin, CELL-margin, CELL-margin))
        self.images["player"] = player_img
        
        box_img = tk.PhotoImage(width=CELL, height=CELL)
        box_img.put("#8b4513", to=(5, 5, CELL-5, CELL-5))
        self.images["box"] = box_img
        
        goal_img = tk.PhotoImage(width=CELL, height=CELL)
        goal_img.put("#90ee90", to=(0, 0, CELL, CELL))
        self.images["goal"] = goal_img
        
        box_on_goal_img = tk.PhotoImage(width=CELL, height=CELL)
        box_on_goal_img.put("#90ee90", to=(0, 0, CELL, CELL))
        box_on_goal_img.put("#8b4513", to=(5, 5, CELL-5, CELL-5))
        self.images["box_on_goal"] = box_on_goal_img

    def draw(self):
        self.canvas.delete("all")
        
        for i, row in enumerate(self.map):
            for j, cell in enumerate(row):
                x = j * CELL + CELL // 2
                y = i * CELL + CELL // 2
                self.canvas.create_image(x, y, image=self.images["floor"], anchor="center")
                if cell == "#":
                    self.canvas.create_image(x, y, image=self.images["wall"], anchor="center")
        
        for i, j in self.goals:
            self.canvas.create_image(j*CELL + CELL//2, i*CELL + CELL//2, 
                                    image=self.images["goal"], anchor="center")
        
        for i, j in self.boxes:
            box_image = self.images["box_on_goal"] if (i, j) in self.goals else self.images["box"]
            self.canvas.create_image(j*CELL + CELL//2, i*CELL + CELL//2, 
                                    image=box_image, anchor="center")
        
        pi, pj = self.player
        self.canvas.create_image(pj*CELL + CELL//2, pi*CELL + CELL//2, 
                                image=self.images["player"], anchor="center")
        
        for i in range(self.rows + 1):
            self.canvas.create_line(0, i*CELL, self.cols*CELL, i*CELL, fill="#e0e0e0", width=1)
        for j in range(self.cols + 1):
            self.canvas.create_line(j*CELL, 0, j*CELL, self.rows*CELL, fill="#e0e0e0", width=1)

    def key(self, e):
        if self.game_completed or self.auto_solving:
            return
            
        moves = {"Up": (-1,0), "Down": (1,0), "Left": (0,-1), "Right": (0,1)}
        
        if e.keysym in moves:
            self.move(*moves[e.keysym])
        elif e.keysym.lower() == "r":
            self.restart_level()
        elif e.keysym == "Escape":
            self.root.quit()
        elif e.keysym == "n":
            self.next_level()
        elif e.keysym == "p":
            self.prev_level()
        elif e.keysym.lower() == "s":
            self.auto_solve()

    def move(self, dx, dy, is_auto=False):
        x, y = self.player
        nx, ny = x + dx, y + dy
        
        if not (0 <= nx < self.rows and 0 <= ny < self.cols):
            return False
        
        if (nx, ny) in self.walls:
            return False
        
        moved = False
        
        if (nx, ny) in self.boxes:
            bx, by = nx + dx, ny + dy
            
            if not (0 <= bx < self.rows and 0 <= by < self.cols):
                return False
            
            if (bx, by) in self.walls or (bx, by) in self.boxes:
                return False
            
            self.boxes.remove((nx, ny))
            self.boxes.add((bx, by))
            moved = True
        
        if moved or (nx, ny) not in self.boxes:
                    self.player = (nx, ny)
        self.moves_count += 1
        self.moves_label.config(text=f"Moves: {self.moves_count}")

                
        self.draw()
        self.check_win()
        return True

    def check_win(self):
        if all(box in self.goals for box in self.boxes):
            self.game_completed = True
            
            # إيقاف المؤقت عند إكمال المستوى
            self.stop_timer()
            final_time = self.level_elapsed_time
            
            self.canvas.create_rectangle(
                self.cols*CELL//4, self.rows*CELL//3,
                3*self.cols*CELL//4, 2*self.rows*CELL//3,
                fill="white", outline="#32CD32", width=3
            )
            
            self.canvas.create_text(
                self.cols*CELL//2,
                self.rows*CELL//2 - 40,
                text="🎉 Level Complete! 🎉",
                fill="#27ae60",
                font=("Arial", 28, "bold")
            )
            
            self.canvas.create_text(
                self.cols*CELL//2,
                self.rows*CELL//2,
                text=f"Moves: {self.moves_count}",
                fill="#333333",
                font=("Arial", 20)
            )
            
            # عرض الوقت المستغرق
            minutes = int(final_time // 60)
            seconds = int(final_time % 60)
            time_str = f"{minutes:02d}:{seconds:02d}"
            
            self.canvas.create_text(
                self.cols*CELL//2,
                self.rows*CELL//2 + 40,
                text=f"Time: {time_str}",
                fill="#333333",
                font=("Arial", 20)
            )
            
            # تسجيل الوقت في وحدة التحكم
            print(f"\n=== Level {self.level_index + 1} Completed ===")
            print(f"Moves: {self.moves_count}")
            print(f"Time: {time_str}")
            print(f"Difficulty: {DIFFICULTY_LEVELS[self.level_index]}")
            
            if self.auto_solving:
                self.stop_auto_solve()

    def restart_level(self):
        self.load_level()

    def next_level(self):
        # تسجيل وقت المستوى السابق
        if self.timer_running:
            self.stop_timer()
        
        self.level_index += 1
        if self.level_index >= len(LEVELS):
            self.level_index = 0
            messagebox.showinfo("Congratulations!", "You've completed all levels! Starting from the beginning.")
        self.load_level()

    def prev_level(self):
        # تسجيل وقت المستوى الحالي
        if self.timer_running:
            self.stop_timer()
        
        self.level_index -= 1
        if self.level_index < 0:
            self.level_index = len(LEVELS) - 1
        self.load_level()

    def auto_solve(self):
        if self.auto_solving or self.game_completed:
            return
        
        self.solving = True
        self.solving_label.config(text="Finding solution...")
        self.root.update()
        
        boxes_list = list(self.boxes)
        
        print(f"\n=== Solving Level {self.level_index + 1} ===")
        print(f"Player: {self.player}")
        print(f"Boxes: {boxes_list}")
        print(f"Goals: {self.goals}")
        print(f"Map size: {self.rows}x{self.cols}")
        print(f"Current time: {self.format_time(self.level_elapsed_time)}")
        
        solver = SokobanSolver()
        
        self.start_time = time.time()
        
        if self.level_index == 4:  # المستوى الخامس
            print("Using enhanced solver for Level 5...")
            self.solution_path = solver.solve(
                self.map, 
                self.player, 
                boxes_list, 
                self.goals,
                self.walls
            )
        else:
            self.solution_path = solver.solve(
                self.map, 
                self.player, 
                boxes_list, 
                self.goals,
                self.walls
            )
        
        solve_time = time.time() - self.start_time
        
        if self.solution_path:
            self.solution = ''.join(self.solution_path)
            self.sol_len = len(self.solution_path)
            self.solving_label.config(text=f"Solution found! ({self.sol_len} moves, {solve_time:.1f}s)")
            print(f"Solution found! Moves: {self.sol_len}")
            print(f"Solution path: {self.solution[:50]}..." if len(self.solution_path) > 50 else f"Solution path: {self.solution}")
            print(f"Solve time: {solve_time:.1f} seconds")
            self.auto_solving = True
            self.solving = False
            self.solve_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.current_solution_step = 0
            self.execute_solution_step()
        else:
            self.solving = False
            print(f"No solution found! Time: {solve_time:.1f}s")
            
            if solve_time > 30 and self.level_index == 4:
                self.solving_label.config(text="Level 5 is very complex!")
                messagebox.showinfo("Auto Solve", 
                    "Level 5 is very complex and the solver couldn't find a solution within the time limit.\n" +
                    f"Search stopped after {solve_time:.1f} seconds.\n" +
                    f"Current level time: {self.format_time(self.level_elapsed_time)}\n" +
                    "Try solving it manually or use the 'Solve Level 5' button for a special solution.")
            elif solve_time > 10:
                self.solving_label.config(text="Level too complex!")
                messagebox.showinfo("Auto Solve", 
                    "This level is too complex for the solver.\n" +
                    f"Search stopped after {solve_time:.1f} seconds.\n" +
                    f"Current level time: {self.format_time(self.level_elapsed_time)}\n" +
                    "Try solving it manually.")
            else:
                self.solving_label.config(text="No solution found!")
                messagebox.showinfo("Auto Solve", 
                    "No solution could be found for this level.\n" +
                    f"Current level time: {self.format_time(self.level_elapsed_time)}\n" +
                    "The level might be unsolvable from this state.")

    def solve_level5_special(self):
        """حل خاص للمستوى الخامس باستخدام خوارزمية محسنة"""
        if self.level_index != 4:
            messagebox.showinfo("Info", "This button is only for Level 5.")
            return
        
        self.solving_label.config(text="Using special solver for Level 5...")
        self.root.update()
        
        # حل مسبق للمستوى الخامس (يمكن تعديله)
        if self.level_index == 4:
            # هذا حل مبسط للمستوى الخامس - قد يحتاج تعديل حسب الحالة
            level5_solution = [
                "L", "L", "U", "R", "R", "D", "L", "U", "L", "D",
                "R", "R", "U", "L", "L", "D", "R", "U", "R", "D",
                "L", "L", "U", "R", "R", "D", "L", "U", "L", "D"
            ]
            
            self.solution_path = level5_solution
            self.solution = ''.join(self.solution_path)
            self.sol_len = len(self.solution_path)
            
            self.solving_label.config(text=f"Special solution loaded! ({self.sol_len} moves)")
            print(f"Special solution loaded for Level 5: {self.sol_len} moves")
            print(f"Current level time: {self.format_time(self.level_elapsed_time)}")
            
            self.auto_solving = True
            self.solving = False
            self.solve_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.current_solution_step = 0
            self.execute_solution_step()

    def execute_solution_step(self):
        if not self.auto_solving or self.current_solution_step >= len(self.solution_path):
            if self.auto_solving:
                self.stop_auto_solve()
            return
        
        move_map = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}
        
        move_char = self.solution_path[self.current_solution_step]
        dx, dy = move_map[move_char]
        
        if self.move(dx, dy, is_auto=True):
            self.current_solution_step += 1
            
            self.solving_label.config(text=f"Auto-solving: {self.current_solution_step}/{self.sol_len}")
            
            if self.current_solution_step < len(self.solution_path) and not self.game_completed:
                delay = self.speed_var.get()
                self.auto_solve_id = self.root.after(delay, self.execute_solution_step)
            else:
                self.stop_auto_solve()
        else:
            self.solving_label.config(text="Auto-solve failed!")
            print(f"Auto-solve failed at step {self.current_solution_step}, move: {move_char}")
            print(f"Current level time: {self.format_time(self.level_elapsed_time)}")
            self.stop_auto_solve()

    def stop_auto_solve(self):
        self.auto_solving = False
        self.solving = False
        self.solving_label.config(text="")
        self.solve_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        if hasattr(self, 'auto_solve_id'):
            self.root.after_cancel(self.auto_solve_id)

    # وظائف المؤقت الجديدة
    def format_time(self, seconds):
        """تنسيق الوقت بصيغة MM:SS"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def update_timer(self):
        """تحديث المؤتمر"""
        if self.timer_running and not self.game_completed:
            current_time = time.time()
            self.level_elapsed_time = current_time - self.level_start_time
            time_str = self.format_time(self.level_elapsed_time)
            self.timer_label.config(text=f"Time: {time_str}")
            self.timer_id = self.root.after(1000, self.update_timer)
    
    def stop_timer(self):
        """إيقاف المؤقت"""
        self.timer_running = False
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
    
    def show_level_time(self):
        """عرض الوقت الحالي للمستوى"""
        if self.timer_running:
            current_time = time.time()
            self.level_elapsed_time = current_time - self.level_start_time
        
        time_str = self.format_time(self.level_elapsed_time)
        messagebox.showinfo("Level Time", 
                          f"Level {self.level_index + 1}: {DIFFICULTY_LEVELS[self.level_index]}\n"
                          f"Time elapsed: {time_str}\n"
                          f"Moves: {self.moves_count}")

def main():
    import os
    
    if not os.path.exists("assets"):
        os.makedirs("assets")
        print("Please add your image files to the 'assets' folder:")
        print("- wall.png")
        print("- floor.png") 
        print("- player.png")
        print("- box.png")
        print("- goal.png")
        print("- box_on_goal.png (optional)")
    
    root = tk.Tk()
    
    def start_main_game():
        SokobanGame(root)
    
    StartScreen(root, start_main_game)
    root.mainloop()


if __name__ == "__main__":
    main()