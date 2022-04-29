import os
import time
import argparse

import cv2
import torch
import torch.nn as nn
import pyvirtualcam
import numpy as np
import mediapipe as mp
from PIL import Image

from models import TalkingAnimeLight
from pose import get_pose
from utils import preprocessing_image, postprocessing_image, blend_with_background

parser = argparse.ArgumentParser()
parser.add_argument('--debug', action='store_true')
parser.add_argument('--input', type=str, default='cam')
parser.add_argument('--character', type=str, default='0001')
parser.add_argument('--output_dir', type=str, default=f'dst')
parser.add_argument('--output_webcam', action='store_true')
parser.add_argument('--bgcolor', type=str)
parser.add_argument('--posefix_x', type=float)
parser.add_argument('--posefix_y', type=float)
parser.add_argument('--posefix_z', type=float)
args = parser.parse_args()

device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

@torch.no_grad()
def main():
    model = TalkingAnimeLight().to(device)
    # model = TalkingAnime().to(device)
    model = model.eval()
    # model = model
    img = Image.open(f"character/{args.character}.png")
    img = img.resize((256, 256))
    input_image = preprocessing_image(img).unsqueeze(0)

    if args.input == 'cam':
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if ret is None:
            raise Exception("Can't find Camera")
    else:
        cap = cv2.VideoCapture(args.input)
        frame_count = 0
        os.makedirs(os.path.join('dst', args.character, args.output_dir), exist_ok=True)

    facemesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

    if args.output_webcam:
        cam = pyvirtualcam.Camera(width=1280, height=720, fps=30)
        print(f'Using virtual camera: {cam.device}')
    
    if args.bgcolor:
        bgc = args.bgcolor.upper()
        if bgc.__eq__("GREEN"): 
            background_choice = 1
        elif bgc.__eq__("BLUE"):
            background_choice = 2
        elif bgc.__eq__("BLACK"):
            background_choice = 3
        elif bgc.__eq__("WHITE"):
            background_choice = 4
        else:
            raise Exception("Should be 'GREEN', 'BLUE', 'BLACK', or 'WHITE'")
    else:
        background_choice = 0 # 0:"NO CHANGE", 1:"GREEN", 2:"BLUE", 3:"BLACK", 4:"WHITE"

    mouth_eye_vector = torch.empty(1, 27)
    pose_vector = torch.empty(1, 3)

    input_image = input_image.to(device)
    mouth_eye_vector = mouth_eye_vector.to(device)
    pose_vector = pose_vector.to(device)

    pose_queue = []

    while cap.isOpened():
        ret, frame = cap.read()
        input_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = facemesh.process(input_frame)

        if results.multi_face_landmarks is None:
            continue

        facial_landmarks = results.multi_face_landmarks[0].landmark

        if args.debug:
            pose, debug_image = get_pose(facial_landmarks, frame)
        else:
            pose = get_pose(facial_landmarks)

        if len(pose_queue) < 3:
            pose_queue.append(pose)
            pose_queue.append(pose)
            pose_queue.append(pose)
        else:
            pose_queue.pop(0)
            pose_queue.append(pose)

        np_pose = np.average(np.array(pose_queue), axis=0, weights=[0.6, 0.3, 0.1])

        eye_l_h_temp = np_pose[0]
        eye_r_h_temp = np_pose[1]
        mouth_ratio = np_pose[2]
        eye_y_ratio = np_pose[3]
        eye_x_ratio = np_pose[4]
        x_angle = np_pose[5]
        y_angle = np_pose[6]
        z_angle = np_pose[7]

        mouth_eye_vector[0, :] = 0

        mouth_eye_vector[0, 2] = eye_l_h_temp
        mouth_eye_vector[0, 3] = eye_r_h_temp

        mouth_eye_vector[0, 14] = mouth_ratio * 1.5

        mouth_eye_vector[0, 25] = eye_y_ratio
        mouth_eye_vector[0, 26] = eye_x_ratio

        # Keep default value from original branch.
        if args.posefix_x:
            pose_vector[0, 0] = (x_angle + args.posefix_x) * 1.6
        else:
            pose_vector[0, 0] = (x_angle - 1.5) * 1.6
        if args.posefix_y:
            pose_vector[0, 1] = (y_angle + args.posefix_y) * 2.0
        else:
            pose_vector[0, 1] = y_angle * 2.0 # temp weight
        if args.posefix_z:
            pose_vector[0, 2] = (z_angle + args.posefix_z) * 2
        else:
            pose_vector[0, 2] = (z_angle + 1.5) * 2 # temp weight

        output_image = model(input_image, mouth_eye_vector, pose_vector)
        
        

        if args.debug:
            out_img = postprocessing_image(output_image.cpu())
            if background_choice != 0: # Have Change
                background = np.zeros((out_img.shape[0], out_img.shape[1], out_img.shape[2]))
                background[:, :, 3] = 255 #Alpha 255
                if background_choice == 1: 
                    background[:, :, 1] = 177
                    background[:, :, 2] = 64
                elif background_choice == 2:
                    background[:, :, 1] = 71
                    background[:, :, 2] = 187
                elif background_choice == 4:
                    background[:, :, 0:3] = 255 # RGBA 255
                output_frame = cv2.cvtColor(blend_with_background(out_img, background), cv2.COLOR_RGBA2BGR)
            else:
                output_frame = cv2.cvtColor(out_img, cv2.COLOR_RGBA2BGR)
            resized_frame = cv2.resize(output_frame, (np.min(debug_image.shape[:2]), np.min(debug_image.shape[:2])))
            output_frame = np.concatenate([debug_image, resized_frame], axis=1)
            cv2.imshow("frame", output_frame)
            # cv2.imshow("camera", debug_image)
            cv2.waitKey(1)
        if args.input != 'cam':
            cv2.imwrite(os.path.join('dst', args.character, args.output_dir, f'{frame_count:04d}.jpeg'))
            frame_count += 1
        if args.output_webcam:
            result_image = np.zeros([720, 1280, 3], dtype=np.uint8)
            out_img = postprocessing_image(output_image.cpu())
            if background_choice != 0: # Transp
                background = np.zeros((out_img.shape[0], out_img.shape[1], out_img.shape[2]))
                background[:, :, 3] = 255
                result_image[:,:] = [0, 0, 0]
                if background_choice == 1: 
                    background[:, :, 1] = 177
                    background[:, :, 2] = 64
                    result_image[:,:] = [0, 177, 64]
                elif background_choice == 2:
                    background[:, :, 1] = 71
                    background[:, :, 2] = 187
                    result_image[:,:] = [0, 71, 187]
                elif background_choice == 4:
                    background[:, :, 0:3] = 255
                    result_image[:,:] = [255, 255, 255]
                result_image[720 - 512:, 1280 // 2 - 256:1280 // 2 + 256] = cv2.resize(
                    cv2.cvtColor(blend_with_background(out_img, background), cv2.COLOR_RGBA2RGB), (512, 512))
            else:
                result_image[720 - 512:, 1280 // 2 - 256:1280 // 2 + 256] = cv2.resize(
                cv2.cvtColor(out_img, cv2.COLOR_RGBA2RGB), (512, 512))
            cam.send(result_image)
            cam.sleep_until_next_frame()


if __name__ == '__main__':
    main()
