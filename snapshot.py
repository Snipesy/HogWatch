import win32gui
import win32ui
from PIL import Image
import numpy as np
import cv2
import time
import threading
import os
import sys
import ctypes
from ctypes import windll
import pygame
import pythoncom, pyHook
import difflib
import math


threshold = 0.991
thresholdLocal = 0.90
thresholdCorner = 0.90


def resourcepath(x):
    head, tail = os.path.split(os.path.realpath(sys.argv[0]))
    l = os.path.join(head, x)
    return l


class Template:
    Alliance = cv2.imread(resourcepath('resources\\ticker\\Alliance.png'),1)     #Friendly
    Blue = cv2.imread(resourcepath('resources\\ticker\\Blue.png'),1)             #Friendly
    BlueMil = cv2.imread(resourcepath('resources\\ticker\\BlueMil.png'),1)       #Friendly
    Bounty = cv2.imread(resourcepath('resources\\ticker\\Bounty.png'),1)         #Hostile
    Corp = cv2.imread(resourcepath('resources\\ticker\\Corp.png'),1)             #Friendly
    Criminal = cv2.imread(resourcepath('resources\\ticker\\Criminal.png'),1)     #Hostile
    Fleet = cv2.imread(resourcepath('resources\\ticker\\Fleet.png'),1)           #Friendly
    KillRight = cv2.imread(resourcepath('resources\\ticker\\KillRight.png'),1)   #Hostile
    LightBlue = cv2.imread(resourcepath('resources\\ticker\\LightBlue.png'),1)   #Friendly
    Limited = cv2.imread(resourcepath('resources\\ticker\\Limited.png'),1)       #Hostile
    MilTarget = cv2.imread(resourcepath('resources\\ticker\\MilTarget.png'),)   #Hostile
    Neutral = cv2.imread(resourcepath('resources\\ticker\Neutral.png'),1)       #Hostile
    Orange = cv2.imread(resourcepath('resources\\ticker\\Orange.png'),1)         #Hostile
    Pirate = cv2.imread(resourcepath('resources\\ticker\\Pirate.png'),1)         #Hostile
    Red = cv2.imread(resourcepath('resources\\ticker\\Red.png'),1)               #Hostile
    Suspect = cv2.imread(resourcepath('resources\\ticker\\Suspect.png'),1)         #Hostile
    WarTarget = cv2.imread(resourcepath('resources\\ticker\\WarTarget.png'),1)   #Hostile
    Yellow = cv2.imread(resourcepath('resources\\ticker\\Yellow.png'),1)
    
Friendlies = [Template.Alliance, Template.Blue, Template.LightBlue, Template.Corp, Template.Fleet ]
Hostiles = [Template.Criminal, Template.Neutral, Template.Orange, Template.Pirate, Template.Red, Template.Suspect, Template.WarTarget, Template.Yellow]
strHostiles = ['Criminal', 'Neutral', 'Orange', 'Pirate', 'Red', 'Suspect', 'WarTarget', 'Yellow']
strFriendlies =['Alliance', 'LightBlue', 'Blue', 'Corp', 'Fleet',]


global window
method = 'cv2.TM_CCOEFF'

def getPix():

    
    hwnd = win32gui.FindWindow(None, window)
    left, top, right, bot = win32gui.GetClientRect(hwnd)
    w = int(right - left)
    h = int(bot - top)
    if right2 != 0:
        w = right - left
    else:
        w = int(280)
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
    saveDC.SelectObject(saveBitMap)
    result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 0)
    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)
    
    # Turns buffer into usable cv array.
    im = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1)
    image = np.array(im)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    

    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)
        
    return image

def getFull():

    global window
    
    hwnd = win32gui.FindWindow(None, window)
    left, top, right, bot = win32gui.GetClientRect(hwnd)
    w = int(right - left)
    h = int(bot - top)
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
    saveDC.SelectObject(saveBitMap)
    result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 0)
    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)
    
    # Turns buffer into usable cv array.
    im = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1)
    image = np.array(im)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    

    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)
        
    return image

lock = threading.Lock()

def KeyEventThread1(i):
    global reset
    global num
    lock.acquire()
    if pygame.mixer.get_busy() == True:
        pygame.mixer.stop()
        print '[INFO] Temporary Mute ACTIVE! Press end again to reset!'
    elif pygame.mixer.get_busy() == False and reset != 1 and num > 0:
        print '[INFO] Resetting...'
        reset = 1
    lock.release()
def KeyEventThread2(i):
    global nudge
    lock.acquire()
    nudge = nudge - 1
    if nudge < 0:
        nudge = 0
    print '[INFO] Nudge = ', nudge
    lock.release()
def KeyEventThread3(i):
    global c
    global nudge
    lock.acquire()
    nudge = nudge + 1
    if nudge > c:
        nudge = nudge - 1
    print '[INFO] Nudge = ', nudge
    lock.release()
def KeyEventThread5(i):
    lock.acquire()
    global volume
    volume = volume - .1
    if volume < .09:
        volume = 0
    if volume == 0:
        print '[INFO] Volume muted.'
    else:
        print '[INFO] Volume = ', volume
    pygame.mixer.Channel(0).set_volume(volume)
    lock.release()
def KeyEventThread4(i):
    lock.acquire()
    global volume
    volume = volume + .1
    if volume > .91:
        volume = 1
    print '[INFO] Volume = ', volume
    pygame.mixer.Channel(0).set_volume(volume)
    lock.release()
def KeyEventThread6(i):
    lock.acquire()
    global right2
    global left2
    try:
        image = getPix()
        ih, iw = image.shape[:2]
        try:
            img2 = image[:,:,2]
            img2 = img2 - cv2.erode(img2, None)
            img2 = img2 - cv2.erode(img2, None)
            template = cv2.imread(resourcepath('resources\\ticker\\Local.png'))[:,:,2]
            template = template - cv2.erode(template, None)
            ccnorm = cv2.matchTemplate(img2, template, cv2.TM_CCORR_NORMED)
            print ccnorm.max()
            #loc = np.where(ccnorm == ccnorm.max())
            thresholdA = 0.95
            loc = np.where( ccnorm >= thresholdLocal)
            th, tw = template.shape[:2]
            for pt in zip(*loc[::-1]):
                #if ccnorm[pt[::-1]] < thresholdA:
                #    continue
                cv2.rectangle(image, (pt[0] - 2, pt[1] - 2), (pt[0] + 2 + tw, pt[1] + 2 + th),
                        (255, 0, 0), 2)
        except Exception as e:
            print e
            print '[WARNING] Error on Local Find'
        else:
            print '[INFO] Local Found'
        try:
            print loc
            debug = image[loc[0] + 18:loc[0] + 30, loc[1]:,2]
            cv2.imwrite('Debug2.png', debug)
            cornerY = loc[0][0] + 18
            cornerX = loc[1][0]
            debug = debug - cv2.erode(debug, None)
            template = cv2.imread(resourcepath('resources\\ticker\\Soldier.png'))[:,:,2]
            template = template - cv2.erode(template, None)
            ccnorm = cv2.matchTemplate(debug,template,cv2.TM_CCOEFF_NORMED)
            print ccnorm.max()
            loc = np.where(ccnorm == ccnorm.max())
            cornerX = loc[1][0] + cornerX
            cornerY = cornerY
            cv2.rectangle(image, (cornerX - 0, cornerY - 1), (cornerX + 11, cornerY + 12),
                        (255, 0, 0), 1)
        except Exception as e:
            print '[WARNING] Error on corner Find'
            print e

        if right2 != 0:
            debug = image[:, left2:right2]
        else:
            debug = image[:, 80:250]
        w = 8
        h = 8
        print '\n[INFO] --- DEBUG --- \n'
        for i in range(len(Hostiles)):
            Ticker = Hostiles[i]
            res = cv2.matchTemplate(debug,Ticker,cv2.TM_CCOEFF_NORMED)
            loc = np.where( res >= threshold)
            for pt in zip(*loc[::-1]):
                cv2.rectangle(image, (pt[0] + left2 - 2, pt[1] - 2), (pt[0] + left2 + w + 2, pt[1] + h + 2), (0,0,255), 2)
            print '[INFO] ', len(loc[0]), strHostiles[i]
        for i in range(len(Friendlies)):
            Ticker = Friendlies[i]
            res = cv2.matchTemplate(debug,Ticker,cv2.TM_CCOEFF_NORMED)
            loc = np.where( res >= threshold)
            for pt in zip(*loc[::-1]):
                cv2.rectangle(image, (pt[0] + left2 - 2, pt[1] - 2), (pt[0] + left2 + w + 2, pt[1] + h + 2), (0,255,0), 2)
            print '[INFO] ', len(loc[0]), strFriendlies[i]

        cv2.rectangle(image, (left2 - 2, 0), (right2 + 2, ih), (255,0,0), 2)
        cv2.imwrite('Debug.png', image)

        cv2.putText(image, "Debug", (5, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 3)
        cv2.imwrite('Debug.png', image)

        print '[INFO] ScreenShots Placed Locally\n'
    except Exception as e:
        print e
            
    lock.release()
def KeyEventThread7(i):
    lock.acquire()
    global left2
    global right2
    global local
    global localC
    global threadStop
    try:
        print '\n[INFO] Attempting to find region....'
        thresholdA = 0.95
        image = getFull()
        ih, iw = image.shape[:2]
        img2 = image[:,:,2]
        img2 = img2 - cv2.erode(img2, None)
        img2 = img2 - cv2.erode(img2, None)
        template = cv2.imread(resourcepath('resources\\ticker\\Local.png'))[:,:,2]
        template = template - cv2.erode(template, None)
        ccnorm = cv2.matchTemplate(img2, template, cv2.TM_CCORR_NORMED)
        if ccnorm.max() < thresholdLocal:
            print '[WARNING] Best match is: ', ccnorm.max()
            beep()
            raise Exception('[WARNING] Threshold less than allowed .90')
        local = np.where(ccnorm == ccnorm.max())
        print '[INFO] Local Found! Attempting to find corner!'
        try:
            debug = image[local[0] + 18:local[0] + 30, local[1]:,2]
            cornerY = local[0][0] - 7
            cornerX = local[1][0]
            debug = debug - cv2.erode(debug, None)
            template = cv2.imread(resourcepath('resources\\ticker\\Soldier.png'))[:,:,2]
            template = template - cv2.erode(template, None)
            ccnorm = cv2.matchTemplate(debug,template,cv2.TM_CCOEFF_NORMED)
            loc = np.where(ccnorm == ccnorm.max())
            if ccnorm.max() < thresholdCorner:
                raise
            cornerX = loc[1][0] + cornerX
            cornerY = cornerY
            localC = (cornerX, cornerY)
            print '[INFO] Corner Found! Attempting to find region....'
            decesion = cornerX
        except Exception:
            print '[NOTICE] Did not find corner. Attempting anyway...'
            decesion = 10000

        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        master = []
        for i in range(len(Hostiles)):
            Ticker = Hostiles[i]
            Ticker = cv2.cvtColor(Ticker, cv2.COLOR_BGR2GRAY)
            res = cv2.matchTemplate(image,Ticker,cv2.TM_CCOEFF_NORMED)
            loc = np.where( res >= threshold)
            if len(loc[0]) > 0:
                for index in range(len(loc[0])):
                    thing = (loc[1][index],loc[0][index])
                    master.append(thing)
        for i in range(len(Friendlies)):
            Ticker = Friendlies[i]
            Ticker = cv2.cvtColor(Ticker, cv2.COLOR_BGR2GRAY)
            res = cv2.matchTemplate(image,Ticker,cv2.TM_CCOEFF_NORMED)
            loc = np.where( res >= threshold)
            if len(loc[0]) > 0:
                for index in range(len(loc[0])):
                    thing = (loc[1][index],loc[0][index])
                    master.append(thing)
        y1 = local[0][0]
        x1 = local[1][0]
        minD = 10000
        if len(master[0]) == 0:
            beep()
            if decesion != 10000:
                left2 = x1
                right2 = decesion
                print '[NOTICE] Since corner was found the region engulfs the local box.' \
                      ' You should press F12 to verify this.'
                print ' This is going to cause lag, so press HOME again the moment a ticker comes into local.'
            else:
                print '[WARNING] Your region is fucked.'
            time.sleep(.2)
            raise Exception("[WARNING] No Tickers Found!")
        for i in range(len(master)):
            x2, y2 = master[i]
            if x1 < x2 and x2 < (decesion + 10) and y2 > y1 + 18:  #Coordinate parsing
                D = math.sqrt( (x2 - x1)**2 + (y2 - y1)**2 )
                if D < minD:
                    minD = D
                    Point = x2, y2
        if minD == 10000:
            beep()
            if decesion != 10000:
                left2 = x1
                right2 = decesion
                print '[NOTICE] Since corner was found the region engulfs the local box. You should press F12' \
                      ' to verify this.'
                print ' This is going to cause lag, so press HOME again the moment a ticker comes into local.'
            else:
                print '[WARNING] Your region is fucked.'
            raise Exception("[WARNING] No Tickers in Region!")
        if minD > 300:
            print '''
[NOTICE] The region is probably not right.
        Insure there is at least ONE ticker in your local box and
        that the closet ticker is to the words \'local\,
        '''
            print '[INFO] Distance to point: ', minD
            beep()
        print '[INFO] Local Ticker = ', Point
        print '[INFO] You should probably press F12 to verify this...'
    except Exception as e:
        print e
    else:
        threadStop = 0
        xp,yp = Point
        left2 = xp - 2
        right2 = xp + 12
        writeValues()

    lock.release()

def localUpdate(run_event):
    global local
    global localC
    global threadStop
    global window
    awin = 0
    spamLock = 0
    start = 1
    while run_event.is_set():
        active = win32gui.GetWindowText(win32gui.GetForegroundWindow())
        if active.lower() == window.lower() or start == 1:
            threadStop = 0
            if awin == 1 and start == 0:
                awin = 0
            start = 0
            try:
                image = getFull()
                img2 = image[:,:,2]
                img2 = img2 - cv2.erode(img2, None)
                img2 = img2 - cv2.erode(img2, None)
                template = cv2.imread(resourcepath('resources\\ticker\\Local.png'))[:,:,2]
                template = template - cv2.erode(template, None)
                ccnorm = cv2.matchTemplate(img2, template, cv2.TM_CCORR_NORMED)
                if ccnorm.max() < thresholdLocal:
                    raise Exception('[WARNING] Threshold less than allowed .98')
                localU = np.where(ccnorm == ccnorm.max())
                try:
                    if localU != local and threadStop == 0:
                        print '[NOTICE] Local Box Channged!'
                        t = threading.Thread(target=KeyEventThread7, args=(1,))
                        threadStop = 1
                        t.start()

                except:
                    local = localU
            except Exception as e:
                print '[INFO] Could Not Find Local for check!'
            else:
                try:
                    debug = image[localU[0] + 18:localU[0] + 30, localU[1]:,2]
                    cornerY = localU[0][0] - 7
                    cornerX = localU[1][0]
                    debug = debug - cv2.erode(debug, None)
                    template = cv2.imread(resourcepath('resources\\ticker\\Soldier.png'))[:,:,2]
                    template = template - cv2.erode(template, None)
                    ccnorm = cv2.matchTemplate(debug,template,cv2.TM_CCOEFF_NORMED)
                    loc = np.where(ccnorm == ccnorm.max())
                    if ccnorm.max() < thresholdCorner:
                        raise Exception('[WARNING] Threshold less than allowed .99')
                    cornerX = loc[1][0] + cornerX
                    cornerY = cornerY
                    cornerCoord = (cornerX, cornerY)
                    if spamLock == 1:
                        print '[INFO] Corner Found! Resuming checks.'
                        spamLock = 0
                    try:
                        if cornerCoord != localC and threadStop == 0:
                            if spamLock == 1:
                                print 'Corner Found!'
                            threadStop = 1
                            print '[Notice] Local Box Changed (Corner)'
                            t = threading.Thread(target=KeyEventThread7, args=(1,))
                            t.start()
                    except:
                        localC = cornerCoord
                except Exception as e:
                    if spamLock == 0:
                        print '[INFO] Could not find local corner for check!'
                        spamLock = 1
            time.sleep(8)
        else:
            if awin == 0:
                start = 1
                awin = 1
        time.sleep(2)

def writeValues():
    global window
    global left2
    global right2
    global volume
    f = open('data.txt', 'w')
    left2s = str(left2) + '\n'
    right2s = str(right2) + '\n'
    windowname = str(window) + '\n'
    volumeS = str(volume)
    f.write(left2s)
    f.write(right2s)
    f.write(windowname)
    f.write(volumeS)
    f.close()
        

def OnKeyboardEvent(event):
    if event.Key == "End":
        t = threading.Thread(target=KeyEventThread1, args=(1,))
        t.start()
    elif event.Key == "Next":
        t = threading.Thread(target=KeyEventThread2, args=(1,))
        t.start()
    elif event.Key == 'Prior':
        t = threading.Thread(target=KeyEventThread3, args=(1,))
        t.start()
    elif event.Key == 'Insert':
        t = threading.Thread(target=KeyEventThread4, args=(1,))
        t.start()
    elif event.Key == 'Delete':
        t = threading.Thread(target=KeyEventThread5, args=(1,))
        t.start()
    elif event.Key == 'F12':
        t = threading.Thread(target=KeyEventThread6, args=(1,))
        t.start()
    elif event.Key == 'Home':
        t = threading.Thread(target=KeyEventThread7, args=(1,))
        t.start()
    # return True to pass the event to other handlers
    return True

        



def pump(run_event):
    hm = pyHook.HookManager()
    hm.KeyDown = OnKeyboardEvent
    hm.HookKeyboard()

    while run_event.is_set():
        time.sleep(.005)
        pythoncom.PumpWaitingMessages()


def intro():
    print '''
    Hog-Watch v1.8
    
    We're out of beta and releasing on time!

    How to:
        Read readme.txt
        Insure your local chat is visible and has
        at least one ticker in it. Then press HOME
        to manually align it.
        For best results keep local unpinned and don't
        fucking use 100% transparency.
    '''
    setup()
    
def setup():

    global left2
    global right2
    global volume
    global window
    
    EnumWindows = ctypes.windll.user32.EnumWindows
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
    GetWindowText = ctypes.windll.user32.GetWindowTextW
    GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
    IsWindowVisible = ctypes.windll.user32.IsWindowVisible
    titles = []
    def foreach_window(hwnd, lParam):
        if IsWindowVisible(hwnd):
            length = GetWindowTextLength(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            GetWindowText(hwnd, buff, length + 1)
            titles.append(buff.value)
        return True
    EnumWindows(EnumWindowsProc(foreach_window), 0)

    titles = filter(lambda element: 'EVE -' in element, titles)
    
    print 'Active Clients: ', titles
    
    try:
        with open("data.txt", "r") as ins:
            array = []
            for line in ins:
                array.append(line)
        ins.close()
        left2 = int(array[0].replace('\n', ''))
        right2 = int(array[1].replace('\n', ''))
        winname = array[2].replace('\n', '')
        volume = float(array[3].replace('\n', ''))
        print 'Leave Blank to use Previous Client: ', winname
    except:
        print '[INFO] No data, using defaults.'
        left2 = 0
        right2 = 0
        volume = .7
        winname = 'No Previous Client'
    
    window = 'EVE - ' + raw_input("Enter your character name: ")
    windowtest = window.lower()
    winname = winname.lower()
    titlesL = map(lambda x:x.lower(),titles)
    if window == 'EVE - ':
            if winname in (titlesL):
                window = winname
                print 'Using client ', window
                main()
            else:
                print '[WARNING] That won\'t work\n \n \n'
                setup()


    if windowtest not in (titlesL):
        try:
            sort = difflib.get_close_matches(window, titles, 1, .7)
            window = sort[0]
            print 'Auto Match:', window
            while window not in (titles):
                print "[WARNING] Try that again. \n \n"
                setup()
        except:
            print '[WARNING] Try that again \n \n'
            setup()
        else:
            writeValues()
            main()
    print 'Using client ', window
    writeValues()
    main()

def beep():
    global volume
    beep = pygame.mixer.Sound(resourcepath('resources\\sounds\\beep.wav'))
    pygame.mixer.stop()
    beep.play()
    beep.set_volume(volume)

def getNum(iff):
    global x
    global nudge
    global f
    global c
    global right2
    global left2


    c = 0
    rec = 0
    
    while True:
    
        try:
            image = getPix()
        except ValueError: # catch
            print '[WARNING] Bad Capture. Window Minimized?'
            beep()
            rec = 1
            time.sleep(5)
        except Exception:
            beep()
            raise Exception('[WARNING] A critical error occured trying to find window. (closed?)')
        else:
            if rec == 1:
                print '[INFO] Capture Restored'
            if right2 != 0:
                image = image[:, left2:right2]
            else:
                image = image[:, 80:250]
            break
        
    if iff == 'Hostiles':
        for i in range(len(Hostiles)):
            Ticker = Hostiles[i]
            while True:
                try:
                    res = cv2.matchTemplate(image,Ticker,cv2.TM_CCOEFF_NORMED)
                    loc = np.where( res >= threshold)
                except Exception as e:
                    print type(e)
                    print e.args
                    print e
                    time.sleep(3)
                except KeyboardInterrupt:
                    break
                else:
                    break
            c = c + len(loc[0])
        while (c -nudge) < 0:
            nudge = nudge - 1
            print '[INFO] Nudge = ', nudge, ' (Auto)'
    else:
        for i in range(len(Friendlies)):
            Ticker = Friendlies[i]
            while True:
                try:
                    res = cv2.matchTemplate(image,Ticker,cv2.TM_CCOEFF_NORMED)
                    loc = np.where( res >= threshold)
                except Exception as e:
                    print type(e)
                    print e.args
                    print e
                    time.sleep(3)
                except KeyboardInterrupt:
                    break
                else:
                    break
            c = c + len(loc[0])
    
    num = c - nudge
    return num

def main():

    global nudge
    global volume
    global reset
    global num

    reset = 0
    timer = 0
    x = 0
    nudge = 0
    d1 = 3
    pygame.mixer.init()
    pygame.mixer.set_num_channels(1)
    alarm = pygame.mixer.Sound(resourcepath('resources\\sounds\\masteralarm.wav'))

    if __name__ == "__main__":
        
        run_event = threading.Event()
        run_event.set()
        t2 = threading.Thread(target = localUpdate, args = (run_event,))
        t3 = threading.Thread(target = pump, args = (run_event,))
        t3.start()
        time.sleep(1)
        t2.start()
        print '\n[INFO] Ready'
        print '[NOTICE] You should probably push HOME to find the region.'
        while True:
            try:
                num = getNum('Hostiles')
                if reset == 1:
                    num = 0
                    reset = 0
                if num == 0 and x == 0: #Clear -> Clear
                    x = num
                elif num == x:          #No Change
                    timer = timer + 10
                    if timer > 1000 and pygame.mixer.get_busy() == True:
                        alarm.stop()
                        print '[INFO] Auto-Mute'
                elif num > x and x == 0:#First
                    print '[INFO] ', num, 'Hostiles!'
                    x = num
                    alarm.play(-1)
                    pygame.mixer.Channel(0).set_volume(volume)

                elif num > 0:           #Change in Hostiles
                    print '[INFO] ', num, 'Hostiles!'
                    timer = timer + 10
                    x = num
                elif x > 0 and num == 0:#X Hostiles -> Clear | Reset Alarm
                    timer = 0
                    print '[INFO] Clear!'
                    alarm.stop()
                    x = num
                else:                   #In case of shit math
                    print '[INFO] ', num, 'Hostiles!'
                    x = num
            except KeyboardInterrupt:
                print "[INFO] Good bye"
                break
            except Exception as e:
                print e
                print '[WARNING] A Critical Error occured. System will now shut down.'
                pygame.mixer.stop()
                beep()
                break
            else:
                time.sleep(d1)
        print 'Stopping threads....'
        run_event.clear()
        t2.join()
        t3.join()
        pygame.mixer.stop()
        print 'Writing data....'
        writeValues()
        print '3'
        time.sleep(1)
        print '2'
        time.sleep(1)
        print '1'
        time.sleep(1)
        sys.exit()

intro()

 