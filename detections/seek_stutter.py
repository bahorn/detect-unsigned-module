import sys


def seek_stutter(filename):
    with open(filename, 'rb') as f:
        possible_len = len(f.read())
        i = 0
        while True:
            # Random seek before each read
            f.seek(i)
            # Then seek to correct position
            try:
                byte = f.read(1)[0]
            except:
                break
            i += 1
        print(possible_len, i)
        if possible_len != i:
            print('mismatch between size read with seek and normally')
        else:
            print('sizes read matched')
    

if __name__ == '__main__':
    seek_stutter(sys.argv[1])
