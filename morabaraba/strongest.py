from math import exp
from core import Color
import random
from morabaraba.morabaraba_player import MorabarabaPlayer
from morabaraba.morabaraba_action import MorabarabaAction
from morabaraba.morabaraba_action import MorabarabaActionType
from morabaraba.morabaraba_rules import MorabarabaRules
from morabaraba.morabaraba_board import MorabarabaBoard

def is_making_mill(board,player,cell)  :   
    player_mills = []
    pieces = board.get_player_pieces_on_board(Color(player))
    mills = board.mills()
    for mill in mills:
        if cell in mill: 
            is_mill = True
            for mill_cell in mill:
                if mill_cell not in pieces and mill_cell != cell : is_mill =  False   
            if is_mill == True: 
                 player_mills.append(mill)

    if len(player_mills) == 0: is_player_mill = False 
    else : is_player_mill = True 
    return [ is_player_mill , player_mills ]


def fly(board,player,actions):
    for action in actions:
        if is_making_mill(board,player, action.get_action_as_dict()['action']['to'])[0]:
            return action
    for action in actions:
        if is_making_mill(board,-1*player, action.get_action_as_dict()['action']['to'])[0]:
            return action
    return False

def is_occasions(board,player):
    pieces = board.get_player_pieces_on_board(Color(player))
    adv_pieces = board.get_player_pieces_on_board(Color(-1*player))
    piece_occasions = []
    occasions_mill = []
    for mill in board.mills():
        if all([adv_piece not in mill for adv_piece in adv_pieces]) and len([i for i in set(pieces) & set(mill)]) > 1:
            for mill_cell in mill:
                if mill_cell not in board.get_all_empty_cells():
                    piece_occasions.append(mill_cell)
                    return [True,piece_occasions]
    return [False,[]]
        
def ADD(board,player,actions) :
    k=-1
    for cell in board.get_all_empty_cells() :
        k+=1
        if is_making_mill(board,player,cell)[0]==True :
            return actions[k] 
    return False

def STEAL(board,player,actions) :
    #to check if the opoenent want to do mill
    steal = is_occasions(board,-1*player)
    if steal[0]:
        for piece in steal[1]:
            if any(is_making_mill(board,-1*player,move) for move in get_effective_cell_moves(board,piece)):
                for action in actions:
                    if action.get_action_as_dict()['action']['at'] == piece:
                        return action
        occurences = [steal[1].count(i) for i in steal[1]]
        for action in actions:
            if action.get_action_as_dict()['action']['at'] == steal[1][occurences.index(max(occurences))]:
                return action
    for cell in board.get_all_empty_cells() :
        mills=is_making_mill(board,player,cell) 
        if mills[0]==True :
            for mill_cell in mills[1][0] :
                if mill_cell != cell and is_making_mill(board,player,mill_cell)[0]:
                    for action in actions:
                        if action.get_action_as_dict()['action']['at'] == mill_cell :
                            return action
                elif mill_cell != cell:
                    for action in actions:
                        if action.get_action_as_dict()['action']['at'] == mill_cell :
                            return action
    for action in actions:
        for piece in board.get_player_pieces_on_board(Color(player)):
            if is_making_mill(board,player, action.get_action_as_dict()['action']['at'])[0]:
                if any([action.get_action_as_dict()['action']['at'] == move for move in get_effective_cell_moves(board,piece)]):
                    return action                        
            elif is_making_mill(board,player, action.get_action_as_dict()['action']['at'])[0]:
                return action
     
    return False 

def block_oponent(board,player,actions):
    good_occasion = []
    pieces = board.get_player_pieces_on_board(Color(-1*player))
    adv_pieces = board.get_player_pieces_on_board(Color(player))

    for mill in board.mills():
            for piece in pieces:
                if all([piece in mill and adv_piece not in mill for adv_piece in adv_pieces]):
                    for cell in mill:
                        if cell in board.get_all_empty_cells(): 
                            good_occasion.append(cell)
    if good_occasion:
        occurences = [good_occasion.count(i) for i in good_occasion]
        return [True,occurences,good_occasion]
    return [False]
    

def make_occasion_add(board,player, actions):
    good_occasion = []
    opoenent_occasions = []
    opoenent_occurences = []
    pieces = board.get_player_pieces_on_board(Color(player))
    adv_pieces = board.get_player_pieces_on_board(Color(-1*player))
    for mill in board.mills():
            for piece in pieces:
                 if all([piece in mill and adv_piece not in mill for adv_piece in adv_pieces]):
                    for cell in mill:
                        if cell in board.get_all_empty_cells(): 
                            good_occasion.append(cell)
    if good_occasion:
        occurences = [good_occasion.count(i) for i in good_occasion]
        block = block_oponent(board,player,actions)
        if block[0]:
            opoenent_occasions = block[2]
            opoenent_occurences = block[1]
        if max(occurences) < 2 and len(opoenent_occasions) > 0:
            intersection = [i for i in set(good_occasion) & set(opoenent_occasions)]
            if len(intersection) > 0:
                occ = [intersection.count(i) for i in intersection]
                for action in actions:
                    if action.get_action_as_dict()['action']=={'to': intersection[occ.index(max(occ))]}:
                        return action
            else:
                for action in actions:
                    if action.get_action_as_dict()['action']=={'to': opoenent_occasions[opoenent_occurences.index(max(opoenent_occurences))]}:
                        return action
        for action in actions:
            if action.get_action_as_dict()['action']=={'to': good_occasion[occurences.index(max(occurences))]}:
                return action
    return False
        
def get_effective_cell_moves(board, cell):
        if board.is_cell_on_board(cell):
            possibles_moves = MorabarabaRules.get_rules_possibles_moves(cell, board)
            effective_moves = []
            for move in possibles_moves:
                if board.is_empty_cell(move):
                    effective_moves.append(move)
            return effective_moves 

def player_mill(board,player):
    p_mills = []
    pieces = board.get_player_pieces_on_board(Color(player))
    for mill in board.mills():
        if mill[0] in pieces and mill[1] in pieces and mill[2] in pieces:
            p_mills.append(mill)
    return p_mills

def Check_Move(state,board,player,actions) :
        for cell in board.get_all_empty_cells() :
            mills=is_making_mill(board,player,cell) 
            if mills[0]==True :
                for mill in mills[1] :
                    for action in actions :
                        if action.get_action_as_dict()['action']['to'] == cell and action.get_action_as_dict()['action']['at'] not in mill  :
                            return action
        adv_actions = MorabarabaRules(-1*player).get_player_actions(state,-1*player)
        for cell in board.get_all_empty_cells() :
            mills=is_making_mill(board,-1*player,cell) 
            if mills[0]==True :
                for mill in mills[1] :
                    for adv_action in adv_actions:
                        if adv_action.get_action_as_dict()['action']['to'] == cell and adv_action.get_action_as_dict()['action']['at'] not in mill :
                            for action in actions:
                                if action.get_action_as_dict()['action']['to'] == cell:
                                    return action
        pieces = board.get_player_pieces_on_board(Color(player))
        cells = []
        movable_pieces = []
        movables = [get_effective_cell_moves(board,piece) for piece in pieces]
        for movable in movables:
            for movable_piece in movable:
                if movable_piece in cells:
                    movable_pieces.append(movable_piece)
                cells.append(movable_piece)
        if movable_pieces : 
            for action in actions:
                if action.get_action_as_dict()['action']['at'] == movable_pieces[0]:
                    return action
        return False

def choix(state, player, action_pre):
    board = state.get_board()
    possibles_moves = get_effective_cell_moves(board,action_pre.get_action_as_dict()['action']['at'])
    for move in possibles_moves:
        board.empty_cell(action_pre.get_action_as_dict()['action']['at'])
        board.fill_cell(move, Color(player))
        state.set_board(board)
        actions = MorabarabaRules(player).get_player_actions(state,player)
        for cell in board.get_all_empty_cells():
            mills=is_making_mill(board,player,cell) 
            if mills[0]==True :
                for mill in mills[1] :
                    for action in actions :
                        if action.get_action_as_dict()['action']['to'] == cell and action.get_action_as_dict()['action']['at'] not in mill and (action.get_action_as_dict()['action']['at'] == move or move in mill):
                            if all([adv_action.get_action_as_dict()['action']['to'] != cell for adv_action in MorabarabaRules(-1*player).get_player_actions(state,-1*player)]):
                                return [True,[move]] 
                            return [True,1]
    return [False,0]

def create_win(board,player,actions,state):
    adv_possible_destination = []
    for piece in board.get_player_pieces_on_board(Color(player)):
        for move in MorabarabaRules.get_rules_possibles_moves(piece,board):
            adv_possible_destination.append(move)
    for mill in player_mill(board,player):
        for cell in mill:
            for action in actions:
                if action.get_action_as_dict()['action']['at'] == cell:
                    if all([piece != cell for piece in adv_possible_destination]):
                        
                        return [True,action]
    return [False]
                  
def Check_block(actions,board,player):
    for action in actions:
        if is_making_mill(board,-1*player,action.get_action_as_dict()['action']['at'])[0]:
            if len(actions) > 1:
              
                actions.remove(action)
    return actions

def play(state, player):

    actions = MorabarabaRules(player).get_player_actions(state,player)
    board = state.get_board()

    if len(actions)==0:
        return None
    else:
        if actions[0].get_action_as_dict()['action_type'] == MorabarabaActionType.MOVE:
            action_choice=Check_Move(state,board,player,actions)
            if action_choice != False :
                 return action_choice
            action_choice=Check_Move(state,board,-1*player,actions)
            if action_choice != False :
                return action_choice
            if create_win(state.get_board(),player,actions,state)[0]:
                return create_win(state.get_board(),player,actions,state)[1]
            elif action_choice == False:
                for action in actions:
                    choice = choix(state, player, action)
                    if choice[0] == True and choice[1] != 1:
                        for action in actions:
                            if  action.get_action_as_dict()['action']['to'] == choice[1]:
                                return action
                    elif choice[1] == 1:
                        return action
                actions = Check_block(actions, state.get_board(),player)
                import random
    
                return random.choice(actions)
            else:
                import random
    
                return random.choice(actions)
        elif actions[0].get_action_as_dict()['action_type'] == MorabarabaActionType.ADD:
            action_choice=ADD(board,player,actions)
            if action_choice != False :
                 return action_choice
            action_choice=ADD(board,-1*player,actions)
            if action_choice != False :
                return action_choice
            action = make_occasion_add(board,player,actions)
            if action != False:
                return action
            import random
            for action in actions:
                if action.get_action_as_dict()['action']['to'] == random.choice([(1,5),(5,1),(1,1),(5,5)]):
                
                    return action
        elif actions[0].get_action_as_dict()["action_type"] == MorabarabaActionType.STEAL: 
            action_choice=STEAL(board,player*-1,actions)
            if action_choice != False :
                return action_choice
            import random 

            return random.choice(actions)
        elif actions[0].get_action_as_dict()["action_type"] == MorabarabaActionType.FLY: 
            if fly(board,player,actions) != False:
                return fly(board,player,actions)
            import random 

            return random.choice(actions)
        import random 
        return random.choice(actions)
            
class AI(MorabarabaPlayer):
    name = "strongest"

    def __init__(self, color):  
        super(AI, self).__init__(color)
        self.position = color.value

    def play(self, state, remain_time):
        
        return play(state, self.position)