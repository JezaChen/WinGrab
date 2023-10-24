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
