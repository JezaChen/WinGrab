# -*- encoding:utf-8 -*-

"""
WinGrab: A simple tool to get the PID of the window under the cursor.

Developed by Jianzhang Chen
LICENSE: MIT
"""
import sys

if sys.platform != 'win32':
    raise NotImplementedError('Only support Windows platform')

import msvcrt
import atexit
import signal
import os
import threading
import contextlib

from ctypes import POINTER, cast, byref, Structure, WinError, get_last_error, c_int, WinDLL, WINFUNCTYPE, c_long
from ctypes.wintypes import (WPARAM, LPARAM, HANDLE, DWORD, BOOL, HINSTANCE, UINT, LPCWSTR, LPDWORD, MSG, HHOOK, HWND,
                             POINT)

__all__ = ['grab', 'cleanup']

user32 = WinDLL('user32', use_last_error=True)

HC_ACTION = 0
WH_MOUSE_LL = 14

WM_NULL = 0x0000
WM_QUIT = 0x0012
WM_MOUSEMOVE = 0x0200
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_RBUTTONDOWN = 0x0204
WM_RBUTTONUP = 0x0205
WM_MBUTTONDOWN = 0x0207
WM_MBUTTONUP = 0x0208
WM_MOUSEWHEEL = 0x020A
WM_MOUSEHWHEEL = 0x020E

WM_TO_TEXT = {
    WM_MOUSEMOVE: 'WM_MOUSEMOVE',
    WM_LBUTTONDOWN: 'WM_LBUTTONDOWN',
    WM_LBUTTONUP: 'WM_LBUTTONUP',
    WM_RBUTTONDOWN: 'WM_RBUTTONDOWN',
    WM_RBUTTONUP: 'WM_RBUTTONUP',
    WM_MBUTTONDOWN: 'WM_MBUTTONDOWN',
    WM_MBUTTONUP: 'WM_MBUTTONUP',
    WM_MOUSEWHEEL: 'WM_MOUSEWHEEL',
    WM_MOUSEHWHEEL: 'WM_MOUSEHWHEEL'
}

IMAGE_CURSOR = 2
LR_SHARED = 0x00008000
LR_COPYFROMRESOURCE = 0x00004000

SPI_SETCURSORS = 0x0057

ULONG_PTR = WPARAM
LRESULT = LPARAM
LPMSG = POINTER(MSG)
HCURSOR = HANDLE

HOOKPROC = WINFUNCTYPE(LRESULT, c_int, WPARAM, LPARAM)
LowLevelMouseProc = HOOKPROC

# https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-peekmessagew
PM_NOREMOVE = 0x0000
PM_REMOVE = 0x0001
PM_NOYIELD = 0x0002


class MSLLHOOKSTRUCT(Structure):
    _fields_ = (('pt', POINT),
                ('mouseData', DWORD),
                ('flags', DWORD),
                ('time', DWORD),
                ('dwExtraInfo', ULONG_PTR))


class _Point(Structure):
    _fields_ = [
        ('x', c_long),
        ('y', c_long),
    ]


LPMSLLHOOKSTRUCT = POINTER(MSLLHOOKSTRUCT)


def errcheck_bool(result, func, args):
    if not result:
        raise WinError(get_last_error())
    return args


def MAKEINTRESOURCEW(x):
    return LPCWSTR(x)


# ===================================
#  SetWindowsHookEx
#  https://learn.microsoft.com/zh-cn/windows/win32/api/winuser/nf-winuser-setwindowshookexw
# ===================================
user32.SetWindowsHookExW.errcheck = errcheck_bool
user32.SetWindowsHookExW.restype = HHOOK
user32.SetWindowsHookExW.argtypes = (
    # _In_ idHook
    c_int,
    # _In_ lpfn
    HOOKPROC,
    # _In_ hMod
    HINSTANCE,
    # _In_ dwThreadId
    DWORD,
)

# ===================================
#  PostThreadMessageW
#  https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-postthreadmessagew
# ===================================
user32.PostThreadMessageW.restype = BOOL
user32.PostThreadMessageW.argtypes = (
    # _In_ idThread
    DWORD,
    # _In_ Msg
    UINT,
    # _In_ wParam
    WPARAM,
    # _In_ lParam
    LPARAM,
)

# ===================================
#  UnhookWindowsHookEx
#  https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-unhookwindowshookex
# ===================================
user32.UnhookWindowsHookEx.restype = BOOL
user32.UnhookWindowsHookEx.argtypes = (
    # _In_ hhk
    HHOOK,
)

# ===================================
#  CallNextHookEx
#  https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-callnexthookex
# ===================================
user32.CallNextHookEx.restype = LRESULT
user32.CallNextHookEx.argtypes = (
    # _In_opt_ hhk
    HHOOK,
    # _In_     nCode
    c_int,
    # _In_     wParam
    WPARAM,
    # _In_     lParam
    LPARAM,
)

# ===================================
#  GetMessageW
#  https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getmessagew
# ===================================
user32.GetMessageW.argtypes = (
    # _Out_    lpMsg
    LPMSG,
    # _In_opt_ hWnd
    HWND,
    # _In_     wMsgFilterMin
    UINT,
    # _In_     wMsgFilterMax
    UINT,
)

# ===================================
#  PeekMessageW
#  https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-peekmessagew
# ===================================
user32.PeekMessageW.argtypes = (
    # _Out_    lpMsg
    LPMSG,
    # _In_opt_ hWnd
    HWND,
    # _In_     wMsgFilterMin
    UINT,
    # _In_     wMsgFilterMax
    UINT,
    # _In_     wRemoveMsg
    UINT,
)

# ===================================
#  TranslateMessage
#  https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-translatemessage
# ===================================
user32.TranslateMessage.argtypes = (
    # _In_ lpMsg
    LPMSG,
)

# ===================================
#  DispatchMessageW
#  https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-dispatchmessagew
# ===================================
user32.DispatchMessageW.argtypes = (
    # _In_ lpMsg
    LPMSG,
)

# ===================================
#  SetSystemCursor
#  https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setsystemcursor
# ===================================
user32.SetSystemCursor.restype = BOOL
user32.SetSystemCursor.argtypes = (
    # _In_ hcur
    HCURSOR,
    # _In_ id
    DWORD,
)

# ===================================
#  LoadCursorFromFileW
#  https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-loadcursorfromfilew
# ===================================
user32.LoadCursorFromFileW.restype = HCURSOR
user32.LoadCursorFromFileW.argtypes = (
    # _In_ lpFileName
    LPCWSTR,
)

# ===================================
#  GetCursorPos
#  https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getcursorpos
# ===================================
user32.GetCursorPos.restype = BOOL
user32.GetCursorPos.argtypes = (
    # _Out_ lpPoint
    POINTER(POINT),
)

# ===================================
#  WindowFromPoint
#  https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-windowfrompoint
# ===================================
user32.WindowFromPoint.restype = HWND
user32.WindowFromPoint.argtype = (
    # _In_ Point
    _Point,
)

# ===================================
#  GetWindowThreadProcessId
#  https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getwindowthreadprocessid
# ===================================
user32.GetWindowThreadProcessId.restype = DWORD
user32.GetWindowThreadProcessId.argtype = (
    # _In_      hWnd
    HWND,
    # _Out_opt_ lpdwProcessId
    LPDWORD,
)

# ===================================
#  SystemParametersInfoW
#  https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-systemparametersinfow
# ===================================
user32.SystemParametersInfoW.restype = BOOL
user32.SystemParametersInfoW.argtypes = (
    # _In_     uiAction
    UINT,
    # _In_     uiParam
    UINT,
    # _Inout_  pvParam
    POINTER(POINT),
    # _In_     fWinIni
    UINT,
)

# Standard cursor identifiers
# https://learn.microsoft.com/en-us/windows/win32/menurc/about-cursors
_standard_cursor_ids = [
    32512,  # IDC_ARROW
    32513,  # IDC_IBEAM
    32514,  # IDC_WAIT
    32515,  # IDC_CROSS
    32516,  # IDC_UPARROW
    32642,  # IDC_SIZENWSE
    32643,  # IDC_SIZENESW
    32644,  # IDC_SIZEWE
    32645,  # IDC_SIZENS
    32646,  # IDC_SIZEALL
    32648,  # IDC_NO
    32649,  # IDC_HAND
    32650,  # IDC_APPSTARTING
]

# Whether to print debug messages
_is_debug = False

# The absolute path of the module
module_path = os.path.dirname(__file__)

# We need to change all standard cursors to our custom cursor
cursor_rel_path = 'cursor.cur'
cursor_absolute_path = os.path.join(module_path, cursor_rel_path)

# The path of the lock file
lock_file_path = os.path.join(module_path, 'WINGRAB.LOCKFILE')

# The result of the grab
_result = 0

# Whether the cursor has been changed
# If the cursor has been changed, we need to restore it when the grab is finished or the program exits.
_is_cursor_changed = False


def _release_lock(f):
    """ Close file and remove lock file.
    """
    f.close()
    try:
        os.remove(lock_file_path)
    except PermissionError:
        # Ignore permission error as it does not affect program execution or subsequent lock operation
        pass


@contextlib.contextmanager
def _global_wingrab_process_lock():
    """
    Context manager for acquiring and releasing a process lock for WinGrab.

    The process lock ensures that only one instance of WinGrab is running at a time.
    If another instance is already running, a `RuntimeError` is raised.

    Example:
        with _global_wingrab_process_lock():
            # Code executed while the lock is held

    :return: None
    """

    # Create a lock file
    try:
        f = open(lock_file_path, 'w+')
    except PermissionError:
        raise RuntimeError(
            'Unable to open lock file. Ensure that the path exists and you have write permission.'
        ) from None

    # Try to acquire the lock
    try:
        msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
    except OSError:
        _release_lock(f)
        raise RuntimeError('Another instance of WinGrab is already running.') from None

    # Yield to the context
    try:
        yield
    finally:
        f.close()
        _cleanup_impl(_from_atexit=True)


def _print_mouse_msg(wParam, msg):
    msg_id = WM_TO_TEXT.get(wParam, str(wParam))
    msg_to_print = ((msg.pt.x, msg.pt.y),
                    msg.mouseData, msg.flags,
                    msg.time, msg.dwExtraInfo)
    print('{:15s}: {}'.format(msg_id, msg_to_print))


def _patch_system_cursors():
    """ Change all standard cursors to our custom cursor. """
    global _is_cursor_changed
    _is_cursor_changed = True

    for cursorId in _standard_cursor_ids:
        newCursor = user32.LoadCursorFromFileW(cursor_absolute_path)
        user32.SetSystemCursor(newCursor, cursorId)


def _restore_system_cursors():
    """ Restore all standard cursors. """
    global _is_cursor_changed
    user32.SystemParametersInfoW(SPI_SETCURSORS, 0, None, 0)
    _is_cursor_changed = False


def _get_pid_from_point(point):
    """ Get the PID of the window under the cursor. """
    win = user32.WindowFromPoint(point)
    pid = c_int()
    user32.GetWindowThreadProcessId(win, byref(pid))
    return pid.value


@LowLevelMouseProc
def _LLMouseProc(nCode, wParam, lParam):
    """ Low-level mouse input event hook procedure. """
    global _result

    if nCode == HC_ACTION:
        if _is_debug:
            msg = cast(lParam, LPMSLLHOOKSTRUCT)[0]
            _print_mouse_msg(wParam, msg)

        if wParam == WM_LBUTTONDOWN:
            return 1

        elif wParam == WM_LBUTTONUP:
            point = POINT()
            user32.GetCursorPos(byref(point))
            _result = _get_pid_from_point(point)

            # Post a WM_NULL message to the current thread to exit the message loop when the grab is finished.
            user32.PostThreadMessageW(threading.current_thread().ident, WM_NULL, 0, 0)
            return 1
    return user32.CallNextHookEx(None, nCode, wParam, lParam)


def _msg_loop():
    """ Start a message loop to grab the PID of the window under the cursor. """
    hook = user32.SetWindowsHookExW(WH_MOUSE_LL, _LLMouseProc, None, 0)
    msg = MSG()

    _patch_system_cursors()

    while _result == 0:
        bRet = user32.PeekMessageW(byref(msg), None, 0, 0, PM_REMOVE)
        if not bRet:
            continue

        if msg.message == WM_QUIT:
            break

        user32.TranslateMessage(byref(msg))
        user32.DispatchMessageW(byref(msg))

    user32.UnhookWindowsHookEx(hook)
    return _result


# region The cleanup function
def _cleanup_impl(*, _from_atexit=False):
    """ Clean up any resources used by the program or manually clean up any leftover state from the 'wingrab' module.
    """
    if _is_debug:
        print("cleaning up......")

    if _from_atexit and _is_cursor_changed:
        # We only need to restore the cursor when **the cursor is changed in this process**.
        # If the cursor is changed in another process (This process will raise an error), we do not need to restore it.
        _restore_system_cursors()

    if os.path.exists(lock_file_path):
        try:
            os.remove(lock_file_path)
        except PermissionError:
            pass  # Ignore the error if the lock file is being used.


def _quit():
    # We just mark the result as -1 to jump out of the message loop.
    # And the cleanup function will be called automatically.
    global _result
    _result = -1


# Register cleanup function
atexit.register(_quit)
try:
    def signal_handler(sig, frame):
        _quit()


    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
except ValueError:  # `signal` only works in the main thread.
    raise ImportError(
        'Please import wingrab in the main thread, even if you want to use it in another thread.'
    ) from None
# endregion


# region The public API
def grab(*, _debug=False):
    with _global_wingrab_process_lock():
        global _is_debug, _result
        _is_debug = _debug

        _result = 0
        _msg_loop()

        r = _result
        return r


def cleanup(*, _debug=False):
    global _is_debug
    _is_debug = _debug

    _cleanup_impl()
# endregion


if __name__ == '__main__':
    print(grab(_debug=False))
