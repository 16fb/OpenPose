### read output keypoints of video, and save into panda df format.
# say will purposely ignore if person more than 1
# saves df of total pose information
# saves df of left kneee


from __future__ import print_function
import numpy as np
import os
import cv2
import json
print('OpenCV - version: ',cv2.__version__)
import pandas as pd

import math

# video file
cap = cv2.VideoCapture('VideoAndImages\BryanTurningHead.mp4')

def get_vid_properties(): 
    width = int(cap.get(3))  # float
    height = int(cap.get(4)) # float
    cap.release()
    return width,height
  
print('Video Dimensions: ',get_vid_properties())

# Load keypoint data from JSON output
column_names = ['x', 'y', 'acc']

# Paths - should be the folder where Open Pose JSON output was stored
path_to_json = "OutputKeypoints\\BryanTurningHead\\"

# Import Json files, pos_json = position JSON
json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
print('Found: ',len(json_files),'json keypoint frame files')
count = 0

width,height = get_vid_properties()

# instanciate dataframes 
body_keypoints_df = pd.DataFrame()

left_knee_df = pd.DataFrame()
right_ear_df = pd.DataFrame()
right_eye_df = pd.DataFrame()
left_eye_df = pd.DataFrame()
left_ear_df = pd.DataFrame()

print('json files: ',json_files[0])   

# Loop through all json files in output directory
# Each file is a frame in the video
# If multiple people are detected - choose the most centered high confidence points
for file in json_files:

    temp_df = json.load(open(path_to_json+file))
    temp = []
    for k,v in temp_df['part_candidates'][0].items(): # returns label,content
        
        # Single point detected
        if len(v) < 4:
            temp.append(v)
            #print('Extracted highest confidence points: ',v)
            
        # Multiple points detected
        elif len(v) > 4: 
            near_middle = width
            np_v = np.array(v)
            
            # Reshape to x,y,confidence
            np_v_reshape = np_v.reshape(int(len(np_v)/3),3)
            np_v_temp = []
            # compare x values
            for pt in np_v_reshape:
                if(np.absolute(pt[0]-width/2)<near_middle):
                    near_middle = np.absolute(pt[0]-width/2)
                    np_v_temp = list(pt)
         
            temp.append(np_v_temp)
            #print('Extracted highest confidence points: ',v[index_highest_confidence-2:index_highest_confidence+1])
        else:
            # No detection - record zeros
            temp.append([0,0,0])
            
    temp_df = pd.DataFrame(temp)
    temp_df = temp_df.fillna(0)
    #print(temp_df)

    try:
        prev_temp_df = temp_df
        body_keypoints_df= body_keypoints_df.append(temp_df)

        # Directions are relative to person
        left_knee_df = left_knee_df.append(temp_df.iloc[13].astype(int)) # 13 refers to left knee
        right_ear_df = right_ear_df.append(temp_df.iloc[17].astype(int)) # 17 refers to right ear
        right_eye_df = right_eye_df.append(temp_df.iloc[15].astype(int)) # 15 refers to right eye
        left_eye_df = left_eye_df.append(temp_df.iloc[16].astype(int)) # 16 refers to left eye
        left_ear_df = left_ear_df.append(temp_df.iloc[18].astype(int)) # 18 refers to left ear
        

    except:
        print('bad point set at: ', file)

# set column names       
body_keypoints_df.columns = column_names
left_knee_df.columns = column_names
right_ear_df.columns = column_names
right_eye_df.columns = column_names
left_eye_df.columns = column_names
left_ear_df.columns = column_names

body_keypoints_df.reset_index()
left_knee_df = left_knee_df.reset_index(drop = True)
right_ear_df = right_ear_df.reset_index(drop = True)
right_eye_df = right_eye_df.reset_index(drop = True)
left_eye_df = left_eye_df.reset_index(drop = True)
left_ear_df = left_ear_df.reset_index(drop = True)


print('body_keypoints_df values:',body_keypoints_df.head(25))

print('length of merged keypoint set: ',body_keypoints_df.size) # number of elements in object [num rows * num column]
print('shape of keypoint set',body_keypoints_df.shape) # (5425 * 3), 3 columns of 5425 rows
# 217 keypoint files x 25 body points x 3 columns = 16275

# Peek at dfs
#print('left knee:',left_knee_df.head())
#print('right_ear_df:',right_ear_df.head())
#print('right_eye_df:',right_eye_df.head())
#print('left_eye_df:',left_eye_df.head())
#print('left_ear_df:',left_ear_df.head())

# X/Y coordinates
# x coordinates seems to be working fine
# y coordinates seems inversed(larger value lower.). [ear y value being marked higher than eye, even when its lower]
# oh. they using computer coordinates.


######## Making Use Of Kepoint Data  ######## 
# TODO put this inside function above.

# Use pythoagoras find distance.
# returns 1 if either value missing
def distance_between_2_points(x1,y1,x2,y2):
    if x1 == 0 or y1 == 0 or x2 == 0 or y2 == 0:
        return 1
    else:
        dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return dist

# Determines left/right/forward from earToEyeDistance x 2
# returns direction as text 
def determine_head_direction(distanceR,distanceL):
        distanceRatio = distanceR/distanceL
        if distanceRatio > 5:
            conclusion = "Left"
        elif distanceRatio < 0.2:
            conclusion = "Right"
        else:
            conclusion = "Forwards"
        return conclusion, distanceRatio

def determine_head_direction_by_absolute_difference(distanceR,distanceL):
    diff = distanceR - distanceL
    threshold = 60 
    if diff > (0+threshold):
        msg = "left"
    elif diff < (0-threshold):
        msg = "right"
    else:
        msg = "forwards"
    return msg 


# Video capture 
cap =  cv2.VideoCapture("OutputVideos\BryanTurningHeadOverlay.avi")

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('outputBryanTurningHead.avi',fourcc, 30, (1280,720)) # outputFile,4CC,fps,resolution,

for idx,files in enumerate(json_files):

    # Read Video
    ret, frame = cap.read() # ret -> bool success/fail, frame -> single read frame

    if ret==True:
        # Read video property values
        #width = cap.get(3); print(width) 
        #height = cap.get(4); print(height)

        # Read keypoints
        x1 = right_eye_df["x"][idx]
        y1 = right_eye_df["y"][idx]

        x2 = right_ear_df["x"][idx]
        y2 = right_ear_df["y"][idx]

        # print("x1 ",x1)
        # print("y1 ",y1)
        # print("x2 ",x2)
        # print("y2 ",y2)

        distanceR = int(distance_between_2_points(x1,y1,x2,y2))
        
        x1 = left_eye_df["x"][idx]
        y1 = left_eye_df["y"][idx]

        x2 = left_ear_df["x"][idx]
        y2 = left_ear_df["y"][idx]

        # print("x1 ",x1)
        # print("y1 ",y1)
        # print("x2 ",x2)
        # print("y2 ",y2)

        distanceL = int(distance_between_2_points(x1,y1,x2,y2))

        # draw conclusion on tresholds 0.8,0.2 by using ratio of both distances
        # TODO figure out a better way of handling ratios. ?? absolute differences?
        conclusion, distanceRatio = determine_head_direction(distanceR,distanceL)

        # use abs distance deterime direction
        res = determine_head_direction_by_absolute_difference(distanceR,distanceL)

        

        # Draw text
        # Syntax: cv2.putText(image, text, org{coords}, font, fontScale, color[, thickness[, lineType[, bottomLeftOrigin]]])
        cv2.putText(frame, "Video Frame Number:{}".format(idx), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
        cv2.putText(frame, "Distance Right side:{}".format(distanceR), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 3)
        cv2.putText(frame, "Distance Left side:{}".format(distanceL), (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 3)
        cv2.putText(frame, "Looking: {} ,Value: {}".format(conclusion,distanceRatio), (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 3)
        cv2.putText(frame, "Looking(abs distance): {} , Value: {}".format(res,distanceRatio), (10, 190), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 3)

        

        # Draw Box
        #Syntax: cv2.rectangle(image, start_point, end_point, color, thickness)
        #cv2.rectangle(frame, (420, 205), (595, 385),(0, 0, 255), -1)

        

        # Save + Display the resulting frame
        out.write(frame)
        cv2.imshow('frame',frame)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
    else:
        print("Failed to read video frame / Video Finished")
        break

