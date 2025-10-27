import cv2
import mediapipe as mp
import math
import pandas as pd
import os

mp_pose = mp.solutions.pose

pose = mp_pose.Pose(static_image_mode = True)

def calc_dist_3d(p1,p2):
    distance = math.sqrt((p1.x-p2.x)**2+(p1.y-p2.y)**2+(p1.z-p2.z)**2)
    return distance

def calc_femur_and_torso_upgrade(img_path, actual_height_cm):
    img = cv2.imread(img_path)

    femur_length = 0
    torso_length = 0
    tfr_ratio = 0
    L_is_reliable = False
    R_is_reliable = False

    scale_factor = 1.0
    selected_side = "none"

    if img is None:
        print(f"'{img_path}' is not detected. plz check the file name")

    else:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        results = pose.process(img_rgb)

        if results.pose_landmarks:
            print("ALLRIGHT!!!")
            landmarks = results.pose_landmarks.landmark

            #For Left
            L_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            L_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
            L_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
            L_heel = landmarks[mp.pose.PoseLandmark.LEFT_HEEL.value]

            L_shoulder_vis = L_shoulder.visibility
            L_hip_vis = L_hip.visibility
            L_knee_vis = L_knee.visibility
            L_heel_vis = L_heel.visibility

            L_vis_avg = (L_shoulder_vis+L_hip_vis+L_knee_vis+L_heel_vis)/4.0

            #For Left
            R_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
            R_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
            R_knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]
            R_heel = landmarks[mp.pose.PoseLandmark.RIGHT_HEEL.value]

            R_shoulder_vis = R_shoulder.visibility
            R_hip_vis = R_hip.visibility
            R_knee_vis = R_knee.visibility
            R_heel_vis = R_heel.visibility

            R_vis_avg = (R_shoulder_vis+R_hip_vis+R_knee_vis+R_heel_vis)/4.0

            nose = landmarks[mp.pose.PoseLandmarks.NOSE.value]
            model_height_3d = -1

            vis_threshold = 0.8
            R_is_vis = False
            L_is_vis = False
            select_L = False
            select_R = False

            if(L_shoulder_vis>vis_threshold and
            L_hip_vis>vis_threshold and
            L_knee_vis>vis_threshold and 
            L_heel_vis>vis_threshold):
                L_is_vis = True

            if(R_shoulder_vis>vis_threshold and
            R_hip_vis>vis_threshold and
            R_knee_vis>vis_threshold and 
            R_heel_vis>vis_threshold):
                R_is_vis = True

            if(L_is_vis or R_is_vis):
                if(L_is_vis and R_is_vis):
                    if(L_vis_avg>R_vis_avg):
                        select_L = True
                    else:
                        select_R = True
            
                elif((L_is_vis and R_is_vis != True) or select_L):
                    print("Left side is selected.")
                    selected_side = "Left"
                    #The Key Value!
                    #femur length = hip ~ knee
                    femur_length = calc_dist_3d(L_hip,L_knee)

                    #torso length = shoulder ~ hip
                    torso_length = calc_dist_3d(L_shoulder, L_hip)
                    model_height_3d = calc_dist_3d(nose, L_heel)


                elif((R_is_vis and L_is_vis != True) or select_R):
                    print("Right side is selected.")
                    selected_side = "Right"
                    #The Key Value!
                    #femur length = hip ~ knee
                    femur_length = calc_dist_3d(R_hip,R_knee)

                    #torso length = shoulder ~ hip
                    torso_length = calc_dist_3d(R_shoulder, R_hip)
                    model_height_3d = calc_dist_3d(nose,R_heel)
                    
                
                if model_height_3d > 0:
                    scale_factor = actual_height_cm/model_height_3d
                    print(f"Model height : {model_height_3d:.4f} units")
                    print(f"Acutal height : {actual_height_cm}cm")
                    print(f"  => Calculated Scale Factor : {scale_factor:.2f}")
                else:
                    print("\n[Error] Model height is 0. Cannot calculate scale")
                    return None


                if torso_length >0:
                    tfr_ratio = femur_length/torso_length

                estimated_femur_len_cm = femur_length*scale_factor
                estimated_torso_len_cm = torso_length*scale_factor

                print(f"The estimated femur length : {estimated_femur_len_cm:.4f}")
                print(f"The estimated torso length : {estimated_torso_len_cm:.4f}")
                print(f"The estimated TFR(femur/torso) ratio : {tfr_ratio:.4f}")


            else:
                print(f"\n [WARNING] TOO LOW RELIABILITY OF THE POINTS (criteria : {vis_threshold}).")
                print("Plz check the angle of the photo or take another snap")

        else:
            print("Cannot detect the points on the image.")
            print("Plz check whether the image is for standing pose.")

        return {
            "femur_length_cm" : estimated_femur_len_cm,
            "torso_length_cm" : estimated_torso_len_cm,
            "tfr_ratio" : tfr_ratio,
            "selected_side" : selected_side,
            "scale_factor" : scale_factor
            
        }