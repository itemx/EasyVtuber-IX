# EasyVtuber

Modified items in this fork.

1. Add options to change background for easier mix to OBS and other capture tools.
2. Add options to directly change pose vector parameters.

Sample:

```python main.py --character amelria --debug --bgcolor green --posefix_x -2 --posefix_y -0.15 --posefix_z 1.55```

# Original readme
![](assets/sample_luda.gif)

- Character Face Generation using Facial landmarks and GANs
- Chat with your own webtoons and cartoon characters on Google Meets, Zoom, etc!
- It works great no matter how many accessories you add!
- Unfortunately, it may not work well in real time under RTX 2070.

<br/><br/>

## Demo
![](assets/sample_luda_debug.gif)
![](assets/sample_zoom.gif)

<br/><br/>

## Requirements
- Python >= 3.8 
- Pytorch >= 1.7 
- pyvirtualcam
- mediapipe
- opencv-python

<br/><br/>

## Quick Start
- ※ This project requires OBS installation before use
- __Please__ follow the installation order below !

1. [Install OBS studio](<https://obsproject.com/>)
   - To use OBS virtualcam, you must install OBS Studio first.
2. ```pip install -r requirements.txt```
   - OBS virtualcam must be installed to use pyvirtualcam included in the requirements.
3. [Download pretrianed model](<https://www.dropbox.com/s/tsl04y5wvg73ij4/talking-head-anime-2-model.zip?dl=0>)
   - This model is provided by the original talking-head-anime-2
   - Put the following files in the __pretrained__ folder.
     - `combiner.pt`
     - `eyebrow_decomposer.pt`
     - `eyebrow_morphing_combiner.pt`
     - `face_morpher.pt`
     - `two_algo_face_rotator.pt`
4. Put the character image in the __character__ folder
   - The character image files must meet the following requirements:
     - Must include an alpha channel (as png extension)
     - Must contains only 1 humanoid character
     - The character must faceing the front side
     - The character's head should fit within the center 128 x 128 pixel (because it resizes to 256 x 256 by default, it must fit within 128x128 based on 256 x 256)
    
    <p align="center">
        <img src="./assets/img.png" alt="Example image is refenced by TalkingHeadAnime2" width="50%" height="50%"/>
    </p>


5.`python main.py --webcam_output`
   - If you want to see how the actual facial features are captured --debug, add an option and run it.



<br/><br/>

## How to make Custom Character
1.Find the character you want on search engines.
   - The image should satisfy the requirements above.
![google search](assets/01_sample_search.gif)
<br/><br/>
2. Crop the image to the aspect ratio 1:1 so that the character's face is in the center.
   - [Image cropping site](https://iloveimg.com/ko/crop-image) This is not an ad.
![crop image](assets/02_sample_crop.gif)
<br/><br/>
3. Remove the background and create an alpha channel.
   - [Background removal](https://remove.bg/) This is not an ad.
![google search](assets/03_sample_remove_backgroud.gif)
<br/><br/>
4. Done!
   - Put the image in the character folder and execute `python main.py --output_webcam --character (filename only, without ".png")`

<br/><br/>

## Folder Structure

```
      │
      ├── character/ - character images 
      ├── pretrained/ - save pretrained models 
      ├── tha2/ - Talking Head Anime2 Library source files 
      ├── facial_points.py - facial feature point constants
      ├── main.py - main script to excute
      ├── models.py - GAN models defined
      ├── pose.py - process facial landmark to pose vector
      └── utils.py - util fuctions for pre/postprocessing image
```

<br/><br/>

## Usage
### Sending to virtual webcam
- `python main.py --output_webcam`
### Choose to use a specific character
- `python main.py --character (File name under character folder without ".png" extension)`
### Check facial features
- `python main.py --debug`
### Video file inference
- `python main.py --input video_file_path --output_dir frame_direct_to_save`

<br/><br/>

## TODOs

Please refer to the original branch.
<br/><br/>

## Thanks to
(No Translate)
- `이루다` 이미지 사용을 허락해주신 [스캐터랩 이루다팀](https://scatterlab.co.kr), `똘순이 MK1` 이미지 사용을 허락해주신 [순수한 불순물](https://pixiv.net/users/21097691) 님, 늦은 밤까지 README 샘플 영상 만들기 위해 도와주신 [성민석 멘토님](https://github.com/minsuk-sung), [박성호](https://github.com/naem1023), [박범수](https://github.com/hanlyang0522) 캠퍼님, 프로젝트 방향성 조언을 해주신 [김보찬 멘토님](https://github.com/MoMentum99) 모두 감사합니다!

<br/><br/>

## Acknowledgements
- EasyVtuber is based on [TalkingHeadAnime2](<https://github.com/pkhungurn/talking-head-anime-2-demo>)
- For the source of the tha2 folder and the pretrained model file, please check the license of the original author's repo before using it.