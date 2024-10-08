import streamlit as st
from pandas import DataFrame
from pymysql import connect

DB_HOST = "tellmoredb.cd24ogmcy170.us-east-1.rds.amazonaws.com"
DB_USER = "admin"
DB_PASS = "2yYKKH8lUzaBvc92JUxW"
DB_PORT = "3306"
DB_NAME = "claires"
CONVO_DB_NAME = "store_questions"

CLAIRE_DEEP_PURPLE = "#553D94"
CLAIRE_MAUVE = "#D2BBFF"

st.set_page_config(
    layout = 'wide', 
    initial_sidebar_state = 'collapsed',
    page_title = 'Store Manager App',
    page_icon = 'claires-logo.svg',
)

if 'history' not in st.session_state:
    st.session_state['history'] = []

if 'display_df_and_nlr' not in st.session_state:
    st.session_state['display_df_and_nlr'] = False

if 'user_input' not in st.session_state:
    st.session_state['user_input'] = ""

def connect_to_db(db_name):
    return connect(
        host = DB_HOST,
        port = int(DB_PORT),
        user = DB_USER,
        password = DB_PASS,
        db = db_name
    )

def set_custom_css():
    custom_css = """
    <style>
        .st-emotion-cache-9aoz2h.e1vs0wn30 {
            display: flex;
            justify-content: center; /* Center-align the DataFrame */
        }
        .st-emotion-cache-9aoz2h.e1vs0wn30 table {
            margin: 0 auto; /* Center-align the table itself */
        }

        .button-container {
            display: flex;
            justify-content: flex-end; /* Align button to the right */
            margin-top: 10px;
        }

        .circular-button {
            border-radius: 50%;
            background-color: #553D94; /* Button color */
            color: white;
            border: none;
            padding: 10px 15px; /* Adjust size as needed */
            cursor: pointer;
        }

        .circular-button:hover {
            background-color: #452a7f; /* Slightly darker shade on hover */
        }
        </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def store_manager_app():
    with open(r'claires-logo.svg', 'r') as image:
        image_data = image.read()
    st.logo(image=image_data)

    store_questions = {
        "Select a query": None,
        "What is the sum of number of transactions this year compared to last year for the store VILLAGE CROSSING?": {
            "sql": "SELECT SUM(f.TransactionCountTY) AS TotalTransactionsTY, SUM(f.TransactionCountLY) AS TotalTransactionsLY FROM fact_Basket f JOIN dim_Location_Latest l ON f.LocationLatestKey = l.LocationLatestKey WHERE l.LatestLocation = 'VILLAGE CROSSING';",
            "nlr": "The data table returned indicates that the total number of transactions for the latest location of the store VILLAGE CROSSING this year is 5,285, while the number of transactions from last year is 0. This suggests that the store either did not operate last year or had no recorded transactions during that time, resulting in a significant increase in activity this year.",
            
        },
        "What are the net margins in USD for the store VILLAGE CROSSING?": {
            "sql": "SELECT f.NetExVATUSDPlan FROM Fact_Store_Plan f JOIN dim_Location_Latest l ON f.LocationLatestKey = l.LocationLatestKey WHERE l.LatestLocation = 'VILLAGE CROSSING';",
            "nlr": "The data table returned consists of a series of net margin values in USD for the store located at VILLAGE CROSSING. The values represent individual entries of net margins, with some figures appearing multiple times, indicating that there may be repeated measurements or records for certain time periods or transactions.\n\nThe margins range from a low of 0.0 USD, which suggests instances where there was no profit, to a high of 17,703.0 USD, indicating significant profitability in some cases. Most values fall within a relatively consistent range, with several margins clustered around the 6,000 to 10,000 USD mark. \n\nThis data provides a comprehensive view of the store's financial performance, highlighting both the variability and consistency in net margins over the observed period. The presence of multiple identical values suggests that certain margins were likely recorded under similar conditions or timeframes.",
        },
        "What is the net sales on July 31, 2023 compared to the same period last year for the store VILLAGE CROSSING?":
        {
            "sql": "SELECT f.NetSaleLocal, f.NetSaleLocalLY FROM fact_Sale f JOIN dim_Calendar c ON f.CalendarKey = c.CalendarKey JOIN dim_Location_Latest l ON f.LocationLatestKey = l.LocationLatestKey WHERE l.LatestLocation = 'VILLAGE CROSSING' AND c.CalendarDate = '2023-07-31';",
            "nlr": "On July 31, 2023, the net sales in USD for the latest location of the store Village Crossing were as follows: 448.98, 49.98, and 40.00. In comparison, there were no net sales recorded for the same period last year."
        },
        "What is the Daily Sales Report (DSR) using our sales records for the store VILLAGE CROSSING on July 31, 2023?": {
            "sql": "SELECT f.NetSaleLocal, f.NetSaleUSD, f.NetQuantity, c.CalendarDate FROM fact_Sale f JOIN dim_Calendar c ON f.CalendarKey = c.CalendarKey JOIN dim_Location_Latest l ON f.LocationLatestKey = l.LocationLatestKey WHERE l.LatestLocation = 'VILLAGE CROSSING' AND c.CalendarDate = '2023-07-31';",
            "nlr": "On July 31, 2023, the Daily Sales Report (DSR) for the Village Crossing store shows the following sales records: The total net sales in the local currency amounted to 448.98 USD, with a total of 82 items sold. Additionally, there were sales of 49.98 USD from 2 items and 40.00 USD from another 2 items.",
        },
        "Compare the average sales revenue for the store VILLAGE CROSSING with the average sales revenue for all stores in USA.": {
            "sql": "SELECT AVG(fs.NetSaleUSD) AS AverageSalesRevenue FROM fact_Sale fs JOIN dim_Location_Latest dl ON fs.LocationLatestKey = dl.LocationLatestKey WHERE dl.LatestLocation = 'VILLAGE CROSSING' \nGROUP BY dl.LatestCountry\nUNION\nSELECT AVG(fs.NetSaleUSD) AS AverageSalesRevenue FROM fact_Sale fs JOIN dim_Location_Latest dl ON fs.LocationLatestKey = dl.LocationLatestKey WHERE dl.LatestCountry = 'USA';",
            "nlr": "The average sales revenue for the store located at VILLAGE CROSSING is approximately 319.77, while the average sales revenue for all stores in the USA is approximately 471.99.",
        },
        "What were the sales during the 'Autumn/Winter' season for the store VILLAGE CROSSING?": {
            "sql": "SELECT dll.LatestLocation,SUM(f.NetSaleUSD) as TotalSales, d.Season, d.FiscalMonthName, d.FiscalYear \nFROM fact_Sale f JOIN dim_Calendar d ON f.CalendarKey = d.CalendarKey JOIN dim_Location_Latest dll ON f.LocationLatestKey =dll.LocationLatestKey WHERE d.Season = 'Autumn/Winter' AND f.LocationLatestKey = (SELECT LocationLatestKey FROM dim_Location_Latest dll WHERE dll.LatestLocation = 'VILLAGE CROSSING') GROUP BY d.FiscalMonthName, d.FiscalYear ORDER BY d.FiscalYear DESC, d.FiscalMonthName;",
            "nlr": "The sales during the 'Autumn/Winter' season for the store located at VILLAGE CROSSING were as follows: In August 2023, the sales totaled 1,235.49 USD; in December 2022, the sales amounted to 29,932.37 USD; and in January 2022, the sales were 18,783.33 USD.",
        },
        "What is the average number of units sold per transaction at the store VILLAGE CROSSING?": {
            "sql": "SELECT AVG(f.TransactionCountTY) AS AverageUnitsSold FROM fact_Basket f\nJOIN dim_Location_Latest d ON f.LocationLatestKey = d.LocationLatestKey\nWHERE d.LatestLocation = 'VILLAGE CROSSING';",
            "nlr": "The average number of units sold per transaction at the latest location of store VILLAGE CROSSING is approximately 22.78.",
        },
    }

    if 'queries' not in st.session_state:
        st.session_state['queries'] = {}

    st.markdown(f"""
    <h4 style="background-color: {CLAIRE_DEEP_PURPLE}; color: white; padding: 10px;">
        STORE MANAGER
    </h4>
    """, unsafe_allow_html=True)

    store_name_id_placeholder = st.markdown(f"""
    <h4 style="background-color: {CLAIRE_MAUVE}; color: black; padding: 10px;">
    </h4>
    """, unsafe_allow_html=True)

    st.markdown("""
        <style>
        div.stButton {
            display: flex;
            justify-content: flex-end; /* Align button to the right */
            font-size: 30px; /* Increase font size */
            margin-top: 10px;
        }
        </style>
        """, unsafe_allow_html=True)

    store_name_id_placeholder.markdown(f"""
    <h4 style="background-color: {CLAIRE_MAUVE}; color: black; padding: 10px;">
        VILLAGE CROSSING
    </h4>
    """, unsafe_allow_html=True)

    query_options = list(store_questions.keys())
    selected_query = st.selectbox("Select a query", query_options if query_options else ["Select a query"])

    if selected_query and selected_query != "Select a query":
        sql_query = store_questions[selected_query]["sql"]
        conn = connect_to_db(DB_NAME)
        cur = conn.cursor()
        cur.execute(sql_query)
        getDataTable = cur.fetchall()
        columns = [column[0] for column in cur.description]
        getDataTable = DataFrame(getDataTable, columns=columns)

        # st.dataframe(getDataTable)

        nlr = store_questions[selected_query]["nlr"]
        st.write(nlr)

# Main Application
set_custom_css()

# Load the STORE MANAGER app directly without sidebar or toggle
store_manager_app()
