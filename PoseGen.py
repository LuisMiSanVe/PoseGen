import pybullet as p
import pybullet_data
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog
import random
import os
from google import genai
import time
import threading
import queue
import json
import subprocess
import re

#Classes
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)
    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, background="#ffffe0", relief="solid", borderwidth=1)
        label.pack()
    def hide_tip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()
class VerticalScrolledFrame(tk.Frame):
    # Credit to the user Gonzo in StackOverflow
    # StackOverflow thread: https://stackoverflow.com/questions/16188420/tkinter-scrollbar-for-frame
    # StackExchange User page: https://stackexchange.com/users/294742/gonzo
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame.
    * Construct and pack/place/grid normally.
    * This frame only allows vertical scrolling.
    """
    def __init__(self, parent, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)

        # Create a canvas object and a vertical scrollbar for scrolling it.
        vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                           yscrollcommand=vscrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=canvas.yview)

        # Reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # Create a frame inside the canvas which will be scrolled with it.
        self.interior = interior = tk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor="nw")

        # Track changes to the canvas and frame width and sync them,
        # also updating the scrollbar.
        def _configure_interior(event):
            # Update the scrollbars to match the size of the inner frame.
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the canvas's width to fit the inner frame.
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the inner frame's width to fill the canvas.
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)

# Functions
# Rendering thread
def render_loop():
    global last_time
    global stopsim
    global CAMERA_SCALE
    while True:
        if not stopsim:
            start = time.time()

            sidemargin = 0
            if root.winfo_height() > 1:
                sidemargin = 4

            # Camera parameters
            view_matrix = p.computeViewMatrixFromYawPitchRoll(
                cameraTargetPosition=start_pos, # Match ground separation to keep camera centered on humanoid
                distance=zoom,
                yaw=h_angle,
                pitch=v_angle,
                roll=0,
                upAxisIndex=2
            )

            camera_width = int((root.winfo_width()/1.5) * CAMERA_SCALE)
            camera_height = int((root.winfo_height()-sidemargin) * CAMERA_SCALE)

            # Convert Camera to Image
            width, height, rgb, depth, seg = p.getCameraImage(
                camera_width, camera_height,
                viewMatrix=view_matrix,
                projectionMatrix=p.computeProjectionMatrixFOV(fov=60, aspect=camera_width/camera_height, nearVal=0.1, farVal=10),
                renderer=p.ER_TINY_RENDERER
            )
            # Get RGB value
            rgb_array = np.array(rgb, dtype=np.uint8).reshape((height, width, 4))[:, :, :3]
            # Render Image
            vw = int(root.winfo_width() / 1.5)
            vh = root.winfo_height() - sidemargin
            img = Image.fromarray(rgb_array).convert("RGBA")
            img = img.resize((vw, vh), Image.LANCZOS)

            if show_ref_image.get() and (ref_image is not None and ref_image is not ''):
                # Reference image render as semitransparent
                overlay = Image.open(ref_image).convert("RGBA")
                opacity = 128  # 50% transparent
                alpha = overlay.split()[3]
                alpha = alpha.point(lambda p: p * (opacity / 255))
                overlay.putalpha(alpha)
                # Recalculate size to fit inside video stream
                vw_ref, vh_ref = img.size
                ow, oh = overlay.size
                scale = min(vw_ref / ow, vh_ref / oh, 1.0)
                new_size = (int(ow * scale), int(oh * scale))
                overlay = overlay.resize(new_size, Image.LANCZOS)
                x = (vw_ref - new_size[0]) // 2
                y = (vh_ref - new_size[1]) // 2

                # Put reference image as overlay
                img.paste(overlay, (x, y), overlay)

            # Put latest frame into queue
            if not frame_queue.full():
                frame_queue.put(img)
            
            # Show current FPS on terminal for debugging
            '''
            now = time.time()
            actual_frame_time = now - last_time
            last_time = now
            print(f"FPS: {1 / actual_frame_time:.1f}")
            '''
            
            # Cap to the target FPS
            elapsed = time.time() - start
            delay = max(0, (1.0 / fps_var.get()) - elapsed)
            time.sleep(delay)
        else:
            time.sleep(0.01)

# GUI update
def update_frame():
    p.stepSimulation()

    # Check if there is a new frame
    try:
        img = frame_queue.get_nowait()
        imgtk = ImageTk.PhotoImage(image=img)
        video_frame.imgtk = imgtk
        video_frame.configure(image=imgtk)
    except queue.Empty:
        pass  # keep last frame

    root.after(1, update_frame)  # schedule next check

# Joint List
# 2  neck
# 3  right_shoulder
# 4  right_elbow
# 6  left_shoulder
# 7  left_elbow
# 9  right_hip
# 10 right_knee
# 11 right_ankle
# 12 left_hip
# 13 left_knee
# 14 left_ankle
def gen_pose():
    reset_humanoid() # Reset to default pose
    joints = random.randint(1, 11) # Random Amount of joints affected
    for i in range(joints):
        joint = random.randint(2, 14) # Random Joint
        # Define limits for each joint
        radius = 0.0
        if articulation_var.get() == 1: # If it has articulations on the limbs
            if stand_var.get() == 1: # If it has a back stand
                if joint in [10, 13]:  # knees
                    radius = random.uniform(-0.1, -2.3)
            if joint in [4, 7]:  # elbows
                radius = random.uniform(0.1, 2.62)
        # Set pose
        if joint in [4, 7, 10, 13]:
            p.setJointMotorControl2(humanoid, joint, p.POSITION_CONTROL, radius)
        else:
            if stand_var.get() == 1 or (stand_var.get() == 0 and joint not in [9, 10, 11, 12, 13, 14]): # If it has a back stand or doesn't have it but is not any leg joint
                target_quat = p.getQuaternionFromEuler([random.uniform(-0.5, 0.5),  # Y
                                                        random.uniform(-0.5, 0.5),  # X
                                                        random.uniform(-0.5, 0.5)]) # Z
                p.setJointMotorControlMultiDof(humanoid, joint, p.POSITION_CONTROL, targetPosition=target_quat)
        # Disable physics
        p.changeDynamics(humanoid, -1, mass=0)
def custom_pose():
    global control_frame
    global custom_frame
    control_frame.pack_forget()
    custom_frame.pack(side=tk.RIGHT, fill=tk.BOTH)
def reset_humanoid():
    global control_frame
    global custom_frame
    global neck_x
    global neck_y
    global neck_z
    global right_shoulder_x
    global right_shoulder_y
    global right_shoulder_z
    global left_shoulder_x
    global left_shoulder_y
    global left_shoulder_z
    global right_elbow
    global left_elbow
    global right_hip_x
    global right_hip_y
    global right_hip_z
    global right_ankle_x
    global right_ankle_y
    global right_ankle_z
    global left_hip_x
    global left_hip_y
    global left_hip_z
    global right_knee
    global left_knee
    global left_ankle_x
    global left_ankle_y
    global left_ankle_z
    global humanoid
    # Reset model and custom pose
    p.resetSimulation()
    p.loadURDF("plane.urdf")
    humanoid = p.loadURDF(current_folder + "/models/humanoid.urdf", start_pos, upright_orientation, useFixedBase=False)
    neck_x.set(0)
    neck_y.set(0)
    neck_z.set(0)
    right_shoulder_x.set(0)
    right_shoulder_y.set(0)
    right_shoulder_z.set(0)
    left_shoulder_x.set(0)
    left_shoulder_y.set(0)
    left_shoulder_z.set(0)
    right_elbow.set(0)
    left_elbow.set(0)
    right_hip_x.set(0)
    right_hip_y.set(0)
    right_hip_z.set(0)
    right_ankle_x.set(0)
    right_ankle_y.set(0)
    right_ankle_z.set(0)
    left_hip_x.set(0)
    left_hip_y.set(0)
    left_hip_z.set(0)
    right_knee.set(0)
    left_knee.set(0)
    left_ankle_x.set(0)
    left_ankle_y.set(0)
    left_ankle_z.set(0)

def reset_camera():
    # Restore camera parameters
    global zoom, h_angle, v_angle
    zoom = 7
    h_angle = 90
    v_angle = 0
def back_control():
    custom_frame.pack_forget()
    control_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH)

def update_neck(_):
    global neck_x
    global neck_y
    global neck_z
    target_quat = p.getQuaternionFromEuler([neck_y.get(), neck_x.get(), neck_z.get()])
    p.setJointMotorControlMultiDof(humanoid, 2, p.POSITION_CONTROL, targetPosition=target_quat)
    p.changeDynamics(humanoid, -1, mass=0)
def update_right_shoulder(_):
    global right_shoulder_x
    global right_shoulder_y
    global right_shoulder_z
    target_quat = p.getQuaternionFromEuler([right_shoulder_y.get(), right_shoulder_x.get(), right_shoulder_z.get()])
    p.setJointMotorControlMultiDof(humanoid, 3, p.POSITION_CONTROL, targetPosition=target_quat)
    p.changeDynamics(humanoid, -1, mass=0)
def update_right_elbow(hinge):
    p.setJointMotorControl2(humanoid, 4, p.POSITION_CONTROL, float(hinge))
    p.changeDynamics(humanoid, -1, mass=0)
def update_left_shoulder(_):
    global left_shoulder_x
    global left_shoulder_y
    global left_shoulder_z
    target_quat = p.getQuaternionFromEuler([left_shoulder_y.get(), left_shoulder_x.get(), left_shoulder_z.get()])
    p.setJointMotorControlMultiDof(humanoid, 6, p.POSITION_CONTROL, targetPosition=target_quat)
    p.changeDynamics(humanoid, -1, mass=0)
def update_left_elbow(hinge):
    p.setJointMotorControl2(humanoid, 7, p.POSITION_CONTROL, float(hinge))
    p.changeDynamics(humanoid, -1, mass=0)
def update_right_hip(_):
    global right_hip_x
    global right_hip_y
    global right_hip_z
    target_quat = p.getQuaternionFromEuler([right_hip_y.get(), right_hip_x.get(), right_hip_z.get()])
    p.setJointMotorControlMultiDof(humanoid, 9, p.POSITION_CONTROL, targetPosition=target_quat)
    p.changeDynamics(humanoid, -1, mass=0)
def update_right_knee(hinge):
    p.setJointMotorControl2(humanoid, 10, p.POSITION_CONTROL, float(hinge))
    p.changeDynamics(humanoid, -1, mass=0)
def update_right_ankle(_):
    global right_ankle_x
    global right_ankle_y
    global right_ankle_z
    target_quat = p.getQuaternionFromEuler([right_ankle_y.get(), right_ankle_x.get(), right_ankle_z.get()])
    p.setJointMotorControlMultiDof(humanoid, 11, p.POSITION_CONTROL, targetPosition=target_quat)
    p.changeDynamics(humanoid, -1, mass=0)
def update_left_hip(_):
    global left_hip_x
    global left_hip_y
    global left_hip_z
    target_quat = p.getQuaternionFromEuler([left_hip_y.get(), left_hip_x.get(), left_hip_z.get()])
    p.setJointMotorControlMultiDof(humanoid, 12, p.POSITION_CONTROL, targetPosition=target_quat)
    p.changeDynamics(humanoid, -1, mass=0)
def update_left_knee(hinge):
    p.setJointMotorControl2(humanoid, 13, p.POSITION_CONTROL, float(hinge))
    p.changeDynamics(humanoid, -1, mass=0)
def update_left_ankle(_):
    global left_ankle_x
    global left_ankle_y
    global left_ankle_z
    target_quat = p.getQuaternionFromEuler([left_ankle_y.get(), left_ankle_x.get(), left_ankle_z.get()])
    p.setJointMotorControlMultiDof(humanoid, 14, p.POSITION_CONTROL, targetPosition=target_quat)
    p.changeDynamics(humanoid, -1, mass=0)
def set_image():
    global ref_image
    # Request image to the user
    ref_image = filedialog.askopenfilename(
        title="Select an Image",
        filetypes=[("Image Files", "*.png")]
    )
    if ref_image is not None and ref_image is not '':
        show_ref_image.set(True)
def gen_ai():
    global ref_image
    global current_folder

    if ref_image is None or ref_image is '':
        set_image()
    if ref_image is not None and ref_image is not '':
        reset_humanoid()
        reset_camera()

        prompt = "You are given a 2D reference image of a humanoid figure. Your task is to generate the joint angles in radians to replicate the pose in a PyBullet humanoid. " \
                 "The humanoid has the following joints: " \
                 "2: neck (3-DOF, order: yaw, pitch, roll) (limits: yaw=-1.05 to 1.05, pitch=-0.79 to 0.79, roll=-1.4 to 1.4) " \
                 "3: right_shoulder (3-DOF) (limits: -1.57 to 1.57, -1.57 to 1.57, -1.57 to 1.57) " \
                 "4: right_elbow (hinge, 1-DOF) (limits: 0 to 2.62) " \
                 "6: left_shoulder (3-DOF) (limits: -1.57 to 1.57, -1.57 to 1.57, -1.57 to 1.57) " \
                 "7: left_elbow (hinge, 1-DOF) (limits: 0 to 2.62) " \
                 "9: right_hip (3-DOF) (limits: -2.09 to 2.09, -0.79 to 0.79, -0.79 to 0.79) " \
                 "10: right_knee (hinge, 1-DOF) (limits: 0 to -2.36) " \
                 "11: right_ankle (3-DOF) (limits: -0.87 to 0.87, -0.35 to 0.35, -0.87 to 0.87) " \
                 "12: left_hip (3-DOF) (limits: -2.09 to 2.09, -0.79 to 0.79, -0.79 to 0.79) " \
                 "13: left_knee (hinge, 1-DOF) (limits: 0 to -2.36) " \
                 "14: left_ankle (3-DOF) (limits: -0.87 to 0.87, -0.35 to 0.35, -0.87 to 0.87) " \
                 "Make sure the randians are inside the limits stablished for each joint, and that they have the correct amount of numbers (hinges have one value and 3-DOF have 3), " \
                 "the output must be a JSON dictionary, keys are joint indices, values are angles. Example: {\"2\": [0.10, -0.05, 0.00],\"3\": [0.20, -0.10, 0.00], \"4\": 1.57, ...} " \
                 "Analyze the reference image, guess 3D positions if necessary to compute joint angles, respect anatomical plausibility and joint limits, output only the JSON with no extra text. " \
                 "In case you are unable to see any humanoid figure posing at all, just return everything with 0 values."
        
        img = Image.open(ref_image)


        with open(current_folder + "/config/apikey.env", "r") as file:
            env = file.read()

        if bool(re.match("^AIza[0-9A-Za-z\-_]{35}$", env)):
            client = genai.Client(api_key=env)
            contents = [
                img,
                prompt
            ]
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=contents
            )

            # Remove style elements
            json_data = response.text.replace("\n", "").replace("```", "").replace("json", "")

            # Parse to JSON
            jsonToPose(json_data)
        else:
            set_apikey()
            raise ValueError("No valid API Key found")
    else:
        ref_image = None
        raise ValueError("No image selected")

def jsonToPose(json_data):
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data

    # Search joints
    for joint_str, value in data.items():
        joint = int(joint_str)
        # Hinge joint
        if joint in [4, 7, 10, 13]:
            if isinstance(value, (list, tuple)):
                print(f"Invalid hinge data for joint {joint}: {value}")
                value = value[0]  # In case it's mistakenly generated with 3-DOFs instead of 1
            p.setJointMotorControl2(
                bodyUniqueId=humanoid,
                jointIndex=joint,
                controlMode=p.POSITION_CONTROL,
                targetPosition=value
            )
        # Multi-DOF joint
        elif joint in [2, 3, 6, 9, 11, 12, 14]:
            if not isinstance(value, (list, tuple)) or len(value) != 3:
                print(f"Invalid 3-DOF data for joint {joint}: {value}")
                continue
            quat = p.getQuaternionFromEuler(value)
            p.setJointMotorControlMultiDof(
                bodyUniqueId=humanoid,
                jointIndex=joint,
                controlMode=p.POSITION_CONTROL,
                targetPosition=quat
            )
        else:
            print(f"Unknown joint index {joint}")
    # Disable physics
    p.changeDynamics(humanoid, -1, mass=0)

def gen_ai_async():
    global ai_label

    ai_label.config(text="Generating pose...")

    thread = threading.Thread(target=gen_ai_task)
    thread.start()
def gen_ai_task():
    global ai_label
    try:
        gen_ai()
        ai_label.config(text="Pose generated!")
    except Exception as e:
       ai_label.config(text=f"AI generation failed: {e}")
def display():
    global video_frame

    if video_frame.winfo_ismapped():
        video_frame.pack_forget()
        root.minsize(300, 520)
    else:
        video_frame.pack(side=tk.LEFT, fill=tk.BOTH)
        root.minsize(850, 520)
def stop_sim():
    global stopsim

    if (stopsim):
        stopsim = False
    else:
        stopsim = True
def update_scale(new_scale):
    global CAMERA_SCALE
    CAMERA_SCALE = float(new_scale)

def save_pose():
    global humanoid
    global current_folder

    joint_map = {
        2: "neck",
        3: "right_shoulder",
        4: "right_elbow",
        6: "left_shoulder",
        7: "left_elbow",
        9: "right_hip",
        10: "right_knee",
        11: "right_ankle",
        12: "left_hip",
        13: "left_knee",
        14: "left_ankle",
    }
    joint_states = {}
    for joint_id in joint_map.keys():
        joint_info = p.getJointInfo(humanoid, joint_id)
        joint_type = joint_info[2]
        # 3-DOF
        if joint_type == p.JOINT_SPHERICAL or joint_type == p.JOINT_PLANAR:
            state = p.getJointStateMultiDof(humanoid, joint_id)
            pos = state[0]
            # Convert quaternion to Euler [yaw, pitch, roll]
            euler = p.getEulerFromQuaternion(pos)
            joint_states[str(joint_id)] = [round(v, 3) for v in euler]
        # 1-DOF
        elif joint_type == p.JOINT_REVOLUTE or joint_type == p.JOINT_PRISMATIC:
            state = p.getJointState(humanoid, joint_id)
            pos = state[0]
            joint_states[str(joint_id)] = round(pos, 3)

    # Save in a file
    folder_path = current_folder + "/saves"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)    
    count = len([f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))])

    with open(current_folder + "/saves/pose" + str(count+1) + ".psgn", "w") as file:
        file.write(json.dumps(joint_states, indent=2))

def load_pose():
    pose_file = filedialog.askopenfilename(
        title="Select a PoseGen save file",
        filetypes=[("PoseGen Files", "*.psgn")]
    )
    if pose_file is not None and pose_file is not '':
        with open(pose_file, "r") as file:
            pose = file.read()
            if pose is not None and pose is not '':
                jsonToPose(pose)

def set_apikey():
    global current_folder
    file_path = current_folder + "/config/apikey.env"
    # Open the file in Notepad
    subprocess.run(["notepad.exe", file_path])

# Events
def on_ctrl_mousewheel(event):
    global zoom
    if event.delta > 0:
        if zoom > 1:
            zoom -= 1 # Wheel up
    else:
        if zoom < 10:
            zoom += 1 # Wheel down
def on_ctrl_drag(event):
    global h_angle
    global v_angle
    # Move left/right
    if not hasattr(on_ctrl_drag, "last_x"):
        on_ctrl_drag.last_x = event.x
    dx = event.x - on_ctrl_drag.last_x
    if dx > 0:
        h_angle -= 2
    elif dx < 0:
        h_angle += 2
    on_ctrl_drag.last_x = event.x
    # Move up/down
    if not hasattr(on_ctrl_drag, "last_y"):
        on_ctrl_drag.last_y = event.y
    dy = event.y - on_ctrl_drag.last_y
    if dy > 0:
        v_angle -= 2
    elif dy < 0:
        v_angle += 2
    on_ctrl_drag.last_y = event.y

# Main
# Get current folder
current_folder = os.path.dirname(os.path.abspath(__file__))
# Load 3D display
physicsClient = p.connect(p.DIRECT)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
# Ground + humanoid
p.loadURDF("plane.urdf")
upright_orientation = p.getQuaternionFromEuler([1.57, 0, 0])
start_pos = [0, 0, 4] # Ground separation
humanoid = p.loadURDF(current_folder + "/models/humanoid.urdf", start_pos, upright_orientation, useFixedBase=False)
# Other parameters
zoom = 7
h_angle = 90
v_angle = 0
ref_image = None
stopsim = False
last_time = 0.0
frame_queue = queue.Queue(maxsize=1)
CAMERA_SCALE = 0.5  # By default it renders at half of its size

# Tkinter setup
root = tk.Tk()
root.title("PoseGen")
root.minsize(850, 520)
# Disable maximize button (Windows only)
try:
    import ctypes
    root.update_idletasks()
    hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
    style = ctypes.windll.user32.GetWindowLongW(hwnd, -16)
    style &= ~0x00010000  # Remove WS_MAXIMIZEBOX
    ctypes.windll.user32.SetWindowLongW(hwnd, -16, style)
except Exception as e:
    pass  # Ignore if not on Windows or error occurs
# Bar menu
menubar = tk.Menu(root)
file_menu = tk.Menu(menubar, tearoff=0)
file_menu.add_command(label="Save pose", command=save_pose)
file_menu.add_command(label="Load pose", command=load_pose)
menubar.add_cascade(label="File", menu=file_menu)
edit_menu = tk.Menu(menubar, tearoff=0)
edit_menu.add_command(label="Start/Stop simulation", command=stop_sim)
edit_menu.add_command(label="Show/Hide 3D display", command=display)
edit_menu.add_separator()
edit_menu.add_command(label="Reset Pose", command=reset_humanoid)
edit_menu.add_command(label="Reset Camera", command=reset_camera)
menubar.add_cascade(label="Edit", menu=edit_menu)
config_menu = tk.Menu(menubar, tearoff=0)
config_menu.add_command(label="Set Gemini API Key", command=set_apikey)
menubar.add_cascade(label="Config", menu=config_menu)
# Display menu
root.config(menu=menubar)

# Main frame
main_frame = tk.Frame(root, width=800, height=450)
main_frame.pack(fill=tk.BOTH)

# Left: video frame
video_frame = tk.Label(main_frame)
video_frame.pack(side=tk.LEFT, fill=tk.BOTH)
video_frame.bind("<Control-MouseWheel>", on_ctrl_mousewheel)
video_frame.bind("<Control-B1-Motion>", on_ctrl_drag)

# Right: control frame
control_frame = tk.LabelFrame(main_frame, text="Controls", padx=10, pady=10)
control_frame.pack(side=tk.RIGHT, fill=tk.BOTH)
# Stop/Start Simulation
tk.Button(control_frame, text="Start/Stop simulation", command=stop_sim).pack(pady=10, anchor="w")
# Show/Hide 3D display
tk.Button(control_frame, text="Show/Hide 3D display", command=display).pack(pady=10, anchor="w")
# 3D display scale
scale_frame = tk.Frame(control_frame)
scale_frame.pack(pady=(15, 5), anchor="w")
tk.Label(scale_frame, text="Resolution scale:").pack(side=tk.LEFT)
scale = tk.Scale(scale_frame, from_=0.1, to=1, orient=tk.HORIZONTAL, resolution=0.1, command=update_scale)
scale.pack(side=tk.RIGHT)
scale.set(0.5)
# Select FPS mode
tk.Label(control_frame, text="Select FPS:").pack(pady=5, anchor="w")
# Options
fps_var = tk.IntVar(value="60")  # default selection
tk.Radiobutton(control_frame, text="60 FPS", variable=fps_var, value=60).pack(padx=5, anchor="w")
tk.Radiobutton(control_frame, text="30 FPS", variable=fps_var, value=30).pack(padx=5, anchor="w")
# Articulation joints (label and checkbox side by side)
articulation_frame = tk.Frame(control_frame)
articulation_frame.pack(pady=(15, 5), anchor="w")
label_articulation = tk.Label(articulation_frame, text="Articulation joints")
label_articulation.pack(side=tk.LEFT)
ToolTip(label_articulation,"Enable/Disable articulation joints (elbows and knees).")
articulation_var = tk.BooleanVar(value=True)
check_articulation = tk.Checkbutton(articulation_frame, variable=articulation_var)
check_articulation.pack(side=tk.RIGHT, padx=5)
# Back stand (label and checkbox side by side)
stand_frame = tk.Frame(control_frame)
stand_frame.pack(pady=(15, 5), anchor="w")
label_stand = tk.Label(stand_frame, text="Back stand")
label_stand.pack(side=tk.LEFT)
ToolTip(label_stand,"Enable/Disable back stand. Enabling allows full leg movement.")
stand_var = tk.BooleanVar(value=True)
check_stand = tk.Checkbutton(stand_frame, variable=stand_var)
check_stand.pack(side=tk.RIGHT, padx=5)
# Reset
reset_frame = tk.Frame(control_frame)
reset_frame.pack(pady=(15, 5), anchor="w")
tk.Button(reset_frame, text="Reset Pose", command=reset_humanoid).pack(side=tk.LEFT)
tk.Button(reset_frame, text="Reset Camera", command=reset_camera).pack(side=tk.LEFT, padx=5)
# Generate random pose button
tk.Button(control_frame, text="Generate Pose", command=gen_pose).pack(pady=10, anchor="w")
# Custom pose button
tk.Button(control_frame, text="Customize Pose", command=custom_pose).pack(pady=10, anchor="w")

# Right: Custom frame
custom_frame = tk.LabelFrame(main_frame, text="Customize Pose", padx=10, pady=10)
scroll_frame = VerticalScrolledFrame(custom_frame)
scroll_frame.pack(padx=10, fill=tk.BOTH, anchor="w")
# 2  neck
neck_frame = tk.Frame(scroll_frame.interior)
neck_frame.pack(pady=(15, 5), anchor="w")
tk.Label(neck_frame, text="Neck:").pack(side=tk.LEFT)
neck_slider_frame = tk.Frame(neck_frame)
neck_slider_frame.pack(padx=5)
neck_slider_x_frame = tk.Frame(neck_slider_frame)
neck_slider_x_frame.pack()
tk.Label(neck_slider_x_frame, text="X").pack(side=tk.LEFT)
neck_x = tk.Scale(neck_slider_x_frame, from_=-1.05, to=1.05, orient=tk.HORIZONTAL, resolution=0.01, command=update_neck)
neck_x.pack(side=tk.RIGHT)
neck_slider_y_frame = tk.Frame(neck_slider_frame)
neck_slider_y_frame.pack()
tk.Label(neck_slider_y_frame, text="Y").pack(side=tk.LEFT)
neck_y = tk.Scale(neck_slider_y_frame, from_=-0.79, to=0.79, orient=tk.HORIZONTAL, resolution=0.01, command=update_neck)
neck_y.pack(side=tk.RIGHT)
neck_slider_z_frame = tk.Frame(neck_slider_frame)
neck_slider_z_frame.pack()
tk.Label(neck_slider_z_frame, text="Z").pack(side=tk.LEFT)
neck_z = tk.Scale(neck_slider_z_frame, from_=-1.4, to=1.4, orient=tk.HORIZONTAL, resolution=0.01, command=update_neck)
neck_z.pack(side=tk.RIGHT)
# 3  right_shoulder
right_shoulder_frame = tk.Frame(scroll_frame.interior)
right_shoulder_frame.pack(pady=(15, 5), anchor="w")
tk.Label(right_shoulder_frame, text="Right Shoulder:").pack(side=tk.LEFT)
right_shoulder_slider_frame = tk.Frame(right_shoulder_frame)
right_shoulder_slider_frame.pack(padx=5)
right_shoulder_slider_x_frame = tk.Frame(right_shoulder_slider_frame)
right_shoulder_slider_x_frame.pack()
tk.Label(right_shoulder_slider_x_frame, text="X").pack(side=tk.LEFT)
right_shoulder_x = tk.Scale(right_shoulder_slider_x_frame, from_=-1.57, to=1.57, orient=tk.HORIZONTAL, resolution=0.01, command=update_right_shoulder)
right_shoulder_x.pack(side=tk.RIGHT)
right_shoulder_slider_y_frame = tk.Frame(right_shoulder_slider_frame)
right_shoulder_slider_y_frame.pack()
tk.Label(right_shoulder_slider_y_frame, text="Y").pack(side=tk.LEFT)
right_shoulder_y = tk.Scale(right_shoulder_slider_y_frame, from_=-1.57, to=1.57, orient=tk.HORIZONTAL, resolution=0.01, command=update_right_shoulder)
right_shoulder_y.pack(side=tk.RIGHT)
right_shoulder_slider_z_frame = tk.Frame(right_shoulder_slider_frame)
right_shoulder_slider_z_frame.pack()
tk.Label(right_shoulder_slider_z_frame, text="Z").pack(side=tk.LEFT)
right_shoulder_z = tk.Scale(right_shoulder_slider_z_frame, from_=-1.57, to=1.57, orient=tk.HORIZONTAL, resolution=0.01, command=update_right_shoulder)
right_shoulder_z.pack(side=tk.RIGHT)
# 4  right_elbow
right_elbow_frame = tk.Frame(scroll_frame.interior)
right_elbow_frame.pack(pady=(15, 5), anchor="w")
tk.Label(right_elbow_frame, text="Right Elbow:").pack(side=tk.LEFT)
right_elbow = tk.Scale(right_elbow_frame, from_=0, to=2.62, orient=tk.HORIZONTAL, resolution=0.01, command=update_right_elbow)
right_elbow.pack(side=tk.RIGHT)
# 6  left_shoulder
left_shoulder_frame = tk.Frame(scroll_frame.interior)
left_shoulder_frame.pack(pady=(15, 5), anchor="w")
tk.Label(left_shoulder_frame, text="Left Shoulder:").pack(side=tk.LEFT)
left_shoulder_slider_frame = tk.Frame(left_shoulder_frame)
left_shoulder_slider_frame.pack(padx=5)
left_shoulder_slider_x_frame = tk.Frame(left_shoulder_slider_frame)
left_shoulder_slider_x_frame.pack()
tk.Label(left_shoulder_slider_x_frame, text="X").pack(side=tk.LEFT)
left_shoulder_x = tk.Scale(left_shoulder_slider_x_frame, from_=-1.57, to=1.57, orient=tk.HORIZONTAL, resolution=0.01, command=update_left_shoulder)
left_shoulder_x.pack(side=tk.RIGHT)
left_shoulder_slider_y_frame = tk.Frame(left_shoulder_slider_frame)
left_shoulder_slider_y_frame.pack()
tk.Label(left_shoulder_slider_y_frame, text="Y").pack(side=tk.LEFT)
left_shoulder_y = tk.Scale(left_shoulder_slider_y_frame, from_=-1.57, to=1.57, orient=tk.HORIZONTAL, resolution=0.01, command=update_left_shoulder)
left_shoulder_y.pack(side=tk.RIGHT)
left_shoulder_slider_z_frame = tk.Frame(left_shoulder_slider_frame)
left_shoulder_slider_z_frame.pack()
tk.Label(left_shoulder_slider_z_frame, text="Z").pack(side=tk.LEFT)
left_shoulder_z = tk.Scale(left_shoulder_slider_z_frame, from_=-1.57, to=1.57, orient=tk.HORIZONTAL, resolution=0.01, command=update_left_shoulder)
left_shoulder_z.pack(side=tk.RIGHT)
# 7  left_elbow
left_elbow_frame = tk.Frame(scroll_frame.interior)
left_elbow_frame.pack(pady=(15, 5), anchor="w")
tk.Label(left_elbow_frame, text="Left Elbow:").pack(side=tk.LEFT)
left_elbow = tk.Scale(left_elbow_frame, from_=0, to=2.62, orient=tk.HORIZONTAL, resolution=0.01, command=update_left_elbow)
left_elbow.pack(side=tk.RIGHT)
# 9  right_hip
right_hip_frame = tk.Frame(scroll_frame.interior)
right_hip_frame.pack(pady=(15, 5), anchor="w")
tk.Label(right_hip_frame, text="Right Hip:").pack(side=tk.LEFT)
right_hip_slider_frame = tk.Frame(right_hip_frame)
right_hip_slider_frame.pack(padx=5)
right_hip_slider_x_frame = tk.Frame(right_hip_slider_frame)
right_hip_slider_x_frame.pack()
tk.Label(right_hip_slider_x_frame, text="X").pack(side=tk.LEFT)
right_hip_x = tk.Scale(right_hip_slider_x_frame, from_=-2.09, to=2.09, orient=tk.HORIZONTAL, resolution=0.01, command=update_right_hip)
right_hip_x.pack(side=tk.RIGHT)
right_hip_slider_y_frame = tk.Frame(right_hip_slider_frame)
right_hip_slider_y_frame.pack()
tk.Label(right_hip_slider_y_frame, text="Y").pack(side=tk.LEFT)
right_hip_y = tk.Scale(right_hip_slider_y_frame, from_=-0.79, to=0.79, orient=tk.HORIZONTAL, resolution=0.01, command=update_right_hip)
right_hip_y.pack(side=tk.RIGHT)
right_hip_slider_z_frame = tk.Frame(right_hip_slider_frame)
right_hip_slider_z_frame.pack()
tk.Label(right_hip_slider_z_frame, text="Z").pack(side=tk.LEFT)
right_hip_z = tk.Scale(right_hip_slider_z_frame, from_=-0.79, to=0.79, orient=tk.HORIZONTAL, resolution=0.01, command=update_right_hip)
right_hip_z.pack(side=tk.RIGHT)
# 10 right_knee
right_knee_frame = tk.Frame(scroll_frame.interior)
right_knee_frame.pack(pady=(15, 5), anchor="w")
tk.Label(right_knee_frame, text="Right Knee:").pack(side=tk.LEFT)
right_knee = tk.Scale(right_knee_frame, from_=0, to=-2.36, orient=tk.HORIZONTAL, resolution=0.01, command=update_right_knee)
right_knee.pack(side=tk.RIGHT)
# 11 right_ankle
right_ankle_frame = tk.Frame(scroll_frame.interior)
right_ankle_frame.pack(pady=(15, 5), anchor="w")
tk.Label(right_ankle_frame, text="Right Ankle:").pack(side=tk.LEFT)
right_ankle_slider_frame = tk.Frame(right_ankle_frame)
right_ankle_slider_frame.pack(padx=5)
right_ankle_slider_x_frame = tk.Frame(right_ankle_slider_frame)
right_ankle_slider_x_frame.pack()
tk.Label(right_ankle_slider_x_frame, text="X").pack(side=tk.LEFT)
right_ankle_x = tk.Scale(right_ankle_slider_x_frame, from_=-0.87, to=0.87, orient=tk.HORIZONTAL, resolution=0.01, command=update_right_ankle)
right_ankle_x.pack(side=tk.RIGHT)
right_ankle_slider_y_frame = tk.Frame(right_ankle_slider_frame)
right_ankle_slider_y_frame.pack()
tk.Label(right_ankle_slider_y_frame, text="Y").pack(side=tk.LEFT)
right_ankle_y = tk.Scale(right_ankle_slider_y_frame, from_=-0.35, to=0.35, orient=tk.HORIZONTAL, resolution=0.01, command=update_right_ankle)
right_ankle_y.pack(side=tk.RIGHT)
right_ankle_slider_z_frame = tk.Frame(right_ankle_slider_frame)
right_ankle_slider_z_frame.pack()
tk.Label(right_ankle_slider_z_frame, text="Z").pack(side=tk.LEFT)
right_ankle_z = tk.Scale(right_ankle_slider_z_frame, from_=-0.87, to=0.87, orient=tk.HORIZONTAL, resolution=0.01, command=update_right_ankle)
right_ankle_z.pack(side=tk.RIGHT)
# 12 left_hip
left_hip_frame = tk.Frame(scroll_frame.interior)
left_hip_frame.pack(pady=(15, 5), anchor="w")
tk.Label(left_hip_frame, text="Left Hip:").pack(side=tk.LEFT)
left_hip_slider_frame = tk.Frame(left_hip_frame)
left_hip_slider_frame.pack(padx=5)
left_hip_slider_x_frame = tk.Frame(left_hip_slider_frame)
left_hip_slider_x_frame.pack()
tk.Label(left_hip_slider_x_frame, text="X").pack(side=tk.LEFT)
left_hip_x = tk.Scale(left_hip_slider_x_frame, from_=-2.09, to=2.09, orient=tk.HORIZONTAL, resolution=0.01, command=update_left_hip)
left_hip_x.pack(side=tk.RIGHT)
left_hip_slider_y_frame = tk.Frame(left_hip_slider_frame)
left_hip_slider_y_frame.pack()
tk.Label(left_hip_slider_y_frame, text="Y").pack(side=tk.LEFT)
left_hip_y = tk.Scale(left_hip_slider_y_frame, from_=-0.79, to=0.79, orient=tk.HORIZONTAL, resolution=0.01, command=update_left_hip)
left_hip_y.pack(side=tk.RIGHT)
left_hip_slider_z_frame = tk.Frame(left_hip_slider_frame)
left_hip_slider_z_frame.pack()
tk.Label(left_hip_slider_z_frame, text="Z").pack(side=tk.LEFT)
left_hip_z = tk.Scale(left_hip_slider_z_frame, from_=-0.79, to=0.79, orient=tk.HORIZONTAL, resolution=0.01, command=update_left_hip)
left_hip_z.pack(side=tk.RIGHT)
# 13 left_knee
left_knee_frame = tk.Frame(scroll_frame.interior)
left_knee_frame.pack(pady=(15, 5), anchor="w")
tk.Label(left_knee_frame, text="Left Knee:").pack(side=tk.LEFT)
left_knee = tk.Scale(left_knee_frame, from_=0, to=-2.36, orient=tk.HORIZONTAL, resolution=0.01, command=update_left_knee)
left_knee.pack(side=tk.RIGHT)
# 14 left_ankle
left_ankle_frame = tk.Frame(scroll_frame.interior)
left_ankle_frame.pack(pady=(15, 5), anchor="w")
tk.Label(left_ankle_frame, text="Left Ankle:").pack(side=tk.LEFT)
left_ankle_slider_frame = tk.Frame(left_ankle_frame)
left_ankle_slider_frame.pack(padx=5)
left_ankle_slider_x_frame = tk.Frame(left_ankle_slider_frame)
left_ankle_slider_x_frame.pack()
tk.Label(left_ankle_slider_x_frame, text="X").pack(side=tk.LEFT)
left_ankle_x = tk.Scale(left_ankle_slider_x_frame, from_=-0.87, to=0.87, orient=tk.HORIZONTAL, resolution=0.01, command=update_left_ankle)
left_ankle_x.pack(side=tk.RIGHT)
left_ankle_slider_y_frame = tk.Frame(left_ankle_slider_frame)
left_ankle_slider_y_frame.pack()
tk.Label(left_ankle_slider_y_frame, text="Y").pack(side=tk.LEFT)
left_ankle_y = tk.Scale(left_ankle_slider_y_frame, from_=-0.35, to=0.35, orient=tk.HORIZONTAL, resolution=0.01, command=update_left_ankle)
left_ankle_y.pack(side=tk.RIGHT)
left_ankle_slider_z_frame = tk.Frame(left_ankle_slider_frame)
left_ankle_slider_z_frame.pack()
tk.Label(left_ankle_slider_z_frame, text="Z").pack(side=tk.LEFT)
left_ankle_z = tk.Scale(left_ankle_slider_z_frame, from_=-0.87, to=0.87, orient=tk.HORIZONTAL, resolution=0.01, command=update_left_ankle)
left_ankle_z.pack(side=tk.RIGHT)
# Buttons
button_frame = tk.Frame(custom_frame)
button_frame.pack(pady=(15, 5), anchor="w")
# Reference Image Buttons
ref_frame = tk.Frame(button_frame)
ref_frame.pack(padx=5, anchor = "w")
tk.Button(ref_frame, text="Set reference Image", command=set_image).pack(side=tk.LEFT)
tk.Label(ref_frame, text="Show").pack(side=tk.LEFT)
show_ref_image = tk.BooleanVar(value=False)
tk.Checkbutton(ref_frame, variable=show_ref_image).pack(side=tk.RIGHT)
# Generate with AI button
tk.Button(button_frame, text="Generate with AI", command=gen_ai_async).pack(pady=10, padx=5, anchor="w")
ai_label = tk.Label(button_frame, text="AI can be mistaken")
ai_label.pack(padx=5, anchor="w")
# Go back to Controls
tk.Button(button_frame, text="Back", command=back_control).pack(pady=10, anchor="w")

# Start rendering thread
render_thread = threading.Thread(target=render_loop, daemon=True)
render_thread.start()

# Update GUI
update_frame()

root.mainloop()
