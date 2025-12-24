import cv2
import dlib
import numpy as np
from imutils import face_utils
from scipy.spatial import distance

class DrowsinessDetector:
    def __init__(self, shape_predictor_path, ear_thresh=0.25, mar_thresh=0.5, frame_check=20):
        self.ear_thresh = ear_thresh
        self.mar_thresh = mar_thresh
        self.frame_check = frame_check
        self.frame_counter = 0

        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(shape_predictor_path)

        # landmark indexes for eyes and mouth
        (self.lStart, self.lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
        (self.rStart, self.rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
        (self.mStart, self.mEnd) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]

    def eye_aspect_ratio(self, eye):
        A = distance.euclidean(eye[1], eye[5])
        B = distance.euclidean(eye[2], eye[4])
        C = distance.euclidean(eye[0], eye[3])
        ear = (A + B) / (2.0 * C)
        return ear

    def mouth_aspect_ratio(self, mouth):
        A = distance.euclidean(mouth[2], mouth[10])  # vertical
        B = distance.euclidean(mouth[4], mouth[8])   # vertical
        C = distance.euclidean(mouth[0], mouth[6])   # horizontal
        mar = (A + B) / (2.0 * C)
        return mar

    def analyze_frame(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = self.detector(gray, 0)

        status = "Active"
        ear, mar = 0, 0

        for rect in rects:
            shape = self.predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)

            # extract eye and mouth coords
            leftEye = shape[self.lStart:self.lEnd]
            rightEye = shape[self.rStart:self.rEnd]
            mouth = shape[self.mStart:self.mEnd]

            ear = (self.eye_aspect_ratio(leftEye) + self.eye_aspect_ratio(rightEye)) / 2.0
            mar = self.mouth_aspect_ratio(mouth)

            # draw contours
            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)
            mouthHull = cv2.convexHull(mouth)

            color = (0, 255, 0)  # green default
            if ear < self.ear_thresh or mar > self.mar_thresh:
                self.frame_counter += 1
                color = (0, 0, 255)  # red
                if self.frame_counter >= self.frame_check:
                    status = "Drowsy"
            else:
                self.frame_counter = 0

            # draw eye and mouth contours
            cv2.drawContours(frame, [leftEyeHull], -1, color, 1)
            cv2.drawContours(frame, [rightEyeHull], -1, color, 1)
            cv2.drawContours(frame, [mouthHull], -1, color, 1)

            # EAR / MAR text
            cv2.putText(frame, f"EAR: {ear:.2f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            cv2.putText(frame, f"MAR: {mar:.2f}", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            cv2.putText(frame, f"Status: {status}", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        return frame, status, ear, mar
