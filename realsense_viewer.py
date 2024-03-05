import cv2
import numpy as np
import pyrealsense2 as rs
import subprocess

# Configure depth and color streams
config = rs.config()
config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)

# Start the RealSense pipeline
pipeline = rs.pipeline()
pipeline.start(config)

# FFmpeg command for streaming
ffmpeg_cmd = [
    'ffmpeg',
    '-f', 'rawvideo',
    '-vcodec', 'rawvideo',
    '-s', '1280x720',
    '-pix_fmt', 'bgr24',
    '-r', '30',
    '-i', '-',
    '-c:v', 'libx264',
    '-pix_fmt', 'yuv420p',
    '-preset', 'ultrafast',
    '-tune', 'zerolatency',
    '-f', 'rtsp',
    'rtsp://172.19.3.20:8554/mystream'
]

# Start the ffmpeg process
ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

try:
    while True:
        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()

        # Get depth frame
        depth_frame = frames.get_depth_frame()

        # Convert the depth frame to a numpy array
        depth_image = np.asanyarray(depth_frame.get_data())

        # Apply colormap to the depth image for visualization
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

        # Display the depth image
        #cv2.imshow('Depth Image', depth_colormap)

        # Write the depth_colormap frame to the ffmpeg process stdin
        ffmpeg_process.stdin.write(depth_colormap.tobytes())

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Stop the RealSense pipeline
    pipeline.stop()

    # Close the OpenCV window
    #cv2.destroyAllWindows()

    # Terminate the ffmpeg process
    ffmpeg_process.terminate()
