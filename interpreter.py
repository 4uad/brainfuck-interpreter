"""
Brainfuck interpreter

About Brainfuck esoteric programming language:
https://en.wikipedia.org/wiki/Brainfuck

This is an implementation of Brainfuck in Python. Running Brainfuck code is a simple as calling brainfuck function.

"""

import os # allows input through a .bf file

class Memory:
    def __init__(self, size = 30000):
        self.cells = [0] * size # Each element of this List is a Memory cell. Initially all zeroes
        self.pointer = 0 # Initially point at 0th cell
        self.value = 0 # Initial value (0th cell) is 0

    def print(self): # Print the value in the current cell
        output = self.value
        if output > 9:
            output = chr(output)
        print(output, end = "")

    def read(self): # Read input and store it in current cell
        inputValue = input("")
        if len(inputValue) == 0:
            inputValue = 0
        inputValue = inputValue[0]
        inputValue = ord(inputValue)
        self.setCellTo(inputValue)
    
    def setPointer(self, increment): # Increment the pointer by "increment"
        self.setPointerTo(self.pointer + increment)

    def setValue(self, increment): # Increment value in current cell by "increment"
        self.setCellTo(self.cells[self.pointer] + increment)

    def setCellTo(self, value): # Set the current cell to any value
        self.cells[self.pointer] = max(value, 0) # There cannot be negative values
        self.value = self.cells[self.pointer]

    def setPointerTo(self, cell): # Set the pointer to any cell
        self.pointer = max(cell, 0) # There are no negative cells
        self.value = self.cells[self.pointer]

def getNestingLevels(text, opening = "[", closing = "]"):

    '''
    Description
    ----------
    Returns a List with the depth levels of each character in the program. This function is intended for internal use only.

    Parameters
    ----------
    text : str
        A Brainfuck program.

    opening : str
        Optional string to treat as opening bracket

    closing : str
        Optional string to treat as closing bracket

    Returns:
        An int List with the depth level for each character in the program.
    '''

    # Input checking
    if not isinstance(text, str):
        raise Exception("Argument text must be a string")

    if len(text) == 0:
        raise Exception("text length cannot be zero")

    # Initialize result vector
    depths = [0] * len(text)

    # Current depth (varies on each iteration)
    depth = 0

    # Position of the last opening bracket
    lastopen = -1

    for i in range(0, len(text)):
        c = text[i]
        
        if c == opening: # There's an opening bracket, depth increases
            lastopen = i
            depth += 1

        if c == closing: # There's a closing bracket, depth decreases
            depth -= 1

        if depth < 0: # If there is a negative depth at any time, there must be an extra closing bracket
            raise Exception("Unmatched closing bracket at position %i" % i)

        depths[i] = depth

    # If at the end of the string the depth is greater than zero, there is an unclosed opening bracket
    if depth > 0:
        raise Exception("Unmatched opening bracket at position %i" % lastopen)

    return depths

def findLevelClosing(levels, i):

    '''
    Description
    ----------
    Returns the position of the first character in the upper level. This function is intended for internal use only.

    Parameters
    ----------
    levels : int List
        A list containing the depth level for every character in the Brainfuck program.
        For example, the depth levels for "+[++[+>]]" are [0, 1, 1, 1, 2, 2, 2, 1, 0]
        Each opening bracket increases depth by 1, closing brackets decrease it.

    i : int
        Current position in list

    Returns:
        An int with the index of the first character in the upper level
    '''

    level = levels[i]
    forward = levels[i:]

    # Look forward and find the next closing bracket leading to a higher level than the current
    for f in range(1, len(forward)):
        if forward[f] < level:
            return i + f + 1
    
    # If it cannot be found, then the current opening bracket is unmatched
    raise Exception("Unmatched opening bracket at position %i" % i)

def findLevelOpening(levels, i):
    '''
    Description
    ----------
    Returns the position of the opening bracket in the current level. This function is intended for internal use only.

    Parameters
    ----------
    levels : int List
        A list containing the depth level for every character in the Brainfuck program.
        For example, the depth levels for "+[++[+>]]" are [0, 1, 1, 1, 2, 2, 2, 1, 0]
        Each opening bracket increases depth by 1, closing brackets decrease it.

    i : int
        Current position in list

    Returns:
        An int with the index of the first character in the current level
    '''

    level = levels[i]
    backward = levels[:i]

    # Look backwards and find the previous closing bracket leading to the current level
    for f in range(len(backward) - 1, 0, -1):
        if backward[f] == level:
            return f + 2

    # If it cannot be found, then the current closing bracket is unmatched
    raise Exception("Unmatched closing bracket at position %i" % i)

def brainfuck(text, memory = None, memsize = 30000):

    '''
    Description
    ----------
    Takes a Brainfuck program and runs it

    Parameters
    ----------
    text : str
        Either a Brainfuck program or a path to a file containing a Brainfuck program.

    memory : Memory
        Optional. Memory instance in which the program will run. It is possible to
        create a single memory instance and use it in multiple Brainfuck programs:

            myMemo = Memory()
            brainfuck("+++", myMemo)
            brainfuck(".", myMemo)
            # outputs "3", value stored in myMemo's 0th cell
            brainfuck(".")
            # outputs "0", value stored in a new Memory instance

    memsize : int
        Optional. Use only if memory is omitted. Number of cells in the memory to
        be created.

    Returns:
        This function does not return any value
    '''

    if memory is None: # If memory argument is not given, create a new Memory.
        mem = Memory(memsize)
    else:
        if isinstance(memory, Memory): # If it is given, check it.
            mem = memory
        else:
            raise Exception("Argument memory must be an instance of Memory class")
    
    if os.path.isfile(text): # Is text an existing file? If it is, read from it.
        with open(text) as f:
            lines = f.readlines()
            script = ''
            for line in lines:
                script += line.rstrip()
    else:
        script = text

    levels = getNestingLevels(script)
    i = 0

    while i < len(script): # Loop through each character in script and call the appropriate Memory method
        l = levels[i]
        c = script[i]

        if c == "+":
            mem.setValue(1)
        elif c == "-":
            mem.setValue(-1)
        elif c == ">":
            mem.setPointer(1)
        elif c == "<":
            mem.setPointer(-1)
        elif c == ".":
            mem.print()
        elif c == ",":
            mem.read()
        elif c == "[":
            if mem.value == 0: # Jump after the next matching closing bracket
                i = findLevelClosing(levels, i)
                continue
        elif c == "]":
            if mem.value != 0: # Jump after the previous matching opening bracket
                i = findLevelOpening(levels, i)
                continue
        else:
            raise Exception("Unknown brainfuck command '%s'" % c)

        i += 1

brainfuck("C:/Users/dmama/Desktop/Projects/brainfuck-interpreter/demo-scripts/helloworld.bf")