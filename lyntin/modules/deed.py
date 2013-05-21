#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: deed.py,v 1.2 2004/04/02 00:04:23 willhelm Exp $
#######################################################################
"""
This module defines the DeedManager which handles deeds (user events).

Deeds can be used to keep track of when things happened.  I tend to
create deeds whenever someone does something nice for me via an action.
This allows me to have a log of who did what to me and when they did it
(if you use the $TIMESTAMP variable) even if I'm away from the computer
or in the midst of copious battle spam.
"""

# deed code originally written by Sebastian John.

import string
from lyntin import manager, utils, exported
from lyntin.modules import modutils

class DeedData:
  def __init__(self):
    self._deeds = []
  
  def addDeed(self, deed):
    """
    Adds a deed to the list.
    
    @param deed: the actual deed text
    @type deed: string
    """
    self._deeds.append(deed)
  
  def clear(self):
    """
    Removes all the deeds.
    """
    self._deeds = []
  
  def getInfo(self, num=""):
    """
    Returns information about the deeds in here.
    
    This is used only by #deed to show all the deeds stored.
    
    @param num: if a number, then returns the last num deeds.  otherwise
        returns deeds that match what this expands to.
    @type num: string or int

    @returns: one big string with all the deeds in it
    @rtype: string
    """
    if not self._deeds:
      return ""
    
    if num.isdigit():
      count = int(num)
      listing = self._deeds[-count:]
    else:
      listing = self._deeds
    
    return string.join(listing, "\n")
  
  def getStatus(self):
    """
    Returns the number of deeds actually stored.

    @returns: the total number of deeds in this DeedData object.
    @rtype: int
    """
    return "%d deed(s)." % len(self._deeds)

class DeedManager(manager.Manager):
  def __init__(self):
    self._deeds = {}

  def getDeedData(self, ses):
    if not self._deeds.has_key(ses):
      self._deeds[ses] = DeedData()
    return self._deeds[ses]

  def clear(self, ses):
    if self._deeds.has_key(ses):
      self._deeds[ses].clear()

  def getInfo(self, ses, num=""):
    return self.getDeedData(ses).getInfo(num)

  def getStatus(self, ses):
    return self.getDeedData(ses).getStatus()


commands_dict = {}

def deed_cmd(ses, args, input):
  """
  Deeds serve as a kind of notebook - whatever you don't want
  to forget, store it in a deed.

  examples::
    #deed                             -- prints all the deeds for 
                                         that session
    #deed {$TIMESTAMP Joe healed me}  -- adds a new deed to the list
    #deed 10                          -- prints the last 10 deeds

  Before a deed is stored, variables are expanded--this allows you
  to use system, global, and session variables in your deeds like
  $TIMESTAMP which will mark when the deed was created.
  
  category: commands
  """
  # original deed_cmd code contributied by Sebastian John

  if (ses.getName() == "common"):
    exported.write_error("deed cannot be applied to common session.", ses)
    return

  deedtext = args["text"]
  quiet = args["quiet"]

  if not deedtext:
    data = exported.get_manager("deed").getInfo(ses)
    if data == "":
      data = "deed: no deeds defined."
    
    exported.write_message(data, ses)
    return
  
  if deedtext.isdigit():
    data = exported.get_manager("deed").getInfo(ses, deedtext)
    if data == "":
      data = "deed: no deeds defined."
    
    exported.write_message(data, ses)
    return

  exported.get_manager("deed").getDeedData(ses).addDeed(deedtext)
  if not quiet:
    exported.write_message("deed: {%s} added." % deedtext, ses)

commands_dict["deed"] = (deed_cmd, "text= quiet:boolean=false")


dm = None

def load():
  """ Initializes the module by binding all the commands."""
  global dm
  modutils.load_commands(commands_dict)
  dm = DeedManager()
  exported.add_manager("deed", dm)


def unload():
  """ Unloads the module by calling any unload/unbind functions."""
  global dm
  modutils.unload_commands(commands_dict.keys())
  exported.remove_manager("deed")

# Local variables:
# mode:python
# py-indent-offset:2
# tab-width:2
# End:
