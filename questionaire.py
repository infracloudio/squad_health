import pandas as pd
import streamlit as st
from datetime import date
from IPython.core.display import HTML

admin_users = ['misra.runit@gmail.com']

def is_admin(user_email):
    if user_email in admin_users:
        return True
    return False

def build_sidebar(user_email):
    if is_admin(user_email):
        sidebar = st.sidebar.selectbox("Select", ['Questionaire', 'Admin'])
    else:
        sidebar = st.sidebar.selectbox("Select", ['Questionaire'])
    return sidebar

def path_to_image_html(word):
    score = {'Positive': 'https://www.pikpng.com/pngl/m/48-484473_green-dot-png-clipart.png',
        'Negative': 'https://toppng.com/uploads/preview/red-dot-icon-png-bowling-ball-transparent-background-11562953794gu3xfby6c8.png',
        'Neutral': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Location_dot_orange.svg/768px-Location_dot_orange.svg.png'}
    path = score[word]
    return '<img src="'+ path + '" width="30" >'

def main_page(user_id, user_email, user_name):
    today = date.today()

    st.title("Infracloud Squad Health Application")
    st.subheader(f"You're logged in as {user_name}, email: {user_email}")
    st.write('Refreshing the page will log you out')

    data = pd.read_csv('demo.csv')
    team_data = pd.read_csv('teams.csv')
    page = build_sidebar(user_email)

    

    if(page == "Questionaire"):
        st.subheader('Your responses so far:')
        st.dataframe(data[data.Email == user_email])
        questions = ["1) Team work",
                "2) Pawns or Players",
                "3) Delivery Value / Being Valued",
                "4) Speed",
                "5) Learning",
                "6) Fun"]

        team_names = list(team_data.Team.unique())
        current_team = st.selectbox("Select your team", team_names)
                
        response = ['Positive', 'Neutral', 'Negative']
            
        st.info(questions[0])
        q1 = st.radio("Select your response: ", response, key=0)
        #q1 = response[q1_radio]

        
        st.info(questions[1])
        q2 = st.radio("Select your response: ", response, key=1)
        #q2 = response[q2_radio]
        
        st.info(questions[2])
        q3 = st.radio("Select your response: ", response, key=2)
        #q3 = response[q3_radio]

        st.info(questions[3])
        q4 = st.radio("Select your response: ", response, key=3)
        #q3 = response[q3_radio]

        st.info(questions[4])
        q5 = st.radio("Select your response: ", response, key=4)
        #q3 = response[q3_radio]

        st.info(questions[5])
        q6 = st.radio("Select your response: ", response, key=5)
        #q3 = response[q3_radio]
        
        if(st.button("Save Your Response")):
            data = data.append({
                        'Date': today,
                        'Email': user_email,
                        'Name': user_name,
                        'Team': current_team,
                        'Team work': q1,
                        'Pawns or Players': q2,
                        'Delivery Value / Being Valued': q3,
                        'Speed': q4,
                        'Learning': q5,
                        'Fun': q6
                        }, ignore_index=True)
            data.to_csv('demo.csv', index=False)
            
            st.balloons()
            st.dataframe(data)
            st.success('Response has been recorded')

    elif(page == "Admin"):
        questions = ['Team work', 'Pawns or Players', 'Delivery Value / Being Valued', 'Speed', 'Learning', 'Fun']
        storage = {}
        rate = []
        
        teams = list(data.Team.unique())
        for tm in teams:
            for q in range(len(questions)):
                resp = data[data.Team == tm][questions[q]].mode()[0]
                rate.append(resp)
            storage[tm] = rate
            rate = []
        new_data = pd.DataFrame(storage, index=questions).T
        st.markdown(new_data.to_html(escape=False,formatters=dict(Q1=path_to_image_html, 
                                                    Q2=path_to_image_html,
                                                    Q3=path_to_image_html,
                                                    Q4=path_to_image_html,
                                                    Q5=path_to_image_html,
                                                    Q6=path_to_image_html)), unsafe_allow_html=True)
        st.dataframe(data)