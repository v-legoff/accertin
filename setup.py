import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["wx", "lyntin"], "excludes": ["tkinter", "tcl"]}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="lyntin",
    version="0.0",
    description="Fork of access-lyntin",
    options = {"build_exe": build_exe_options},
    executables = [Executable("start.pyw", base=base)])