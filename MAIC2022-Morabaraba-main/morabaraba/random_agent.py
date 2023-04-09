from morabaraba.morabaraba_player import MorabarabaPlayer
from morabaraba.morabaraba_action import MorabarabaAction
from morabaraba.morabaraba_action import MorabarabaActionType
from morabaraba.morabaraba_rules import MorabarabaRules
from core import Color
import random


class AI(MorabarabaPlayer):
    name = "SGCM 1"

    def __init__(self, color):  
        super(AI, self).__init__(color)
        self.position = color.value

    def play(self, state, remain_time): 
        # try:
            print("Joueur 1")
            rules=MorabarabaRules(self.position)
            board=state.get_board()
            actions=rules.get_player_actions(state,self.position)
            if actions[0].get_action_as_dict()["action_type"] == MorabarabaActionType.ADD :
                action_choice=ADD(state,self.position,actions)
                if action_choice != False :
                    return action_choice
                action_choice=more_occasion(state,-1*self.position,actions)
                if action_choice != False :
                    return action_choice
                action_choice=ADD_block(state,-1*self.position,actions)
                if action_choice != False :
                    return action_choice
                return Make_occasion(rules,state,self.position,actions)
            elif actions[0].get_action_as_dict()["action_type"] == MorabarabaActionType.STEAL  : 
                action_choice=STEAL(rules,state,-1*self.position,actions)
                if action_choice != False :
                    return action_choice
                return MorabarabaRules.random_play(state, self.position)
            elif actions[0].get_action_as_dict()["action_type"] == MorabarabaActionType.MOVE:
                action_choice=Move(state,rules,actions,self.position,self.position)
                if action_choice != False :
                    return action_choice
                action_choice=Move(state,rules,actions,-1*self.position,self.position)
                if action_choice != False :
                    return action_choice
                return Make_occasion(rules,state,self.position,actions)
            else :
                action_choice=Move(state,rules,actions,self.position,self.position)
                if action_choice != False :
                    return action_choice
                action_choice=Move(state,rules,actions,-1*self.position,self.position)
                if action_choice != False :
                    return action_choice
                return Make_occasion(rules,state,self.position,actions)
        # except:
        #     rules=MorabarabaRules(self.position)
        #     actions=rules.get_player_actions(state,self.position)
        #     print("\n\n exception")
        #     return random.choice(actions)

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

def is_effective_making_mill(state,player,rules,cell,mill) :
    actions=rules.get_player_actions(state,player)
    is_mill=False
    for action in actions :
        if action.get_action_as_dict()['action']['to'] == cell and action.get_action_as_dict()['action']['at'] not in mill and is_mill == False:
            is_mill=True
    return is_mill

def ADD(state,player,actions) :
    board=state.get_board()
    cells=[]
    for cell in board.get_all_empty_cells() :
        if is_making_mill(board,player,cell)[0] == True :
            cells.append(cell)

    if len(cells) == 0 :
        return False
    else :
        choices=ADD_and_Ocassion(state,player)
        choice=[cell for cell in cells if cell in choices]
        if len(choice) == 0 :
            choices=ADD_and_Ocassion(state,-player)
            choice=[cell for cell in cells if cell in choices]
            if len(choice) == 0 :
                choice=cells[0]
            else :
                choice=choice[0]
        else :
            choice=choice[0]
        for action in actions :
            if action.get_action_as_dict()["action"]["to"] == choice :
                return action

def ADD_block(state,player,actions) :
    board=state.get_board()
    cells=[]
    for cell in board.get_all_empty_cells() :
        if is_making_mill(board,player,cell)[0] == True :
            cells.append(cell)

    if len(cells) == 0 :
         return False
    else :
        my_potential_occasion,my_occasions=Occasion(state,-player)
        choices=[cell for cell in set(my_occasions) & set(cells)]
        
        if len(choices) == 0 :
             choices=ADD_and_Ocassion(state,-player)
             choice=[cell for cell in cells if cell in choices]
             if len(choice) == 0 :
                choices=ADD_and_Ocassion(state,player)
                choice=[cell for cell in cells if cell in choices]
                if len(choice) == 0 :
                    choice=cells[0]
                else :
                    choice=choice[0]
             else :
                choice=choice[0]
        else :
            choice=choices[0]

        for action in actions :
            if action.get_action_as_dict()["action"]["to"] == choice :
                return action

def try_again(state,occasions,adverse_occasions,double,player) :
    board=state.get_board()
    for occasion in occasions :
        board.fill_cell(occasion,Color(player))
        cells=cells_make_mill(board,player)
        board.empty_cell(occasion)
        if len(set(cells) & set(adverse_occasions)) == 0 and len(set(cells) & set(double)) :
            return occasion
    return False

def ADD_and_Ocassion(state,player) :
    my_potential_occasion,my_occasions=Occasion(state,player)
    adverse_potential_occasion,adverse_occasions=Occasion(state,-1*player)
    choice=[]
    enter=False
    if (len(my_occasions) == 0 and len(adverse_occasions) == 0 ) :
            choice=[(5,1),(1,5)]
    elif len(my_occasions) == 0 and len(adverse_occasions) != 0 :
        if state.get_player_info(player)["in_hand"] == 12 :
            choice=[(5,1),(1,5)]
        else :
            choice=[adverse_potential_occasion[1]]
    elif len(my_occasions) != 0 and len(adverse_occasions) == 0 :
        choice=[my_potential_occasion[1]]
    else :
        if my_potential_occasion[0] >= adverse_potential_occasion[0] and my_potential_occasion[0] != 1 :
            choice=[my_potential_occasion[1]]
        elif adverse_potential_occasion[1] in my_occasions and adverse_potential_occasion[0] !=1 :
            choice=[adverse_potential_occasion[1]]
        elif adverse_potential_occasion[0] > my_potential_occasion[0] :
            if adverse_potential_occasion[2] > 1 :
                enter = True
                choice=[try_again(state,my_occasions,adverse_occasions,double(state,-player),player)]
            if len(choice) == 0 or (enter == True and choice[0] == False):
                my_occasions.insert(0,my_potential_occasion[1])
                choice=[block_double(state,my_occasions,player)]
                if choice[0] == False :
                    choice=[adverse_potential_occasion[1]]
        else :
            choice=[cell for cell in my_occasions if cell in adverse_occasions]
            if len(choice) == 0 :
                 if player == -1 :
                    cells=get_single_in_mill(state,-1*player)
                    my_double=double(state,player)
                    if len(choice) == 0 :
                        choice=[x for x in set(my_occasions) & set(my_double)]
                    if len(choice) == 0 :
                        choice=[x for x in set(my_double) & set(cells)]
                    if len(choice) == 0 :
                        choice=my_double
                    if len(choice) == 0 :
                        choice=list(reversed(my_occasions))
                 else :
                    cells=get_single_in_mill(state,-player)
                    my_double=double(state,player)
                    choice=[x for x in set(adverse_occasions) & set(cells) & set(my_double)]
                    if len(choice) == 0 :
                        choice=[x for x in set(adverse_occasions) & set(my_double)]
                    if len(choice) == 0 :
                        choice=[x for x in set(my_double) & set(cells)]
                    if len(choice) == 0 :
                        choice=my_double
                    if len(choice) == 0 :
                        choice=list(reversed(adverse_occasions))
                
    return choice

def double(state,player) :
    cells=[]
    board=state.get_board()
    for cell in board.get_all_empty_cells() :
        board.fill_cell(cell,Color(player))
        state.set_board(board)
        luck,occasions=Occasion(state,player)
        if luck[0] > 1 and luck[1] not in cells_make_mill(board,player):
            cells.append(cell)
        board.empty_cell(cell)
    return cells

def block_double(state,cells,player) :
    board=state.get_board()
    for cell in cells :
        board.fill_cell(cell,Color(player))
        state.set_board(board)
        luck,adverse_occasions=Occasion(state,-player)
        board.empty_cell(cell)
        if luck[0] < 2 :
            return cell
    return False

def cells_make_mill(board,player) :
    cells=[]
    for cell in board.get_all_empty_cells() :
        if is_making_mill(board,player,cell)[0] == True :
            cells.append(cell)
    return cells

def get_single_in_mill(state,player) :
    all_mills=get_piece_mills(state,player,1) 
    cells=[]
    if all_mills :
         for mill in all_mills :
            cells.append(mill[1])
            cells.append(mill[2])
    return cells

def STEAL(rules,state,player,actions) :
    board=state.get_board()
    if state.get_latest_move()['action_type'] ==  "ADD" :
        choice=""
        in_between_more_my_piece,in_between_my_piece,in_double_occasion=In_between_my_piece(board,player)
        potential_fatal_cell,fatal_cells=Fatal_cells(board,player)
        adverse_potential_occasion,adverse_occasions=Occasion(state,player)
        if len(in_between_my_piece) == 0 and len(fatal_cells) == 0 and len(adverse_occasions) !=0 :
            choice=Cell(board,player,adverse_potential_occasion[1])
        elif len(in_between_my_piece) == 0 and len(fatal_cells) !=0 :
            choice=potential_fatal_cell[1]
        elif len(in_between_my_piece) !=0 and len(fatal_cells) == 0 :
            if len(adverse_occasions) == 0 and in_double_occasion[0] == True:
                choice=in_double_occasion[1][0]
            else :
                choice=in_between_more_my_piece[1]
        elif len(in_between_my_piece) !=0 and len(fatal_cells) !=0 and potential_fatal_cell[1] in in_between_my_piece :
            choice=potential_fatal_cell[1]
        elif len(in_between_my_piece) !=0 and len(fatal_cells) !=0 and potential_fatal_cell[1] not in in_between_my_piece :
            intersection=[x for x in in_between_my_piece if x in fatal_cells]
            if len(intersection) !=0 :
                choice=intersection[0]
            else :
                choice=in_between_more_my_piece[1]
        else :
            choice=(6,0)
        for action in actions :
            if action.get_action_as_dict()['action']['at'] == choice :
                return action

    else :
        piece=steal_move(rules,state,player)
        print("\n\n",piece)
        if piece != False :
            for action in actions :
                if action.get_action_as_dict()['action']['at'] == piece :
                    return action
        else :
            player_mills=board.player_mills(-1*player)
            if len(player_mills) != 0 :
                for player_mill in player_mills :
                    for mill_cell in player_mill :
                        mills=[mill for mill in board.mills() if mill_cell in mill and mill not in player_mills] 
                        for mill in mills :
                            for cell in mill :
                                if cell in board.get_player_pieces_on_board(Color(player)) and free(state,rules,cell,player) in [True,1]:
                                    for action in actions :
                                        if action.get_action_as_dict()['action']['at'] == cell :
                                                return action
            else :
                for cell in board.get_all_empty_cells() :
                    mills=is_making_mill(board,player,cell) 
                    if mills[0]==True :
                        for mill_cell in mills[1][0] :
                            if mill_cell != cell :
                                for action in actions :
                                    if action.get_action_as_dict()['action']['at'] == mill_cell :
                                        return action
    return actions[0]

def free(state,rules,cell,player) :
    board=state.get_board()
    pieces=board.get_player_pieces_on_board(Color(player))
    cells=rules.get_rules_possibles_moves(cell, board)
    inter=[cell for cell in cells if cell in pieces]

    if len(inter) == 0 :
        print("\n\n il peut pas venir au",cell)
        return True
    else :
        intersection=[]
        for mill in board.player_mills(player) :
            for mill_cell in mill :
                if mill_cell in inter :
                    intersection.append(mill_cell)  
        if intersection :
            # cells=rules.get_rules_possibles_moves(intersection[0], board)
            # inter=[cell for cell in cells if cell in board.get_player_pieces_on_board(Color(-1*player))]
            # if inter :
            #     print("\n\nil est dans un mill et s'il vient me bloquer j'irai le bloquer aussi ",cell)
            #     return 1
            # print("\n\n il est dans un mill et peut mais je peux pas aller détruit son mill",cell)
            return False
        else :
            print("\n\n il n'est pas dans un mill mais il peut venir au",cell)
            return 1

def get_effective_cell_moves(board, cell) :
    if board.is_cell_on_board(cell):
        possibles_moves = MorabarabaRules.get_rules_possibles_moves(cell, board)
        effective_moves = []
        for move in possibles_moves:
            if board.is_empty_cell(move):
                effective_moves.append(move)
        return effective_moves 

def get_effective_cell_moves_improve(state,cell,player) :
    board=state.get_board()

    actions = MorabarabaRules.get_player_actions(state,player)
    effective_moves = []
    for action in actions :
        if action.get_action_as_dict()["action"]["at"] == cell :
            effective_moves.append(action.get_action_as_dict()["action"]["to"])
    return effective_moves 

def steal_move(rules,state,player) :
    board=state.get_board()
    all_pieces=board.get_player_pieces_on_board(Color(player))
    player_mills=board.player_mills(player)
    pieces_mills=[]
    mills=[]
    cells_mill=[]
    is_mill=False

    if len(board.get_player_pieces_on_board(Color(player))) == 4 :
        print("\n\n Nouvelle notion")
        all_mills=get_piece_mills(state,player,2)
        if len(all_mills) != 0 :
          print("\n\n ça fait mal")
          return all_mills[0][1] 


    for mill in player_mills :
        for mill_cell in mill :
           pieces_mills.append(mill_cell)  

    pieces=[x for x in all_pieces if x not in pieces_mills]

    for piece in all_pieces :
        cells=get_effective_cell_moves_improve(state,piece,player)
        for cell in cells :
            mills=is_making_mill(board,player,cell)
            if mills[0] == True and (len([mill for mill in mills[1] if piece in mill and cell in mill]) == 0 or len(mills[1])>=2) and is_mill==False:
                is_mill=True

    if is_mill == True :

        piece=destroy_more_mill(state,player,rules)
        if piece != False :
            return piece
        
        for piece in pieces_mills :
            cells=get_effective_cell_moves_improve(state,piece,player)
            for cell in cells :
                mills=is_making_mill(board,player,cell)
                if mills[0] == True and (len([x for x in mills[1] if piece in x and cell in x]) == 0 or len(mills[1])>=2) :
                    for mill in mills[1] :
                        for mill_cell in mill :
                            if mill_cell != cell :
                                print("\n\n no vas et viens")
                                return mill_cell

        for piece in pieces :
            cells=get_effective_cell_moves_improve(state,piece,player)
            for cell in cells :
                mills=is_making_mill(board,player,cell)
                if mills[0] == True and len(mills[1])>=2 and (len([mill for mill in mills[1] if piece in mill and cell in mill]) == 0 or len(mills[1])>=2):
                    print("\n\n donc c'est toi")
                    return piece

        for piece in pieces :
            cells=get_effective_cell_moves_improve(state,piece,player)
            for cell in cells :
                mills=is_making_mill(board,player,cell)
                if mills[0] == True and (len([mill for mill in mills[1] if piece in mill and cell in mill]) == 0 or len(mills[1])>=2) :
                    return piece
    else :
        print("\n\n je peux manger au prochaine cours")
        my_pieces=board.get_player_pieces_on_board(Color(player*-1))
        board_mills=board.mills()
        pity=[]
        for piece in pieces :
            cond=free(state,rules,piece,player) 
            if cond  != False :
                new_pieces=[x for x in rules.get_rules_possibles_moves(piece,board) if x in my_pieces]
                board.empty_cell(piece)
                state.set_board(board)
                for my_piece in new_pieces :
                    cells=get_effective_cell_moves_improve(state,my_piece,-1*player)
                    for cell in cells :
                        mills=is_making_mill(board,player*-1,cell)
                        if mills[0] == True and (len([mill for mill in mills[1] if my_piece in mill and cell in mill]) == 0 or len(mills[1])>=2) :
                            if cond == True :
                                print("\n\n je le suprime kabo kabo",cond,piece)
                                return piece
                            else :
                                pity.append(piece)
                board.fill_cell(piece,Color(player))
                state.set_board(board)
          
        is_mill=False
        for piece in all_pieces :
            cells=rules.get_effective_cell_moves(state,piece)
            for cell in cells :
                mills=is_making_mill(board,player,cell)
                if mills[0] == True and (len([mill for mill in mills[1] if piece in mill and cell in mill]) == 0 or len(mills[1])>=2) and is_mill==False:
                    is_mill=True

        if is_mill == True :

            for piece in pieces :
                is_mill=False
                board.empty_cell(piece)
                for x in [y for y in pieces if y != piece] :
                    if is_mill == False :
                        cells=get_effective_cell_moves(board,x)
                        for cell in cells :
                            mills=is_making_mill(board,player,cell)
                            if mills[0] == True and (len([mill for mill in mills[1] if x in mill and cell in mill]) == 0 or len(mills[1])>=2) and is_mill == False:
                                is_mill=True
                board.fill_cell(piece,Color(player))
                if is_mill == False :
                    return piece
            state.set_board(board)
            
            for piece in pieces_mills :
                cells=rules.get_effective_cell_moves(state,piece)
                for cell in cells :
                    mills=is_making_mill(board,player,cell)
                    if mills[0] == True and (len([x for x in mills[1] if piece in x and cell in x]) == 0 or len(mills[1])>=2) :
                        for mill in mills[1] :
                            for mill_cell in mill :
                                if mill_cell != cell :
                                    print("\n\n no vas et viens")
                                    return mill_cell

            for piece in pieces :
                cells=rules.get_effective_cell_moves(state,piece)
                for cell in cells :
                    mills=is_making_mill(board,player,cell)
                    if mills[0] == True and len(mills[1])>=2 and (len([mill for mill in mills[1] if piece in mill and cell in mill]) == 0 or len(mills[1])>=2):
                        return piece

            for piece in pieces :
                cells=rules.get_effective_cell_moves(state,piece)
                for cell in cells :
                    mills=is_making_mill(board,player,cell)
                    if mills[0] == True and (len([mill for mill in mills[1] if piece in mill and cell in mill]) == 0 or len(mills[1])>=2) :
                        return piece

        if len(pity) != 0 :
            return pity[0]
            
    print("\n\nno comprend")
    
    return False
     
def Move(state,rules,actions,player_current,player) :
   board=state.get_board()
   if player == player_current :
        actions_mill=get_actions_can_make_mill(player,state,rules)
        if len(actions_mill) == 0 :
            return False
        elif len(actions_mill) == 1 :
            if len(get_actions_can_make_mill(-1*player,state,rules)) == 0 and free(state,rules,actions_mill[0].get_action_as_dict()["action"]["to"],-1*player) == True :
                mill=save_mills(state,player)[1]
                rest_moves=[x for x in which_move(state,rules,actions,player) if x not in mill]
                if len(rest_moves) != 0 :
                    at,to=ordinateur(state,rules,rest_moves,player,mill)
                    if at != False :
                        for action in actions :
                            if action.get_action_as_dict()['action']['to'] == to and action.get_action_as_dict()['action']['at'] == at :
                                return action

            return actions_mill[0]
        else :
            luck,pity=move_and_occasion(actions_mill,state,rules,player)
            if len(luck) != 0 :
                return luck[0]
            elif len(pity) != 0 :
                return pity[0]
            else :
                for action in actions_mill :
                    if free(state,rules,actions_mill[0].get_action_as_dict()["action"]["at"],-player) != False :
                        return action
                return actions_mill[0]

   else :
        for cell in board.get_all_empty_cells() :
            mills=is_making_mill(board,player_current,cell) 
            if mills[0]==True :
                for mill in mills[1] :
                    for action in actions :
                        if action.get_action_as_dict()['action']['to'] == cell and action.get_action_as_dict()['action']['at'] not in mill  and is_effective_making_mill(state,player_current,rules,cell,mill) == True :
                            return action
   return False

def move_and_occasion(actions,state,rules,player) :
    luck=[]
    pity=[]
    board=state.get_board()
    for action in actions :
        tmp=action.get_action_as_dict()
        at = tmp['action']['at']
        to = tmp['action']['to']
        board.empty_cell(at)
        board.fill_cell(to,Color(player))
        state.set_board(board)
        occasion=get_actions_can_make_mill(player,state,rules)
        if len(occasion) > 1 :
            luck.insert(0,action)
        elif len(occasion) == 1 :
            degre=free(state,rules,occasion[0].get_action_as_dict()["action"]["to"],-player) 
            if degre == True :
                luck.append(action)
            elif degre == 1 :
                pity.append(action)
        board.empty_cell(to)
        board.fill_cell(at,Color(player))
    return luck,pity

def ordinateur(state,rules,pieces,player,dont_move_cell) :
    board=state.get_board()
    
    if len(pieces) == 0  :
         pieces=board.get_player_pieces_on_board(Color(player))

    for piece in pieces :
        cells=get_effective_cell_moves(board,piece)
        if len(cells) != 0 :
            for cell in cells :
                board.empty_cell(piece)
                board.fill_cell(cell,Color(player))
                new_pieces=[x for x in board.get_player_pieces_on_board(Color(player)) if x not in dont_move_cell]
                for x in new_pieces :
                    cells_move=get_effective_cell_moves(board,x)
                    for cell_move in cells_move :
                        mills=is_making_mill(board,player,cell_move)
                        if mills[0] == True  and  ( len(mills[1])>=2 or len([mill for mill in mills[1] if x in mill and cell_move in mill]) == 0) and len([n for n in rules.get_rules_possibles_moves(cell_move,board) if n in board.get_player_pieces_on_board(Color(-1*player))]) == 0 :
                             return piece,cell
                board.empty_cell(cell)
                board.fill_cell(piece,Color(player))
    return False,False


def get_actions_can_make_mill(player,state,rules) :
    board=state.get_board()
    actions_mill=[]
    actions=rules.get_player_actions(state,player)
    for action in actions :
        tmp=action.get_action_as_dict()
        at = tmp['action']['at']
        to = tmp['action']['to']
        mills=is_making_mill(board,player,to)
        if mills[0] == True and (len([mill for mill in mills[1] if to in mill and at in mill]) == 0 or len(mills[1])>=2) :
            actions_mill.append(action)
    return actions_mill

def block_mills(state,player) :
    board = state.get_board()
    save_mill = save_mills(state,player)
    print("\n\n block mills",save_mill)
    if save_mill[0] == True :
        
        for cell in MorabarabaRules.get_effective_cell_moves(state,save_mill[2]) :
            if cell in board.get_all_empty_cells() :
                for second_cell in MorabarabaRules.get_effective_cell_moves(state,cell) :
                    if second_cell in board.get_player_pieces_on_board(Color(-1*player)) :
                        return cell
    return False

def save_mills(state,player):
    board = state.get_board()
    save_mills = get_piece_mills(state,player,2)
    
    for mill in save_mills:
        for move in MorabarabaRules.get_rules_possibles_moves(mill[2],board):
            if move in board.get_player_pieces_on_board(Color(player)) and move not in mill :
                mill[2]=move
                return [True,mill,move]
    return [False,[]]

def get_piece_mills(state,player,number):
    board = state.get_board()
    pieces = board.get_player_pieces_on_board(Color(player))
    adv_pieces = board.get_player_pieces_on_board(Color(-1*player))
    all_mills=[]
    for mill in board.mills():
        if all([adv_piece not in mill for adv_piece in adv_pieces]) and len(set(mill) & set(pieces)) == number:
            cells_pieces = []
            for cell in mill:
                if cell in board.get_all_empty_cells():
                    cells_pieces.append(cell)
                else:
                    cells_pieces.insert(0,cell)
            all_mills.append(cells_pieces)

    return all_mills

def Cell(board,player,cell) :
    is_cell=True
    mills=[mill for mill in board.mills() if cell in mill]
    for mill in mills :
        for mill_cell in mill :
            if mill_cell in board.get_player_pieces_on_board(Color(player)) :
                cell=mill_cell
            if mill_cell in board.get_player_pieces_on_board(Color(-1*player)) :
                is_cell=False
        if is_cell == True :
            return cell

def Fatal_cells(board,player) :
    fatal_cells=[]
    potential_fatal_cell=[0,(0,0)]
    for cell in board.get_all_empty_cells() :
        mills=is_making_mill(board,player,cell)
        if mills[0] == True :
            for mill in mills[1] :
                for mill_cell in mill :
                    if mill_cell != cell :
                        fatal_cells.append(mill_cell)
    for fatal_cell in fatal_cells :
        if fatal_cells.count(fatal_cell) > potential_fatal_cell[0] :
            potential_fatal_cell=[fatal_cells.count(fatal_cell),fatal_cell]
    return potential_fatal_cell,fatal_cells

def In_between_my_piece(board,player) :
    mills=board.mills()
    in_between_my_piece=[]
    in_double_occasion=[False,[]]
    in_between_more_my_piece=[0,(0,0)]
    pieces = board.get_player_pieces_on_board(Color(-1*player))
    pieces_adverses = board.get_player_pieces_on_board(Color(player))
    for mill in mills :
        empty_cell=0
        my_color=[]
        not_my_color=[]
        for mill_cell in mill :
            if mill_cell in pieces :
                my_color.append(mill_cell)
            elif mill_cell in pieces_adverses :
                not_my_color.append(mill_cell)
            else :
                empty_cell+=1
        if empty_cell == 0 and len(my_color) == 2 :
            in_between_my_piece.append(not_my_color[0])
        if empty_cell == 1 and len(my_color) == 1 :
            if not_my_color[0] in in_double_occasion[1] :
                in_double_occasion[0]=True
            in_double_occasion[1].append(not_my_color[0])

    for cell in in_between_my_piece :
        if in_between_my_piece.count(cell) > in_between_more_my_piece[0] :
            in_between_more_my_piece=[in_between_my_piece.count(cell),cell]
  
    return in_between_more_my_piece,in_between_my_piece,in_double_occasion
            

def more_occasion(state,player,actions) :
    adverse_potential_occasion,adverse_occasions=Occasion(state,player)
    my_potential_occasion,my_occasions=Occasion(state,player)
    if adverse_potential_occasion[0] > 2 and my_potential_occasion[0] < 2 :
        for action in actions :
            if action.get_action_as_dict()['action']['to'] == adverse_potential_occasion[1]  :
                    return action
    return False

def Occasion(state,player) :
    occasions=[]
    board=state.get_board()
    mills = board.mills()
    pieces = board.get_player_pieces_on_board(Color(player))
    pieces_adverses = board.get_player_pieces_on_board(Color(-1*player))
    if len(pieces) == 0 :
        return [0,[],0] , []
    else :
        for piece in pieces :
            for mill in mills :
                luck=True
                if piece in mill :
                    for mill_cell in mill :
                        if mill_cell in pieces_adverses :
                            luck=False
                    if luck == True :
                        for mill_cell in mill :
                            if mill_cell != piece and mill_cell in board.get_all_empty_cells() :
                                occasions.append(mill_cell)
        luck=[0,(0,0),0]
        preced=[]
        if len(occasions) == 0 :
            return [0,[],0] , []
        else :
            for occasion in occasions :
                if occasions.count(occasion) > luck[0] :
                    luck=[occasions.count(occasion),occasion,luck[2]]
                if occasions.count(occasion) > 1 and occasion not in preced:
                    preced.append(occasion)
                    luck[2]+=1
            return luck,occasions

def get_action(cell,player_mill,player,state,rules) :
   mills=[]
   luck=True
   can_move=False
   can_go=[]
   board=state.get_board()
   player_mills=board.player_mills(player)
   cells=rules.get_effective_cell_moves(state,cell)

   if len(cells) != 0 :
        for mill_cell in player_mill :
            if mill_cell != cell :
                for x in rules.get_effective_cell_moves(state,mill_cell) :
                    can_go.append(x)

        if len(can_go) != 0 :
            for mill in board.mills() :
                for cell in cells :
                    if cell in mill and len([x for x in can_go if x in mill]) != 0:
                        mills.append(mill)

        if len(mills) != 0 :
             for mill in mills :
                for mill_cell in mill :
                    if mill_cell in board.get_player_pieces_on_board(Color(-1*player)) :
                        luck=False
                    if mill_cell in board.get_player_pieces_on_board(Color(player)) :
                        can_move=True
                if luck == True and can_move == True :
                   mill_cell=[x for x in mill if x in cells]
                   return mill_cell[0]
   return False


def are_same_color(rules,state,mills,player,cell) :
    board=state.get_board()
    pieces=board.get_player_pieces_on_board(Color(player))

    cells=rules.get_effective_cell_moves(state,cell)
    if len(cells) == 2 :
        return True
    elif len(cells) == 1 :
        if len(mills) == 2 :
            mill=[x for x in mills if cells[0] not in x][0]
            if mill[1] in pieces :
                return True
        if len(mills) == 1 :
            mill=mills[0]
            if mill.index(cell) in [0,2] :
                return True
            else :
                if mill[0] in pieces or mill[2] in pieces :
                    return True
    else :
        return False


def Make_occasion(rules,state,player,actions) :
    board=state.get_board()
    if actions[0].get_action_as_dict()["action_type"] == MorabarabaActionType.ADD :

        choice=ADD_and_Ocassion(state,player)
        
        for cell in choice :
            for action in actions :
                if action.get_action_as_dict()['action']['to'] == cell  :
                        return action
        return MorabarabaRules.random_play(state,player)
               
    elif actions[0].get_action_as_dict()["action_type"] == MorabarabaActionType.MOVE :
        pieces=board.get_player_pieces_on_board(Color(player))
        player_mills=board.player_mills(player)
        mills=board.mills()
        dont_move_cell=[]

        if len(get_actions_can_make_mill(player*-1,state,rules)) == 0 :

           pieces=which_move(state,rules,actions,player)

           at,to=ordinateur_improve(state,rules,pieces,player)

           if at != False :
                for action in actions :
                    if action.get_action_as_dict()['action']['to'] == to and action.get_action_as_dict()['action']['at'] == at :
                        return action
           else :
                to = block_mills(state,-player) 
                if to != False :
                    ats=[]
                    for action in actions :
                        if action.get_action_as_dict()["action"]["to"] == to :
                            at.append(action.get_action_as_dict()["action"]["at"])

                    ats=filter(state,at,player)

                    for action in actions :
                        if action.get_action_as_dict()['action']['at'] in ats  :
                            return action

                else :
                    for player_mill in player_mills :
                        for mill_cell in player_mill :
                            new_mills=[mill for mill in mills if mill_cell in mill and mill != player_mill ]
                            luck=are_same_color(rules,state,new_mills,player,mill_cell)
                            if luck == True :
                                for action in actions :
                                    if action.get_action_as_dict()['action']['at'] == mill_cell  :
                                        return action

                    for player_mill in player_mills :
                        for mill_cell in player_mill :
                            luck=get_action(mill_cell,player_mill,player,state,rules)
                            if luck != False :
                                for action in actions :
                                    if action.get_action_as_dict()['action']['at'] == mill_cell and  action.get_action_as_dict()['action']['to'] == luck :
                                        return action

                choice=[x for x in which_move(state,rules,actions,player) if x not in save_mills(state,player)[1]]

                choice=filter(state,pieces,player)

                for action in actions :
                    if action.get_action_as_dict()['action']['at'] in choice  :
                        return action
        
           return MorabarabaRules.random_play(state,player)
        else :
            for mill in player_mills :
                for mill_cell in mill :
                    dont_move_cell.append(mill_cell)
            
            new_pieces=which_move(state,rules,actions,player)
            new_actions=[action for action in actions if action.get_action_as_dict()["action"]["at"] in new_pieces]

            action=make_double_mill(state,rules,player,new_actions)
            if action != False :
                return action

            choice=[x for x in new_pieces if x not in dont_move_cell]
            choice=filter(state,choice,player)
            if len(choice) == 0 :
                choice=filter(state,new_pieces,player)

            if choice  :
               for action in actions :
                    if action.get_action_as_dict()['action']['at'] in choice  :
                        return action
            print("\n\n random")
            return MorabarabaRules.random_play(state,player)
        print("\n\n random")
        return MorabarabaRules.random_play(state,player)
    else :
        print("\n\n random")
        return MorabarabaRules.random_play(state,player)

def ordinateur_improve(state,rules,pieces,player) :
    board=state.get_board()
    
    if len(pieces) == 0  :
         pieces=board.get_player_pieces_on_board(Color(player))

    for piece in pieces :
        cells=get_effective_cell_moves_improve(state,piece,player)
        if len(cells) != 0 :
            for cell in cells :
                board.empty_cell(piece)
                board.fill_cell(cell,Color(player))
                state.set_board(board)
                new_pieces=board.get_player_pieces_on_board(Color(player))
                for x in new_pieces :
                    cells_move=get_effective_cell_moves(board,x)
                    for cell_move in cells_move :
                        mills=is_making_mill(board,player,cell_move)
                        if mills[0] == True  and  ( len(mills[1])>=2 or len([mill for mill in mills[1] if x in mill and cell_move in mill]) == 0) and len([n for n in rules.get_rules_possibles_moves(cell_move,board) if n in board.get_player_pieces_on_board(Color(-1*player))]) == 0 :
                             return piece,cell
                board.empty_cell(cell)
                board.fill_cell(piece,Color(player))
                state.set_board(board)

    return False,False

def make_double_mill(state,rules,player,actions) :
    board=state.get_board()
    for action in actions :
        tmp=action.get_action_as_dict()
        at = tmp['action']['at']
        to = tmp['action']['to']
        board.empty_cell(at)
        board.fill_cell(to,Color(player))
        state.set_board(board)
        if len(get_actions_can_make_mill(player,state,rules)) > 1 :
            luck=destroy_more_mill(state,player,rules)
            if luck == False :
                return action

        board.fill_cell(at,Color(player))
        board.empty_cell(to)

    return False

def destroy_more_mill(state,player,rules) :
     board=state.get_board()
     all_pieces=board.get_player_pieces_on_board(Color(player))
     pieces=rules.stealables(player, board)
     for piece in pieces :
        is_mill=False
        board.empty_cell(piece)
        state.set_board(board)
        for x in [y for y in all_pieces if y != piece] :
            if is_mill == False :
                cells=get_effective_cell_moves_improve(state,x,player)
                for cell in cells :
                    mills=is_making_mill(board,player,cell)
                    if mills[0] == True and (len([mill for mill in mills[1] if x in mill and cell in mill]) == 0 or len(mills[1])>=2) and is_mill == False :
                        is_mill=True
        if is_mill == False :
            return piece
        board.fill_cell(piece,Color(player))
        state.set_board(board)
     return False

def contracte(dont_move_cell,actions,state,rules,player) :

    dont_do_action=[action for action in actions if action.get_action_as_dict()["action"]["at"] in dont_move_cell]

    if len(dont_move_cell) != 0 :
        new_actions=[new_action for new_action in actions if new_action.get_action_as_dict()["action"]['at'] not in dont_move_cell]
        if len(new_actions) != 0 :
            choice=which_move(state,rules,new_actions,player)
            if len(choice) == 0 :
                choice=which_move(state,rules,dont_do_action,player)
                if len(choice) == 0 :
                    choice=random_play(dont_do_action)
                    if len(choice) == 0 :
                        choice=random_play(actions)
        else :
            choice=which_move(state,rules,dont_do_action,player)
            if len(choice) == 0 :
                choice=random_play(dont_do_action)
                if len(choice) == 0 :
                        choice=random_play(actions)
    else :
        choice=which_move(state,rules,actions,player)
        if len(choice) == 0 :
            choice=random_play(actions)

    return choice    

def filter(state,pieces,player):
    rest_pieces = pieces
    board = state.get_board()
    for piece in pieces :
        if len(rest_pieces) > 1 :
            board.empty_cell(piece)
            state.set_board(board)
            at,to = ordinateur(state,MorabarabaRules,[],-player,[])
            if at != False and to == piece :
                rest_pieces.remove(piece)
            board.fill_cell(piece,Color(player))
            state.set_board(board)
    return rest_pieces

def which_move(state,rules,actions,player) :
    board=state.get_board()
    rest_actions=[]
    for action in actions :
        tmp=action.get_action_as_dict()
        at = tmp['action']['at']
        to = tmp['action']['to']
        board.empty_cell(at)
        board.fill_cell(to,Color(player))
        state.set_board(board)
        mills=is_making_mill(board,player*-1,at)
        if mills[0] != True or is_effective_making_mill(state,player*-1,rules,at,mills[1][0]) == False :
           if at not in rest_actions :
                rest_actions.append(at)
        
        board.fill_cell(at,Color(player))
        board.empty_cell(to)
        
    return rest_actions            

def random_play(actions) :
    if len(actions) != 0 :
        print("\n\n random")
        return [random.choice(actions).get_action_as_dict()["action"]["at"]]
    return False