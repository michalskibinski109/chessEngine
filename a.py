from multiprocessing import Pool
from time import sleep

def f(x, t = 2):
    sleep(x - t)
    print(t)
    return str(x*x)

if __name__ == '__main__':
    with Pool(5) as p:
        print(p.map(f, [4, 5, 6]))