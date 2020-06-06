#!/usr/bin/python3


import sys, os
from random import randint     
from argparse import ArgumentParser

class  Error (Exception):
    """Base class for user defined exceptions"""
    pass 

class TooSmallValue(Error):
    """Raise exception if a value in the file is negative""" 
    pass

class TooLargeValue(Error):
    """Raise exception if a value in the file is greater than 10"""
    pass

class ValueOfFrameTooLarge(Error):
    """Raise exception if the total pins knocked down in a frame is larger than 10"""
    pass

class MissingBonusRolls(Error):
    """Raise exception if the last frame was a spare or a strike and is missing a (or 2) bonus roll(s))"""
    pass

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
            frame_score = sum(list(frame.roll_data))
            if frame_score == 10 and idx != 9:
                next_frame_rolls = self.frames[idx+1].roll_data
                if 10 in frame.roll_data:
                    frame_score += next_frame_rolls[0]
                    frame_score += next_frame_rolls[1] if len(next_frame_rolls) >= 2 else self.frames[idx+2].roll_data[0]
                else:
                    frame_score += next_frame_rolls[0]
            
            self.score += frame_score
       
    def print_ids(self, frame):
        w = len(frame.roll_output) - 2
        return "| {:^{width}} ".format(frame.id, width=w)

    def print_rolls(self, frame):
        return "|{}".format(frame.roll_output)
         
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
    	self.roll_data = None
    	self.roll_output = ""

    def set_roll_info(self, *args):
        self.roll_data = args
        self.format_output(self.roll_data)

    def format_output(self, roll_data):
        if len(roll_data) == 1:
            self.roll_output = "X   "
        elif len(roll_data) == 2:
            if sum(roll_data) == 10:
                if 10 in roll_data:
                    self.roll_output = "-, X"
                else:
                    self.roll_output = "{}, /".format(roll_data[0])
            else:
                arg1 = "-" if roll_data[0] == 0 else roll_data[0]
                arg2 = "-" if roll_data[1] == 0 else roll_data[1]
                self.roll_output = "{}, {}".format(arg1, arg2) 
        elif self.id == "f10": 
            if 10 not in roll_data:
                self.roll_output = "{}, /, {}".format(roll_data[0], roll_data[2])
            else:
                if roll_data[0] == 10:
                   self.roll_output = "X, {}, {}".format(roll_data[1], roll_data[2]) 
                else:
                   self.roll_output = "-, X, {}, {}".format(roll_data[2], roll_data[3])
            

    def __str__(self):
        return "{}".format(self.roll_output)

    __repr__ = __str__


def generate_game_with_random_values(game):
    while game.number_of_frames() < 10:
        turn = game.number_of_frames() + 1
        frame = Frame(turn)
        roll1 = randint(0, 10)
        if roll1 == 10:
            if turn < 10:
                frame.set_roll_info(10)
            else:
                #we're in the 10th frame and it's a strike, so player gets 2 more rolls
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
                    #we're in the 10th frame, roll1 was a gutter ball and roll2 was a strike, so the player gets 2 bonus rolls
                    bonus_roll1 = randint(0, 10)
                    remaining_pins = 10 - bonus_roll1
                    bonus_roll2 = randint(0, (remaining_pins if remaining_pins != 0 else 10))
                    frame.set_roll_info(0, 10, bonus_roll1, bonus_roll2)
                elif roll1 + roll2 == 10:
                    #we're in the 10th frame and it's a spare, so the player gets 1 bonus roll
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
                    #we're handling the 10th frame and expect 2 more values since we encountered a strike
                    idx2 = idx1 + 1
                    idx3 = idx2 + 1
                    try:
                        if idx3 > len(values) - 1:
                            raise MissingBonusRolls
                    except MissingBonusRolls:
                        sys.exit("The input file contains a strike in the last frame but is missing one or both required bonus roll points; please add these") 
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
                    #spare or strike in second roll (1st roll was a gutter ball)
                    if turn < 10:
                        frame.set_roll_info(roll1, roll2)
                    else:
                        #handle bonus rolls in the 10th frame 
                        idx3 = idx2 + 1
                        if roll2 == 10:
                            #the second roll was a strike
                            idx4 = idx3 + 1
                            try:
                                if idx4 > len(values) - 1:
                                    raise MissingBonusRolls
                            except MissingBonusRolls:
                                sys.exit("The input file contains a strike in the last frame but is missing one or both required bonus roll points; please add these") 
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
                                sys.exit("The input file contains a spare in the last frame but is missing the required bonus roll points; please add these") 
                            else:
                                roll3 = values[idx3]
                                frame.set_roll_info(roll1, roll2, roll3)
                        
        except ValueOfFrameTooLarge:
            sys.exit("The values {} and {} at indexes {} and {} belong to the same frame but their sum exceeds 10, please adjust the values in the input file".format(roll1, roll2, idx1, idx2))
        else:
            game.add_frame(frame)
              
            
def parse_command_line():
    parser = ArgumentParser(description='Play a game of Bowling!')
    parser.add_argument('-file', help='provide an input file with a comma separated list of numbers between 0 and 10')
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
                sys.exit("Cannot process input file; file must contain a comma separated list of integers only")
            except TooSmallValue:
                sys.exit("Cannot process input file; encountered a negative value, file must contain a comma separated list of integers between 0 and 10")
            except TooLargeValue:
                sys.exit("Cannot process input file; encountered a value greater than 10, file must contain a comma separated list of integers between 0 and 10")
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
            sys.exit("The file '{}' does not exist - please provide a valid file name".format(args.file))
        input_values = parse_file(args.file)
        generate_game_with_file_values(input_values, game) 

    game.calculate_game_score() 
    print(game)


if __name__ == "__main__":
    main()
