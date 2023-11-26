import streamlit as st
import requests
import base64
import json
import time
from PIL import Image
import io
import redis
import json

# TODO: 
# Add information about recycling
# Add logic to add NFT to wallet once image is scanned
# Add logic to limit to 1 per type of item and 10 total recycable items per day
# Add logic to update user profile

# Functions
def send_image_to_server(image, url):
    """
    Sends an image to a server using a POST request with retry on failure.

    Args:
        image (bytes): The image data in bytes.
        url (str): The URL of the server to send the image to.

    Returns:
        requests.Response: The response from the server.
    """
    encoded_string = base64.b64encode(image).decode()
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    data = json.dumps({"image": encoded_string})

    for attempt in range(3):
        try:
            response = requests.post(url, data=data, headers=headers)
            return response
        except requests.ConnectionError:
            if attempt < 2:  # Don't show a message on the final attempt
                st.warning("Connection error, retrying...")
            time.sleep(1)
    return None

def retrieve_recycling_information_redis():
    hostname = 'redis-12111.c321.us-east-1-2.ec2.cloud.redislabs.com'
    port = 12111
    password = 'ijNeFVOexsgOvFBn0Q4grGb3OOwXACkZ'
    key = 'RecyclingData'

    # Attempt to retrieve data from Redis
    try:
        return json.loads(redis.Redis(host = hostname, port = port, password = password, ssl=False).get(key))
    except Exception as e:
        return None


def app():
    st.header("Scan")
    st.write("Scan items to recycle them correctly.")

    img_file_buffer = st.camera_input("Take a picture")

    if img_file_buffer is not None:
        image_bytes = img_file_buffer.getvalue()

        # Button to send the request
        if st.button("Scan"):
            with st.spinner("Processing..."):
                progress_bar = st.progress(0)
                for percent_complete in range(100):
                    time.sleep(0.06)
                    progress_bar.progress(percent_complete + 1)
            
            response = send_image_to_server(image=image_bytes, url='http://localhost:5000/objects')
            
            if response is not None:
                progress_bar.empty()
                response_data = response.json()

                class_ids = [obj['class_id'] for obj in response_data['objects']]
                st.write("Class IDs:", class_ids)

                # Display information about recycling ♻️
                st.header("♻️ Recycling Information")

                # Display JSON
                st.markdown("""
                    <style>
                    .big-font {
                        font-size: 30px !important;
                        color: lightgreen;
                    }
                    </style>
                    <p class='big-font'>The Data From our AI</p>
                    """, unsafe_allow_html=True)
                st.write(response_data)

                # Display image
                response_image = response_data['image']
                decoded_image = base64.b64decode(response_image)
                image = Image.open(io.BytesIO(decoded_image))
                st.markdown("""
                    <style>
                    .big-font {
                        font-size: 30px !important;
                        color: lightgreen;
                    }
                    </style>
                    <p class='big-font'>The image from our AI</p>
                    """, unsafe_allow_html=True)
                st.image(image, caption='What we see', use_column_width=True)

                # Save image to Website\Usage History
                image.save('Usage History/' + str(time.time()) + '.jpg')


                # TODO: Add logic to add NFT to wallet once image is scanned
                # Implement logic to limit to 1 per type of item and 10 total recycable items per day
                # Implement logic to update user profile
                
                # Display Success Messages if item is recyclable based on above
                st.success("Item scanned successfully!")
                st.balloons()
                st.write("You have earned 1 RecycleCoin!")

                # st.write(retrieve_recycling_information_redis())
            else:
                st.error("Failed to connect to the server after several attempts.")
                progress_bar.empty()
    else:
        st.write("No image selected")