import threading
import time

import wingrab


def run_in_another_thread():
    # import wingrab  # if you import wingrab in another thread, you will get an error
    wingrab.grab(_debug=True)


if __name__ == '__main__':
    thread = threading.Thread(target=run_in_another_thread)
    thread.start()
    for i in range(100):
        print('<test>')
        time.sleep(1)
