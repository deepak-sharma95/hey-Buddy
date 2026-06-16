import os
import eel

from engin.feature import playAssistantsound
from engin.command import *

eel.init("www")

playAssistantsound()

eel.start('index.html', mode='edge', host='localhost', block=True, port=0)
    