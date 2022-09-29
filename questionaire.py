from csv import reader
import pandas as pd
import streamlit as st
from datetime import date

'''
Admin Users taken from admins.csv file
'''
admin_data = pd.read_csv('admins.csv')
admin_users = list(admin_data.Admins.unique())

'''
Utility function to convert DataFrame
to CSV
'''
def df_to_csv(df):
    return df.to_csv().encode('utf-8')

'''
Utility function to lookup 
a particular value in a CSV
'''
def csv_lookup(csv_file, lookup_value):
    file = open(csv_file)
    for row in reader(file):
        if lookup_value in row[0]:
            return row[1]

'''
Check if a given user is an admin or not
'''
def is_admin(user_email):
    if user_email in admin_users:
        return True
    return False

'''
Build the streamlit sidebar conditionally if user is admin
'''
def build_sidebar(user_email):
    if is_admin(user_email):
        sidebar = st.sidebar.selectbox("Select", ['Questionaire', 'Admin'])
    else:
        sidebar = st.sidebar.selectbox("Select", ['Questionaire'])
    return sidebar

'''
Convert words "Negative", "Positive" or "Neutral" to image paths of 
green, red or yellow dots that can be embedded in html
'''
def path_to_image_html(word='Positive'):
    score = {'Positive': 'https://upload.wikimedia.org/wikipedia/commons/2/2d/Basic_green_dot.png',
        'Negative': 'https://upload.wikimedia.org/wikipedia/commons/0/0e/Basic_red_dot.png',
        'Neutral': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Location_dot_orange.svg/768px-Location_dot_orange.svg.png'}
    path = score[word]
    return '<img src="'+ path + '" width="30" >'

'''
Determine the overall sentiment score of a project with individual scores of
the members. Negative score has the highest weight to make sure negative
experiences are not overshadowed by majority positive experiences
'''
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

'''
Render the questions and the radio buttons in the questionaire
'''
def render_radios(disabled=False):
    questions = ["1) Team work",
                "2) Pawns or Players",
                "3) Delivery Value / Being Valued",
                "4) Speed",
                "5) Learning",
                "6) Fun"]
    smiley_response = ['No Response', 'Happy 🙂', 'Neutral 😐', 'Sad 😞']
    response_dict = {
        'No Response' : 'na',
        'Happy 🙂' : 'Positive',
        'Neutral 😐' : 'Neutral',
        'Sad 😞' : 'Negative'
    }
    response_list = []
    col1, col2 = st.columns(2)
    if not disabled:
        for i in range(len(questions)):
            if i < 3:
                with col1:
                    st.subheader(questions[i])
                    response_list.append(response_dict[st.radio("Select your response: ", smiley_response, key=i)])
            else:
                with col2:
                    st.subheader(questions[i])
                    response_list.append(response_dict[st.radio("Select your response: ", smiley_response, key=i)])
    else:
        for i in range(len(questions)):
            if i < 3:
                with col1:
                    st.subheader(questions[i])
                    response_list.append(response_dict[st.radio("Select your response: ", smiley_response, key=i, disabled=True)])
            else:
                with col2:
                    st.subheader(questions[i])
                    response_list.append(response_dict[st.radio("Select your response: ", smiley_response, key=i, disabled=True)])
    return response_list

def main_page(user_email, user_name):
    today = date.today()

    st.title("InfraCloud Squad Health Application")
    st.write('Refreshing the page will log you out')

    data = pd.read_csv('master_data.csv')
    team_data = pd.read_csv('teams.csv')
    page = build_sidebar(user_email)
    team_names = list(team_data.Team.unique())
    responses = []

    if(page == "Questionaire"):
        
        col7, col8, col10, col11 = st.columns([0.65,2,1,1])
        col7.markdown('<h4> Select your team: </h4>', unsafe_allow_html=True)
        current_team = col8.selectbox("You can add responses for multiple teams", team_names)
        col10.empty
        col11.empty
        
        if pd.to_datetime(data.Date[(data.Email == user_email)&(data.Team == current_team)]).dt.month.max() == date.today().month and pd.to_datetime(data.Date[(data.Email == user_email)&(data.Team == current_team)]).dt.year.max() == date.today().year:
            responses = render_radios(disabled=True)
        else:
            responses = render_radios()

        st.write('')
        if st.button("Save Your Response"):
            if current_team == '-':
                st.error('Please select your Team')
            elif 'na' in responses:
                st.error('Please respond to all questions')
            else:
                data = data.append({
                            'Date': today,
                            'Email': user_email,
                            'Name': user_name,
                            'Team': current_team,
                            'Team_work': responses[0],
                            'Pawns_or_Players': responses[1],
                            'Delivering_Value_Being_Valued': responses[2],
                            'Speed': responses[3],
                            'Learning': responses[4],
                            'Fun': responses[5]
                            }, ignore_index=True)
                data.to_csv('master_data.csv', index=False)
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
                rate.append(resp)
            storage[tm] = rate
            rate = []
        new_data = pd.DataFrame(storage, index=questions)
        formatted_dict = {}
        for i in new_data.columns:
            formatted_dict[i]=path_to_image_html

        st.markdown('<div style="overflow-x:auto">'+new_data.to_html(escape=False,formatters=formatted_dict)+'</div>', unsafe_allow_html=True)
        new_data_csv = df_to_csv(new_data)
        st.download_button(
            label="Download as CSV",
            data=new_data_csv,
            file_name='traffic_light.csv',
            mime='text/csv'
        )
        st.markdown('#')
        
        st.subheader('Filtered Table')
        col3, col4, col5, col6 = st.columns(4)
        with col3:
            project_filter = st.selectbox('Project', new_data.columns)
        with col4:
            st.empty
        with col5:
            st.empty
        with col6:
            st.empty
        filtered_data = data[data.Team == project_filter]
        st.markdown(filtered_data.to_html(escape=False,formatters=dict(Team_work=path_to_image_html,
                                                                       Pawns_or_Players=path_to_image_html,
                                                                       Delivering_Value_Being_Valued=path_to_image_html,
                                                                       Speed=path_to_image_html,
                                                                       Learning=path_to_image_html,
                                                                       Fun=path_to_image_html)), unsafe_allow_html=True)
        st.markdown('#')
        st.subheader('All user data')
        st.dataframe(data)
        with open('master_data.csv') as dl:
            st.download_button('Download as CSV', dl, 'data.csv', 'text/csv')
