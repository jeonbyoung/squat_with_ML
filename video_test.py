import cv2

cap = cv2.VideoCapture('squat_video_test.mov')

while True:
    ret, frame = cap.read()

    if not ret:
        print("video is finished!")
        break

    cv2.imshow('Squat!', frame)

    key = cv2.waitKey(30) & 0xFF
    if key == ord('q') or key == ord('Q'):
        break

cap.release()
cv2.destroyAllWindows()