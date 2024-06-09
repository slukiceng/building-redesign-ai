import streamlit as st
from io import BytesIO
from PIL import Image, ImageOps
import base64
import replicate
import os

st.set_page_config(page_title='Building Redesign AI Model', page_icon='👁️')

st.markdown('# Building Redesign AI')

with st.sidebar:
    api_key = st.text_input('Replicate API Key', '', type='password')
    # Get user inputs
    text_input = st.text_input("Describe how you'd like to restyle your image", "")

    img_input = st.file_uploader('Upload an Image', type=['jpg', 'jpeg', 'png'])

    if img_input is not None:
        st.session_state.img_input = Image.open(img_input)


    # Convert uploaded image to base64 with URI prefix
    def convert_image_to_base64(image):
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        img_uri = f"data:application/octet-stream;base64,{img_str}"
        return img_uri
    
    # Custom purple button
    custom_button = """
    <style>
    .stButton > button {
        background-color: #6a0dad;
        color: white;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
        cursor: pointer;
        border-radius: 5px;
    }
    .stButton > button:hover {
        background-color: #4a0070;
    }
    </style>
    """
    st.markdown(custom_button, unsafe_allow_html=True)


    if st.button('Render new idea'):
        if not api_key:
            st.warning('API Key required')
            st.stop()
        if not text_input and not img_input:
            st.warning('You can\'t just send nothing!')
            st.stop()

        if img_input is not None:
            image = Image.open(img_input)
            img_base64 = convert_image_to_base64(image)
        else:
            img_base64 = None

        st.session_state.text_input = text_input
        st.session_state.api_key = api_key

        input = {
            "prompt": text_input,
            "image": img_base64,
        }

        os.environ["REPLICATE_API_TOKEN"] = api_key

        model = "jagilley/controlnet-hough:854e8727697a057c525cdb45ab037f64ecca770a1769cc52287c2e56472a247b"

        output = replicate.run(model, input=input)

        st.session_state.output = output

if 'img_input' in st.session_state:
    st.image(st.session_state.img_input, caption='Uploaded Image')

    if 'output' in st.session_state:
        for out_img in st.session_state.output:
            st.image(out_img, caption='Output Image')
else:
    
    # Function to load and crop images to a fixed size
    def load_and_crop_image(image_path, size=(200, 200)):
        img = Image.open(image_path)
        img = ImageOps.fit(img, size, Image.Resampling.LANCZOS)
        return img

    # Show stock images from the images directory
    st.markdown('## Examples')
    images_dir = 'images'
    images = os.listdir(images_dir)
    images = [os.path.join(images_dir, img) for img in images if img.endswith(('jpg', 'jpeg', 'png'))]
    # reorder images based on file name
    images = sorted(images)
    
    for i in range(0, len(images), 4):
        cols = st.columns(4)
        for col, img_path in zip(cols, images[i:i+4]):
            img = load_and_crop_image(img_path)
            col.image(img)

