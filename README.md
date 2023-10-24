# WinGrab
<div align="center">A simple tool to get the PID of the window under the cursor.</div>

## Installation
### From pip

```bash
pip install wingrab
```

### From source code

Download the wingrab.py and cursor.cur files and place them in your project directory, 
ensuring the `cursor.cur` file is in the same location as `wingrab.py`.

## Usage

### Run directly in CLI

**Ensure the `wingrab` package is installed via pip**, You can then run it directly in the CLI using:

```bash
py-wingrab
```

or

```bash
py-wingrab grab
```

If `wingrab` crashes, and the mouse cursor has changed to a cross, 
run the `cleanup` command to try to restore the mouse cursor.

```bash
py-wingrab cleanup
```

### Integrate into your Python code

It is very simple to integrate `wingrab` into your Python code,
you just need to call the `grab` function in the `wingrab` package.

```python
from wingrab import wingrab

pid = wingrab.grab()
```

The `grab` function returns the PID of the window under the cursor as an integer.

Note that the `grab` will block the current thread until the user clicks the left mouse button,
so if you want to use it in a GUI application,
you had better call the `grab` function in a sub thread. (See examples below)

**Note: `wingrab` can be used in both the main thread and the sub threads, 
but if you want to use it in a sub thread, make sure to call `wingrab.grab()` in the main thread first.**

To restore the global mouse cursor to the default when `wingrab` crashes, invoke the `cleanup` function.

```python
from wingrab import wingrab

wingrab.cleanup()
```

## Examples

`examples` directory contains several examples which demonstrate usage and integration methods. 
You can run them directly after installing the package:

- `pyqt5_example.py`: An example of using `wingrab` in the main thread of a PyQt5 application.
- `pyqt5_example_run_in_sub_thread.py`: An example of using `wingrab` in the sub thread of a PyQt5 application.
- `tkinter_example.py`: An example of using `wingrab` in a Tkinter application.
- `run_in_sub_thread.py`: An example of using `wingrab` in a sub thread of a console application.
