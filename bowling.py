#!/usr/bin/python3


import sys, os
from random import randint     
from argparse import ArgumentParser

'''
User defined Exception classes
'''
class  Error (Exception):
    """Base class for user defined exceptions"""
    pass 

class TooSmallValue(Error):
    """Value in input file is negative""" 
    pass

class TooLargeValue(Error):
    """Value in input file is greater than 10"""
    pass

class ValueOfFrameTooLarge(Error):
    """Total pins knocked down in a frame is larger than 10"""
    pass

class MissingBonusRolls(Error):
    """Last frame was a spare or strike but is missing bonus rolls)"""
    pass


'''
* User defined class for the Bowling game:
 - The Game class keeps track of the 10 frames within a game and sums up
   the total game score once the 10 frames have been generated.
 - The Frame class holds information about the rolls and how many pins
   were knocked down per roll (i.e. number of points achieved per roll);
   It also keeps an string attribute for printing Strikes, Spares and
   gutter balls correectly (X, /, -)
'''
class Game():
    def __init__(self):
        self.frames = []
        self.score = 0

    def add_frame(self, frame):
        self.frames.append(frame)

    def number_of_frames(self):
        return len(self.frames)

    def calculate_game_score(self):
        for idx, frame in enumerate(self.frames):
            frame_score = sum(list(frame.roll_points))
            if frame_score == 10 and idx != 9:
                next_frame_rolls = self.frames[idx+1].roll_points
                if 10 in frame.roll_points:
                    frame_score += next_frame_rolls[0]
                    if len(next_frame_rolls) >= 2:
                        frame_score += next_frame_rolls[1]
                    else:
                        frame_score += self.frames[idx+2].roll_points[0]
                else:
                    frame_score += next_frame_rolls[0]
            
            self.score += frame_score
       
    def print_ids(self, frame):
        w = len(frame.roll_str) - 2
        return "| {:^{width}} ".format(frame.id, width=w)

    def print_rolls(self, frame):
        return "|{}".format(frame.roll_str)
         
    def __str__(self):
        for item in map(self.print_ids, self.frames):
            print(item, end="")
        print("|")
        for item in map(self.print_rolls, self.frames):
            print(item, end="")
        print(" |")
        return "Game score: {}".format(self.score)

    __repr__ = __str__


class Frame():
    def __init__(self, index):
    	self.id = "f{}".format(index)
    	self.roll_points = None
    	self.roll_str = ""

    def set_roll_info(self, *args):
        self.roll_points = args
        self.points_to_str(self.roll_points)

    def points_to_str(self, points):
        if len(points) == 1:
            self.roll_str = "X   "
        elif len(points) == 2:
            if sum(points) == 10:
                if 10 in points:
                    self.roll_str = "-, X"
                else:
                    self.roll_str = "{}, /".format(points[0])
            else:
                arg1 = "-" if points[0] == 0 else points[0]
                arg2 = "-" if points[1] == 0 else points[1]
                self.roll_str = "{}, {}".format(arg1, arg2) 
        elif self.id == "f10": 
            if 10 not in points:
                self.roll_str = "{}, /, {}".format(points[0], points[2])
            else:
                if points[0] == 10:
                   self.roll_str = "X, {}, {}".format(points[1], points[2]) 
                else:
                   self.roll_str = "-, X, {}, {}".format(points[2], points[3])
            

    def __str__(self):
        return "{}".format(self.roll_str)

    __repr__ = __str__


'''
* 2 functions: generate_game_with_random_values and 
  generate_game_with_file_values
* These generate a game (and its 10 frames) based on input filee values
  or if no file i provided, the program randomly generates a game for us 
'''
def generate_game_with_random_values(game):
    while game.number_of_frames() < 10:
        turn = game.number_of_frames() + 1
        frame = Frame(turn)
        roll1 = randint(0, 10)
        if roll1 == 10:
            if turn < 10:
                frame.set_roll_info(10)
            else:
                #10th frame: player gets 2 bonus rolls after a strike
                bonus_roll1 = randint(0, 10)
                remaining_pins = 10 - bonus_roll1
                bonus_roll2 = randint(0, (remaining_pins if remaining_pins != 0 else 10))
                frame.set_roll_info(10, bonus_roll1, bonus_roll2)
        else:
            roll2 = randint(0, 10 - roll1)
            if turn < 10:
                frame.set_roll_info(roll1, roll2)
            else:
                if roll2 == 10:
                    #10th frame: roll1 was a gutter ball, roll2 a strike
                    #player gets 2 bonus rolls
                    bonus_roll1 = randint(0, 10)
                    remaining_pins = 10 - bonus_roll1
                    bonus_roll2 = randint(0, (remaining_pins if remaining_pins != 0 else 10))
                    frame.set_roll_info(0, 10, bonus_roll1, bonus_roll2)
                elif roll1 + roll2 == 10:
                    #10th frame: player gets 1 bonus roll after a spare
                    bonus_roll = randint(0, 10)
                    frame.set_roll_info(roll1, roll2, bonus_roll)
                else:
                   frame.set_roll_info(roll1, roll2)

        game.add_frame(frame)


def generate_game_with_file_values(values, game):
    idx = 0
    while game.number_of_frames() < 10:
        turn = game.number_of_frames() + 1
        frame = Frame(turn)
        try:
            idx1 = idx
            roll1 = values[idx1]
            if roll1 == 10:
                if turn < 10:
                    frame.set_roll_info(roll1)
                    idx = idx1 + 1
                else:
                    #10th frame: use 2 more values after a strike
                    idx2 = idx1 + 1
                    idx3 = idx2 + 1
                    try:
                        if idx3 > len(values) - 1:
                            raise MissingBonusRolls
                    except MissingBonusRolls:
                        sys.exit("Input file is missing bonus rolls") 
                    else:
                        roll2 = values[idx2]
                        roll3 = values[idx3]
                        frame.set_roll_info(roll1, roll2, roll3)
            else:
                idx2 = idx1 + 1
                idx = idx2 + 1
                roll2 = values[idx2]
                if roll1 + roll2 < 10:
                    frame.set_roll_info(roll1, roll2)
                elif roll1 + roll2 > 10:
                    raise ValueOfFrameTooLarge
                else:
                    #spare or strike in 2nd roll (1st roll was a gutter)
                    if turn < 10:
                        frame.set_roll_info(roll1, roll2)
                    else:
                        #10th frame: handle bonus rolls
                        idx3 = idx2 + 1
                        if roll2 == 10:
                            #2nd roll was a strike
                            idx4 = idx3 + 1
                            try:
                                if idx4 > len(values) - 1:
                                    raise MissingBonusRolls
                            except MissingBonusRolls:
                                sys.exit("Input file is missing bonus rolls") 
                            else:
                                roll3 = values[idx3]
                                roll4 = values[idx4]
                                frame.set_roll_info(roll1, roll2, roll3, roll4)
                        else:
                            #we got a spare in the last round
                            try:
                                if idx3 > len(values) - 1:
                                    raise MissingBonusRolls
                            except MissingBonusRolls:
                                sys.exit("Input file is missing bonus roll") 
                            else:
                                roll3 = values[idx3]
                                frame.set_roll_info(roll1, roll2, roll3)
                        
        except ValueOfFrameTooLarge:
            sys.exit("Sum of frame points {} and {} (idx:{} and {}) exceeds 10".format(roll1, roll2, idx1, idx2))
        else:
            game.add_frame(frame)


'''
The below 2 functions parse the command line and the input file (if one
is provided)
'''              
def parse_command_line():
    parser = ArgumentParser(description='Play a game of Bowling!')
    parser.add_argument('-file', help='provide an input file with a comma separated list of digits between 0 and 10')
    return parser.parse_args()


def parse_file(input_file):
    with open(input_file) as f:
        line = f.readline().strip()
        input_values = []
        for value in line.split(','):
            try: 
                digit = int(value)
                if digit < 0:
                    raise TooSmallValue
                elif digit > 10:
                    raise TooLargeValue
            except ValueError:
                sys.exit("Input file must contain comma separated list of integers only")
            except TooSmallValue:
                sys.exit("Negative values are not accepted, only values between 0 and 10")
            except TooLargeValue:
                sys.exit("Values > 10 are not accepted, only values between 0 and 10")
            else: 
                input_values.append(digit)
    
    return input_values


def main():
    args = parse_command_line()
    game= Game()

    if args.file is None:
        generate_game_with_random_values(game)
    else:
        if not os.path.isfile(args.file):
            sys.exit("File '{}' does not exist - pls provide a valid file name".format(args.file))
        input_values = parse_file(args.file)
        generate_game_with_file_values(input_values, game) 

    game.calculate_game_score() 
    print(game)


if __name__ == "__main__":
    main()
