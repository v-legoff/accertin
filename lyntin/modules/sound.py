from lyntin import exported
from lyntin.modules import modutils

# this will hold the command information for adding to
# Lyntin later on
commands_dict = {}

#import pySonic

#w = pySonic.World()

volume = 50

sources = []

def play(sound):
    global sources, volume
    #src = pySonic.Source()
    #src.Sound = pySonic.FileSample(sound)
    #src.Volume = int((volume * 255) / 100)
    src.Play()
    #sources.append(src)
    #for src in sources[:]:
    #    if not src.IsPlaying():
    #        sources.remove(src)

def sound_cmd(ses, args, input):
    """
    This command allows you to play a sound.
    """
    filename = args["filename"]
    try:
        play('sounds/%s' % filename)
    except:
        exported.write_message("couldn't play sound: %s" % filename)

commands_dict["sound"] = (sound_cmd, "filename")

def soundvolume_cmd(ses, args, input):
    """
    This command allows you to set the sound volume (from 0 to 100).
    """
    global volume
    try:
        v = int(args["volume"])
        if 0 <= v <= 100:
            volume = v
            exported.write_message("sound volume set to %s" % args["volume"])
        else:
            raise
    except:
        exported.write_message("couldn't set volume: %s must be an integer from 0 to 100" % args["volume"])

commands_dict["soundvolume"] = (soundvolume_cmd, "volume")

def load():
    """ Initializes the module by binding all the commands."""
    modutils.load_commands(commands_dict)

def unload():
    """ Unbinds the commands (for when we reimport the module)."""
    modutils.unload_commands(commands_dict)
