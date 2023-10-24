# WinGrab
<div align="center">A simple tool to get the PID of the window under the cursor.</div>

## Installation
### From pip

```bash
pip install wingrab
```

### From source code

You just need to download the `wingrab.py` and `cursor.cur` files and put them in your project, 
make sure that the `cursor.cur` file is in the same directory as `wingrab.py`.

## Usage

### In your code

```python
from wingrab import wingrab

wingrab.grab()
```

**Note: `wingrab` can be used in both the main thread and the sub thread, 
but if you want to use it in the sub thread, you need to call `wingrab.grab()` in the main thread first.**

## Examples

We provide some examples in the `examples` directory, you can run them directly after installation.

- `pyqt5_example.py`: An example of using `wingrab` in the main thread of a PyQt5 application.
- `pyqt5_example_run_in_sub_thread.py`: An example of using `wingrab` in the sub thread of a PyQt5 application.
- `tkinter_example.py`: An example of using `wingrab` in a Tkinter application.
- `run_in_sub_thread.py`: An example of using `wingrab` in a sub thread of a console application.
