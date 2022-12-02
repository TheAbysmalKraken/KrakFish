#TheAbysmalKraken's Stardew Valley Fishing Automation

import numpy as np
import mss
import cv2
from pynput.keyboard import Key, Controller
import time
import threading

BAR_TOP_COLOUR = np.array([0, 193, 73, 255])
BAR_BOTTOM_COLOUR = np.array([1, 101, 33, 255])
BAR_COLUMN = 20
FISH_COLOUR = np.array([151, 96, 2, 255])
FISH_COLUMN = 20
EXC_COLOUR1 = np.array([0, 186, 247, 255])
EXC_COLOUR2 = np.array([0, 249, 251, 255])

def holdC(holdTime):
    keyboard.press('c')
    time.sleep(holdTime)
    keyboard.release('c')
    return

def findTopBar(screen):
    topBarY = -1
    for row in range(0,600):
        if screen[row][BAR_COLUMN].tolist() == BAR_TOP_COLOUR.tolist():
            topBarY = row
            break

    return topBarY

def findBottomBar(screen):
    bottomBarY = -1
    for row in range(599,0,-1):
        if screen[row][BAR_COLUMN].tolist() == BAR_BOTTOM_COLOUR.tolist():
            bottomBarY = row
            break

    return bottomBarY

def findFish(screen):
    fishY = -1
    for row in range(0,600):
        if screen[row][FISH_COLUMN].tolist() == FISH_COLOUR.tolist():
            fishY = row
            break

    return fishY
    

#Program start delay
startDelay = 5
for i in range(startDelay, 0, -1):
    print(f"Starting in {i}...")
    time.sleep(1)
print("Program started.")

#Create keyboard controller
keyboard = Controller()

fishingTop = cv2.imread('Images\\fishingTop.png',0)
barTop = cv2.imread('Images\\topBarNew2.png',0)

with mss.mss() as sct:

    # The screen part to capture
    monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}
    smallRegion = {}
    
    while True:

        foundUI = False

        while foundUI == False:

            # Grab the data
            screen = np.array(sct.grab(monitor))
            newScreen = cv2.cvtColor(screen, cv2.COLOR_RGB2GRAY)

            #Detect when fishing
            res = cv2.matchTemplate(newScreen,fishingTop,cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            if(max_val > 0.95):
                print("Fishing started!")
                foundUI = True
                smallRegion = {"top": monitor['top'] + max_loc[1], "left": monitor['left'] + max_loc[0], "width": 60, "height": 600}

        barY = 0
        fishY = 0
        prevdy = 0
        prevBarY = 550

        fishing = True

        #GET BAR LENGTH

        # Grab the data
        screen = np.array(sct.grab(smallRegion))

        #Find top bar
        topBarY = findTopBar(screen)

        #Find bottom bar
        bottomBarY = findBottomBar(screen)

        centrePerc = 0.50

        barLength = bottomBarY - topBarY
        barAddition = int(centrePerc*barLength)

        while fishing == True:

            # Grab the data
            screen = np.array(sct.grab(smallRegion))

            #Find top bar
            topBarY = findTopBar(screen)
            if topBarY == -1:
                # If top bar not found, use bottom bar
                bottomBarY = findBottomBar(screen)
                if bottomBarY != -1:
                    topBarY = findBottomBar(screen) - barLength
                else:
                    # If bottom bar also not found, use template matching
                    newScreen = cv2.cvtColor(screen, cv2.COLOR_RGB2GRAY)
                    res = cv2.matchTemplate(newScreen,barTop,cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                    if(max_val > 0.80):
                        topBarY = max_loc[1]

            #Find fish
            fishY = findFish(screen)
            if fishY == -1:
                print("Restarting...\n")
                fishing = False

            barY = topBarY + barAddition   #'Centre' of the bar
            dy = barY - fishY                   #Distance between bar and fish
            dVel = dy - prevdy                  #Rate of change in distance
            barVel = barY - prevBarY            #Velocity of bar
            a = 0.5/100
            b = 1.5/100
            c = 0.9/100

            prevdy = dy
            prevBarY = barY

            holdTime = (a*dy) + (b*dVel) + (c*barVel)
            if(holdTime > 0.7):
                holdTime = holdTime

            if(holdTime > 0):
                t = threading.Thread(target=holdC, args=(holdTime,))
                t.start()

            if cv2.waitKey(25) & 0xFF == ord("q"):
                cv2.destroyAllWindows()
                break

print("Program ended.")
