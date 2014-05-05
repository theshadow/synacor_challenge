def f2178(x, y):
    loop_count = 0
    if x == 0 or y == 0:
        return 0, 0, loop_count
    if y > x:
        x, y = y, x
    z, x = x, 0
    while True:
        loop_count += 1
        x = (x + y) % 32768
        if y > x:
            return x, 1, loop_count
        z = (z + 32767) % 32768
        if z > 0:
            continue
        return x, 0, loop_count
    


if __name__ == "__main__":
    print f2178(32767, 1)
    print f2178(32767, 0)
    print f2178(0, 32767)
    print f2178(0, 32768)
    print f2178(32767, 32767)
    print f2178(3, 32767)
