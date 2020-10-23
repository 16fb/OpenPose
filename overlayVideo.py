# read video from file, display with text overlay + box rectangle, save.
from __future__ import print_function
import numpy as np
import cv2


cap =  cv2.VideoCapture("OutputVideos\BryanTurningHeadOverlay.avi")

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('outputBryanTurningHead.avi',fourcc, 30, (1280,720)) # outputFile,4CC,fps,resolution,
# Note: wrong resolution -> corrupted, wrong framerate = weird

while cap.isOpened():

    # Read Video
    ret, frame = cap.read() # ret -> bool success/fail, frame -> single read frame

    if ret==True:
        # Read video property values
        #width = cap.get(3); print(width) 
        #height = cap.get(4); print(height)

        # Our operations on the frame come here
        #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #frame = cv2.flip(frame, 0)
        
        # Draw text
        # Syntax: cv2.putText(image, text, org{coords}, font, fontScale, color[, thickness[, lineType[, bottomLeftOrigin]]])
        cv2.putText(frame, "Video Frame Number:{}".format(420), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
        
        # Draw Box
        #Syntax: cv2.rectangle(image, start_point, end_point, color, thickness)
        cv2.rectangle(frame, (420, 205), (595, 385),(0, 0, 255), -1)

        
        # Save frame
        out.write(frame)

        # Display the resulting frame
        cv2.imshow('frame',frame)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
    else:
        print("Failed to read video frame / Video Finished")
        break

# When everything done, release the capture
cap.release()
out.release()
cv2.destroyAllWindows()