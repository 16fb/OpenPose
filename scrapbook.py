import math


# use pythoagoras find distance.
def distance_between_2_points(x1,y1,x2,y2):
    dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return dist

print(distance_between_2_points(4,5,2,3))

