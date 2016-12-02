"""
All the functions in this module relate to the inner workings of
'Chrono Trigger', and share parts of how the game works to generate random
numbers, quotes, etc.
"""
import random
with open('CT_RNG_Table.txt', 'r') as fp:
    raw_data = fp.read()
RNG_table = [int(raw_data[i:i + 2], 16) for i in range(0, len(raw_data), 2)]
# the first index we get
index = random.randrange(0, 256)


def updateRNG():
    global index
    index += 1
    RandomNum = RNG_table[index % 256]
    return RandomNum
