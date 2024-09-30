"""
web app chatbot Gemini function calling
"""
import os
from dotenv import load_dotenv
import urllib
import urllib.request
import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import linregress
import matplotlib.pyplot as plt

import vertexai
from vertexai import generative_models
from google.cloud import bigquery
from vertexai.generative_models import (
    FunctionDeclaration,
    GenerativeModel,
    GenerationConfig,
    Tool,
    Part,
    SafetySetting
)

from tools import search_for_similar_records, search_for_links


#AUTHIENTICATION
# if "auth" not in st.session_state:
load_dotenv()
st.session_state.PROJECT_ID = os.getenv('PROJECT_ID')
st.session_state.LOCATION = os.getenv('LOCATION')
vertexai.init(project=st.session_state.PROJECT_ID , location=st.session_state.LOCATION)
st.session_state.bq_client = bigquery.Client(project=st.session_state.PROJECT_ID)
st.session_state.auth = True

# Functions declaration
search_for_similar_records_yaml = FunctionDeclaration(
    name="search_for_similar_records",
    description="This function takes a query as input and returns the most similar documents or links based on the provided constraints, such as file source, type, size, and date range.",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "A string representing the summarized search query for which similar records need to be found.",
            },
            "file_source": {
                "type": "string",
                "enum": ["any", "web", "google_drive", "avoma"],
                "description": "The source of the files to be searched. Acceptable values are 'web', 'google_drive', 'avoma', or 'any' (no restriction).",
                "default": "any"
            },
            "file_extension": {
                "type": "string",
                "enum": ["any", "web link", "pdf", "docx", "pptx", "xlsx"],
                "description": "The file extension type to be searched. Acceptable values are 'web link', 'pdf', 'docx', 'pptx', 'xlsx', or 'any' (no restriction).",
                "default": "any"
            },
            "file_size": {
                "type": "integer",
                "description": "The size of the file in megabytes (MB). If set to 'any', there is no restriction on file size.",
                "default": "any"
            },
            "nfiles_to_return": {
                "type": "integer",
                "description": "Number of files to return",
                "default": 10
            },
            "start_date": {
                "type": "string",
                "description": "The start date to filter the files by creation date, in the format %Y-%m-%d (e.g., 2024-01-01).",
                "default": "2024-01-01"
            },
            "end_date": {
                "type": "string",
                "description": "The end date to filter the files by creation date, in the format %Y-%m-%d (e.g., 2024-09-29).",
                "default": "2024-09-29"
            },
        },
    }
)

search_for_links_yaml = FunctionDeclaration(
    name="search_for_links",

    description="Searches for web links based on the provided query and returns the most recent result.",

    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query string.",
            }
        },
    }
)

query_tools = Tool(function_declarations=[search_for_similar_records_yaml, search_for_links_yaml])

#WEB App Interface
st.set_page_config(
    page_title="AI Agent - File Search",
    page_icon=":male-office-worker:",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.title("AI Agent - File Search")

tile = st.container(border=True)
tile.write(
"""
This is the File Search AI Agent, designed to streamline the process of locating and accessing files. 
Users can effortlessly search for documents by file name, file type, source, or specific keywords 
through a user-friendly chat interface. 
""")

tile = st.container(border=True)

with tile.expander("Sample Prompts", expanded=False):
    st.write(
        """
        - Could you find the last team meeting from january?
        - Could you pull up all the product meetings from 2024?
        - Can you find the most recent file related to Product X?
        - Can you get all the documents for Product X and Product Y that were uploaded last month?
        - Can you list all the PDFs in the Product folder on Google Drive?
        - Could you locate marketing.pdf in the Product folder on Google Drive?
        - Can you get the product files that are smaller than 1MB from Google Drive?
        - Could you share the link to our home page?
        - Retrieve 2 files on Product X.
    """
    )

#keep sessions
if "messages" not in st.session_state:
    st.session_state.messages = []

if 'gemini_history' not in st.session_state:
    st.session_state.gemini_history = []

st.session_state.model = GenerativeModel(
                            model_name="gemini-1.0-pro-002",

                            system_instruction=["You are a Query Search AI Agent designed to facilitate efficient file or link retrieval.", "Your primary tasks is to search for files or links based on queries and constraints, if any!", "Observation date starts at 2024 jaunary and ends in september 2024."
                            , "Do not respond to questions outside these tasks. Please use the provided tools to give concise and accurate answers.", "Do not hallucinate!"
                            "DO NOT MAKE UP ANY ANSWERS IF NOT PROVIDED BY THE TOOLS!"],
                            
                            generation_config=GenerationConfig(temperature=0,
                                                                top_p=0.95,
                                                                top_k=10,
                                                                candidate_count=1,
                                                                max_output_tokens=8000,
                                                                stop_sequences=["STOP!"]
                            ),
                            safety_settings=[SafetySetting(
                                                category=generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                                                threshold=generative_models.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE
                                            ),
                                            SafetySetting(
                                                category=generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                                                threshold=generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
                                            ),
                                            SafetySetting(
                                                category=generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT,
                                                threshold=generative_models.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE
                                            ),
                                            SafetySetting(
                                                category=generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                                                threshold=generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
                                            ),
                            ],
                            tools=[query_tools]
)

if 'chat' not in st.session_state:
    st.session_state.chat = st.session_state.model.start_chat(response_validation=True,
                                                            history=st.session_state.gemini_history)
def reset_conversation():
    del st.session_state.gemini_history
    del st.session_state.chat
    del st.session_state.messages

st.button(label='Reset', key='reset', on_click=reset_conversation)

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar='🧑🏻' if message['role']=='user' else '🤖'):
        st.markdown(message["content"])  # noqa: W605
        try:
            with st.expander("Function calls, parameters, and responses"):
                st.markdown(message["backend_details"])
        except KeyError:
            pass

if prompt := st.chat_input(placeholder="Ask me about file retrieval, searching for specific documents, or accessing files from various sources..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar='🧑🏻'):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar='🤖'):

        message_placeholder = st.empty()
        full_response = "" # pylint: disable=invalid-name
        response = st.session_state.chat.send_message(prompt)
        response = response.candidates[0].content.parts[0]

        backend_details = "" # pylint: disable=invalid-name
        api_requests_and_responses  = []

        function_calling_in_process = True # pylint: disable=invalid-name

        result_info = {}

        while function_calling_in_process:
            try:
                params = {}

                for key, value in response.function_call.args.items():
                    params[key] = value

                print(response.function_call.name)
                print(params)

                if response.function_call.name == "search_for_similar_records":
                    result, result_info, api_response = search_for_similar_records(**params)
                    st.write(result)
                    st.markdown("#### response")
                    st.json(result_info) 
                    api_requests_and_responses.append([response.function_call.name, params, api_response])
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": "retrieved_files",
                            "retrieved_files": result_info,
                        }
                    )

                if response.function_call.name == "search_for_links":
                    result, api_response = search_for_links(**params)
                    st.write(result)
                    st.markdown("#### response")
                    api_requests_and_responses.append([response.function_call.name, params, api_response])
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": "retrieved_files",
                            "retrieved_files": api_response,
                        }
                    )

                print(api_response)

                response = st.session_state.chat.send_message(
                    Part.from_function_response(
                        name=response.function_call.name,
                        response={
                            "role": "assistant",
                            "content": api_response,
                        },
                    ),
                )

                backend_details += "- Function call:\n"
                backend_details += (
                    "   - Function name: ```"
                    + str(api_requests_and_responses[-1][0])
                    + "```"
                )
                backend_details += "\n\n"
                backend_details += (
                    "   - Function parameters: ```"
                    + str(api_requests_and_responses[-1][1])
                    + "```"
                )
                backend_details += "\n\n"
                backend_details += (
                    "   - Function API response: ```"
                    + str(api_requests_and_responses[-1][2])
                    + "```"
                )
                backend_details += "\n\n"

                with message_placeholder.container():
                    st.markdown(backend_details)

                response = response.candidates[0].content.parts[0]
                print(f"function return: {api_response}, model_response: {response}")
            except AttributeError:
                function_calling_in_process = False # pylint: disable=invalid-name

        st.session_state.gemini_history = st.session_state.chat.history
        full_response = response.text

        with message_placeholder.container():
            # st.json(result_info)  # noqa: W605
            with st.expander("Function calls, parameters, and responses:"):
                st.markdown(backend_details)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": full_response,
            }
        )