# import the necessary packages
from imutils.video import VideoStream
from imutils import face_utils
import datetime
import argparse
import imutils
import time
import dlib
import cv2
import math
import pickle


PATH_TO_LANDMARK_DETECTOR = "./shape_predictor_68_face_landmarks.dat"
FILE_NAME = "mouth_test"


def calc_geometric_distance(x1, y1, x2, y2):
	return math.sqrt( (x2-x1)**2 + (y2-y1)**2 )





# define a dictionary that maps the indexes of the facial
# landmarks to specific face regions
LM = dict({
	"mouth_outer": (48, 59),
	"mouth_inner": (60, 67),
	"mouth": (48, 68),
	"right_eyebrow": (17, 22),
	"left_eyebrow": (22, 27),
	"right_eye": (36, 42),
	"left_eye": (42, 48),
	"nose": (27, 35),
	"jaw": (0, 17)
})

# initialize dlib's face detector (HOG-based) and then create
# the facial landmark predictor
print("[INFO] loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(PATH_TO_LANDMARK_DETECTOR)

# initialize the video stream and allow the cammera sensor to warmup
print("[INFO] camera sensor warming up...")
# vs = VideoStream(0).start()
cap = cv2.VideoCapture(0)
time.sleep(2.0)

frame_number = -1
target_mouth_feature_list = pickle.load( open( FILE_NAME+".p", "rb") )
target_video_cap = cv2.VideoCapture( FILE_NAME+".avi")

# loop over the frames from the video stream
while True:


	frame_number += 1
	current_mouth_features = []
	# grab the frame from the threaded video stream, resize it to
	# have a maximum width of 400 pixels, and convert it to
	# grayscale
	# frame = vs.read()
	ret,frame = cap.read()
	if ret == True:
		frame = imutils.resize(frame, width=720)
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	 
		# detect faces in the grayscale frame
		rects = detector(gray, 0)
		

		if len(rects) > 0:		
			# determine the facial landmarks for the face region, then
			# convert the facial landmark (x, y)-coordinates to a NumPy
			# array
			shape = predictor(gray, rect)
			shape = face_utils.shape_to_np(shape)
			
	 
			# loop over the (x, y)-coordinates for the facial landmarks
			# and draw them on the image
			for idx, (x, y) in enumerate(shape):
				# cv2.putText(frame, str(idx), (x,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255,255,255))
				cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)

			for j in range(LM["mouth_outer"][0], LM["mouth_outer"][1]):
				cv2.line(frame, (shape[j][0], shape[j][1]), (shape[j+1][0], shape[j+1][1]), (255,255,255))
				current_mouth_features.append(calc_geometric_distance(shape[j][0], shape[j][1], shape[j+1][0], shape[j+1][1]))

				if j == LM["mouth_outer"][1]-1:
					cv2.line(frame, (shape[j+1][0], shape[j+1][1]), (shape[ LM["mouth_outer"][0] ][0], shape[ LM["mouth_outer"][0] ][1]), (255,255,255))
					current_mouth_features.append(calc_geometric_distance( shape[j+1][0], shape[j+1][1], shape[ LM["mouth_outer"][0] ][0], shape[ LM["mouth_outer"][0] ][1] ))

			# for j in range(LM["mouth_inner"][0], LM["mouth_inner"][1]):
			# 	cv2.line(frame, (shape[j][0], shape[j][1]), (shape[j+1][0], shape[j+1][1]), (255,255,255))
			# 	current_mouth_features.append(calc_geometric_distance( shape[j][0], shape[j][1], shape[j+1][0], shape[j+1][1] ))
			# 	if j == LM["mouth_inner"][1]-1:
			# 		cv2.line(frame, (shape[j+1][0], shape[j+1][1]), (shape[ LM["mouth_inner"][0] ][0], shape[ LM["mouth_inner"][0] ][1]), (255,255,255))
			# 		current_mouth_features.append(calc_geometric_distance( shape[j+1][0], shape[j+1][1], shape[ LM["mouth_inner"][0] ][0], shape[ LM["mouth_inner"][0] ][1] ))

			for j in range(LM["mouth_inner"][0], LM["mouth_inner"][1]+1):
				for k in range(LM["mouth_inner"][0], LM["mouth_inner"][1]+1):
					cv2.line(frame, (shape[j][0], shape[j][1]), (shape[k][0], shape[k][1]), (200, 200, 200))
					current_mouth_features.append(calc_geometric_distance( shape[j][0], shape[j][1], shape[k][0], shape[k][1] ))
		
		most_similar_frame = (0, 0)
		min_diff = -1

		if len(current_mouth_features) > 0:
			for features in target_mouth_feature_list:
				frame_features, curr_frame_number = features[0], features[1]
				total_diff = 0
				print(len(frame_features))
				for idx in range(len(frame_features)):
					diff = abs(current_mouth_features[idx] - frame_features[idx])
					if idx > 20:
						total_diff += 2*diff
					else:
						total_diff += diff
				if total_diff < min_diff or min_diff == -1:
					min_diff = total_diff
					most_similar_frame = (frame_features, curr_frame_number)
		target_frame_number = most_similar_frame[1]
		target_video_cap.set(1, target_frame_number)
		ret, similar_frame = target_video_cap.read()
		if ret == True:
			cv2.imshow("similar_frame", similar_frame)




		# if len(current_mouth_features) > 0:
		# 	target_mouth_feature_list.append(current_mouth_features)
		# show the frame
		cv2.imshow("Frame", frame)
		key = cv2.waitKey(1) & 0xFF
	 
		# if the `q` key was pressed, break from the loop
		if key == ord("q"):
			break
	else:
		break

print(len(target_mouth_feature_list))
# do a bit of cleanup
cv2.destroyAllWindows()