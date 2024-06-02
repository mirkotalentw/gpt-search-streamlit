import re
from openai import OpenAI
import os
import streamlit as st
from dotenv import load_dotenv
import json
from pydantic import BaseModel, validator
from typing import List, Optional
from photon import get_city_country
 
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
 
# Make sure you have the API key in the environment variable; otherwise, this will be None.
if openai_api_key is None:
    raise ValueError("OPENAI_API_KEY environment variable not found.")
 
# Set the API key for the OpenAI client
OpenAI.api_key = openai_api_key
 
# openai_api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI()

def load_languages(path_to_languages):
    with open(path_to_languages, "r") as file:
        return set(json.load(file))


languages_en = load_languages("./languages_en.json")
languages_de = load_languages("./languages_de.json")
languages_all = languages_en | languages_de

class GptOutput(BaseModel):
    jobTitle: str
    city: Optional[str] = None
    country: Optional[str] = None
    radius: Optional[int] = 0
    mandatorySkills: Optional[List[str]] = None
    optionalSkills: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    suggestions: bool = False
    yearsOfExperienceFrom: Optional[int] = 0
    yearsOfExperienceTo: Optional[int] = 0
    yearsInJobFrom: Optional[int] = 0
    yearsInJobTo: Optional[int] = 0
    email: Optional[bool] = False
    phone: Optional[bool] = False
    worksAt: Optional[str] = None
    doesNotWorkAt: Optional[str] = None
    previouslyWorkedAt: Optional[str] = None
    doesNotPreviouslyWorkAt: Optional[str] = None
    personIs: Optional[List[str]] = None
    personIsNot: Optional[List[str]] = None
    previouslyAs: Optional[str] = None
    doesNotPreviouslyWorkAs: Optional[str] = None
    
    @validator('mandatorySkills', pre=True, always=True)
    def set_default_for_mandatory_skills(cls, v):
        if v is None:
            return []
        return v
    
    @validator('optionalSkills', pre=True, always=True)
    def set_default_for_optional_skills(cls, v):
        if v is None:
            return []
        return v
    
    @validator('languages', pre=True, always=True)
    def set_default_for_languages(cls, v):
        if v is None:
            return []
        return v
    
    @validator('personIs', pre=True, always=True)
    def set_default_for_person_is(cls, v):
        if v is None:
            return []
        return v
    
    @validator('personIsNot', pre=True, always=True)
    def set_default_for_person_is_not(cls, v):
        if v is None:
            return []
        return v
 
system_instruction = """
You are an assistant tasked with extracting specific information from user inputs where applicable. Extract the following details:
- Job title
- City related to the job position
- Country related to the job position
- Radius (distance to the location specified)
- Mandatory skills (key skills required for the role, but please provide shorter versions of the skills if possible for example 'python' instead of 'Python programming language', 'machine learning' instead of 'Machine Learning algorithms' and etc.)
- Optional skills (desirable skills that are beneficial for the role, but please provide shorter versions of the skills if possible for example 'python' instead of 'Python programming language', 'machine learning' instead of 'Machine Learning algorithms' and etc.)
- Languages required
- Years of experience required (specify as a range if possible)
- Years in job represents the number of years the person should have been in the current job position
- Email (indicate whether an email address is required in the applicant's profile)
- Phone (indicate whether a phone number is required in the applicant's profile)
- Company preferences (include preferences such as 'worksAt', 'doesNotWorkAt', 'previouslyWorkedAt', 'doesNotPreviouslyWorkAt' specifically for company names, please exclude industries from this)
- 'personIs': a list with potential entries including 'Female', 'Male', 'Consultant', 'Executive', 'Freelancer', 'Scientist', 'Student' (add to the list based on user input)
- 'personIsNot': a list with potential entries including 'Consultant', 'Executive', 'Freelancer', 'Scientist', 'Student' (add to the list based on user input stating the person should NOT be one of these)
- 'previouslyAs': previously worked as (specify the previous job title if mentioned)
- 'doesNotPreviouslyWorkAs': specify the job title the person should not have previously worked as
- Industry (sector, field of the job position like finance, accounting and etc.)

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
    "doesNotPreviouslyWorkAs": "",
    "industry": ""
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
                
def data_extraction(job_description):
    completion = client.chat.completions.create(
                  model='gpt-4o',
                  temperature=0,
                  messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": job_description},
                ])
    
    generated_text = completion.choices[0].message.content  
    print(generated_text)
    try:
        data = json.loads(generated_text)
        return GptOutput(**data)
    except:
        return GptOutput(jobTitle="")
    
def denormalize_job_title(s):
    pattern = r'\b(\S*/in)\b'

    matches = re.findall(pattern, s)
    if not matches:
        return [s]  

    if ' ' in s.strip():
        without_in = re.sub(pattern, lambda m: m.group(1)[:-3], s)  # Remove /in
        with_in = re.sub(pattern, lambda m: m.group(1)[:-3] + 'in', s)  # Replace /in with in
        return [without_in, with_in]
    else:
        return [re.sub(pattern, lambda m: m.group(1)[:-3] + '*', s)]
    
    
def query_title(job_title, suggestions):
    job_titles = []
    
    job_titles.extend(denormalize_job_title(job_title))
        
    job_query = ' OR '.join([job if ' ' not in job else f'"{job}"' for job in job_titles])
    
    return f'({job_query})'


def query_location(city=None, country=None, distance=0):
    location = ''
    
    if city:
        location += f'{city}'
    
    if location and distance > 0:
        location += f' DISTANCE {distance}'
        
    return location


def query_location_v2(city=None, country=None, distance=0):
    location = ''
    city_normalized, country_normalized = get_city_country(url="http://photon.talentwunder.io:2322", city=city, country=country, lang='de')
    if city_normalized:
        location += f'{city_normalized}'
    
    if location and distance > 0:
        location += f' DISTANCE {distance}'
        
    if country_normalized:
        location += f' COUNTRY {country_normalized}'
        
    return location


def query_languages(optional_skills=[], mandatory_skills=[]):
    skills_set = set(optional_skills + mandatory_skills)
    languages = {skill for skill in skills_set if skill.lower() in languages_all}
    return ' AND '.join([f'"{lang}"' for lang in languages])


def query_languages_v2(languages=[]):
    return ' AND '.join([f'"{lang}"' for lang in languages])

    
    
def boolean_query_v2(job_title, city, country, radius, mandatory_skills, optional_skills,
                                languages, yearsOfExperienceFrom, yearsOfExperienceTo, yearsInJobFrom, yearsInJobTo,
                                email, phone, worksAt, doesNotWorkAt, previouslyWorkedAt, doesNotPreviouslyWorkAt,
                                personIs, personIsNot, doesNotPreviouslyWorkAs, previouslyAs):
    query = query_title(job_title=job_title, suggestions=False)
    location_query = query_location_v2(city, country, radius)
    languages_query = query_languages_v2(languages)
    
    # if skills_query:
    #     query += f' AND {skills_query}'
    skills = list(set(optional_skills + mandatory_skills))
    if len(skills) > 0:
        optional_query = ' OR '.join([f'"{skill}"' for skill in skills if skill.lower() not in languages_all and skill!=''])
        query += f' AND ({optional_query})'

    if location_query:
        query += f' IN {location_query}'
        
    if languages_query:
        query += f' SPEAKS {languages_query}'
        
    if previouslyAs:
        query += f' PREVIOUSLY_AS "{previouslyAs}"'
        
    if doesNotPreviouslyWorkAs:
        query += f' PREVIOUSLY_AS NOT "{doesNotPreviouslyWorkAs}"'
        
    if worksAt:
        query += f' AT "{worksAt}"'
        
    if doesNotWorkAt:
        query += f' AT NOT "{doesNotWorkAt}"'
        
    if previouslyWorkedAt:
        query += f' PREVIOUSLY_AT "{previouslyWorkedAt}"'
        
    if doesNotPreviouslyWorkAt:
        query += f' PREVIOUSLY_AT NOT "{doesNotPreviouslyWorkAt}"'
        
    if len(personIs):
        queryPersonIs = ' '.join([f' IS {person.upper()}' for person in personIs])
        query += queryPersonIs
        
    if len(personIsNot):
        queryPersonIsNot = ' '.join([f' IS NOT {person.upper()}' for person in personIsNot])
        query += queryPersonIsNot
        
    if (yearsOfExperienceFrom>0) or (yearsOfExperienceTo>0):
        if (yearsOfExperienceTo == 0):
            yearsOfExperienceTo = yearsOfExperienceFrom+10
        query += f' YEARS_WORKING {yearsOfExperienceFrom} TO {yearsOfExperienceTo}'
        
    if (yearsInJobFrom>0) or (yearsInJobTo>0):
        if (yearsInJobTo == 0):
            yearsInJobTo = yearsInJobFrom+10
        query += f' YEARS_IN_JOB {yearsInJobFrom} TO {yearsInJobTo}' 
        
    if email:
        query += f' HAS EMAIL'
        
    if phone:
        query += f' HAS PHONE'
            
    return query
                
                
def display_main_app():
    st.title('AI Search Generator')
    selected_model = "gpt-4o"
    user_input = st.text_area("Enter your prompt:", height=150)
 
    if st.button('Generate Text'):
        if user_input:
            with st.spinner('Generating text... Please wait'):
                gpt_output = data_extraction(user_input)
                job_title = gpt_output.model_dump().get("jobTitle")
                city = gpt_output.model_dump().get("city")
                country = gpt_output.model_dump().get("country")
                radius = gpt_output.model_dump().get("radius")
                mandatory_skills = gpt_output.model_dump().get("mandatorySkills")
                optional_skills = gpt_output.model_dump().get("optionalSkills")
                languages = gpt_output.model_dump().get("languages")
                yearsOfExperienceFrom = gpt_output.model_dump().get("yearsOfExperienceFrom")
                yearsOfExperienceTo = gpt_output.model_dump().get("yearsOfExperienceTo")
                yearsInJobFrom = gpt_output.model_dump().get("yearsInJobFrom")
                yearsInJobTo = gpt_output.model_dump().get("yearsInJobTo")
                email = gpt_output.model_dump().get("email")
                phone = gpt_output.model_dump().get("phone")
                worksAt = gpt_output.model_dump().get("worksAt")
                doesNotWorkAt = gpt_output.model_dump().get("doesNotWorkAt")
                previouslyWorkedAt = gpt_output.model_dump().get("previouslyWorkedAt")
                doesNotPreviouslyWorkAt = gpt_output.model_dump().get("doesNotPreviouslyWorkAt")
                personIs = gpt_output.model_dump().get("personIs")
                personIsNot = gpt_output.model_dump().get("personIsNot")
                previouslyWorkedAt = gpt_output.model_dump().get("previouslyWorkedAt")
                doesNotPreviouslyWorkAs = gpt_output.model_dump().get("doesNotPreviouslyWorkAs")
                personIs = gpt_output.model_dump().get("personIs")
                personIsNot = gpt_output.model_dump().get("personIsNot")
                previouslyAs = gpt_output.model_dump().get("previouslyAs")
                doesNotPreviouslyWorkAs = gpt_output.model_dump().get("doesNotPreviouslyWorkAs")
        
        
                result = boolean_query_v2(job_title, city, country, radius, mandatory_skills, optional_skills,
                                        languages, yearsOfExperienceFrom, yearsOfExperienceTo, yearsInJobFrom, yearsInJobTo,
                                        email, phone, worksAt, doesNotWorkAt, previouslyWorkedAt, doesNotPreviouslyWorkAt,
                                        personIs, personIsNot, doesNotPreviouslyWorkAs, previouslyAs)
                st.write(result)
                
 
# Decide which part of the app to display based on login status
if not st.session_state.logged_in:
    display_login_form()
else:
    display_main_app()