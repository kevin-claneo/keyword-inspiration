import streamlit
import praw
import csv
import pandas as pd
import base64

from http.client import HTTPSConnection
from base64 import b64encode
from json import loads, dumps

LANGUAGES = ["Afrikaans","Albanian","Amharic","Arabic","Armenian","Azerbaijani","Basque","Belarusian","Bengali","Bosnian","Bulgarian","Catalan","Cebuano","Chinese (Simplified)","Chinese (Traditional)","Corsican","Croatian","Czech","Danish","Dutch","English","Esperanto","Estonian","Finnish","French","Frisian","Galician","Georgian","German","Greek","Gujarati","Haitian Creole","Hausa","Hawaiian","Hebrew","Hindi","Hmong","Hungarian","Icelandic","Igbo","Indonesian","Irish","Italian","Japanese","Javanese","Kannada","Kazakh","Khmer","Kinyarwanda","Korean","Kurdish","Kyrgyz","Lao","Latvian","Lithuanian","Luxembourgish","Macedonian","Malagasy","Malay","Malayalam","Maltese","Maori","Marathi","Mongolian","Myanmar (Burmese)","Nepali","Norwegian","Nyanja (Chichewa)","Odia (Oriya)","Pashto","Persian","Polish","Portuguese (Portugal","Punjabi","Romanian","Russian","Samoan","Scots Gaelic","Serbian","Sesotho","Shona","Sindhi","Sinhala (Sinhalese)","Slovak","Slovenian","Somali","Spanish","Sundanese","Swahili","Swedish","Tagalog (Filipino)","Tajik","Tamil","Tatar","Telugu","Thai","Turkish","Turkmen","Ukrainian","Urdu","Uyghur","Uzbek","Vietnamese","Welsh","Xhosa","Yiddish","Yoruba","Zulu"]
COUNTRIES = ["Afghanistan", "Albania", "Antarctica", "Algeria", "American Samoa", "Andorra", "Angola", "Antigua and Barbuda", "Azerbaijan", "Argentina", "Australia", "Austria", "The Bahamas", "Bahrain", "Bangladesh", "Armenia", "Barbados", "Belgium", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Belize", "Solomon Islands", "Brunei", "Bulgaria", "Myanmar (Burma)", "Burundi", "Cambodia", "Cameroon", "Canada", "Cape Verde", "Central African Republic", "Sri Lanka", "Chad", "Chile", "China", "Christmas Island", "Cocos (Keeling) Islands", "Colombia", "Comoros", "Republic of the Congo", "Democratic Republic of the Congo", "Cook Islands", "Costa Rica", "Croatia", "Cyprus", "Czechia", "Benin", "Denmark", "Dominica", "Dominican Republic", "Ecuador", "El Salvador", "Equatorial Guinea", "Ethiopia", "Eritrea", "Estonia", "South Georgia and the South Sandwich Islands", "Fiji", "Finland", "France", "French Polynesia", "French Southern and Antarctic Lands", "Djibouti", "Gabon", "Georgia", "The Gambia", "Germany", "Ghana", "Kiribati", "Greece", "Grenada", "Guam", "Guatemala", "Guinea", "Guyana", "Haiti", "Heard Island and McDonald Islands", "Vatican City", "Honduras", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Israel", "Italy", "Jamaica", "Japan", "Kazakhstan", "Jordan", "Kenya", "South Korea", "Kuwait", "Kyrgyzstan", "Laos", "Lebanon", "Lesotho", "Latvia", "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Mauritania", "Mauritius", "Mexico", "Monaco", "Mongolia", "Moldova", "Montenegro", "Morocco", "Mozambique", "Oman", "Namibia", "Nauru", "Nepal", "Netherlands", "Curacao", "Sint Maarten", "Caribbean Netherlands", "New Caledonia", "Vanuatu", "New Zealand", "Nicaragua", "Niger", "Nigeria", "Niue", "Norfolk Island", "Norway", "Northern Mariana Islands", "United States Minor Outlying Islands", "Federated States of Micronesia", "Marshall Islands", "Palau", "Pakistan", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Pitcairn Islands", "Poland", "Portugal", "Guinea-Bissau", "Timor-Leste", "Qatar", "Romania", "Rwanda", "Saint Helena, Ascension and Tristan da Cunha", "Saint Kitts and Nevis", "Saint Lucia", "Saint Pierre and Miquelon", "Saint Vincent and the Grenadines", "San Marino", "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Vietnam", "Slovenia", "Somalia", "South Africa", "Zimbabwe", "Spain", "Suriname", "Eswatini", "Sweden", "Switzerland", "Tajikistan", "Thailand", "Togo", "Tokelau", "Tonga", "Trinidad and Tobago", "United Arab Emirates", "Tunisia", "Turkey", "Turkmenistan", "Tuvalu", "Uganda", "Ukraine", "North Macedonia", "Egypt", "United Kingdom", "Guernsey", "Jersey", "Tanzania", "United States", "Burkina Faso", "Uruguay", "Uzbekistan", "Venezuela", "Wallis and Futuna", "Samoa", "Yemen", "Zambia"]
DEVICES = ["mobile", "desktop"]

# -------------
# Variables
# -------------

preferred_countries = ["Germany", "Austria", "Switzerland", "United Kingdom", "United States", "France", "Italy", "Netherlands"]
preferred_languages = ["German", "English", "French", "Italian", "Dutch"]

class RestClient:
    domain = "api.dataforseo.com"

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def request(self, path, method, data=None):
        connection = HTTPSConnection(self.domain)
        try:
            base64_bytes = b64encode(
                ("%s:%s" % (self.username, self.password)).encode("ascii")
                ).decode("ascii")
            headers = {'Authorization' : 'Basic %s' %  base64_bytes, 'Content-Encoding' : 'gzip'}
            connection.request(method, path, headers=headers, body=data)
            response = connection.getresponse()
            return loads(response.read().decode())
        finally:
            connection.close()

    def get(self, path):
        return self.request(path, 'GET')

    def post(self, path, data):
        if isinstance(data, str):
            data_str = data
        else:
            data_str = dumps(data)
        return self.request(path, 'POST', data_str)


# -------------
# Streamlit App Configuration
# -------------

st.set_page_config(
    page_title="Keyword Inspiration",
    page_icon=":mag:",
    layout="wide",
    menu_items={
        'Get Help': 'https://www.linkedin.com/in/kirchhoff-kevin/',
        'About': "This is an app for keyword inspiration"
    }
)

def setup_streamlit():
    st.image("https://www.claneo.com/wp-content/uploads/Element-4.svg", width=600, use_column_width=None, clamp=False, channels="RGB", output_format="auto")
    st.caption("👋 Developed by [Kevin](https://www.linkedin.com/in/kirchhoff-kevin/)") 
    st.title("Get Keyword Inspiration")
    st.divider()

def custom_sort(all_items, preferred_items):
  sorted_items = preferred_items + ["_____________"] + [item for item in all_items if item not in preferred_items]
  return sorted_items

def show_dataframe(report):
  """
  Shows a preview of the first 100 rows of the report DataFrame in an expandable section.
  """
  with st.expander("Preview the First 100 Rows"):
      st.dataframe(report.head(100))
    
def add_questions_from_listing(subreddit, listing, limit, questions):
    for submission in listing(limit=limit):
        if submission.title.endswith('?'):
            questions.add(submission.title
                          
def scrape_subreddit(subreddit, limit=1000):
    questions = set()
    add_questions_from_listing(subreddit, reddit.subreddit(subreddit).new, limit, questions)
    add_questions_from_listing(subreddit, reddit.subreddit(subreddit).hot, limit, questions)
    add_questions_from_listing(subreddit, reddit.subreddit(subreddit).top, limit, questions)
    add_questions_from_listing(subreddit, reddit.subreddit(subreddit).controversial, limit, questions)
    return questions

def scrape_multiple_subreddits_to_single_file(input_filename, output_filename, limit=1000):
    all_questions = set()
    with open(input_filename, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            subreddit = row[0]
            print(f"Scraping subreddit: {subreddit}")
            questions = scrape_subreddit(subreddit, limit)
            all_questions.update(questions)

    with open(output_filename, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['Question'])
        writer.writerows([[q] for q in all_questions])

def main():
  setup_streamlit()
  username = st.text_input("👤 DataforSEO API Login", help="Get your login credentials here: https://app.dataforseo.com/api-dashboard")
  password = st.text_input("🔑 DataforSEO API Password", type="password")
    # Reddit API credentials
  client_id = st.text_input("👤 Reddit Client ID", help="Get your login credentials here: https://developers.reddit.com/")
  client_secret = st.text_input("🔑 Reddit Client Secret", type="password")
  user_agent = st.text_input("👤 Reddit Client ID", help="Get your login credentials here: https://developers.reddit.com/")
  if username and password is not None:
      client = RestClient(str(username), str(password))
      # Initialize PRAW with your credentials
      reddit = praw.Reddit(client_id=client_id, client_secret=client_secret,user_agent=user_agent)
      # Upload Excel file
      uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])
      sorted_countries = custom_sort(COUNTRIES, preferred_countries)
      sorted_languages = custom_sort(LANGUAGES, preferred_languages)
    
      country = st.selectbox("Country", sorted_countries)
      language = st.selectbox("Language", sorted_languages)
      device = st.selectbox("Device", DEVICES)
    
      if uploaded_file is not None:
          # Read Excel file into a DataFrame
          df = pd.read_excel(uploaded_file)
          df.rename(columns={"Search term": "Keyword", "keyword": "Keyword", "query": "Keyword", "query": "Keyword", "Top queries": "Keyword", "queries": "Keyword", "Keywords": "Keyword","keywords": "Keyword", "Search terms report": "Keyword"}, inplace=True)
          # Check if the 'Keyword' column exists
          if 'Keyword' not in df.columns:
              st.error("Please make sure your Excel file contains a column named 'Keyword'!")
          else:
              # Input domain and competitors
              domain = st.text_input("Enter your domain")
              num_competitors = st.number_input("Enter the number of competitors", min_value=1, value=1, step=1)
    
              competitors = []
              for i in range(num_competitors):
                  competitor = st.text_input(f"Enter competitor {i+1}")
                  competitors.append(competitor)
              
    
              if st.button("Get Keyword Data"):
                  # Get search volume
                  chunks = chunk_dataframe(df)
                  all_sv_results = pd.DataFrame()
                  all_sv_errors = []
    
                  for chunk in chunks:
                      sv_results, sv_errors = get_search_volume(chunk, client, country, language, device)
                      all_sv_results = pd.concat([all_sv_results, sv_results])
                      all_sv_errors.extend(sv_errors)
                  
                  sv = pd.DataFrame(all_sv_results)
    
                  # Get ranking positions
                  results, errors = get_ranking_positions(client, sv, country, language, device)
    
                  # Process SERP results
                  report_df, serp_df = process_serp_results(results, sv, domain, competitors)
                  
                  # Display the results
                  st.subheader("Report")
                  show_dataframe(report_df)
                  download_excel_link(report_df, "keyword_analysis_results")
                  
                  top10serp_df = transpose_serp_results(serp_df)
    
                  st.subheader("Top 10 SERP Data")
                  show_dataframe(top10serp_df)
                  download_excel_link(top10serp_df, "top-10_serp_data")

if __name__ == "__main__":
        main()
