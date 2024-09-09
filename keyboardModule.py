import cv2
import numpy as np
import time
from keys import Key
from handTracker import HandTracker
from pynput.keyboard import Controller


def getMousePos(event, x, y, flags, param):
    global clickedX, clickedY, mouseX, mouseY
    if event == cv2.EVENT_LBUTTONUP:
        clickedX, clickedY = x, y
    if event == cv2.EVENT_MOUSEMOVE:
        mouseX, mouseY = x, y


def calculateIntDistance(pt1, pt2):
    return int(((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2) ** 0.5)


def runVirtualKeyboard():
    # Creating keys
    w, h = 80, 60
    gap = 5
    startX, startY = 40, 200
    keys = []
    letters = list("1234567890QWERTYUIOPASDFGHJKLZXCVBNM")

    for i, l in enumerate(letters):
        if i < 10:  # First row
            x = startX + i * (w + gap)
            y = startY
        elif i < 20:  # Second row
            x = startX + (i - 10) * (w + gap)
            y = startY + h + gap
        elif i < 29:  # Third row
            x = startX + (i - 20) * (w + gap) + 40
            y = startY + 2 * (h + gap)
        else:  # Fourth row
            x = startX + (i - 29) * (w + gap) + 75
            y = startY + 3 * (h + gap)
        keys.append(Key(x, y, w, h, l))

    keys.append(Key(startX + 25, startY + 4 * h + 20, 5 * w, h, "Space"))
    keys.append(Key(startX + 8 * w + 40, startY + 3 * h + 15, w, h, "clr"))
    keys.append(Key(startX + 5 * w + 30, startY + 4 * h + 20, 5 * w, h, "<--"))

    textBox = Key(startX, startY - h - 5, 10 * w + 9 * 5, h, '')

    cap = cv2.VideoCapture(1)
    ptime = 0

    # Initiating the hand tracker
    tracker = HandTracker(detectionCon=0.8)
    frameHeight, frameWidth, _ = cap.read()[1].shape

    clickedX, clickedY = 0, 0
    mouseX, mouseY = 0, 0
    cv2.namedWindow('video')
    counter = 0
    previousClick = 0

    keyboard = Controller()

    while True:
        if counter > 0:
            counter -= 1

        signTipX, signTipY = 0, 0
        thumbTipX, thumbTipY = 0, 0

        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (int(frameWidth * 1.5), int(frameHeight * 1.5)))
        frame = cv2.flip(frame, 1)
        frame = tracker.findHands(frame)
        lmList = tracker.getPosition(frame, draw=False)

        if lmList:
            signTipX, signTipY = lmList[8][1], lmList[8][2]
            thumbTipX, thumbTipY = lmList[4][1], lmList[4][2]
            if calculateIntDistance((signTipX, signTipY), (thumbTipX, thumbTipY)) < 50:
                centerX = int((signTipX + thumbTipX) / 2)
                centerY = int((signTipY + thumbTipY) / 2)
                cv2.line(frame, (signTipX, signTipY), (thumbTipX, thumbTipY), (0, 255, 0), 2)
                cv2.circle(frame, (centerX, centerY), 5, (0, 255, 0), cv2.FILLED)

        ctime = time.time()
        fps = int(1 / (ctime - ptime))
        ptime = ctime

        cv2.putText(frame, str(fps) + " FPS", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        cv2.setMouseCallback('video', getMousePos)

        alpha = 0.5
        textBox.drawKey(frame, (255, 255, 255), (0, 0, 0), 0.3)
        for k in keys:
            if k.isOver(mouseX, mouseY) or k.isOver(signTipX, signTipY):
                alpha = 0.1
                if k.isOver(clickedX, clickedY):
                    if k.text == '<--':
                        textBox.text = textBox.text[:-1]
                    elif k.text == 'clr':
                        textBox.text = ''
                    elif len(textBox.text) < 30:
                        if k.text == 'Space':
                            textBox.text += " "
                        else:
                            textBox.text += k.text

                if k.isOver(thumbTipX, thumbTipY):
                    clickTime = time.time()
                    if clickTime - previousClick > 0.4:
                        if k.text == '<--':
                            textBox.text = textBox.text[:-1]

                        elif k.text == 'clr':
                            textBox.text = ''
                        elif len(textBox.text) < 30:
                            if k.text == 'Space':
                                textBox.text += " "

                            else:
                                textBox.text += k.text
                                keyboard.press(k.text)
                        previousClick = clickTime
            k.drawKey(frame, (255, 255, 255), (0, 0, 0), alpha=alpha)
            alpha = 0.5
        clickedX, clickedY = 0, 0

        cv2.imshow('video', frame)

        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()



