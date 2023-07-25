
import os
import time
import webbrowser
import copy

"""
    this is a simple GO chess game written by dobach ! 
    the game follows the jappanese rules

    the game can be played in 3 modes :
        - 1 : 9x9 board
        - 2 : 13x13 board
        - 3 : 19x19 board
    
    i'm still a noob so my algorithm can't decide which group of stones are prisoners . it is
    guaranteed that player should clear the board before counting the territories!

"""




def get_valid_choice(range_of_choice: int,message: str) -> int:
    """
        this functin display the message and get the choice in the given range
        parameters :
            range_of_choice : int , the range of valid choices (from 1 to range_of_choice)
            message : str, the message to display 
        return: int the valid choice in the given range
    """

    choice = 0 
    while choice < 1 or choice > range_of_choice:
        #while the choice is not valid , get the choice 
        #if range_of_choice is 3 mean that there is 3 choices ( 1 , 2 and 3)
        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")

        print(message)  

        try :
            choice = int(input("    input your choice: "))
        except:
            print("Invalid choice")
            time.sleep(3)

        if choice < 1 or choice > range_of_choice:
            print("Invalid choice")
            time.sleep(3)
        
    return choice

    

class menu:
    modes="""
    ----------------------
    |     IGO CHESS      |
    |   1   PLAY         |
    |   2   RULES        |
    |   3   EXIT         |
    ----------------------
"""
    boards = """
    ----------------------
    |    SELECT BOARD    |
    |   1      9X9       |
    |   2     13X13      |
    |   3     19x19      |
    ----------------------
"""

class cell:
    EMPTY = 0
    BLACK = 1
    WHITE = 2

class state:
    PLACE = 1
    SKIP = 2
    SURRENDER = 3




cell.EMPTY = 0
cell.BLACK = 1
cell.WHITE = 2
state.PLACE = 1
state.SKIP = 2
X = 0 
Y = 1



class GameManager:
    

    def __init__(self,board_size: int) -> None:

        # initialize the game board
        self._board = [[cell.EMPTY] * board_size for _ in range(board_size)]

        # turn will be changed each time there is a performance
        self._turn = cell.BLACK # cell.BLACK will start first

        #the coordinates that is locked to prevent round-placing units
        self._locked_coord = None

        #the cell.EMPTY coordinates remain
        self._empty_coordinate_counts = board_size * board_size 

        #the score of cell.cell.WHITE players
        self._white_score = 0

        #the score of cell.BLACK players
        self._black_score = 0

        #the copy board for log information
        self.copyboard = None
    def _is_valid_coordinates(self, coordinates: tuple) -> bool:
        """
            this function checks if the coordinates is valid
            arguments: coordinates int, the coordinates to check
            return : bool True if the coordinates are valid, False otherwise
        """

        return coordinates[X] >= 0 and coordinates[X] < len(self._board) and coordinates[Y] >= 0 and coordinates[Y] < len(self._board)

    _status = """
    ----------------------
    |    YOUR CHOICE     |
    |     1  PLACE       |
    |     2  SKIP        |
    |     3  SURRENDER   |
    ----------------------
"""

    
    def _change_turn(self) -> None:
        """
            this function changes the turn of the player 
            parameters : None
            return : None
        """
        if self._turn == cell.BLACK:
            self._turn = cell.WHITE
        else:
            self._turn = cell.BLACK
        

    def game_loop(self):

        skip_strek = 0
        surrender = None
        # this is the game loop 
        while self._empty_coordinate_counts != 0:#while there is still cell.EMPTY cells in the board

            status_choice = self._get_status_choide()


            if status_choice == state.PLACE:
                skip_strek = 0#stop the trek if there is one player decide to state.PLACE a unit
                self._place()
                self._empty_coordinate_counts -= 1 #if we can state.PLACE a unit means that an cell.EMPTY coordinate is now gone

            roll_back = False

            if status_choice == state.SKIP:
                skip_strek += 1

                if skip_strek == 2:# if 2 players decide to state.SKIP mean that they want to end this game 
                    skip_choice = 'a'
                    # display the warning message again to make sure they have cleared the board before count the points

                    while skip_choice.lower() != 'y' and skip_choice.lower() != 'n':
                        self._display_warning_message()
                        skip_choice = input("    do you want to end this game? (y/n): ")
                    
                    if skip_choice.lower() == 'y':
                        self.copyboard = copy.deepcopy(self._board)
                        self._calculate_points()
                        break # exit the game loop s
                    else : 
                        roll_back = True
            if status_choice == state.SURRENDER:
                surrender = self._turn
                break

            if roll_back :
                skip_strek -= 1
                continue

            self._print_board()
            self._change_turn()
        self._define_winners(surrender)
        

    def _get_status_choide(self):
        status_choice = 0
        # print the board and ask for next perfomance
        while True:
            #clear the screen 
            if os.name == "nt":
                os.system("cls")
            else:
                os.system("clear")
            
            self._print_board()
            print(self._status)
            try:
                status_choice = int(input())
            except:
                print("Invalid choice")
                time.sleep(3)
            
            if status_choice == state.SKIP or status_choice == state.PLACE or status_choice == state.SURRENDER: 
                break
            print("Invalid choice")
            time.sleep(3)
        return status_choice

    def _print_board(self) -> None:
        '''
            this function prints the board
            arguments : none
            return : none
        '''
        # print the coordinates marker for easier use (x , first row)
        print("x",end = "   ")
        for i in range(len(self._board)):
            print(i,end = " ")
        
        print()
        print("y")
        index = 0
        # print each row of the board
        for row in self._board:
            #print the index of the rows
            if index < 10:
                print(index,end="   ")
            else :
                print(index,end="  ")
            index += 1

            #print each unit in a row
            
            for unit in row:
                if unit == cell.EMPTY:
                    print(".", end=" ")
                elif unit == cell.BLACK:
                    print("X", end=" ")
                elif unit == cell.WHITE:
                    print("O", end=" ")
                else:
                    print(unit, end=" ")
            print()
        print("current turn : " + ('WHITE' if self._turn == cell.WHITE else 'BLACK'))

    def _place(self):
        """
            this function will state.PLACE a unit on the board
            arguments : none
            return : none
        """
        while True:# get coordinates that the player can state.PLACE a unit on
            if self._can_place_a_unit():
                break
            print("can't state.PLACE unit here !")

    def _can_place_a_unit(self):
        """
            this function checks whether the player can state.PLACE a unit here
            arguments : none
            return : bool True if the player can state.PLACE a unit here, False otherwise
        """
        coordinate = self._get_input_coordinates()
        
    
        adjacents = self._get_adjacent(coordinate)
        # we will first state.PLACE the unit to this coordinate and check if we can capture opponent units 
        self._board[coordinate[X]][coordinate[Y]] = self._turn

        # if we can captured some opponent units , mean that this coordinate is valid to be placed on
        if self._can_capture_opponent(adjacents):
            return True
        
    
        if self._is_surrounded(adjacents) or self._is_self_corrupted(coordinate):# if we can't capture any units and this coordinate is surrounded by opponent units
            #  this coordinate is not validated to be placed on 
            self._board[coordinate[X]][coordinate[Y]] = cell.EMPTY #rollback 
            return False
    
        
        # if it not surrounded by opponent units then we can state.PLACE units here
        return True
    
    def _get_input_coordinates(self) -> tuple:
        """
            this function will get the valid coordinates from user input
            arguments : none
            return : coordinates list  the valid coordinates (x,y)
        """
        coordinates = [-1,-1]
        # get the valid coordinates and the coordinates that haven't been placed yet!
        while True:
            #clear the screen 
            if os.name == "nt":
                os.system("cls")
            else:
                os.system("clear")
            self._print_board()
            try:
                coordinates[X] = int(input("coordinates y: "))
                coordinates[Y] = int(input("coordinates x: "))
            except:
                print("Invalid coordinates")
                time.sleep(3)

            if self._is_valid_coordinates(coordinates) and self._board[coordinates[X]][coordinates[Y]] == cell.EMPTY and tuple(coordinates) != self._locked_coord:
                break

            print("Invalid coordinates")
            time.sleep(3)
            
        #clear the locked coordinate after the player have choose a valid coordinate
        self._locked_coord = None

        return tuple(coordinates)
    
    def _get_adjacent(self, coordinates : tuple) -> list:
        """
            this function will get the coordinates of the adjacent ki 
            arguments : coordinates list, the coordinates of the unit to state.PLACE
            return : list of coordinates, the coordinates of the adjacent ki

        # this is the four adjacent ki 
        #      X
        #    X O X
        #      X
        """
        result = [
            (coordinates[X] + 1 , coordinates[Y]), 
            (coordinates[X] - 1 , coordinates[Y]), 
            (coordinates[X] , coordinates[Y] + 1),
            (coordinates[X] , coordinates[Y] - 1)]
        
        return result
    
    def _can_capture_opponent(self,adjacents: list) -> bool:
        """
            this function will check if this player can capture opponents unit by state.PLACE a new unit in this coordinates
            arguments :
            coordinates list, the coordinates of the unit to state.PLACE
            adjacent_ki list, the coordinates of the adjacent ki
            return : bool True if this player can capture the opponents unit, False otherwise 
        """
        can_capture = False
        for adjacent in adjacents:
            if self._is_valid_coordinates(adjacent) and self._is_opponent_unit(adjacent):# if this adjacent coordinates is valid and posseses by opponent unit
                if self._DFS_and_capture(adjacent): # if these opponent units can be captured then remove it from the board 
                    can_capture = True
        return can_capture
    
    def _is_opponent_unit(self,coordinate: tuple):
        """
            this function check if the coordinate is posses by an opponent unit
            arguments : coordinate, the coordinate to check
            return : bool True if it is a opponent unit , False otherwise
        """
        if self._board[coordinate[X]][coordinate[Y]] == cell.BLACK and self._turn == cell.WHITE:
            return True
        if self._board[coordinate[X]][coordinate[Y]] == cell.WHITE and self._turn == cell.BLACK:
            return True

        return False



    def _DFS_and_capture(self,coordinates: tuple) -> bool:
        """
            this function checks if the opponent units are collapsed and if so , it will remove them from the board
            arguments: coordinates int, the opponent units coordinates 
            return : bool True if these opponent units can be captured, False otherwise
        """
        travelled = set()
        query = [coordinates]#using stack for  DFS , it will reach all the enemy units that is connected and will check if there are at least 1 safe points for the enemy

        #while there is pending coordinates
        while len(query) > 0:
            current_coordinate = query.pop()
            travelled.add(current_coordinate)

            adjacents = self._get_adjacent(current_coordinate)# get all the adjacent coordinates to check
            for adjacent in adjacents:
                if not self._is_valid_coordinates(adjacent) :# check if adjacent is a valid coordinate
                    continue
                if self._board[adjacent[X]][adjacent[Y]] == cell.EMPTY:# check if adjacent iself._board[coordinates[X]][coordinates[Y]]s cell.EMPTY means that there is still ki for opponent units . therefore , can't capture these units
                    return False
                if self._board[adjacent[X]][adjacent[Y]] == self._board[coordinates[X]][coordinates[Y]] and adjacent not in travelled:# if adjacent is the same type of unit with coordinates and haven't travelled , add it to the query for next check
                    query.append(adjacent)

        # if we completely travel all the opponent units without finding an cell.EMPTY ki , that means these units is corrupted and needs to be removed 
        self._remove_units_from_board(travelled)

        return True

    def _remove_units_from_board(self,removed_coordinates: set) -> None:
        """
            this function removes opponent units from the board and make it a
            valid coordinates for the next turn
            arguments: removed_coordinates set, the coordinates of the opponent units to remove
            return : none
        """
        
        
        for coordinate in removed_coordinates:
            self._board[coordinate[X]][coordinate[Y]] = cell.EMPTY
            self._empty_coordinate_counts += 1 # we remove the opponent unit from a coordinate and make it an cell.EMPTY coordinate

        if len(removed_coordinates) == 1:# if we only capture 1 unit , there might be a chance that this is the ko position , we have to lock it to prevent repeating state.PLACE
            self._locked_coord = removed_coordinates.pop()

    def _is_surrounded(self,adjacents: list):
        """
            this function check if the four adjacent coordinates are surrounded by the opponets or not.
            arguments: adjacents list, the coordinates of the adjacent coordinates
            return : bool True if the four adjacent coordinates are surrounded by the opponets, False otherwise
        """
        for adjacent in adjacents:
            if self._is_valid_coordinates(adjacent) and not self._is_opponent_unit(adjacent):# check if there at least one ki is not controlled by opponent unit
                return False

        return True

    def _is_self_corrupted(self,coordinate: tuple) -> bool:
        """
            this function will check if the coordinate that player state.PLACE will result in a corrupted stones (commit suicide)
        """
        query = [coordinate]
        travelled = set()

        while len(query) > 0:
            current_coordinate = query.pop()
            travelled.add(current_coordinate)

            adjacents = self._get_adjacent(current_coordinate)# get all the adjacent coordinates to check
            for adjacent in adjacents:
                if not self._is_valid_coordinates(adjacent) or adjacent in travelled :# check if adjacent is a valid coordinate and haven't travelled yet
                    continue
                
                if self._board[adjacent[X]][adjacent[Y]] == cell.EMPTY:# check if adjacent iself._board[coordinates[X]][coordinates[Y]]s cell.EMPTY means these stones not corrupted
                    return False
                
                if self._board[adjacent[X]][adjacent[Y]] == self._turn:# check if adjacent is the same kind of unit 
                    query.append(adjacent) # then add it to the query for further processing
                
        return True
    
    def _display_warning_message(self) -> None:
        '''
        this function will display a warning message to the user
        arguments : none
        return : none
        '''

        message =  '''
        ATTENTION !
        have you think twice ? after this performance , the game will be over and the will count the areas that 
        each player have conquered. the algorithm can't decide which units are dead so it is guaranteed to 
        eleminate all the dead units and only stop the game when there are no space to state.PLACE anymore or 2 players 
        decide to stop inorder to prevent points misscalculations

'''
        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")

        self._print_board()
        print(message)
        
    def _calculate_points(self):
        '''
            intuition : going through the board and find an cell.EMPTY cell.
            start DFS from it till we can't find any cell.EMPTY cells any more.
            check if there exist 2 type of unit on the path. if there is then this path
            won't be count because it still be in the disputed area

            if there exist only one type of unit then count all the points for that type of unit!
            there will be at least one type of unit on the DFS path!!!

        '''

        for x in range(0,len(self._board)):
            for y in range(0,len(self._board)):
                if self._board[x][y] == cell.EMPTY:
                    self._travell_and_calculate_points((x,y))

    def _travell_and_calculate_points(self,coordinate: tuple):
        """
            this function will travell all the cell.EMPTY cells (DFS) and determine if these cell.EMPTY cells are belong to a player or not 
            arguments: coordinate int, the coordinates of the cell.EMPTY cell to start searching
            return: None 
        """

        travelled = set()
        query = [coordinate] # using stack for dfs
        type_endcounters = set()
        
        while len(query) > 0:
            current_coordinate = query.pop()
            travelled.add(current_coordinate)# add the current coordinate to the travelled array 
            adjacents = self._get_adjacent(current_coordinate)

            for adjacent in adjacents:
                if not self._is_valid_coordinates(adjacent) or adjacent in travelled:# check if this is a valid coordinate and it haven't been travelled
                    continue
                if self._board[adjacent[X]][adjacent[Y]] == cell.EMPTY :# if this is cell.EMPTY  add this coordinate to the query for further searching
                    query.append(adjacent)
                    continue

                type_endcounters.add(self._board[adjacent[X]][adjacent[Y]]) # if this is not an cell.EMPTY cell , no need to travell this coordinate
            
        if len(type_endcounters) > 1:# if there are multible units that posses these cells , then no players get a point
            return 

        type = type_endcounters.pop()

        if type == cell.BLACK:
            self._collected_and_add_point_for_black(travelled)
        if type == cell.WHITE:
            self._collected_and_add_point_for_white(travelled)


    def _collected_and_add_point_for_black(self,travelled: set) -> None:
        """
            this function will collect all the type of unit on the BFS path and add the points to the cell.BLACK score
            travelled set, the coordinates of the cell.EMPTY cells that cell.BLACK has conquered
            return : None
        """
        for coordinate in travelled:
            self._board[coordinate[X]][coordinate[Y]] = 'X'
            self._black_score += 1
    
    def _collected_and_add_point_for_white(self,travelled: set) -> None:
        """
            this function will collect all the type of unit on the BFS path and add the points to the cell.WHITE score
            travelled set, the coordinates of the cell.EMPTY cells that cell.WHITE has conquered
            return : None
        """
        for coordinate in travelled:
            self._board[coordinate[X]][coordinate[Y]] = 'O'
            self._white_score += 1

    def _define_winners(self,surrender: int) -> None:
        """
            this function will define the winner of the game
            return : None
        """
        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")



        self._print_board()
        if self._black_score > self._white_score or surrender == cell.WHITE:
            print("BLACK WIN !")
        elif self._black_score < self._white_score or surrender == cell.BLACK:
            print("WHITE WIN !")
        else:
            print("DRAW!")

    




def main():
    PLAY = 1
    RULES = 2
    EXIT = 3

    while True:
        mode_selection = get_valid_choice(3,menu.modes)
                
        

        if mode_selection == PLAY:
            board_selection = get_valid_choice(3,menu.boards)
            
            BOARD_SIZE_9 = 9
            BOARD_SIZE_13 = 13
            BOARD_SIZE_19 = 19

            game = None
            if board_selection == 1: # 9x9 case
                game = GameManager(BOARD_SIZE_9)
            if board_selection == 2:#13x19 case
                game = GameManager(BOARD_SIZE_13)
            if board_selection == 3:#19x19 case
                game = GameManager(BOARD_SIZE_19)
                
            game.game_loop()

            last_log = input("print the real board for research ?(y or else): ")
            if last_log.lower() == "y":
                print_log_board(game.copyboard)

            break
        elif mode_selection == RULES:
            webbrowser.open("https://www.cs.cmu.edu/~wjh/go/rules/Japanese.html")
        elif mode_selection == EXIT:
            print("THANK YOU FOR PLAYING THE GAME !!!")
            break        
    
def print_log_board(board: list[list]) -> None:
    """
        this function will print the latest board for the players to do research !
        arguments: board list[list], the latest board for the players to do research
    """
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

    for row in board:
        for cell in row:
            print(cell,end="  ")
        print()
        

if __name__ == "__main__":
    main()


