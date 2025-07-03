import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime
import base64
import os
import google.generativeai as genai
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import json
import requests
from geopy.geocoders import Nominatim
import cv2
from PIL import Image
import io
import subprocess
import threading
import queue

# Set page config
st.set_page_config(
    page_title="Tech Internship Dashboard",
    layout="wide",
    page_icon="🚀"
)

# Custom CSS for styling
st.markdown("""
<style>
.section {
    border-left: 5px solid #4CAF50;
    padding: 10px 15px;
    margin: 15px 0;
    border-radius: 5px;
    background-color: #f9f9f9;
}
.header-text {
    color: #1e3a8a;
}
.stExpander > div > div {
    background-color: #f0f7ff;
}
.task-complete {
    color: #4CAF50;
    font-weight: bold;
}
.task-pending {
    color: #FF9800;
}
.map-container {
    height: 400px;
    border-radius: 10px;
    overflow: hidden;
    margin-top: 15px;
}
.docker-command {
    background-color: #2d2d2d;
    color: #f1f1f1;
    padding: 10px;
    border-radius: 5px;
    font-family: monospace;
    margin: 5px 0;
}
</style>
""", unsafe_allow_html=True)

# ==================== HELPER FUNCTIONS ====================
def get_docker_output(command):
    """Simulate Docker command output"""
    outputs = {
        "Run a Container": """Hello from Docker!
This message shows that your installation appears to be working correctly.

To generate this message, Docker took the following steps:
 1. The Docker client contacted the Docker daemon.
 2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
 3. The Docker daemon created a new container from that image.
 4. The Docker daemon streamed that output to the Docker client.""",
        
        "Pull an Image": """Using default tag: latest
latest: Pulling from library/nginx
Digest: sha256:0d17b565c37bcbd895e9d92315a05c1c3c9a29f762b011a10c54a66cd53c9b31
Status: Downloaded newer image for nginx:latest
docker.io/library/nginx:latest""",
        
        "List All Images": """REPOSITORY    TAG       IMAGE ID       CREATED        SIZE
nginx         latest    abc123456789   2 weeks ago    133MB
hello-world   latest    def456789abc   3 months ago   13.3kB""",
        
        "List Running Containers": """CONTAINER ID   IMAGE         COMMAND                  CREATED         STATUS         PORTS     NAMES
a1b2c3d4e5f6   nginx         "/docker-entrypoint.…"   5 minutes ago   Up 5 minutes   80/tcp    webserver""",
        
        "Stop a Container": "Container abc123456789 stopped",
        
        "Delete a Container": "Container def456789abc removed"
    }
    return outputs.get(command, "Command executed successfully")

def get_docker_explanation(command):
    """Get explanation for Docker commands"""
    explanations = {
        "Run a Container": """
        The `docker run` command creates and starts a container from a specified image.
        
        **Options:**
        - `-d`: Run container in background (detached mode)
        - `-p`: Publish a container's port(s) to the host
        - `--name`: Assign a name to the container
        
        **Example:**
        ```bash
        docker run -d -p 8080:80 --name mynginx nginx
        ```
        """,
        
        "Pull an Image": """
        The `docker pull` command downloads an image from a Docker registry.
        
        **Syntax:**
        ```bash
        docker pull [OPTIONS] NAME[:TAG|@DIGEST]
        ```
        
        **Example:**
        ```bash
        docker pull ubuntu:20.04
        ```
        """,
        
        "List All Images": """
        The `docker images` command lists all Docker images stored locally.
        
        **Options:**
        - `-a`: Show all images (default hides intermediate images)
        - `-q`: Only show image IDs
        
        **Example:**
        ```bash
        docker images --format "table {{.ID}}\t{{.Repository}}\t{{.Tag}}"
        ```
        """,
        
        "List Running Containers": """
        The `docker ps` command lists running containers.
        
        **Options:**
        - `-a`: Show all containers (including stopped ones)
        - `-q`: Only display container IDs
        - `--format`: Format output using a Go template
        
        **Example:**
        ```bash
        docker ps -a --format "table {{.ID}}\t{{.Names}}\t{{.Status}}"
        ```
        """,
        
        "Stop a Container": """
        The `docker stop` command stops one or more running containers.
        
        **Syntax:**
        ```bash
        docker stop [OPTIONS] CONTAINER [CONTAINER...]
        ```
        
        **Options:**
        - `-t`: Seconds to wait for stop before killing it (default 10)
        
        **Example:**
        ```bash
        docker stop my_container
        ```
        """,
        
        "Delete a Container": """
        The `docker rm` command removes one or more containers.
        
        **Syntax:**
        ```bash
        docker rm [OPTIONS] CONTAINER [CONTAINER...]
        ```
        
        **Options:**
        - `-f`: Force removal (running containers)
        - `-v`: Remove volumes associated with the container
        
        **Example:**
        ```bash
        docker rm -f old_container
        ```
        """
    }
    return explanations.get(command, "No explanation available")

# Create main tabs
ml_tab, fullstack_tab, devops_tab, genai_tab = st.tabs([
    "🤖 AI/ML", 
    "💻 FullStack", 
    "🐳 DevOps", 
    "🧠 Generative AI"
])

# ==================== AI/ML SECTION ====================
with ml_tab:
    st.header("AI/ML Internship Dashboard", divider="blue")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Upload Files & User Details")
        
        with st.form("user_details_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email Address")
            university = st.text_input("University/Institution")
            uploaded_file = st.file_uploader("Upload your document (PDF, DOC, TXT)", type=["pdf", "docx", "txt"])
            
            submitted = st.form_submit_button("Submit Details")
            
            if submitted:
                if name and email and university:
                    st.session_state.user_details = {
                        "name": name,
                        "email": email,
                        "university": university,
                        "file_name": uploaded_file.name if uploaded_file else "No file uploaded",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.success("Details submitted successfully!")
                else:
                    st.error("Please fill in all required fields")
        
        if "user_details" in st.session_state:
            st.subheader("Submitted Information")
            st.json(st.session_state.user_details)
            
            if uploaded_file:
                st.download_button(
                    label="Download Uploaded File",
                    data=uploaded_file.getvalue(),
                    file_name=uploaded_file.name,
                    mime="application/octet-stream"
                )
    
    with col2:
        st.subheader("Marks Prediction Model")
        st.info("Using Linear Regression to predict marks based on study hours")
        
        # Sample dataset
        data = {
            'Hours': [2.5, 5.1, 3.2, 8.5, 3.5, 1.5, 9.2, 5.5, 8.3, 2.7, 7.7, 5.9, 4.5, 3.3, 1.1, 8.9, 2.5, 1.9, 6.1, 7.4],
            'Marks': [21, 47, 27, 75, 30, 20, 88, 60, 81, 25, 85, 62, 41, 42, 17, 95, 30, 24, 67, 69]
        }
        df = pd.DataFrame(data)
        
        # Train the model
        X = df[['Hours']]
        y = df['Marks']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        # Show data
        st.write("Sample Dataset:")
        st.dataframe(df.head(8))
        
        # Visualization
        st.line_chart(df.set_index('Hours'))
        
        # Prediction
        hours = st.slider("Select study hours", 1.0, 10.0, 5.0)
        prediction = model.predict([[hours]])[0]
        
        st.metric("Predicted Marks", f"{prediction:.2f}", "Marks")
        st.caption(f"Model Accuracy: {model.score(X_test, y_test)*100:.2f}%")

# ==================== FULLSTACK SECTION ====================
with fullstack_tab:
    st.header("FullStack Development Dashboard", divider="green")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Media Capture Tools")
        
        # Camera capture
        st.write("### Capture Image from Camera")
        img_file_buffer = st.camera_input("Take a picture")
        
        if img_file_buffer is not None:
            st.session_state.captured_image = img_file_buffer
            st.success("Image captured!")
            
            if st.button("Save Image to Computer", key="save_image"):
                if 'captured_image' in st.session_state:
                    with open("captured_image.jpg", "wb") as f:
                        f.write(st.session_state.captured_image.getbuffer())
                    st.success("Image saved as 'captured_image.jpg'")
                else:
                    st.warning("No image captured yet")
        
        # Video recording
        st.write("### Record a 10-Second Video")
        if st.button("Start Recording", key="start_recording"):
            st.session_state.recording = True
            st.session_state.recording_start = time.time()
            st.info("Recording started...")
            
            # Simulate recording in background
            def record_video():
                time.sleep(10)
                st.session_state.recording = False
                st.session_state.video_recorded = True
                st.experimental_rerun()
            
            threading.Thread(target=record_video, daemon=True).start()
        
        if 'recording' in st.session_state and st.session_state.recording:
            elapsed = time.time() - st.session_state.recording_start
            st.warning(f"Recording... {min(10, int(elapsed))}/10 seconds")
            
        if 'video_recorded' in st.session_state and st.session_state.video_recorded:
            st.success("Recording complete!")
            with open("sample_video.mp4", "rb") as f:
                video_bytes = f.read()
            st.video(video_bytes)
            st.download_button(
                label="Download Video",
                data=video_bytes,
                file_name="recorded_video.mp4",
                mime="video/mp4"
            )
    
    with st.container():
        st.subheader("Location Services")
        st.write("### Fetch Live Location")

        if st.button("Get My Location", key="get_location"):
            try:
                response = requests.get("https://ipinfo.io/json")
                data = response.json()

                if 'loc' in data:
                    lat, lon = map(float, data['loc'].split(','))
                    st.session_state.location = (lat, lon)
                    st.success(f"Location found: {data.get('city', 'Unknown')}, {data.get('region', '')}, {data.get('country', '')}")
                else:
                    st.error("Could not retrieve location")
                    st.session_state.location = None
            except Exception as e:
                st.error(f"Error retrieving location: {str(e)}")
                # Fallback
                st.session_state.location = (37.7749, -122.4194)

        if 'location' in st.session_state and st.session_state.location is not None:
            st.map(pd.DataFrame({
                'lat': [st.session_state.location[0]],
                'lon': [st.session_state.location[1]]
            }))
            st.write(f"**Coordinates:** {st.session_state.location[0]}, {st.session_state.location[1]}")
        else:
            st.warning("No location data available. Click 'Get My Location' to fetch your location.")

        
        # HTML Interpreter
        st.subheader("Live HTML Interpreter")
        html_code = st.text_area("Enter HTML code:", height=200, 
                                value="<h1>Hello World</h1>\n<p>This is a paragraph</p>\n<ul><li>Item 1</li><li>Item 2</li></ul>")
        
        if st.button("Render HTML", key="render_html"):
            st.session_state.html_to_render = html_code
        
        if 'html_to_render' in st.session_state:
            st.write("Rendered Output:")
            st.components.v1.html(st.session_state.html_to_render, height=300, scrolling=True)

# ==================== DEVOPS SECTION ====================
with devops_tab:
    st.header("DevOps Operations Dashboard", divider="orange")
    
    st.subheader("Docker Command Center")
    
    # Docker commands with simulated output
    docker_commands = {
        "Run a Container": "sudo docker run hello-world",
        "Pull an Image": "sudo docker pull nginx",
        "List All Images": "sudo docker images",
        "List Running Containers": "sudo docker ps",
        "Stop a Container": "sudo docker stop <container_id>",
        "Delete a Container": "sudo docker rm <container_id>"
    }
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.write("### Docker Commands")
        selected_command = st.selectbox("Select a Docker command:", list(docker_commands.keys()))
        
        if st.button("Execute Command", key="run_docker"):
            st.session_state.docker_command = selected_command
            st.session_state.docker_output = get_docker_output(selected_command)
    
    with col2:
        st.write("### Command Output")
        if 'docker_command' in st.session_state:
            st.code(docker_commands[st.session_state.docker_command], language="bash")
            st.write("Output:")
            st.code(st.session_state.docker_output, language="text")
        else:
            st.info("Select a command and click 'Execute Command' to see output")
    
    # Docker command explanations
    st.subheader("Docker Command Reference")
    for cmd, syntax in docker_commands.items():
        with st.expander(f"{cmd}: `{syntax}`"):
            st.write(get_docker_explanation(cmd))

# ==================== GENERATIVE AI SECTION ====================
import streamlit as st
import google.generativeai as genai

with genai_tab:
    st.header("Generative AI Playground", divider="violet")
    
    # Gemini API Key input
    st.subheader("Gemini API Configuration")
    api_key = st.text_input("Enter your Gemini API Key:", type="password")
    
    if api_key:
        try:
            genai.configure(api_key=api_key)
            st.success("Gemini API key configured successfully!")
        except Exception as e:
            st.error(f"API Configuration Error: {str(e)}")
    else:
        st.info("Please enter your Gemini API key to use this feature")
    
    st.subheader("AI Chat Interface")
    user_input = st.text_area("Enter your prompt:", height=150,
                              placeholder="Ask something like: Explain how AI works in a few words")
    
    if st.button("Generate Response", disabled=not api_key):
        if user_input.strip():
            with st.spinner("Generating response..."):
                try:
                    # ✅ Use Gemini 2.0 Flash model (as shown in your curl)
                    model = genai.GenerativeModel("models/gemini-2.0-flash")
                    response = model.generate_content(user_input)
                    st.session_state.ai_response = response.text
                except Exception as e:
                    st.error(f"Error generating response: {str(e)}")
        else:
            st.warning("Please enter a prompt first.")
    
    if 'ai_response' in st.session_state:
        st.subheader("AI Response:")
        st.write(st.session_state.ai_response)

# Initialize session state variables
if 'location' not in st.session_state:
    st.session_state.location = None
if 'html_to_render' not in st.session_state:
    st.session_state.html_to_render = None
if 'docker_command' not in st.session_state:
    st.session_state.docker_command = None
if 'docker_output' not in st.session_state:
    st.session_state.docker_output = None
if 'ai_response' not in st.session_state:
    st.session_state.ai_response = None
if 'recording' not in st.session_state:
    st.session_state.recording = False
if 'video_recorded' not in st.session_state:
    st.session_state.video_recorded = False
if 'captured_image' not in st.session_state:
    st.session_state.captured_image = None
if 'user_details' not in st.session_state:
    st.session_state.user_details = None
