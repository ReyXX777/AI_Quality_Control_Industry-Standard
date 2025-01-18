import streamlit as st
from PIL import Image
import requests
import io

# Set page title
st.set_page_config(page_title="AI-Powered Quality Control", layout="wide")

# Header
st.title("AI-Powered Quality Control for Manufacturing")
st.subheader("Mobile-Optimized Quality Control Dashboard")

# User Authentication Component
def authenticate_user(username: str, password: str) -> bool:
    """
    Simulate user authentication (replace with actual authentication logic).
    """
    return username == "admin" and password == "password"

# Display login form if not authenticated
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.sidebar.header("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if authenticate_user(username, password):
            st.session_state.authenticated = True
            st.sidebar.success("Login successful!")
        else:
            st.sidebar.error("Invalid username or password")
    st.stop()

# Navigation
nav = st.sidebar.radio("Navigation", ["Home", "Defect Detection", "Maintenance Prediction", "Quality Standards", "Feedback"])

# Home Page
if nav == "Home":
    st.image("assets/quality_control_image.jpg", caption="Streamline your manufacturing process with AI.")
    st.write("Welcome to the AI-powered quality control solution tailored for the manufacturing sector in India. "
             "This platform helps improve product quality, reduce defects, and predict maintenance needs.")

# Defect Detection Page
elif nav == "Defect Detection":
    st.header("Defect Detection")
    st.write("Upload an image of the product for defect detection.")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Display uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        # Simulate API call for defect detection (replace with actual API call)
        if st.button("Detect Defect"):
            # Simulate prediction (Replace with API call result)
            result = {"defect_found": True, "confidence": 95.7}
            if result["defect_found"]:
                st.write(f"Defect Detected! Confidence: {result['confidence']}%")
            else:
                st.write(f"No Defect Found. Confidence: {result['confidence']}%")

# Maintenance Prediction Page
elif nav == "Maintenance Prediction":
    st.header("Predictive Maintenance")
    equipment_id = st.text_input("Enter Equipment ID", "EQUIP-001")
    if st.button("Predict Maintenance"):
        # Simulate API call for predictive maintenance (replace with actual API call)
        prediction = {"next_maintenance_date": "2025-03-15", "risk_score": 80}
        st.write(f"Next Maintenance Date: {prediction['next_maintenance_date']}")
        st.write(f"Risk Score: {prediction['risk_score']}")

# Quality Standards Page
elif nav == "Quality Standards":
    st.header("Manage Quality Standards")
    st.write("Create and manage your quality standards for manufacturing.")
    st.text_input("Standard Name", "")
    st.text_area("Standard Description", "")
    st.button("Save Standard")

# Feedback Collection Component
elif nav == "Feedback":
    st.header("Provide Feedback")
    feedback = st.text_area("Share your feedback or report issues:")
    if st.button("Submit Feedback"):
        st.success("Thank you for your feedback! We will review it shortly.")

# Footer
st.markdown("""
    ---
    **AI-Powered Quality Control** - Developed to support India's manufacturing industry.  
    © 2025 AI Quality Control Solutions
""")
