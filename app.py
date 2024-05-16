from openai import OpenAI
import os
import streamlit as st
from dotenv import load_dotenv
import json
 
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
 
# Make sure you have the API key in the environment variable; otherwise, this will be None.
if openai_api_key is None:
    raise ValueError("OPENAI_API_KEY environment variable not found.")
 
# Set the API key for the OpenAI client
OpenAI.api_key = openai_api_key
 
# openai_api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI()
 
system_instruction = """
You are an assistant tasked with extracting specific information from user inputs where applicable. Extract the following details:
- Job title
- City related to the job position
- Country related to the job position
- Radius (distance to the location specified)
- Mandatory skills (key skills required for the role)
- Optional skills (desirable skills that are beneficial for the role)
- Languages required
- Years of experience required (specify as a range if possible)
- Years in job represents the number of years the person should have been in the current job position
- Email (indicate whether an email address is required in the applicant's profile)
- Phone (indicate whether a phone number is required in the applicant's profile)
- Company preferences (include preferences such as 'worksAt', 'doesNotWorkAt', 'previouslyWorkedAt', 'doesNotPreviouslyWorkAt' specifically for company names)
- 'personIs': a list with potential entries including 'Female', 'Male', 'Consultant', 'Executive', 'Freelancer', 'Scientist', 'Student' (add to the list based on user input)
- 'personIsNot': a list with potential entries including 'Consultant', 'Executive', 'Freelancer', 'Scientist', 'Student' (add to the list based on user input stating the person should NOT be one of these)
- 'previouslyAs': previously worked as (specify the previous job title if mentioned)
- 'doesNotPreviouslyWorkAs': specify the job title the person should not have previously worked as

Ensure the output is structured as follows:
{
    "jobTitle": "",
    "city": "",
    "country": "",
    "radius": 0,
    "mandatorySkills": [],
    "optionalSkills": [],
    "languages": [],
    "yearsOfExperienceFrom": 0,
    "yearsOfExperienceTo": 0,
    "yearsInJobFrom": 0,
    "yearsInJobTo": 0,
    "email": false,
    "phone": false,
    "worksAt": "",
    "doesNotWorkAt": "",
    "previouslyWorkedAt": "",
    "doesNotPreviouslyWorkAt": "",
    "personIs": [],
    "personIsNot": [],
    "previouslyAs": "",
    "doesNotPreviouslyWorkAs": ""
}
"""
# Placeholder for a real authentication mechanism
def check_credentials(username, password):
    # Fetch the password from environment variables
    correct_password = os.getenv('USER_PASSWORD')
    return username == "talentwunder" and password == correct_password
 
                
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
 
# Function to display the login form
def display_login_form():
    st.title("Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")
        if login_button:
            if check_credentials(username, password):
                st.session_state.logged_in = True
                st.success("Logged in successfully.")
                # Using st.experimental_rerun() to force the app to rerun might help, but use it judiciously.
                st.experimental_rerun()
            else:
                st.error("Incorrect username or password.")
                
                
def display_main_app():
    st.title('AI Search Generator')
    selected_model = "gpt-4o"
    user_input = st.text_area("Enter your prompt:", height=150)
 
    if st.button('Generate Text'):
        if user_input:
            with st.spinner('Generating text... Please wait'):
                # Call the OpenAI API with the provided user prompt and selected model
                completion = client.chat.completions.create(
                  model=selected_model,
                  temperature=0,
                  messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_input},
                ]
            )
            
                # Extract and display only the message text
                generated_text = completion.choices[0].message.content  
                try:
                    data = json.loads(generated_text)
                    st.json(data)
                except:
                    st.write(generated_text)
 
# Decide which part of the app to display based on login status
if not st.session_state.logged_in:
    display_login_form()
else:
    display_main_app()