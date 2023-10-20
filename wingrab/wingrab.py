# -*- encoding:utf-8 -*-

"""
WinGrab: A simple tool to get the PID of the window under the cursor.

Developed by Jianzhang Chen
LICENSE: MIT
"""
import sys
if sys.platform != 'win32':
    raise NotImplementedError('Only support Windows platform')

import os
import threading

from ctypes import POINTER, cast, byref, Structure, WinError, get_last_error, c_int, WinDLL, WINFUNCTYPE, c_long
from ctypes.wintypes import (WPARAM, LPARAM, HANDLE, DWORD, BOOL, HINSTANCE, UINT, LPCWSTR, LPDWORD, MSG, HHOOK, HWND,
                             POINT)

__all__ = ['grab']

user32 = WinDLL('user32', use_last_error=True)

HC_ACTION = 0
WH_MOUSE_LL = 14

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

ULONG_PTR = WPARAM
LRESULT = LPARAM
LPMSG = POINTER(MSG)
HCURSOR = HANDLE

HOOKPROC = WINFUNCTYPE(LRESULT, c_int, WPARAM, LPARAM)
LowLevelMouseProc = HOOKPROC


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
#  LoadImageW
#  https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-loadimagew
# ===================================
user32.LoadImageW.restype = HANDLE
user32.LoadImageW.argtypes = (
    # _In_opt_ hinst
    HINSTANCE,
    # _In_     lpszName
    LPCWSTR,
    # _In_     uType
    UINT,
    # _In_     cxDesired
    c_int,
    # _In_     cyDesired
    c_int,
    # _In_     fuLoad
    UINT,
)

# ===================================
#  CopyImage
#  https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-copyimage
# ===================================
user32.CopyImage.restype = HANDLE
user32.CopyImage.argtypes = (
    # _In_ h
    HANDLE,
    # _In_ uType
    UINT,
    # _In_ cxDesired
    c_int,
    # _In_ cyDesired
    c_int,
    # _In_ fuFlags
    UINT,
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

# Save system cursors, before changing it
_saved_system_cursors = {}

# We need to change all standard cursors to our custom cursor
cursor_rel_path = 'cursor.cur'
cursor_absolute_path = os.path.join(os.path.dirname(__file__), cursor_rel_path)

_result = 0


def _print_mouse_msg(wParam, msg):
    msg_id = WM_TO_TEXT.get(wParam, str(wParam))
    msg_to_print = ((msg.pt.x, msg.pt.y),
                    msg.mouseData, msg.flags,
                    msg.time, msg.dwExtraInfo)
    print('{:15s}: {}'.format(msg_id, msg_to_print))


def _patch_system_cursors():
    for cursorId in _standard_cursor_ids:
        oldCursorImg = user32.LoadImageW(0, MAKEINTRESOURCEW(cursorId), IMAGE_CURSOR, 0, 0, LR_SHARED)
        _saved_system_cursors[cursorId] = user32.CopyImage(oldCursorImg, IMAGE_CURSOR,
                                                           0, 0, LR_COPYFROMRESOURCE)

        newCursor = user32.LoadCursorFromFileW(cursor_absolute_path)
        user32.SetSystemCursor(newCursor, cursorId)


def _restore_system_cursors():
    for cursorId in _standard_cursor_ids:
        user32.SetSystemCursor(_saved_system_cursors[cursorId], cursorId)


def _get_pid_from_point(point):
    win = user32.WindowFromPoint(point)
    pid = c_int()
    user32.GetWindowThreadProcessId(win, byref(pid))
    return pid.value


@LowLevelMouseProc
def _LLMouseProc(nCode, wParam, lParam):
    global _result

    if nCode == HC_ACTION:
        if _is_debug:
            msg = cast(lParam, LPMSLLHOOKSTRUCT)[0]
            _print_mouse_msg(wParam, msg)

        if wParam == WM_LBUTTONDOWN:
            return 1

        elif wParam == WM_LBUTTONUP:
            _restore_system_cursors()
            user32.PostThreadMessageW(threading.current_thread().ident, WM_QUIT, 0, 0)
            point = POINT()
            user32.GetCursorPos(byref(point))
            _result = _get_pid_from_point(point)
            return 1
    return user32.CallNextHookEx(None, nCode, wParam, lParam)


def _msg_loop():
    user32.SetWindowsHookExW(WH_MOUSE_LL, _LLMouseProc, None, 0)
    msg = MSG()

    _patch_system_cursors()

    while True:
        bRet = user32.GetMessageW(byref(msg), None, 0, 0)
        if not bRet:
            break
        if bRet == -1:
            raise WinError(get_last_error())
        user32.TranslateMessage(byref(msg))
        user32.DispatchMessageW(byref(msg))
    return _result


def grab(_debug=False):
    global _is_debug, _result
    _is_debug = _debug

    import threading

    t = threading.Thread(target=_msg_loop)
    t.start()
    t.join()

    r = _result
    _result = 0
    return r


if __name__ == '__main__':
    print(grab(True))
