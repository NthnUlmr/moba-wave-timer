# <GPLv3_Header>
## - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# \copyright
#                    Copyright (c) 2024 Nathan Ulmer.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# <\GPLv3_Header>

##
# \mainpage Moba Wave Timer
#
# \copydoc WaveTimer.py

##
# \file WaveTimer.py
#
# \author Nathan Ulmer
#
# \date \showdate "%A %d-%m-%Y"
#
# \brief A simple script which looks at the screen to see when the game (league of ... you know) starts and then starts
# a timer. That timer then counts up and is triggered at certain predefined times to print an event and play a
# corresponding sound. The intent is to make it easier to know when waves, dragons, etc are spawning. This is basically
# already a feature of Porofessor (an Overwolf addon) but I wanted to be able to get a better feel of which waves were
# cannon waves and which were not in addition to dragon timers and stuff.
#
# This uses PIL and cv2 to actually tell when the game starts, which is important for the timers. It does this by looking
# for an exact color in the corner of the screen. It's not the most sophisticated way to detect the start of the game, but
# for one patch it was very effective.
#
## \todo Fix issue where corner pixel is no longer expected color when the game starts.
## \todo Look into Overwolf and how it sees the screen and knows about the game. It's probably using a hook into the game
# memory? This is just a basic timer.
import time
import winsound
frequency = 2500
cannonFrequency = 1500
duration = 200
# Time waves in Lol
spawnStartTime = 65
waveTime = 30
dragonSpawnTime = 5 * 60
baronSpawnTime = 20 * 60
riftSpawnTime = 10 * 60
lvl6Time = 6 * 60

def timeWave(startTime,waveCount,lastWave):
    currentTime = time.time()

    if currentTime - lastWave >= waveTime and startTime > spawnStartTime:

        waveCount = waveCount + 1
        if ((waveCount % 3 == 0 and waveCount < 41) or (waveCount >= 41 and waveCount % 2 == 0) or (waveCount >= 70)):
            print(waveCount, "CANNON")
            winsound.Beep(cannonFrequency, duration)
        else:
            print(waveCount, "WAVE")
            winsound.Beep(frequency, duration)
        lastWave = time.time()


def pollIsGameStarted(viewer):
    viewer.center()
    regionOfInterest = viewer.grab()
    height, width, channel = np.array(regionOfInterest).shape
    image = Image.frombytes('RGB', regionOfInterest.size, regionOfInterest.bgra, 'raw', 'BGRX')

    bb = image.getbbox()
    bottomRightCorner = image.getpixel((bb[2]-1,bb[3]-1))

    print(bottomRightCorner)

    if(bb[2] > viewer.initialSize[0] and bb[3] > viewer.initialSize[1] and bottomRightCorner==(38, 47, 48)): # Hardcoded border color fror map in game
        print("SUCCESS!!! FOUND GAME")
        return True

    return False


def main():
    gameStarted = False
    winsound.Beep(frequency, duration)


    viewer = GameViewer()

    while(not gameStarted):
        viewer.center()
        gameStarted = pollIsGameStarted(viewer)
        viewer.center()
    viewer.stop()
    startTime = time.time()
    lastWave = startTime
    waveCount = 0
    while(True):
        #timeWave(startTime,waveCount,lastWave)
        currentTime = time.time()

        if currentTime - lastWave >= waveTime and (currentTime - startTime) > spawnStartTime:

            waveCount = waveCount + 1
            if ((waveCount % 3 == 0 and waveCount < 41) or (waveCount >= 41 and waveCount % 2 == 0) or (
                    waveCount >= 70)):
                print('%.2ds' % (currentTime-startTime), "Wave",waveCount,": CANNON")
                winsound.Beep(cannonFrequency, duration)
            else:
                print('%.2ds' % (currentTime-startTime),"Wave",waveCount,": baby")
                winsound.Beep(frequency, duration)
            lastWave = time.time()


        if (currentTime - startTime) > dragonSpawnTime:
            print('%.2ds' % (currentTime - startTime), "--FIRST DRAGON SPAWN!!")
            winsound.Beep(cannonFrequency, duration*4)

        if (currentTime - startTime) > baronSpawnTime:
            print('%.2ds' % (currentTime - startTime), "--FIRST BARON SPAWN!!")
            winsound.Beep(cannonFrequency, duration * 4)

        if (currentTime - startTime) > riftSpawnTime:
            print('%.2ds' % (currentTime - startTime), "--FIRST RIFT HERALD SPAWN!!")
            winsound.Beep(cannonFrequency, duration * 4)


        if (currentTime - startTime) > lvl6Time:
            print('%.2ds' % (currentTime - startTime), "--YOU SHOULD BE AT LVL 6!!!")
            winsound.Beep(cannonFrequency, duration * 4)



import numpy as np
import cv2
from PIL import Image
from mss import mss
import win32api
import win32gui
import win32con
import time
class GameViewer:
    def __init__(self,windowTitle="League of Legends (TM) Client"):
        print("GameViewer")
        self.windowTitle = windowTitle
        self.capture = cv2.VideoCapture(0)

        self.image_list = []
        self.start = time.time()

        self.hwnd = win32gui.FindWindow(None, self.windowTitle)
        win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        self.rect = win32gui.GetWindowPlacement(self.hwnd)[-1]
        self.initialSize = (self.rect[2]-self.rect[0],self.rect[3]-self.rect[1] )
        self.origStart = time.time()
        print(self.rect)
        # The screen part to capture
        self.monitor = {"top": self.rect[1], "left": self.rect[0], "width":self.rect[2]-self.rect[0] , "height": self.rect[3]-self.rect[1]}
        self.output = "sct-{top}x{left}_{width}x{height}.png".format(**self.monitor)

    def stop(self):
        self.capture.release()
    def center(self):
        self.windowTitle = "League of Legends (TM) Client"
        self.hwnd = win32gui.FindWindow(None, self.windowTitle)
        self.rect = win32gui.GetWindowPlacement(self.hwnd)[-1]
        self.monitor = {"top": self.rect[1], "left": self.rect[0], "width": self.rect[2] - self.rect[0],
                        "height": self.rect[3] - self.rect[1]}
        self.output = "sct-{top}x{left}_{width}x{height}.png".format(**self.monitor)

    def grab(self):
        ret, frame = self.capture.read()

        with mss() as sct:
            #self.image_list.append(sct.grab(monitor))

            while (time.time() - self.start < 1.0 / 2.0):
                pass
            self.start = time.time()
            return sct.grab(self.monitor)

if __name__ == '__main__':
    print("HELLO")
    main()


# <GPLv3_Footer>
################################################################################
#                      Copyright (c) 2024 Nathan Ulmer.
################################################################################
# <\GPLv3_Footer>