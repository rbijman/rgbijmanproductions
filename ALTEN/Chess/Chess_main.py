# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 14:51:12 2025

@author: rbijman
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time
import os 
import chess


plt.ion()

class Piece:
    def __init__(self,name,piece_type,piece_type_idx,color,player_id):
        self.name = name
        self.color = color
        self.player_id = player_id
        self.type = piece_type
        self.type_idx = piece_type_idx
        #instantiate other atributes
        self.allowed_movements = None
        self.status = 'safe'
        self.ann = []
        self.loc = {'x':None,'y':None}
        #init_member_functions
        self.__initiate_allowed_movements()
        
    def show_piece(self,ax,ismove):
        annotation = ax.annotate(self.name, [self.loc['x'],self.loc['y']],ha='center',color=self.color)
        self.ann.append(annotation)
        plt.draw()
        if ismove:
            plt.pause(0.1)
                
    def hide_piece(self):
        for annotation in self.ann:
            annotation.remove()
        self.ann.clear()
    
    def set_location(self,new_loc_x,new_loc_y):
        self.loc = {'x':new_loc_x,'y':new_loc_y}
        
    def change_status(self):
        return
    
    def __initiate_allowed_movements(self):
        match self.type:
            case 'pawn':
                if self.player_id==1:
                    self.allowed_movements = {'normal':[(0,1)],'attack':[(1,1),(-1,1)],'initial':[(0,1),(0,2)]} #Fix initial movement of pon! make sure that it only happens 
                else:
                    self.allowed_movements = {'normal':[(0,-1)],'attack':[(1,-1),(-1,-1)],'initial':[(0,-1),(0,-2)]}
            case 'rook':
                self.allowed_movements = {'normal':[(x,0) for x in range(-8,9) if x != 0] + [(0,x) for x in range(-8,9) if x != 0]}
                self.allowed_movements['attack'] = self.allowed_movements['normal']
                self.allowed_movements['initial'] = self.allowed_movements['normal']
            case 'knight':
                self.allowed_movements = {'normal':[(1,2),(1,-2),(2,1),(2,-1),(-1,2),(-1,-2),(-2,1),(-2,-1)]}
                self.allowed_movements['attack'] = self.allowed_movements['normal']
                self.allowed_movements['initial'] = self.allowed_movements['normal']
            case 'bishop':
                self.allowed_movements = {'normal':[(x,x) for x in range(-8,9) if x != 0] + [(x,-x) for x in range(-8,9) if x != 0] }
                self.allowed_movements['attack'] = self.allowed_movements['normal']
                self.allowed_movements['initial'] = self.allowed_movements['normal']
            case 'queen':
                self.allowed_movements = {'normal':[(x,0) for x in range(-8,9) if x != 0] + [(0,x) for x in range(-8,9) if x != 0] + [(x,x) for x in range(-8,9) if x != 0] + [(x,-x) for x in range(-8,9) if x != 0]}
                self.allowed_movements['attack'] = self.allowed_movements['normal']
                self.allowed_movements['initial'] = self.allowed_movements['normal']
            case 'king':
                self.allowed_movements = {'normal':[(x,y) for x in range(-1,2) for y in range(-1,2) if not (x ==0 and y ==0)]}
                self.allowed_movements['attack'] = self.allowed_movements['normal']
                self.allowed_movements['initial'] = self.allowed_movements['normal']
       

class Board:
    def __init__(self):
        self.dimension_x = 8
        self.dimension_y = 8
        self.tiles = None
        self.build_board()
        return
        
    def build_board(self):
        self.tiles = np.empty((8,8),dtype='object')
        for x in range(0,self.dimension_x):
            for y in range(0,self.dimension_y):
                self.tiles[x,y] = Tile(x,y)
    
    def place_piece_on_board(self,piece):
        self.tiles[piece.loc['x'],piece.loc['y']].put_piece_on_tile(piece)
        
    def remove_piece_from_board(self,piece):
        piece.hide_piece()
        self.tiles[piece.loc['x'],piece.loc['y']].remove_piece_from_tile()
        
    def show_board(self,ax):
        # Create an 8x8 chessboard
        chessboard = np.ones((self.dimension_x,self.dimension_y))

        # Alternate black and white squares
        chessboard[1::2, ::2] = 0
        chessboard[::2, 1::2] = 0
        
        # Create the plot
        ax.imshow(chessboard, cmap='gray')
        ax.axis('on')  # Turn off the axis
            

class Tile:    
    def __init__(self,loc_x,loc_y):
        self.loc = {'x':loc_x,'y':loc_y}
        self.occupied_with = None
        
    def put_piece_on_tile(self,piece):
        self.occupied_with = piece
    
    def remove_piece_from_tile(self):
        self.occupied_with = None
    
    def get_occupation_of_tile(self):
        if self.occupied_with is None:
            return 'empty'
        else:
            return self.occupied_with.name    
        

class Game:    
    def __init__(self,colors):
        self.colors = colors
        self.board = None
        self.__pieces = self.pieces = dict(zip(self.colors, [[] for x in range(len(self.colors))]))
        self.fig, self.ax = plt.subplots()
        self.stack = dict(zip(self.colors, [[] for x in range(len(self.colors))]))
        self.scatter = None
        return
        
    def start_game(self):
        self.board = Board()
        self.__make_all_pieces(1)
        self.__make_all_pieces(2)
        self.put_all_pieces_at_inital_location()
        
    def put_all_pieces_at_inital_location(self):
        for color in self.colors:
            for piece in self.__pieces[color]:
                match piece.type:
                    case 'pawn':
                        piece.initial_loc = {'x':piece.type_idx-1,'y':1+5*(piece.player_id-1)}
                    case 'rook':
                        piece.initial_loc = {'x':0+(piece.type_idx-1)*7,'y':0+7*(piece.player_id-1)}
                    case 'knight':
                        piece.initial_loc = {'x':1+(piece.type_idx-1)*5,'y':0+7*(piece.player_id-1)}
                    case 'bishop':
                        piece.initial_loc = {'x':2+(piece.type_idx-1)*3,'y':0+7*(piece.player_id-1)}
                    case 'queen':
                        piece.initial_loc = {'x':3,'y':0+7*(piece.player_id-1)}
                    case 'king':
                        piece.initial_loc = {'x':4,'y':0+7*(piece.player_id-1)}
                piece.set_location(piece.initial_loc['x'],piece.initial_loc['y'])
                self.board.place_piece_on_board(piece)
     
    def show_move_options(self,pieces,tactic): #FIX THIS ONE
        options = {}
        for piece in pieces:
            suboptions = []
            for movement in piece.allowed_movements['normal'] + piece.allowed_movements['initial'] + piece.allowed_movements['attack']:
                 x = piece.loc['x'] + movement[0]
                 y = piece.loc['y'] + movement[1]
                 try:
                     # self.__validate_beta(x, y,tactic,piece.player_id)
                     tactic = self.__validate_move(piece, x, y)
                 except ValueError as e:
                     print(f" Caught an error: {e}")
                 else:
                     suboptions.append((x,y))
                    
                     # scatter = plt.scatter(x=x,y=y,s=100,marker='*',color=color)
                     # plt.draw()
                     # plt.pause(0.1)
            options[piece.name] = suboptions
            print(piece.name)
            # if self.scatter != None:
            #     self.scatter.remove()
            #     self.scatter = None
            match tactic:
                case 'normal':
                    color = piece.color
                case 'attack': 
                    color = 'yellow'
            self.scatter = plt.scatter(x=[x[0] for x in suboptions],y=[x[1] for x in suboptions],s=100,marker='*',color=color)
            plt.draw()
            plt.pause(0.1)

        return options
                     
     
    def move_piece(self,piece,new_loc_x,new_loc_y):
        try:
          tactic = self.__validate_move(piece,new_loc_x, new_loc_y)
        except ValueError as e:
           print(f'Error occured: {e}') 
           self.show_move_options([self.get_all_pieces_on_board(piece.player_id)[piece.name]],'normal')
           raise
        else:           
           if tactic == 'attack':
               self.__remove_attacked_piece_to_stack(self.board.tiles[new_loc_x,new_loc_y].occupied_with)
           
           self.__move_piece_to_new_location(piece, new_loc_x, new_loc_y)     
                                   
    def show_all(self):
        
        self.board.show_board(self.ax)
        
        for color in self.colors:
            for piece in list(self.get_all_pieces_on_board(1).values()) + list(self.get_all_pieces_on_board(2).values()):
                piece.show_piece(self.ax,False)  
              
        plt.figure(1)
        plt.show()
        plt.pause(0.1)


    def get_all_pieces_on_board(self,player_id):
        pieces = [(tile[0].occupied_with.name,tile[0].occupied_with) for tile in self.board.tiles.reshape(-1,1) if (tile[0].get_occupation_of_tile() != 'empty' and tile[0].occupied_with.player_id==player_id)]
        pieces_player = dict(pieces)
        return pieces_player
    
    def get_all_pieces_in_stack(self,player_id):
        pieces_player_in_stack = [piece.name for piece in self.stack[self.colors[player_id-1]]]
        return pieces_player_in_stack
    
    def play_game_scenario(self,player_moves,pause_time,game_mode):          
        
        match game_mode:
            case 'demo':
                for move_idx in range(len(player_moves[1])):
                    for player_idx in range(len(player_moves)):
                        plt.title(f'Player {player_idx+1} to move',color=self.colors[player_idx])
                        plt.pause(0.001)
                        if move_idx > len(player_moves[player_idx+1])-1:
                            print(f'We arived at move {move_idx} out of {len(player_moves[player_idx+1])-1} for player {player_idx+1}')
                        else:
                            move = player_moves[player_idx+1][move_idx]
                            self.__move_selecter(move,player_idx)
                os.system("pause")
            case 'manual':
                move_idx = 0
                prompt = 'y'
                player_idx = 0
                while prompt != 'n':
                    self.__move_selecter(None, player_idx)
                    move_idx +=1
                    player_idx = 0 if move_idx%2==0 else 1
                    prompt = str(input(f"Do you want to continue? (with player {player_idx+1}):"))
                    

    def __move_selecter(self,move,player_idx):
            # plt.text(-3,-1,f'Stack: {self.get_all_pieces_in_stack(1)}',color=self.colors[0])
            # plt.text(8,-1,f'Stack: {self.get_all_pieces_in_stack(2)}',color=self.colors[1])
            
            try:
                if not isinstance(move,tuple):
                    raise ValueError("this is invalid input")
                  
                if isinstance(move[0],str):
                    piece_name = move[0]
                elif isinstance(move[0],tuple):
                    x_loc_old = move[0][0]
                    y_loc_old = move[0][1]
                    piece_name = self.board.tiles[x_loc_old][y_loc_old].occupied_with.name
                x_loc_new = move[1][0]
                y_loc_new = move[1][1]
                self.move_piece(self.get_all_pieces_on_board(player_idx+1)[piece_name],x_loc_new,y_loc_new)
                
                time.sleep(pause_time)
            except ValueError:
                while True:
                    new_move = eval(input("give a valid move this time ('PieceName',(x,y)): "))
                    if self.scatter != None:
                        self.scatter.remove()
                        self.scatter = None
                    try:
                        if not isinstance(new_move,tuple):
                            raise ValueError("this is invalid input")
                        self.move_piece(self.get_all_pieces_on_board(player_idx+1)[new_move[0]],new_move[1][0],new_move[1][1])
                        break
                    except ValueError:
                        print("That's also not a valid move. Please try again.")

    def add_random_piece(self,name,piece_type,idx,player_id,loc_x,loc_y):
        new_piece = Piece(name,piece_type,idx,self.colors[player_id-1],player_id)
        new_piece.set_location(loc_x, loc_y)
        self.__pieces[new_piece.color].append(new_piece)
        self.board.place_piece_on_board(new_piece)

    def __make_all_pieces(self,player_id):
        new_pieces = []
        for idx in range(1,9):
            new_pieces.append(Piece(f'P{idx}','pawn',idx,self.colors[player_id-1],player_id))     
        for idx in range(1,3):
            new_pieces.append(Piece(f'R{idx}','rook',idx,self.colors[player_id-1],player_id))
            new_pieces.append(Piece(f'N{idx}','knight',idx,self.colors[player_id-1],player_id))
            new_pieces.append(Piece(f'B{idx}','bishop',idx,self.colors[player_id-1],player_id))
        new_pieces.append(Piece('Q','queen',1,self.colors[player_id-1],player_id))
        new_pieces.append(Piece('K','king',1,self.colors[player_id-1],player_id))
        self.__pieces[self.colors[player_id-1]] = new_pieces


    def __validate_move(self,piece,new_loc_x,new_loc_y): #player_id is part of piece
        
        if new_loc_x not in range(0,self.board.dimension_x) or new_loc_y not in range(0,self.board.dimension_y):
            raise ValueError(f'x={new_loc_x},y={new_loc_y}: This location exceeds the board dimensions')
        
        delta_x = new_loc_x - piece.loc['x']
        delta_y = new_loc_y - piece.loc['y']
        
        if piece.type in ['rook','bishop','queen']:
            path = self.__get_path((piece.loc['x'],piece.loc['y']), (new_loc_x,new_loc_y),piece.type)
            for tile in path:
                if self.board.tiles[tile[0]][tile[1]].get_occupation_of_tile() != 'empty':
                    raise ValueError(f'Move {piece.name} to x={new_loc_x},y={new_loc_y} is not valid because there is an occupied tile on its path')
                    
            
            
        if (delta_x,delta_y) in piece.allowed_movements['normal']:
            if self.board.tiles[new_loc_x,new_loc_y].get_occupation_of_tile() == 'empty':
                return 'normal'
            elif self.board.tiles[new_loc_x,new_loc_y].occupied_with.player_id == piece.player_id: 
                raise ValueError(f'Move {piece.name} to x={new_loc_x},y={new_loc_y} is not valid because the field is already ocipied by one of your pieces')
            elif self.board.tiles[new_loc_x,new_loc_y].occupied_with.player_id != piece.player_id:
                if (delta_x,delta_y) in piece.allowed_movements['attack']:
                    print('you can attack your opponent')
                    return 'attack'
                else:
                    raise ValueError(f'Move {piece.name} to x={new_loc_x},y={new_loc_y} is not valid because the field is already ocipied by one of your opponents pieces')
        elif (delta_x,delta_y) in piece.allowed_movements['initial']:
            if piece.loc != piece.initial_loc:
                raise ValueError(f'Move {piece.name} to x={new_loc_x},y={new_loc_y} is not valid because {piece.name} is no longer on its initial spot')
            elif self.board.tiles[new_loc_x,new_loc_y].get_occupation_of_tile() == 'empty':
                return 'normal'
            elif self.board.tiles[new_loc_x,new_loc_y].occupied_with.player_id == piece.player_id: 
                raise ValueError(f'Move {piece.name} to x={new_loc_x},y={new_loc_y} is not valid because the field is already ocipied by one of your pieces')
            elif self.board.tiles[new_loc_x,new_loc_y].occupied_with.player_id == piece.player_id:
                raise ValueError(f'Move {piece.name} to x={new_loc_x},y={new_loc_y} is not valid because the field is already ocipied by one of your opponents pieces')
        elif (delta_x,delta_y) in piece.allowed_movements['attack']:
            if self.board.tiles[new_loc_x,new_loc_y].get_occupation_of_tile() != 'empty':
                if self.board.tiles[new_loc_x,new_loc_y].occupied_with.player_id != piece.player_id:
                    print('you can attack your opponent')
                    return 'attack'
                elif self.board.tiles[new_loc_x,new_loc_y].occupied_with.player_id == piece.player_id:
                    raise ValueError(f"You cannot attack (x={new_loc_x},y={new_loc_y}) with {piece.name} because it has a piece ({self.board.tiles[new_loc_x,new_loc_y].occupied_with.name} from yourself")
            else:
                raise ValueError(f"You cannot attack (x={new_loc_x},y={new_loc_y}) with {piece.name} because it is empty")
        else:
            raise ValueError(f'Move {piece.name} to x={new_loc_x},y={new_loc_y} is not valid because it is outside the allowed range of {piece.name}')
            

            
    def __move_piece_to_new_location(self,piece,new_loc_x,new_loc_y):
        self.board.remove_piece_from_board(piece)
        piece.set_location(new_loc_x,new_loc_y)
        self.board.place_piece_on_board(piece)
        piece.show_piece(self.ax,True)
        
    def __remove_attacked_piece_to_stack(self,piece):
        self.board.remove_piece_from_board(piece)
        piece.set_location(None,None)
        self.stack[piece.color].append(piece)
        
        
    def __get_path(self,start, end,piece_type):

        path = []
        start_x, start_y = start
        end_x, end_y = end
        
        # Horizontal or vertical movement (rook-like)
        if piece_type in ['rook','queen']:
            if start_x == end_x:
                if start_y < end_y:
                    path = [(start_x, y) for y in range(start_y + 1, end_y)]
                else:
                    path = [(start_x, y) for y in range(start_y - 1, end_y, -1)]
            elif start_y == end_y:
                if start_x < end_x:
                    path = [(x, start_y) for x in range(start_x + 1, end_x)]
                else:
                    path = [(x, start_y) for x in range(start_x - 1, end_x, -1)]
            
        # Diagonal movement (bishop-like)
        if piece_type in ['bishop','queen']:
            if abs(start_x - end_x) == abs(start_y - end_y):
                step_x = 1 if end_x > start_x else -1
                step_y = 1 if end_y > start_y else -1
                x, y = start_x + step_x, start_y + step_y
                while (x, y) != (end_x, end_y):
                    path.append((x, y))
                    x += step_x
                    y += step_y
    
        return path

class hystorical_data():
        
    def __init__(self):
        return
    
    def get_data_from_kaggle(self):
        chess_games =  pd.read_csv(r"C:\Users\rbijman\OneDrive - ALTEN Group\Documents\Projects\Python\Chess\games.csv")
        return chess_games        
    
    def __algebraic_to_coordinates(self,move, board):
        try:
            chess_move = board.push_san(move)  # This will parse the move in algebraic notation
            start_square = chess_move.from_square
            end_square = chess_move.to_square
            return (chess.square_file(start_square), chess.square_rank(start_square)), (chess.square_file(end_square), chess.square_rank(end_square))
        except ValueError as e:
            print(f"Invalid move {move}: {e}")
            return None

    def convert_to_coordinates(self,game_moves,print_coordinates):
        move_coordinates = []
        # Initialize the chess board
        board = chess.Board()
        
        # Example game moves in algebraic notation

        
        for move in game_moves:
            coordinates = self.__algebraic_to_coordinates(move, board)
            if coordinates and print_coordinates:
                start, end = coordinates
                print(f"Move: {move} | Start: {start} → End: {end}")
            move_coordinates.append(coordinates)
        return move_coordinates
    
    def split_coordinates_in_player_moves(self,coordinates):
        player_moves = {1:[],2:[]}
        for move_idx, move in enumerate(coordinates):
            player_idx = 1 if move_idx%2==0 else 2
            player_moves[player_idx].append(move)
        return player_moves


hyst_data = hystorical_data()
chess_games = hyst_data.get_data_from_kaggle()
moves = chess_games.iloc[2].moves
moves = moves.split()

coordinates = hyst_data.convert_to_coordinates(moves,print_coordinates=False)
player_moves2 = hyst_data.split_coordinates_in_player_moves(coordinates)

#%%
#Game scenario
player_moves = {}
player_moves[1] = [('P3',(2,2)),('P3',(2,4)),('N1',(2,2)),('P3',(3,4))]
player_moves[2] = [('P4',(3,5)),('P4',(3,4)),('N1',(2,5)),('P1',(1,1))]
     
plt.close()
pause_time = 0.1
game1 = Game(['green','red'])
game1.start_game()
game1.show_all()

game_mode = input("What is the game_mode you want?:") or 'demo'
game1.play_game_scenario(player_moves2, pause_time, game_mode)  

print('Pieces in stack- player1:', game1.get_all_pieces_in_stack(1), 'player2:' ,game1.get_all_pieces_in_stack(2))


# os.system("pause")






#game1.add_random_piece('test', 'king', 3, 2, 1,3)
#game1.add_random_piece('Erik', 'king2', 3, 2, 2,3)

