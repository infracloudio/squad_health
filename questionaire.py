import pandas as pd
import streamlit as st
from datetime import date

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
    score = {'Positive': 'https://upload.wikimedia.org/wikipedia/commons/2/2d/Basic_green_dot.png',
        'Negative': 'https://upload.wikimedia.org/wikipedia/commons/0/0e/Basic_red_dot.png',
        'Neutral': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Location_dot_orange.svg/768px-Location_dot_orange.svg.png'}
    path = score[word]
    return '<img src="'+ path + '" width="30" >'

def score(data, question):
    
    all_rates = list(data[question])
    neu = all_rates.count('Neutral')
    neg = all_rates.count('Negative')
    pos = all_rates.count('Positive')
    
    if (neg != 0) & (not 'Neutral' in all_rates) & (not 'Positive' in all_rates):
        return 'Negative'
    elif (pos != 0) & (not 'Neutral' in all_rates) & (not 'Negative' in all_rates):
        return 'Positive'
    elif (neu != 0) & (not 'Positive' in all_rates) & (not 'Negative' in all_rates):
        return 'Neutral'
    elif (neu > pos) & ('Negative' in all_rates):
        return 'Negative'
    elif (neu < pos) & ('Negative' in all_rates):
        return 'Neutral'
    elif (neu > pos) & (not 'Negative' in all_rates):
        return 'Neutral'
    elif (neu < pos) & (not 'Negative' in all_rates):
        return 'Positive'
    elif (neu == pos) & ('Negative' in all_rates):
        return 'Neutral'
    elif (neu == pos) & (not 'Negative' in all_rates):
        return 'Neutral'
    elif (neg == pos):
        return 'Neutral'

def main_page(user_email, user_name):
    today = date.today()

    st.title("Infracloud Squad Health Application")
    st.write('Refreshing the page will log you out')

    data = pd.read_csv('demo.csv')
    team_data = pd.read_csv('teams.csv')
    page = build_sidebar(user_email)

    

    if(page == "Questionaire"):
        questions = ["1) Team work",
                "2) Pawns or Players",
                "3) Delivery Value / Being Valued",
                "4) Speed",
                "5) Learning",
                "6) Fun"]

        team_names = list(team_data.Team.unique())
        st.write('<h3> Select your team: </h3>', unsafe_allow_html=True)
        current_team = st.selectbox("You can add responses for multiple teams", team_names)
                
        response = ['Positive', 'Neutral', 'Negative']
        
        col1, col2 = st.columns(2)

        with col1:
            st.subheader(questions[0])
            q1 = st.radio("Select your response: ", response, key=0)
            #q1 = response[q1_radio]

            
            st.subheader(questions[1])
            q2 = st.radio("Select your response: ", response, key=1)
            #q2 = response[q2_radio]
            
            st.subheader(questions[2])
            q3 = st.radio("Select your response: ", response, key=2)
            #q3 = response[q3_radio]

        with col2:
            st.subheader(questions[3])
            q4 = st.radio("Select your response: ", response, key=3)
            #q3 = response[q3_radio]

            st.subheader(questions[4])
            q5 = st.radio("Select your response: ", response, key=4)
            #q3 = response[q3_radio]

            st.subheader(questions[5])
            q6 = st.radio("Select your response: ", response, key=5)
            #q3 = response[q3_radio]
        
        st.write('')
        if(st.button("Save Your Response")):
            if(not data[(data.Email == user_email)&(data.Team == current_team)].empty):
                st.error('Data Already Exists !!')
            else:
                data = data.append({
                            'Date': today,
                            'Email': user_email,
                            'Name': user_name,
                            'Team': current_team,
                            'Team_work': q1,
                            'Pawns_or_Players': q2,
                            'Delivering_Value_Being_Valued': q3,
                            'Speed': q4,
                            'Learning': q5,
                            'Fun': q6
                            }, ignore_index=True)
                data.to_csv('demo.csv', index=False)
                
                st.success('Response has been recorded')
                st.subheader('Your responses so far:')
                st.dataframe(data[data.Email == user_email])


    elif(page == "Admin"):
        questions = ['Team_work', 'Pawns_or_Players', 'Delivering_Value_Being_Valued', 'Speed', 'Learning', 'Fun']
        storage = {}
        rate = []
        
        teams = list(data.Team.unique())
        for tm in teams:
            for q in range(len(questions)):
                resp = score(data[data.Team == tm], questions[q])
                # resp = data[data.Team == tm][questions[q]].mode()[0]
                rate.append(resp)
            storage[tm] = rate
            rate = []
        new_data = pd.DataFrame(storage, index=questions).T        
        st.subheader('Traffic light view')
        st.markdown(new_data.to_html(escape=False,formatters=dict(Team_work=path_to_image_html, 
                                                    Pawns_or_Players=path_to_image_html,
                                                    Delivering_Value_Being_Valued=path_to_image_html,
                                                    Speed=path_to_image_html,
                                                    Learning=path_to_image_html,
                                                    Fun=path_to_image_html)), unsafe_allow_html=True)
        st.markdown('#')
        st.subheader('All user data')
        st.dataframe(data)
        with open('demo.csv') as dl:
            st.download_button('Download data as CSV', dl, 'data.csv', 'text/csv')