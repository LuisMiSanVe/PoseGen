> [See in spanish/Ver en español](https://github.com/LuisMiSanVe/PoseGen/blob/main/README.es.md)
# 🧎 PoseGen
[![image](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white)](https://aistudio.google.com/app/apikey)
[![image](https://img.shields.io/badge/Visual_Studio_Code-0078D4?style=for-the-badge&logo=visual%20studio%20code&logoColor=white)](https://code.visualstudio.com/)
[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
[![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white)](https://numpy.org/)
[![image](https://img.shields.io/badge/json-5E5C5C?style=for-the-badge&logo=json&logoColor=white)](https://docs.python.org/es/3/library/json.html)

Random pose generator for articulable figurines inspiration.

## 📝 Technology Explanation
The main screen is divided in two:
- The 3D display: Using pyBullet to generate the 3D graphics and then rendering them on a video.
- Controls menu: Using Tkinter to show various options and buttons.

On the program you can choose the number of articulations and it stablishes a logic limit for then in order to create replicable poses on real articulable figurines.

In the AI pose generation feature, it checks the reference image used and tries to replicate it in a pose.

## 📋 Prerequisites
You'd need to install the [Python](https://www.python.org/) libraries that generates the 3D graphics, process arrays in order to stream them to video and generate poses with AI:
```
pip install pybullet numpy pillow google-genai
```
In case this command fails try using:
```
py -m pip install pybullet numpy pillow google-genai
```
In case you want to use the AI pose generation, you'd need to obtain your Gemini API Key by visiting [Google AI Studio](https://aistudio.google.com/app/apikey). Ensure you're logged into your Google account, then press the blue button that says 'Create API key' and follow the steps to set up your Google Cloud Project and retrieve your API key. **Make sure to save it in a safe place**.
Google allows free use of this API without adding billing information, but there are some limitations.

In Google AI Studio, you can monitor the AI's usage by clicking 'View usage data' in the 'Plan' column where your projects are displayed. I recommend monitoring the 'Quota and system limits' tab and sorting by 'actual usage percentage,' as it provides the most detailed information.

## ⚙️ Project Usage Explanation
In order to Debug the program, use the repo's `PoseGen.py`, as it opens the program alongside a debug terminal.
You can enable a debug FPS counter in this [line](https://github.com/LuisMiSanVe/PoseGen/blob/main/PoseGen.py#L151)

For regular use, just get the `PoseGen.pyw` (only for Windows) in the [Github Releases](https://github.com/LuisMiSanVe/PoseGen/releases) page.

In the upper menu, you can save or load a pose in `PoseGen` format `(.psgn)`, use some settings from the controls menu and set the Gemini API Key.

On the 3D display you can use your mouse to move the camera around the model and zoom in and out.

> [!TIP]
> You must press `Ctrl` + mouse movement/wheel to modify the camera.

From the controls, you can setup different settings like changing stream resolution, FPS cap or reseting to the initial pose or camera angle, generate a new pose or access the Custom Pose screen, where you can customize the pose at your liking.

Inside that menu you can add a reference image on the background as reference and generate poses with AI using that image.

## 📂 Files
To start the program, you must have on the same folder as the Python executable this folders:
- `models/`: It must have the base 3D model in its folder `models/humanoid.urdf`.
- `config/`: It must have the API Key config file `config/apikey.env` with the necessary API Key inside to use the AI pose function.
- `saves/`: It stores a file with the pose we saved, like this: `saves/pose1.psgn`.

> [!NOTE]
> The 3D model belongs to the base pyBullet models, all credits to their respective creators.

## 🎨 Customization Options
In the controls menu, you can customize various settings of the program with this options:
- Start/Stop simulation: It stops the video stream from showing the changes*.
- Show/Hide 3D Display: Choose to display or not the 3D video stream.
- Resolution Scale: Change the internal resolution of the video stream, by default is in half of resolution, this setting drastically determines the performance of the program.
- 60 FPS: Stream rate is capped at 60 FPS, more fluid, but needs more resources to keep up the rate.
- 30 FPS: Stream rate is capped at 30 FPS, less fluid and needs less resources.

> [!IMPORTANT]
> *: The modifications applied while the simulation is stopped will accumulate and be applied when the simulation is resumed, this can lead to unwanted changes, so be aware.

## 🚀 Releases
The version will be released using these versioning policies:\
New major features and critical bug fixes will cause the immediate release of a new version, while other minor changes or fixes will wait one week since the time the change is introduced in the repository before being included in the new version, so that other potential changes can be added.
>[!NOTE]
>These potencial new changes will not increase the wait time for the new version beyond one week.

The version number will follow this format: \
\[Major Feature\].\[Minor Feature\].\[Bug Fixes\]

## 💻 Technologies Used
- Programming Language: [Python](https://www.python.org/)
- Libraries:
  - [pyBullet](https://pypi.org/project/pybullet/) (3.2.7)
  - [numpy](https://pypi.org/project/numpy/) (2.3.3)
  - [PIL](https://pypi.org/project/pillow/) (11.3.0)
  - [Tkinter](https://docs.python.org/es/3.13/library/tkinter.html)
  - [VerticalScrolledFrame class](https://stackoverflow.com/questions/16188420/tkinter-scrollbar-for-frame) (by [Gonzo](https://stackexchange.com/users/294742/gonzo))
- Other:
  - Google Gemini AI (2.0)
  - [Humanoid model](https://github.com/bulletphysics/bullet3/blob/master/examples/pybullet/gym/pybullet_data/humanoid/humanoid.urdf) (by pyBullet)
- Recommended IDE: [VS Code](https://code.visualstudio.com/)
