"""
This module filters MUD data from MultiMUD:
- add accented characters
- reformat prompts
"""
from lyntin import ansi, manager, utils, exported
from lyntin.modules import modutils

import re
import string

def init_accents():
    global accents
    accents = {}
    for line in open("accents.txt"):
        a = line.split()
        if len(a) == 2:
            accents[a[0]] = a[1]

init_accents()

def add_special_characters(s):
    global accents
    tokens = []
    t = ""
    for c in s:
        if c not in string.letters:
            tokens.append(t)
            t = ""
            tokens.append(c)
        else:
            t += c
    if t:
        tokens.append(t)
    s2 = ""
    for w in tokens:
        if accents.has_key(w.lower()):
            w = w.lower()
#            open("utile.txt", "at").write("%s %s\n" % (w, accents[w]))
            w = accents[w]
        s2 += w
    return s2

prev = {"sang": None, "vie": None, "magie": None, "mouv": None, "adversaire": None}

def sur(s):
    return s.replace("/", " sur ")

def play_prop_sound(a, b, enemy=False):
    if enemy:
        base = 6000
    else:
        base = 6100
    ratio = divmod(a * 10, b)[0]
    exported.lyntin_command("#sound %s.ogg" % (ratio + base), internal=1)

def play_var_sound(mem):
    v1, v2 = mem.split("/")
    play_prop_sound(int(v1), int(v2))

def _prop(mem):
    if not mem:
        return None
    v1, v2 = mem.split("/")
    return divmod(int(v1) * 10, int(v2))[0]

def stats_filter(mem):
    def repl(m):
        global prev
        s = ""
        for k, v in m.groupdict().items():
            if v is None:
                continue
            if v != prev[k] and k != "mouv" or \
               _prop(v) != _prop(prev[k]) and k == "mouv":
                if k == "vie":
                    play_var_sound(v)
                s += k + " " + sur(v) + "\n"
            prev[k] = v
        return s
    def repl2(m):
        global prev
        s = ""
        for k, v in m.groupdict().items():
            if v != prev[k]:
                try:
                    play_prop_sound(int(v), 100, enemy=True)
                except:
                    pass
                s += k + " " + v + " pour cent\n"
            prev[k] = v
        return s
#    open("log.txt", "a").write(mem + "$$$")
    mem = re.sub("(?m)^(\{(?P<sang>[0-9]+/[0-9]+)\} )?Vie: (?P<vie>[0-9]+/[0-9]+)  Mag: (?P<magie>[0-9]+/[0-9]+)  Mou: (?P<mouv>[0-9]+/[0-9]+) ", repl, mem)
    mem = re.sub("(?m)^ Style-\[.*?\]  Action-\[.*?\]  Adv-\[(?P<adversaire>[0-9]+)%\] ", repl2, mem)
    return mem

prev_mem = ""

def group_line(mem):
    global prev_mem
    prev_mem += mem
#    if prev_mem[-1:] == "\n":
    if "\n" in prev_mem:
        r = prev_mem
        prev_mem = ""
        return r
    else:
        return ""

def remove_lines_without_letters_or_prompt(mem):
    return re.sub("^[^a-zA-Z0-9>]*$", "", mem)

def my_filters(mem):
#    mem = group_line(mem)
    mem = remove_lines_without_letters_or_prompt(mem)
    mem = add_special_characters(mem)
    mem = stats_filter(mem)
    return mem

def mudfilter(args):
    text = args["dataadj"]
    return my_filters(text)

commands_dict = {}

def multimud_var_cmd(ses, args, input):
    """
    This command allows you to display a variable (mouv, vie, magie) from multimud.
    """
    exported.write_message("%s" % prev[args["var_name"]])

commands_dict["multimud_var"] = (multimud_var_cmd, "var_name")

def multimud_play_var_cmd(ses, args, input):
    """
    This command allows you to play a variable (mouv, vie, magie) from multimud.
    """
    play_var_sound("%s" % prev[args["var_name"]])

commands_dict["multimud_play_var"] = (multimud_play_var_cmd, "var_name")

def load():
    """ Initializes the module by binding all the commands."""
    exported.hook_register("mud_filter_hook", mudfilter)
    modutils.load_commands(commands_dict)

def unload():
    """ Unloads the module by calling any unload/unbind functions."""
    exported.hook_unregister("mud_filter_hook", mudfilter)
    modutils.unload_commands(commands_dict)
