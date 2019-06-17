from my_CNN_model import *
import cv2
import numpy as np

# Load the model built in the previous step
my_model = load_my_CNN_model('my_model_10')
my_model2 = load_my_CNN_model('my_model_200')

# Face cascade to detect faces
face_cascade = cv2.CascadeClassifier('cascades/haarcascade_frontalface_default.xml')

# Define the upper and lower boundaries for a color to be considered "Blue"
blueLower = np.array([100, 60, 60])
blueUpper = np.array([140, 255, 255])

# Define a 5x5 kernel for erosion and dilation
kernel = np.ones((5, 5), np.uint8)

filterIndex = 0

camera = cv2.VideoCapture(0)


def showModel(face_resized, model, title):
    # Predicting the keypoints using the model
    keypoints = model.predict(face_resized)
    # De-Normalize the keypoints values
    keypoints = keypoints * 48 + 48
    # Map the Keypoints back to the original image
    face_resized_color = cv2.resize(color_face, (96, 96), interpolation=cv2.INTER_AREA)
    face_resized_color2 = np.copy(face_resized_color)
    # Pair them together
    points = []
    for i, co in enumerate(keypoints[0][0::2]):
        points.append((co, keypoints[0][1::2][i]))
    # Add KEYPOINTS to the frame2
    for keypoint in points:
        cv2.circle(face_resized_color2, keypoint, 1, (0, 255, 0), 1)
    frame2[y:y + h, x:x + w] = cv2.resize(face_resized_color2, original_shape, interpolation=cv2.INTER_CUBIC)
    cv2.imshow(title, frame2)


while True:
    (grabbed, frame) = camera.read()
    frame = cv2.flip(frame, 1)
    frame2 = np.copy(frame)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.25, 6)

    # Determine which pixels fall within the blue boundaries and then blur the binary image
    blueMask = cv2.inRange(hsv, blueLower, blueUpper)
    blueMask = cv2.erode(blueMask, kernel, iterations=2)
    blueMask = cv2.morphologyEx(blueMask, cv2.MORPH_OPEN, kernel)
    blueMask = cv2.dilate(blueMask, kernel, iterations=1)

    # Find contours (bottle cap in my case) in the image
    contours, hierarchy = cv2.findContours(blueMask.copy(), cv2.RETR_EXTERNAL,
                                        cv2.CHAIN_APPROX_SIMPLE)
    center = None

    # Check to see if any contours were found
    if len(contours) > 0:
        cnt = sorted(contours, key = cv2.contourArea, reverse = True)[0]
        ((x, y), radius) = cv2.minEnclosingCircle(cnt)

        M = cv2.moments(cnt)
        center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))

        if center[1] <= 65:
            if 500 <= center[0] <= 620: # Next Filter
                filterIndex += 1
                filterIndex %= 6
                continue

    if len(faces) == 0:
        cv2.imshow("10 epochs", frame)
        cv2.imshow("200 epochs", frame)
    for (x, y, w, h) in faces:

        # Grab the face
        gray_face = gray[y:y+h, x:x+w]
        color_face = frame[y:y+h, x:x+w]

        # Normalize to match the input format of the model - Range of pixel to [0, 1]
        gray_normalized = gray_face / 255

        # Resize it to 96x96 to match the input format of the model
        original_shape = gray_face.shape # A Copy for future reference
        face_resized = cv2.resize(gray_normalized, (96, 96), interpolation = cv2.INTER_AREA)
        face_resized_copy = face_resized.copy()
        face_resized = face_resized.reshape(1, 96, 96, 1)

        showModel(face_resized, my_model, '10 epochs')
        showModel(face_resized, my_model2, '200 epochs')

    # If the 'q' key is pressed, stop the loop
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
