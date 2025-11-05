import sys, os, cv2

openpose_path = r"C:\openpose"
sys.path.append(os.path.join(openpose_path, "bin\python\openpose\Release"))
os.environ['PATH'] = os.environ['PATH'] + ';' + os.path.join(openpose_path, "build/x64/Release") + ';' + os.path.join(
    openpose_path, "bin")

import pyopenpose as op

params = dict()
params["model_folder"] = os.path.join(openpose_path, "models")
params["model_pose"] = "BODY_25"

opWrapper = op.WrapperPython()
opWrapper.configure(params)
opWrapper.start()

cap = cv2.VideoCapture("sprint1mp4.mp4")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # menší obraz
    frame = cv2.resize(frame, (640, 360))  # např. zmenšení na 640×360

    datum = op.Datum()
    datum.cvInputData = frame
    opWrapper.emplaceAndPop(op.VectorDatum([datum]))

    cv2.imshow("OpenPose", datum.cvOutputData)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
