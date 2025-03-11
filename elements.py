import streamlit as st
import time



#Text Elements
st.title("My First Streamlit App")
st.header("This is a header")
st.subheader("This is a subheader")
st.text("This is simple text")
st.markdown("**Bold text**")


# Sliders & Progress
value = st.slider("Select a value", 0, 100, 50)
st.write("Slider Value:", value)


st.progress(0)
for i in range(value):
    time.sleep(0.01)
    st.progress(i + 1)

with st.spinner("Loading..."):
    time.sleep(2)
st.success("Done!")

#MEDIA Elements
st.image("https://www.streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.png", caption="Streamlit Logo")
# st.audio("audio_file.mp3")
st.video("file_example_MP4_640_3MG.mp4")