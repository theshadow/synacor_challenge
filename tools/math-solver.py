import random

def main():
    red = 2
    blue = 9
    shiny = 5
    concave = 7
    corroded = 3

    random_set = [red, blue, shiny, concave, corroded]

    while True:
        random.shuffle(random_set)
        if calculate(*random_set):
            print "Found it!", random_set
            break


def calculate (a, b, c, d, e):
    # _ + _ * _^2 + _^3 - _ = 399
    result = a + b * c**2 + d**3 - e
    if result == 399:
        return True
    else:
        return False


if __name__ == "__main__":
    main()
