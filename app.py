import requests
import streamlit as st
import asyncio
import json

from session_state import get
from questionaire import main_page
from httpx_oauth.clients.google import GoogleOAuth2

st.set_page_config(page_title='Squad Health', page_icon="👥", layout="wide")

hide_streamlit_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .css-18e3th9 {padding: 0rem 1rem 10rem;}
        h4 {padding: 2.25rem 0px 1rem;}
        </style>
        """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

async def write_authorization_url(client,
                                  redirect_uri):
    authorization_url = await client.get_authorization_url(
        redirect_uri,
        scope=["profile", "email"],
        extras_params={"access_type": "offline"},
    )
    return authorization_url


async def write_access_token(client,
                             redirect_uri,
                             code):
    token = await client.get_access_token(code, redirect_uri)
    return token


async def get_email(client,
                    token):
    _, user_email = await client.get_id_email(token)
    return user_email

async def get_name(id_token):
    query = {'id_token': id_token}
    resposne = requests.get('https://www.googleapis.com/oauth2/v3/tokeninfo', params=query)
    user_name = resposne.json()['name']
    return user_name

def get_google_creds():
    creds_file = open('google_client_creds.json')
    creds_json = json.load(creds_file)
    client_id = creds_json['web']['client_id']
    client_secret = creds_json['web']['client_secret']
    redirect_uri = creds_json['web']['redirect_uris'][2]
    return client_id, client_secret, redirect_uri

if __name__ == '__main__':
    client_id, client_secret, redirect_uri = get_google_creds()

    client = GoogleOAuth2(client_id, client_secret)
    authorization_url = asyncio.run(
        write_authorization_url(client=client,
                                redirect_uri=redirect_uri)
    )

    session_state = get(token=None)
    if session_state.token is None:
        try:
            code = st.experimental_get_query_params()['code']
        except:
            st.title('InfraCloud Squad Health Application')
            st.subheader('Please login using your InfraCloud Gmail account.')
            st.write(f'''<h1><a target="_self" href="{authorization_url}">Login</a></h1>''', unsafe_allow_html=True)
        else:
            # Verify token is correct:
            try:
                token = asyncio.run(
                    write_access_token(client=client,
                                       redirect_uri=redirect_uri,
                                       code=code))
            except:
                st.title('InfraCloud Squad Health Application')
                st.subheader('You have refreshed the page and have been logged out.')
                st.write(f'''<h1><a target="_self" href="{authorization_url}">Login</a></h1>''', unsafe_allow_html=True)
            else:
                # Check if token has expired:
                if token.is_expired():
                    if token.is_expired():
                        st.title('InfraCloud Squad Health Application')
                        st.subheader('The Session token has expired. Please login again')
                        st.sidebar.write(f'''<h1><a target="_self" href="{authorization_url}">Login</a></h1>''', unsafe_allow_html=True)
                else:
                    session_state.token = token
                    user_email = asyncio.run(
                        get_email(client=client,
                                  token=token['access_token'])
                    )
                    user_name = asyncio.run(
                        get_name(id_token=token['id_token'])
                    )
                    session_state.user_email = user_email
                    session_state.user_name = user_name
                    main_page(user_email=session_state.user_email,
                         user_name=session_state.user_name)
    else:
        main_page(user_email=session_state.user_email,
             user_name=session_state.user_name)
