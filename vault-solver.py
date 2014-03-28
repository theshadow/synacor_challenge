import random

class Vault(object):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

    DIRECTIONS = [
        "NORTH",
        "EAST",
        "SOUTH",
        "WEST"
    ]

    def __init__(self, grid):
        self.grid = grid

    def get_room(self, x, y):
        if x < 0 or x > 3:
            raise ValueError("X must be between 0 and 3: {0}".format(x))
        if y < 0 or y > 3:
            raise ValueError("Y must be between 0 and 3: {0}".format(y))

        return self.grid[y][x]

    def get_exits(self, x, y):
        exits = []
        if x > 0:
            exits.append(Vault.WEST)
        if x < 3:
            exits.append(Vault.EAST)

        if y > 0:
            exits.append(Vault.NORTH)
        if y < 3:
            exits.append(Vault.SOUTH)

        return exits

    def move(self, x, y, direction):
        if direction == Vault.NORTH:
            y -= 1
        elif direction == Vault.SOUTH:
            y += 1
        elif direction == Vault.EAST:
            x += 1
        elif direction == Vault.WEST:
            x -= 1
        return x, y


class Orb(object):
    def __init__(self, weight):
        self.weight = weight

    def add(self, value):
        self.weight += value

    def sub(self, value):
        self.weight -= value

    def mult(self, value):
        self.weight *= value

def solve_vault(limit):
    grid = [
        ('mult', 8, 'sub', 1),
        (4, 'mult', 111, 'mult'),
        ('add', 4, 'sub', 118),
        (22, 'sub', 9, 'mult'),
    ]

    vault = Vault(grid=grid)
    orb = Orb(weight=None)

    x, y = 0, 3

    buffer = []
    moves = []

    while len(moves) <= limit:
        if orb.weight == 30 and x == 3 and y == 0:
            break

        room = vault.get_room(x, y)
        exits = vault.get_exits(x, y)

        # we can't go back into 0, 3 so we just eliminate it
        if x == 0 and y == 2:
            exits = [e for e in exits if e != Vault.SOUTH]
        elif x == 1 and y == 3:
            exits = [e for e in exits if e != Vault.WEST]

        # we can't enter 3, 0 if our weight isn't 30
        if orb.weight != 30 and x == 2 and y == 0:
            exits = [e for e in exits if e != Vault.EAST]
        elif orb.weight != 30 and x == 3 and y == 1:
            exits = [e for e in exits if e != Vault.NORTH]

        random.shuffle(exits)

        exit = exits.pop()

        if orb.weight is None and isinstance(room, int):
            #print "Starting in ({0}, {1})".format(x, y)
            #print "Setting initial weight to 22"
            orb.weight = room
            room = None

        if len(buffer) == 2:
            value = buffer.pop()
            operation = buffer.pop()

            #print "Modifying the weight by {0}ing it by {1}".format(operation, value)

            getattr(orb, operation)(value)

        if room is not None:
            buffer.append(room)

        #print "Moving {0}".format(Vault.DIRECTIONS[exit])

        (x, y) = vault.move(x, y, exit)

        moves += [Vault.DIRECTIONS[exit]]

    #print orb.weight, moves

    if orb.weight != 30:
        return False

    if len(moves) > limit:
        return False

    return x, y, orb, moves


def main():
    attempts = 0
    max_attempts = 1000000
    max_steps = 15

    while attempts < max_attempts:
        result = solve_vault(max_steps)

        if not isinstance(result, bool):
            (x, y, orb, moves) = result
            print "Found it. Last position ({0},{1}) and weight {2}".format(x, y, orb.weight), moves
            break
        #else:
        #    print "Failed, too many moves"

        attempts += 1

    if attempts == max_attempts:
        print "No solution found within {0} attempts and {1} steps".format(attempts, max_steps)



if __name__ == '__main__':
    main()