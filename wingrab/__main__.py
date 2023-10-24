import sys
import wingrab


def main():
    if len(sys.argv) < 2 or sys.argv[1] == 'grab':
        print(wingrab.grab())
    elif sys.argv[1] == 'clean':
        wingrab.cleanup()
        print('Cleaned up.')
    else:
        print(f'Unknown command: {sys.argv[1]}\nUsage: wingrab [grab|clean]')


if __name__ == '__main__':
    main()
