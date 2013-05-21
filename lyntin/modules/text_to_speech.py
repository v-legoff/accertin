"""Text to speech Lyntin module with ScreenReaderAPI.

This Lyntin module is used when lines are received by the
client.  These lines should be spoken aloud curtesy of the
ScreenReaderAPI dll.  This DLL will use the available screen
reader on the computer, if any, or use SAPI if not.

"""

import ctypes

from lyntin import exported
from lyntin.ansi import filter_ansi

# Load and configure the ScreenReaderAPI DLL
srapi = ctypes.windll.ScreenReaderAPI
srapi.sapiEnable(1)

def handle_recv_data(args):
    """This function should be called when some datas are received."""
    data = args["data"]
    srapi.sayStringA(filter_ansi(data), 0)
    return data

def load():
    """Initializes the module by binding all the commands."""
    exported.hook_register("net_read_data_filter", handle_recv_data)

def unload():
    """Unbinds the commands (for when we reimport the module)."""
    exported.hook_unregister("net_read_data_filter", handle_recv_data)
