> [See in spanish/Ver en español](https://github.com/LuisMiSanVe/PoseGen/blob/main/README.es.md)
# 🧎 PoseGen
[![image](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white)](https://aistudio.google.com/app/apikey)
[![image](https://img.shields.io/badge/Visual_Studio_Code-0078D4?style=for-the-badge&logo=visual%20studio%20code&logoColor=white)](https://code.visualstudio.com/)
[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
[![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white)](https://numpy.org/)

Random pose generator for articulable figurines inspiration.

## 📝 Technology Explanation
The main screen is divided in two:
- The 3D display: Using pyBullet to generate the 3D graphics and then rendering them on a video.
- Controls menu: Using Tkinter to show various options and buttons.

On the program you can choose the number of articulations and it stablishes a logic limit for then in order to create replicable poses on real articulable figurines.

In the AI pose generation feature, it checks the reference image used and tries to replicate it in a pose.

## 📋 Prerequisites
You'd need to install the [Python](https://www.python.org/) libraries that generates the 3D graphics and process arrays in order to stream them to video:
```
pip install pybullet numpy pillow
```

In case you want to use the AI pose generation, you'd need to obtain your Gemini API Key by visiting [Google AI Studio](https://aistudio.google.com/app/apikey). Ensure you're logged into your Google account, then press the blue button that says 'Create API key' and follow the steps to set up your Google Cloud Project and retrieve your API key. **Make sure to save it in a safe place**.
Google allows free use of this API without adding billing information, but there are some limitations.

In Google AI Studio, you can monitor the AI's usage by clicking 'View usage data' in the 'Plan' column where your projects are displayed. I recommend monitoring the 'Quota and system limits' tab and sorting by 'actual usage percentage,' as it provides the most detailed information.

## ⚙️ Project Usage Explanation
On the 3D display you can use your mouse to move the camera around the model and zoom in and out.

From the controls, you can setup different settings like reseting to the initial pose or camera angle, generate a new pose or access the Custom Pose screen, where you can customize the pose at your liking.

Inside that menu you can add a reference image on the background, add accessories (1 max. per limb) and generate poses with AI using the reference image.

## 📂 Files
To start the program, you must have downloaded on the same folder as the Python executable, the base 3D model in its folder `models/humanoid.urdf`.

This 3D model belongs to the base pyBullet models, all credits to their respective creators.

## 🎨 Customization Options
In the controls menu, you can customize the performance of the program with this options:
- 60 FPS: More fluid 3D rendering, uses more resources.
- 30 FPS: Less fluid 3D rendering, uses less resources.

> [!TIP]
> In order to get a decent performance, I recommend keeping the window resolution as the default one, for that reason, the maximize window button is disabled (only on Windows) but if you still want to resize it, you can manually do so.

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
