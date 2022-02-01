import requests
import streamlit as st
import asyncio

from session_state import get
from questionaire import main_page
from httpx_oauth.clients.google import GoogleOAuth2

st.set_page_config(page_title='Squad Health', page_icon="👥", layout="wide")

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
    user_id, user_email = await client.get_id_email(token)
    return user_id, user_email

async def get_name(id_token):
    query = {'id_token': id_token}
    resposne = requests.get('https://www.googleapis.com/oauth2/v3/tokeninfo', params=query)
    user_name = resposne.json()['name']
    return user_name

def main(user_id, user_email, user_name):
    main_page(user_id, user_email, user_name)


if __name__ == '__main__':
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    redirect_uri = os.getenv('REDIRECT_URI')

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
            st.title('Infracloud Squad Health Application')
            st.subheader('Please login using your Infracloud Gmail account.')
            st.write('Link is in the sidebar')
            st.sidebar.write(f'''<h1><a target="_self" href="{authorization_url}">Login</a></h1>''', unsafe_allow_html=True)
        else:
            # Verify token is correct:
            try:
                token = asyncio.run(
                    write_access_token(client=client,
                                       redirect_uri=redirect_uri,
                                       code=code))
            except:
                st.title('Infracloud Squad Health Application')
                st.subheader('You have refreshed the page and have been logged out.')
                st.sidebar.write(f'''<h1><a target="_self" href="{authorization_url}">Login</a></h1>''', unsafe_allow_html=True)
            else:
                # Check if token has expired:
                if token.is_expired():
                    if token.is_expired():
                        st.title('Infracloud Squad Health Application')
                        st.subheader('The Session token has expired. Please login again')
                        st.sidebar.write(f'''<h1><a target="_self" href="{authorization_url}">Login</a></h1>''', unsafe_allow_html=True)
                else:
                    session_state.token = token
                    user_id, user_email = asyncio.run(
                        get_email(client=client,
                                  token=token['access_token'])
                    )
                    user_name = asyncio.run(
                        get_name(id_token=token['id_token'])
                    )
                    session_state.user_id = user_id
                    session_state.user_email = user_email
                    session_state.user_name = user_name
                    main(user_id=session_state.user_id,
                         user_email=session_state.user_email,
                         user_name=session_state.user_name)
    else:
        main(user_id=session_state.user_id,
             user_email=session_state.user_email,
             user_name=session_state.user_name)
