import sys


def main():
    fname = sys.argv[1]
    with open(fname, 'r') as f:
        for line in f:
            path = line.split(' ')[-1].split('/', 1)[1].strip()
            print(path)


if __name__ == "__main__":
    main()
