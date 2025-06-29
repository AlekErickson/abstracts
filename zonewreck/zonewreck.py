class Piece:
    def __init__(self, P, A=0, H=0, S=0, D=0, color=None):
        self.P = P
        self.A = A
        self.H = H
        self.S = S
        self.D = D
        self.position = None
        self.color = color

class Player:
    def __init__(self, color):
        self.color = color
        self.reserve = 140
        self.pieces = []

    def add_piece_to_zone(self, game, piece, position):
        if game.is_in_zone(position, self.color):
            piece.position = position
            game.board[position[0]][position[1]] = piece
            self.pieces.append(piece)
            self.reserve -= (piece.A + piece.H + piece.S + piece.D)
            return True
        return False


    def move_piece(self, game, piece, destination):
        if not game.is_valid_move(piece, destination):
            return False

        enemy_piece = game.board[destination[0]][destination[1]]
        # If there's an enemy piece at the destination, handle combat
        if enemy_piece is not None:
            winner = game.combat(piece, enemy_piece)
            if winner == enemy_piece:
                # The piece that moved lost
                self.pieces.remove(piece)
                game.board[piece.position[0]][piece.position[1]] = None
            else:
                # The piece that moved won
                if winner not in self.pieces:
                    self.pieces.append(winner)
                game.opponent().pieces.remove(enemy_piece)
                game.board[destination[0]][destination[1]] = piece

        else:
            # If the move is in the enemy zone, deduct points from the enemy's reserve
            if game.is_in_zone(destination, 'White' if piece.color == 'Black' else 'Black'):
                game.opponent().reserve -= piece.A

            game.board[piece.position[0]][piece.position[1]] = None
            piece.position = destination
            game.board[destination[0]][destination[1]] = piece

        return True



class Game:

    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.players = [Player('White'), Player('Black')]
        self.current_turn = self.players[0]

    def switch_turn(self):
        self.current_turn = self.players[1] if self.current_turn == self.players[0] else self.players[0]

    def is_in_zone(self, position, color):
        row = position[0]
        if color == 'White' and row == 7:
            return True
        if color == 'Black' and row == 0:
            return True
        return False






    def is_valid_move(self, piece, destination):
        start_row, start_col = piece.position
        dest_row, dest_col = destination

        vertical_diff = dest_row - start_row
        horizontal_diff = dest_col - start_col
        
        # 1. Move exceeds the distance of the piece
        if abs(horizontal_diff) > piece.D or abs(vertical_diff) > piece.D:
            return False  

        # 2. If destination is empty
        if self.board[dest_row][dest_col] is None:
            # 2a. Movement restrictions outside the enemy zone based on piece color
            if piece.color == 'White' and vertical_diff >= 0:
                return False  # White pieces can't move backward or horizontally outside enemy zone
            if piece.color == 'Black' and vertical_diff <= 0:
                return False  # Black pieces can't move forward or horizontally outside enemy zone
            
            return True

        # 3. If destination has an enemy piece
        elif self.board[dest_row][dest_col].color != piece.color:
            return True

        # 4. Catch all other moves as invalid
        return False



    def combat(self, attacker, defender):
        # Determine the attacking order based on speed
        first_attacker, second_attacker = (attacker, defender) if attacker.S > defender.S else (defender, attacker)

        # If speeds are the same, the moving (active) piece attacks first
        if attacker.S == defender.S:
            first_attacker, second_attacker = attacker, defender

        round_num = 1
        while True:
            print("Round {}: {} attacks {}!".format(round_num, first_attacker.color, second_attacker.color))
            # First attacker attacks
            second_attacker.H -= first_attacker.A
            print("{}'s health is now {}.".format(second_attacker.color, second_attacker.H))
            if second_attacker.H <= 0:
                print("{} wins the combat!".format(first_attacker.color))
                return first_attacker  # First attacker wins

            print("Round {}: {} attacks {}!".format(round_num, second_attacker.color, first_attacker.color))
            # Second attacker attacks
            first_attacker.H -= second_attacker.A
            print("{}'s health is now {}.".format(first_attacker.color, first_attacker.H))
            if first_attacker.H <= 0:
                print("{} wins the combat!".format(second_attacker.color))
                return second_attacker  # Second attacker wins

            round_num += 1

 

    def play(self):
        print("Welcome to Zone Wreck!")
        
        while True:
            # Display Current State
            self.display_board()
            print(self.current_turn.color + "'s Turn. Points in reserve: " + str(self.current_turn.reserve))



            print("Placement Phase:")
            while True:
                try:
                    piece_P = int(input("Enter power level of the piece you want to place (or 0 to skip): "))
                    if piece_P <= 0:
                        break
                    A = self.get_stat_input(piece_P, "Attack")
                    H = self.get_stat_input(piece_P, "Health", allocated=A)
                    S = self.get_stat_input(piece_P, "Speed", allocated=A+H)
                    D = self.get_stat_input(piece_P, "Distance", allocated=A+H+S)
                    if A + H + S + D > 4 * piece_P:
                        print("Total allocated points exceed available budget. Try again.")
                        continue
                    col = int(input("Enter column (0-7) to place the piece in your zone: "))
                    position = (0, col) if self.current_turn.color == 'Black' else (7, col)
                    piece = Piece(P=piece_P, A=A, H=H, S=S, D=D, color=self.current_turn.color)
                    if self.current_turn.add_piece_to_zone(self, piece, position):
                        break
                    else:
                        print("Invalid placement. Try again.")
                except ValueError:
                    print("Invalid input. Try again.")



            
            # Movement Phase
            print("Movement Phase:")
            while True:
                try:
                    row = int(input("Enter row of the piece you want to move (or -1 to skip): "))
                    if row == -1:
                        break
                    col = int(input("Enter column of the piece you want to move: "))
                    dest_row = int(input("Enter destination row: "))
                    dest_col = int(input("Enter destination column: "))
                    piece = self.board[row][col]
                    if piece and piece.color == self.current_turn.color:
                        if self.current_turn.move_piece(self, piece, (dest_row, dest_col)):
                            break
                        else:
                            print("Invalid move. Try again.")
                    else:
                        print("Invalid selection. Try again.")
                except ValueError:
                    print("Invalid input. Try again.")
            
            # Check Endgame Condition
            if self.current_turn.reserve <= 0:
                print(self.current_turn.color + " has no points left in reserve. " + self.opponent().color + " wins!")

                break
            
            # Switch Turn
            self.switch_turn()

    def get_stat_input(self, piece_P, stat_name, allocated=0):
        while True:
            try:
                stat_value = int(raw_input("Allocate points to {0} (up to {1}): ".format(stat_name, 4*piece_P - allocated)))
                if 0 <= stat_value <= 4*piece_P - allocated:
                    return stat_value
                else:
                    print("Invalid allocation. Points exceed available budget. Try again.")
            except ValueError:
                print("Invalid input. Try again.")



    def opponent(self):
        return self.players[1] if self.current_turn == self.players[0] else self.players[0]

    def display_board(self):
        for row in self.board:
            print(' '.join(['.' if piece is None else piece.color[0] for piece in row]))
        print()

# Run the game
game = Game()
game.play()

