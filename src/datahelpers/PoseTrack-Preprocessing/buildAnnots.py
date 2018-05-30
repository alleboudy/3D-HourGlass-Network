import ref
import os
import torch
import numpy as np 
import scipt.io as sio
from helperFunctions import *

class Bbox:
	def __init__(self):
		self.mean = None
		self.delta = None

def makeBoundingBox(joints, slack = 0.2): 
	#slack is the percent of the extra area that we keep in the crop, ie, right now the total width will be 1.2 times the maximum distance between the
	#joints that are farthest apart along the x axis
	minX = 20000
	maxX = 0
	minY = 20000
	maxY = 0
	for joint in joints:
		minX = min(minX, joint[0])
		maxX = max(maxX, joint[0])
		minY = min(minY, joint[1])
		maxY = max(maxY, joint[1])
	box = Bbox()
	box.mean = ((minX + maxX)/2.0, (minY + maxY)/2.0)
	box.delta = max(maxX - minX, maxY - minY)*(1.0 + slack)
	newJoints = np.zeros((len(joints), 2))
	for i in range(len(joints)):
		newJoints[i][0] = joints[i][0] - box.mean[0]
		newJoints[i][1] = joints[i][1] - box.mean[1]
	return box, newJoints




os.system("ls > output")
file = open("output", 'r')
matList = ""
for chunk in file:
	matList += chunk
file.close()
matList = matList.split()
matList = [x for x in matList if (x[-3:] == 'mat')]

##### MADE A LIST OF THE FILES IN THE DIRECTORY

file = open("labels", 'w')
count = 0

total = len(videoList)


finalData = []

for mat in matList:
	file = sio.load(mat)
	file = file['annolist']
	size = file.shape[0]
	whichFrames = []
	frameWiseData = {}
	for i in range(size):
		thisFrame = file[i]
		isAnnotated = thisFrame[3][0][0]

		if isAnnotated:
			imageName = thisFrame[0][0][0][0][0]
			whichFrames.append(imageName[-12:-4])
			countPeople = thisFrame[1][0].shape[0]
			personWiseData = []
			for j in range(countPeople):
				person = thisFrame[1][0][j][0]
				crazyJoints = person[7][0][0][0][0]
				joints = stabilize(crazyJoints)


				"""
				COMPLETE HERE!!!
				given set of n Joints (here probably 13 but better make invariant to it)
				give me a bounding box, no cropping required (as memory pains ho skta thoda)
				that is we'll runtime on crop, give boundingBox + updated pixels
				
				also better to give a bounding box in the following manney :
					1) give me the center root relative krke (average of joints[2,:] and joints[3,:])
					2) number of pixels to crop from centre on each sidex (delta/2 on each side give me the delta)
				also give the changed pixel coors as a numpy array of shape 
							Nx2 (N is number of joints)
				return them as a tuple of bbox,newJoints
				"""

				bbox,newJoints = makeBoundingBox(joints) ##Bbox is a class, with bbox.mean a tuple of x, y and bbox.delta
				personWiseData.append([bbox,newJoints])
		frameWiseData[imageName] = (personWiseData)

		# Here imageName is the relative path from the PoseTrackDataDirectory (so yeah keep the images folder!!)
	finalData.append((whichFrames,person))


pickle.dump(finalData, open('annotations.pkl','rb'))