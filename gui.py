from tkinter import (Frame, Canvas, ttk, HORIZONTAL, VERTICAL, IntVar, Scale, Button, Label, PhotoImage, BOTH, LEFT, Y,
                     X, TOP, messagebox)

from numpy import int_

from gamestate import GameState
from meta import GameMeta
from rave_mctsagent import (RaveMctsAgent, LGRMctsAgent, PoolRaveMctsAgent, DecisiveMoveMctsAgent)
from ucb1_tuned_mctsagent import UCB1TunedMctsAgent
from uct_mcstsagent import UctMctsAgent


class Gui:
    """
    This class is built to let the user have a better interaction with
    game.
    inputs =>
    root = Tk() => an object which inherits the traits of Tkinter class
    agent = an object which inherit the traits of mctsagent class.

    """

    agent_type = {1: "UCT", 2: "RAVE", 3: "LAST-GOOD-REPLY", 4: "POOLRAVE", 5: "DECISIVE-MOVE", 6: "UCB1-TUNED"}

    AGENTS = {"UCT": UctMctsAgent,
              "RAVE": RaveMctsAgent,
              "LAST-GOOD-REPLY": LGRMctsAgent,
              "POOLRAVE": PoolRaveMctsAgent,
              "DECISIVE-MOVE": DecisiveMoveMctsAgent,
              "UCB1-TUNED": UCB1TunedMctsAgent}

    def __init__(self, root, agent_name='UCT'):
        self.root = root
        self.root.geometry('1366x690+0+0')
        self.agent_name = agent_name
        try:
            self.agent = self.AGENTS[agent_name]()
        except KeyError:
            print("Unknown agent defaulting to basic")
            self.agent_name = "uct"
            self.agent = self.AGENTS[agent_name]()
        self.game = GameState(8)
        self.agent.set_gamestate(self.game)
        self.time = 1
        self.root.configure(bg='#363636')
        self.colors = {'white': '#ffffff',
                       'milk': '#e9e5e5',
                       'red': '#9c0101',
                       'orange': '#ee7600',
                       'yellow': '#f4da03',
                       'green': '#00ee76',
                       'cyan': '#02adfd',
                       'blue': '#0261fd',
                       'purple': '#9c02fd',
                       'gray1': '#958989',
                       'gray2': '#3e3e3e',
                       'black': '#000000'}
        global BG
        BG = self.colors['gray2']
        self.last_move = None
        self.frame_board = Frame(self.root)  # main frame for the play board
        self.canvas = Canvas(self.frame_board, bg=BG)
        self.scroll_y = ttk.Scrollbar(self.frame_board, orient=VERTICAL)
        self.scroll_x = ttk.Scrollbar(self.frame_board, orient=HORIZONTAL)

        # the notebook frame which holds the left panel frames

        self.notebook = ttk.Notebook(self.frame_board, width=350)
        self.panel_game = Frame(self.notebook, highlightbackground=self.colors['white'])
        self.developers = Frame(self.notebook, highlightbackground=self.colors['white'])

        # Registering variables for:

        self.game_size_value = IntVar()  # size of the board
        self.game_time_value = IntVar()  # time of CPU player
        self.game_turn_value = IntVar()  # defines whose turn is it

        self.switch_agent_value = IntVar()  # defines which agent to play against
        self.switch_agent_value.set(1)

        self.game_turn_value.set(1)
        self.turn = {1: 'white', 2: 'black'}

        self.game_size = Scale(self.panel_game)
        self.game_time = Scale(self.panel_game)
        self.game_turn = Scale(self.panel_game)
        self.generate = Button(self.panel_game)
        self.reset_board = Button(self.panel_game)

        self.switch_agent = Scale(self.panel_game)
        self.agent_show = Label(self.panel_game, font=('Calibri', 14, 'bold'), fg='white', justify=LEFT,
                                bg=BG, text='Agent Policy: ' + self.agent_name + '\n')

        self.hex_board = []
        # Holds the IDs of hexagons in the main board for implementing the click and play functions
        self.game_size_value.set(8)
        self.game_time_value.set(1)
        self.size = self.game_size_value.get()
        self.time = self.game_time_value.get()
        self.board = self.game.board
        self.board = int_(self.board).tolist()
        self.gameboard2hexagons(self.board)  # building the game board
        self.logo = PhotoImage(file='image/hex.png')
        self.uut_logo = PhotoImage(file='image/uut_2.png')
        self.generate_black_edge()
        self.generate_white_edge()

        # Frame_content

        self.frame_board.configure(bg=BG, width=1366, height=760)
        self.frame_board.pack(fill=BOTH)
        self.notebook.add(self.panel_game, text='       Game       ')
        self.notebook.add(self.developers, text='    Developers    ')
        self.notebook.pack(side=LEFT, fill=Y)
        self.canvas.configure(width=980, bg=BG, cursor='hand2')
        self.canvas.pack(side=LEFT, fill=Y)
        self.canvas.configure(yscrollcommand=self.scroll_y.set)
        self.scroll_y.configure(command=self.canvas.yview)
        self.scroll_x.configure(command=self.canvas.xview)
        self.scroll_y.place(x=387, y=482)
        self.scroll_x.place(x=370, y=500)

        # Frame_left_panel

        """
        the left panel notebook ---->   Game

        """
        self.panel_game.configure(bg=BG)
        Label(self.panel_game, text='Board size',
              font=('Calibri', 14, 'bold'),
              foreground='white', bg=BG, pady=10).pack(fill=X, side=TOP)  # label ---> Board size
        self.game_size.configure(from_=3, to=20, tickinterval=1, bg=BG, fg='white',
                                 orient=HORIZONTAL, variable=self.game_size_value)
        self.game_size.pack(side=TOP, fill=X)
        Label(self.panel_game, text='Time',
              font=('Calibri', 14, 'bold'),
              foreground='white', bg=BG, pady=10).pack(side=TOP, fill=X)  # label ---> Time
        self.game_time.configure(from_=1, to=20, tickinterval=1, bg=BG, fg='white',
                                 orient=HORIZONTAL, variable=self.game_time_value)
        self.game_time.pack(side=TOP, fill=X)
        Label(self.panel_game, text='Player',
              font=('Calibri', 14, 'bold'),
              foreground='white', bg=BG, pady=10).pack(side=TOP, fill=X)  # label ---> Turn
        self.game_turn.configure(from_=1, to=2, tickinterval=1, bg=BG, fg='white',
                                 orient=HORIZONTAL, variable=self.game_turn_value)
        self.game_turn.pack(side=TOP)
        Label(self.panel_game, text='   ',
              font=('Calibri', 14, 'bold'),
              foreground='white', bg=BG).pack(side=TOP, fill=X)

        #  ################################## AGENT CONTROLS #############################

        self.agent_show.pack(fill=X, side=TOP)
        self.switch_agent.configure(from_=1, to=len(self.agent_type), tickinterval=1, bg=BG, fg='white',
                                    orient=HORIZONTAL, variable=self.switch_agent_value, )
        self.switch_agent.pack(side=TOP, fill=X)

        #  ################################## MOVE LABELS ################################
        self.move_label = Label(self.panel_game, font=('Calibri', 15, 'bold'), height=5, fg='white', justify=LEFT,
                                bg=BG, text='PLAY : CLICK A CELL ON GAME BOARD \nMCTS BOT: CLICK GENERATE')
        self.move_label.pack(side=TOP, fill=X)

        self.reset_board.configure(text='Reset Board', pady=10,
                                   cursor='hand2', width=22,
                                   font=('Calibri', 12, 'bold'))
        self.reset_board.pack(side=LEFT)
        self.generate.configure(text='Generate', pady=10,
                                cursor='hand2', width=22,
                                font=('Calibri', 12, 'bold'))
        self.generate.pack(side=LEFT)

        """
        the left panel notebook ---> Developers

        """
        self.developers.configure(bg=BG)
        Label(self.developers,
              text='HEXPY',
              font=('Calibri', 18, 'bold'),
              foreground='white', bg=BG, pady=5).pack(side=TOP, fill=X)
        Label(self.developers,
              text='DEVELOPED BY:\n'
                   + 'Masoud Masoumi Moghadam\n\n'
                   + 'SUPERVISED BY:\n'
                   + 'Dr.Pourmahmoud Aghababa\n'
                   + 'Dr.Bagherzadeh\n\n'
                   + 'SPECIAL THANKS TO:\n'
                   + 'Nemat Rahmani\n',
              font=('Calibri', 16, 'bold'), justify=LEFT,
              foreground='white', bg=BG, pady=10).pack(side=TOP, fill=X)
        Label(self.developers, image=self.uut_logo, bg=BG).pack(side=TOP, fill=X)
        Label(self.developers, text='Summer 2016',
              font=('Calibri', 17, 'bold'), wraplength=350, justify=LEFT,
              foreground='white', bg=BG, pady=30).pack(side=TOP, fill=X)

        # Binding Actions

        """
        Binding triggers for the actions defined in the class.

        """
        self.canvas.bind('<1>', self.click2play)
        self.game_size.bind('<ButtonRelease>', self.set_size)
        self.game_time.bind('<ButtonRelease>', self.set_time)
        self.generate.bind('<ButtonRelease>', self.click_to_bot_play)
        self.reset_board.bind('<ButtonRelease>', self.reset)
        self.switch_agent.bind('<ButtonRelease>', self.set_agent)

    @staticmethod
    def top_left_hexagon():
        """
        Returns the points which the first hexagon has to be created based on.

        """
        return [[85, 50], [105, 65], [105, 90], [85, 105], [65, 90], [65, 65]]

    def hexagon(self, points, color):
        """
        Creates a hexagon by getting a list of points and their assigned colors
        according to the game board
        """
        if color is 0:
            hx = self.canvas.create_polygon(points[0], points[1], points[2],
                                            points[3], points[4], points[5],
                                            fill=self.colors['gray1'], outline='black', width=2, activefill='cyan')
        elif color is 1:
            hx = self.canvas.create_polygon(points[0], points[1], points[2],
                                            points[3], points[4], points[5],
                                            fill=self.colors['yellow'], outline='black', width=2, activefill='cyan')
        elif color is 2:
            hx = self.canvas.create_polygon(points[0], points[1], points[2],
                                            points[3], points[4], points[5],
                                            fill=self.colors['red'], outline='black', width=2, activefill='cyan')
        elif color is 3:
            hx = self.canvas.create_polygon(points[0], points[1], points[2],
                                            points[3], points[4], points[5],
                                            fill=self.colors['black'], outline='black', width=2)
        else:
            hx = self.canvas.create_polygon(points[0], points[1], points[2],
                                            points[3], points[4], points[5],
                                            fill=self.colors['white'], outline='black', width=2)
        return hx

    def generate_row(self, points, colors):
        """
        By getting a list of points as the starting point of each row and a list of
        colors as the dedicated color for each item in row, it generates a row of
        hexagons by calling hexagon functions multiple times.
        """
        x_offset = 40
        row = []
        temp_array = []
        for i in range(len(colors)):
            for point in points:
                temp_points_x = point[0] + x_offset * i
                temp_points_y = point[1]
                temp_array.append([temp_points_x, temp_points_y])
            if colors[i] is 0:
                hx = self.hexagon(temp_array, 0)
            elif colors[i] is 1:
                hx = self.hexagon(temp_array, 4)
            else:
                hx = self.hexagon(temp_array, 3)
            row.append(hx)
            temp_array = []
        return row

    def gameboard2hexagons(self, array):
        """
        Simply gets the game_board and generates the hexagons by their dedicated colors.
        """
        initial_offset = 20
        y_offset = 40
        temp = []
        for i in range(len(array)):
            points = self.top_left_hexagon()
            for point in points:
                point[0] += initial_offset * i
                point[1] += y_offset * i
                temp.append([point[0], point[1]])
            row = self.generate_row(temp, self.board[i])
            temp.clear()
            self.hex_board.append(row)

    def generate_white_edge(self):
        """
        Generates the white zones in the left and right of the board.

        """
        init_points = self.top_left_hexagon()
        for pt in init_points:
            pt[0] -= 40
        for pt in init_points:
            pt[0] -= 20
            pt[1] -= 40
        label_x, label_y = 0, 0
        init_offset = 20
        y_offset = 40
        temp_list = []
        for i in range(len(self.board)):
            for pt in range(len(init_points)):
                init_points[pt][0] += init_offset
                init_points[pt][1] += y_offset
                label_x += init_points[pt][0]
                label_y += init_points[pt][1]
            label_x /= 6
            label_y /= 6
            self.hexagon(init_points, 4)
            self.canvas.create_text(label_x, label_y, fill=self.colors['black'], font="Times 20 bold",
                                    text=chr(ord('A') + i))
            label_x, label_y = 0, 0
            for j in init_points:
                temp_list.append([j[0] + (len(self.board) + 1) * 40, j[1]])
            self.hexagon(temp_list, 4)
            temp_list.clear()

    def generate_black_edge(self):
        """
        Generates the black zones in the top and bottom of the board.

        """
        init_points = self.top_left_hexagon()
        label_x, label_y = 0, 0
        temp_list = []
        for pt in init_points:
            pt[0] -= 60
            pt[1] -= 40
        for t in range(len(init_points)):
            init_points[t][0] += 40
            label_x += init_points[t][0]
            label_y += init_points[t][1]
        label_x /= 6
        label_y /= 6
        for i in range(len(self.board)):
            self.hexagon(init_points, 3)
            self.canvas.create_text(label_x, label_y, fill=self.colors['white'], font="Times 20 bold", text=i + 1)
            label_x, label_y = 0, 0
            for pt in init_points:
                temp_list.append([pt[0] + (len(self.board) + 1) * 20, pt[1] + (len(self.board) + 1) * 40])
            self.hexagon(temp_list, 3)
            temp_list.clear()
            for j in range(len(init_points)):
                init_points[j][0] += 40
                label_x += init_points[j][0]
                label_y += init_points[j][1]
            label_x /= 6
            label_y /= 6

    def click2play(self, event):
        """
        Whenever any of the hexagons in the board is clicked, depending
        on the player turns, it changes the color of hexagon to the player
        assigned color.

        """
        if self.winner() == 'none':
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            idd = self.canvas.find_overlapping(x, y, x, y)
            idd = list(idd)
            if len(idd) is not 0:
                clicked_cell = idd[0]
                if any([clicked_cell in x for x in self.hex_board]):
                    coordinated_cell = clicked_cell - self.hex_board[0][0]
                    col = (coordinated_cell % self.size)
                    turn = self.turn[self.game_turn_value.get()]
                    if coordinated_cell % self.size == 0:
                        row = int(coordinated_cell / self.size)
                    else:
                        row = int(coordinated_cell / self.size)
                        cell = str(chr(65 + row)) + str(col + 1)
                        self.move_label.configure(text=str(turn) + ' played ' + cell, justify=LEFT, height=5)
                    if self.board[row][col] == 0:
                        self.board[row][col] = self.game_turn_value.get()
                        if self.game_turn_value.get() == 1:
                            self.game_turn_value.set(2)
                        else:
                            self.game_turn_value.set(1)
                    self.refresh()
                    y = row
                    x = col
                    if turn[0].lower() == 'w':
                        self.last_move = (x, y)
                        if self.game.turn() == GameMeta.PLAYERS["white"]:
                            self.game.play((x, y))
                            self.agent.move((x, y))
                            if self.winner() != 'none':
                                messagebox.showinfo(" GAME OVER", " Wow, You won! \n Winner is %s" % self.winner())
                            return
                        else:
                            self.game.place_white((x, y))
                            self.agent.set_gamestate(self.game)
                            if self.winner() != 'none':
                                messagebox.showinfo(" GAME OVER", " Wow, You won! \n Winner is %s" % self.winner())
                            return
                    elif turn[0].lower() == 'b':
                        self.last_move = (x, y)
                        if self.game.turn() == GameMeta.PLAYERS["black"]:
                            self.game.play((x, y))
                            self.agent.move((x, y))
                            if self.winner() != 'none':
                                messagebox.showinfo(" GAME OVER", " Wow, You won! \n Winner is %s" % self.winner())
                            return
                        else:
                            self.game.place_black((x, y))
                            self.agent.set_gamestate(self.game)
                            if self.winner() != 'none':
                                messagebox.showinfo(" GAME OVER", " Wow, You won! \n Winner is %s" % self.winner())
                            return
        else:
            messagebox.showinfo(" GAME OVER ", " The game is already over! Winner is %s" % self.winner())

    def set_size(self, event):
        """
        It changes the board size and reset the whole game.

        """
        self.canvas.delete('all')
        self.size = self.game_size_value.get()
        self.game = GameState(self.size)
        self.agent.set_gamestate(self.game)
        self.board = self.game.board
        self.board = int_(self.board).tolist()
        self.last_move = None
        self.move_label.config(text='PLAY : CLICK A CELL ON GAME BOARD \nMCTS BOT: CLICK GENERATE', justify='left',
                               height=5)
        self.refresh()

    def set_time(self, event) -> None:
        """
        It changes the time for CPU player to think and generate a move.

        """
        self.time = self.game_time_value.get()
        print('The CPU time = ', self.time, ' seconds')

    def set_agent(self, event) -> None:
        """
        It changes the time for CPU player to think and generate a move.

        """
        agent_num = self.switch_agent_value.get()
        self.agent_name = self.agent_type[agent_num]
        self.agent = self.AGENTS[self.agent_name](self.game)
        self.agent_show.config(font=('Calibri', 14, 'bold'), justify=LEFT,
                               text='Agent Policy: ' + self.agent_name + '\n')

    def winner(self) -> str:
        """
        Return the winner of the current game (black or white), none if undecided.

        """
        if self.game.winner == GameMeta.PLAYERS["white"]:
            return "white"
        elif self.game.winner == GameMeta.PLAYERS["black"]:
            return "black"
        else:
            return "none"

    def click_to_bot_play(self, event):
        """
        By pushing the generate button, It produces an appropriate move
        by using monte carlo tree search algorithm for the player which
        turn is his/hers! .

        """
        if self.winner() == 'none':
            self.agent.search(self.time)
            num_rollouts, node_count, run_time = self.agent.statistics()
            move = self.agent.best_move()  # the move is tuple like (3, 1)
            self.game.play(move)
            self.agent.move(move)
            row, col = move  # Relating the 'move' tuple with index of self.board
            self.board[col][row] = self.game_turn_value.get()
            if self.game_turn_value.get() == 1:  # change the turn of players
                self.game_turn_value.set(2)
            else:
                self.game_turn_value.set(1)
            self.refresh()
            player = self.turn[self.game_turn_value.get()]
            cell = chr(ord('A') + move[1]) + str(move[0] + 1)
            self.move_label.config(font=('Calibri', 15, 'bold'), justify='left',
                                   text=str(num_rollouts) + ' Game Simulations ' + '\n'
                                                          + 'In ' + str(run_time) + ' seconds ' + '\n'
                                                          + 'Node Count : ' + str(node_count) + '\n'
                                                          + player + ' played at ' + cell, height=5)
            print('move = ', cell)
            if self.winner() != 'none':
                messagebox.showinfo(" GAME OVER", " Oops!\n You lost! \n Winner is %s" % self.winner())
        else:
            messagebox.showinfo(" GAME OVER", " The game is already over! Winner is %s" % self.winner())

    def refresh(self):
        """
        Delete the whole world and recreate it again

        """
        self.canvas.delete('all')
        self.hex_board.clear()
        self.gameboard2hexagons(self.board)
        self.generate_black_edge()
        self.generate_white_edge()

    def reset(self, event):
        """
        By clicking on the Reset button game board would be cleared
        for a new game

        """
        self.game = GameState(self.game.size)
        self.agent.set_gamestate(self.game)
        self.set_size(event)
        self.last_move = None
        self.game_turn_value.set(1)
        self.move_label.config(text='PLAY : CLICK A CELL ON GAME BOARD \nMCTS BOT: CLICK GENERATE', justify='left',
                               height=5)
