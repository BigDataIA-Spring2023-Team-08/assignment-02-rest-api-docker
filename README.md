[![fastapi-test-ci](https://github.com/BigDataIA-Spring2023-Team-08/assignment-02-rest-api-docker/actions/workflows/fastapi-test.yml/badge.svg)](https://github.com/BigDataIA-Spring2023-Team-08/assignment-02-rest-api-docker/actions/workflows/fastapi-test.yml)

# assignment-02-rest-api-docker

# Building a API for Satellite Data Exploration Tool for Geospatial Startups: Utilizing NOAA's NexRad and GOES Satellite Data Sources
-----

> ✅ Active status <br>
> [🔗 Application link](https://satellite-data-team-08.streamlit.app/) <br>
> [🎬 Codelab Slides](https://codelabs-preview.appspot.com/?file_id=1rG9fxVZ4SBsdXiCKXDtpCvfvNyWXzKivUAqlXrMw5L8#2)


----- 

## Index
  - [Abstract 📝](#abstract)
  - [Architecture Diagram](#architecture-diagram)
  - [Data Sources 💽](#data-sources)
  - [Scraping Data and Copying to AWS S3 bucket🧊](#scraping-data-and-copying-to-aws-s3-bucket)
  - [SQLite DB 🛢](#sqlite-db)
  - [Fast API ⚡️](#fast-api)  
  - [Streamlit UI 🖥️](#streamlit)
  - [Storing logs to AWS CloudWatch 💾](#storing-logs-to-aws-cloudwatch)
  - [Unit Testing ⚒️](#unit-testing)
  - [Great Expectations ☑️](#great-expectations)




## Abstract
The task involves decoupling the client and server from our data exploration tool and to host a private streamlit client
This work can help one: 

- Access the publicly available SEVIR satellite radar data in a highly interactive & quick way
- Scrap the data from public AWS S3 buckets to store them into a personal S3 bucket making it convenient to then perform additional tasks or use these saved files from your personal bucket. Government’s public data can always be hard to navigate across but we make it easy with our application
- Get files through the application by 2 options: searching by fields or directly entering a filename to get the URL from the source
- View the map plot of all the NEXRAD satellite locations in the USA
.

The application site for the project hosted on streamlit cloud can be accessed [here](https://satellite-data-team-08.streamlit.app/).

## Architecture Diagram
This architecture diagram depicts the flow of the application and the relationships between services.
![Architecure Diagram](architectural_diagram_for_assignment_2.png)

## Data Sources
The National Oceanic and Atmospheric Administration (NOAA) is a government agency responsible for monitoring the weather and climate of the United States. It operates two types of satellites, the [Geostationary Operational Environmental Satellite (GOES)](https://www.goes.noaa.gov) and the [Next Generation Weather Radar (NexRad)](https://www.ncei.noaa.gov/products/radar/next-generation-weather-radar) , which collect data on various meteorological phenomena. This data is then made publicly available through the NOAA website, allowing data analysts to easily access it. We have aimed to build a data exploration tool that leverages these publicly available data sources to simplify the process of downloading and analyzing the data.

## Scraping Data and Copying to AWS S3 bucket
Data scraping for the data sources is done from the publicly accessible AWS S3 bucket for eac - [GOES (provided by NOAA)](https://registry.opendata.aws/noaa-goes/) & [NEXRAD data registry](https://registry.opendata.aws/noaa-nexrad/). For the purpose of our application, we restrict our data to [GOES-18 data](https://noaa-goes18.s3.amazonaws.com/index.html) and [NEXRAD level 2](https://noaa-nexrad-level2.s3.amazonaws.com/index.html) buckets respectively. Within this, the data for our prototype application is further restricted (mentioned below). The third data source needed for this application is the latitude, longitudes and state information for all NEXRAD satellites in the US. This scraping is done from a [.txt file](https://www.ncei.noaa.gov/access/homr/file/nexrad-stations.txt) found on NOAA’s data registry. The final sources where data is scraped from: 

- Product `ABI-L1b-RadC/` within GOES-18
- Years `2022` and `2023` for NEXRAD
- NEXRAD satellite’s geographical locations

### Set up AWS account & credential variables:
Scraping of data from these sources is done using the `boto3` python library which allows you to connect to AWS resources using your credentials. After creating a free AWS account, one needs to store their `AWS_ACCESS_KEY` & `AWS_SECRET_KEY` in their local `.env` configuration file in order to access these keys while executing the code.

### Executing code to scrape all data:
Only the `scraper_main.py` script needs to be executed to perform scraping & storing scraped data into the SQLite database. This script calls the 3 data scraper function for the 3 data sources defined above: `scraper_goes18.py, scraper_nexrad.py, scraper_mapdata.py`.
The two scripts scripts `scraper_goes18.py` & `scraper_nexrad.py` access the relevant S3 bucket and return the data as a dataframe. Similarly, the `scraper_mapdata.py` function returns the data scraped from the txt file. 

At the end, the `scraper_main.py` script calls the `store_scraped_data_to_db` function to store this scraped metadata in the relevant tables within our SQLite database.

## SQLite DB
After the metadata is scraped and stored as dataframes each corresponding to GOES18, NexRad and NexRad location maps, we first check if the database exists and initialize it if there is no database. This creates a `.db` file. Once a connection to the database is established, SQL queries are made to create tables to store the scraped data (GOES, NexRad and  NexRad location maps) in the [SQLite](https://www.sqlite.org/index.html) database. These create tables statements can be found in `sql_script_goes18.sql, sql_script_nexrad.sql, sql_script_mapdata.sql` files. The tables are named `GOES_METADATA, NEXRAD_METADATA and MAPDATA_NEXRAD`. 

After populating these, the SQLite database is further used throughout our application to query field values when the user is on the search by fields page on the streamlit UI. In order to enable the users to dynamically get relevant fields selection box options in search by field criteria on UI, they should be presented with the values based on their selection. This is done in the backend through SQL queries to the database to fetch data depending on the user’s selections dynamically. These queries can be found in the `query_metadata_database.py` script. 

The NexRad map plot page on the streamlit UI queries all data from the `MAPDATA_NEXRAD` table in the SQLite database. The query pertaining to this is also present in the `query_metadata_database.py` script.

## Fast API


## Streamlit
The data exploration tool for the Geospatial startup uses the Python library [Streamlit](https://streamlit.iohttps://streamlit.io) for its user interface. The tool offers a user-friendly experience with three distinct pages, each dedicated to NexRad, GOES, and NexRad location maps. On each page, users can choose between downloading satellite data based on filename or specific field criteria. The UI then displays a download link to the S3 bucket, enabling users to successfully retrieve the desired satellite images.

### Streamlit UI layout:

  - Login/ Signup Functionality
    - Login page for returning users to enter username and password to get access to the data exploration application
    - Signup page for new users to enter name, username, password and confirm password to access the application
  - Logout
    - Logout users to end session and return to Login/ Signup page
  - GOES18 data downloader page
      - Download file by entering field values
      - Get public URL by entering filename
  - NEXRAD data downloaded page
      - Download file by entering field values
      - Get public URL by entering filename
  - NEXRAD Maps Location page

### Flow for Download file by entering field values
1. Enter text box fields for each value (for example, in GOES18 it is year, day & hour)
2. Once these initial selections are made, dynamically list the files available at the folder with the selections given 
3. Choose a file from the list to download it via a URL

### Flow for Get public URL by entering filename
1. Enter a filename (along with the file extension, if any) and hit enter
2. If found, the URL from the public bucket is shown, else a relevant error/warning is given 

### Flow for NEXRAD Maps Location page
1. Displays a map of all satellite locations with hover text for all points

### Steps to run application:
1. Install Streamlit package

```
pip install streamlit
```

2. Create a new file [streamlit_app.py](streamlit_app.py) to build a UI for the app. Code snippet for main function, depicting 3 different pages for GOES, NEXRAD and NEXRAD locations Map:
```
def main():
    st.set_page_config(page_title="Weather Data Files", layout="wide")
    page = st.sidebar.selectbox("Select a page", ["GOES-18", "NEXRAD", "NEXRAD Locations - Map"])   #main options of streamlit app

    if page == "GOES-18":
        with st.spinner("Loading..."): #spinner element
            goes_main()
    elif page == "NEXRAD":
        with st.spinner("Loading..."): #spinner element
            nexrad_main()
    elif page == "NEXRAD Locations - Map":
        with st.spinner("Generating map..."): #spinner element
            map_main()

```
3. Run the code
```
streamlit run streamlit_app.py
```

### Deploying the streamlit application 

In order to make our application publicly accessible without the users needing to do any setup, we have deployed our application on Streamlit Cloud. [Streamlit Cloud](https://streamlit.io/cloud) allows you to deploy your hosted application in one click, it directly uses the code from GitHub and thus enables to have instant code changed reflected in the running deployed application. 

After signing in to streamlit cloud using GitHub sign in (recommended way, or else you needed to link your GitHub after creating an accounting) you can easily add a new application. When doing this, all it asks is the repository link and the file name which contains the stream code. In our case, this is the `streamlit_app.py` file. To successfully use the environment variables (aka secrets) defined in the .env configuration file in this hosted application, we use the secrets option. Before deploying the application, go to the advanced settings and in secrets paste in the contents of the .env configuration file. Only one change needs to be done, the values need to be enclosed within quotations `“ “` now. Then click save and deploy the application. The streamlit application is now live! 


## Storing logs to AWS CloudWatch
Logging is an essential part of any code/application. It gives us details about code functioning and can be helpful while testing out the code. Not only this, logging user level actions also gives an idea about what actions are being performed both in the UI as well as the functions being executed in our backend. We implement logs using AWS CloudWatch. 

### Set up for logging to AWS CloudWatch:

For this, you need to set up an IAM AWS user with a policy attached for full access to logs. After this, generate your credentials as previously done for the boto3 client and store these logging credentials in the .env configuration file as AWS_LOG_ACCESS_KEY and AWS_LOG_SECRET_KEY. Initialize this client using boto3 as follows: 

```
#authenticate S3 client for logging with your user credentials that are stored in your .env config file
clientLogs = boto3.client('logs',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_LOG_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_LOG_SECRET_KEY')
                        )
```

After this, we create a log group within CloudWatch and 4 different log streams as follows:

- `db-logs`: to store logs of all activity related to the database. For example, scraping data & storing on database tables
- `s3-bucket-logs`: logs for s3 bucket activity, that is when you successfully copying file from public s3 bucket to personal bucket
- `user-input-logs`: logs the pages user opens while running our application, or when filename format is invalid or when a user selects a particular file for download
- `test-logs`: logs related to execution of testing code

### Incorporating logs into your code: 

Logging is just like storing a print statement into your log with a timestamp. Timestamp is crucial to know what happens when. The text that is logged depends on what we wish to display in the log. A thing to take care of is we need to always define the log stream as well so that we rightly log things based on the category of action. All of this is simply achieved through the `boto3` client we initialized for logs above by using the `put_log_events()` function in `boto3`. Necessary log code blocks have been added throughout our python files to enable logging. 

```
clientLogs.put_log_events(      #logging to AWS CloudWatch logs
        logGroupName = "assignment01-logs",   #log group name
        logStreamName = "db-logs",    #log stream name
        logEvents = [
            {
            'timestamp' : int(time.time() * 1e3),   #timestmp value
            'message' : "User opened NEXRAD Locations - Map page"    #message of the log
            }
        ]
    )
```

The logs can be viewed by opening your AWS management console and going to CloudWatch under which on the left you will find log groups and within these you will find your log streams. Clicking on each log stream will show the logs captured along with time time stamp.

## Unit Testing
[PyTest](https://docs.pytest.org/en/7.1.x/contents.html) framework implemented to write tests which is easy to use but can be scaled to support functional testing for applications and libraries.

### Steps:
1. Install PyTest package
```
pip3 install pytest

#For HTML PyTest Report, Install package:
pip3 install pytest-html
```

2. Create Tests
* Create a new file [test.py](test.py), containing test functions
* Implemented testing functions `test_gen_goes_url(), test_gen_nexrad_url()` that tests functions `generate_goes_url(filename), generate_nexrad_url(filename)` which takes goes and nexrad filenames to generate respective urls.

```
# Code snippet for test functions

def test_gen_goes_url():
    assert generate_goes_url(fileGOES1) == urlGOES1
def test_gen_nexrad_url():
    assert generate_nexrad_url(fileNEXRAD1) == urlNEXRAD1
    
```
3. Run tests
```
pytest -v test.py
```
4. Export test result to log or html file
```
# Export to log file
pytest -v test.py > test_results.log

# Export to html file 
pytest --html=test_results.html test.py
```

## Great Expectations
[Great Expectations](https://docs.greatexpectations.io/docs/) is a tool used to validate, document and profile data in order to eliminate pipeline debt. 
- The python library has been used with Amazon Web Services (AWS) using S3 and Pandas to validate,document and generate reports for GOES18 and NEXRAD data stored in s3 bucket.
- Great Expectation Checkpoints are executed in Apache Airflow by triggering validation of data asset using expectations suite directly within an Airflow DAG

### Steps

**Part 1. Setup**

1.1. Verify AWS CLI 
```
aws --version
```
1.2. Verify AWS credentials
```
aws sts get-caller-identity
```

1.3. Install Great_Expectation module
```
pip3 install great_expectations
```
1.4. Verify version
```
great_expectations --version
```
output:`great_expectations, version 0.15.50`

1.5. Install boto3
```
python3 -m pip install boto3
```

1.6. Create Data Context
```
great_expectations init
```

1.7 Configure Expectations and Validations Store on Amazon S3

file-contents: `great_expectations.yml`

```
stores:
  expectations_S3_store:
      class_name: ExpectationsStore
      store_backend:
          class_name: TupleS3StoreBackend
          bucket: '<your_s3_bucket_name>'
          prefix: '<your_s3_bucket_folder_name>'
```

```
expectations_store_name: expectations_S3_store
```

```
stores:
  validations_S3_store:
      class_name: ValidationsStore
      store_backend:
          class_name: TupleS3StoreBackend
          bucket: '<your_s3_bucket_name>'
          prefix: '<your_s3_bucket_folder_name>'
```

```
validations_store_name: validations_S3_store
```
  1.7.1 Verify Amazon S3 Expectations Stores
  
  `Command`
  ```
  great_expectations store list
  ```
  
  `Output`
  ```
  - name: expectations_S3_store
  class_name: ExpectationsStore
  store_backend:
    class_name: TupleS3StoreBackend
    bucket: '<your_s3_bucket_name>'
    prefix: '<your_s3_bucket_folder_name>'
  ```
  
  ```
  - name: validations_S3_store
  class_name: ValidationsStore
  store_backend:
    class_name: TupleS3StoreBackend
    bucket: '<your_s3_bucket_name>'
    prefix: '<your_s3_bucket_folder_name>'
  ```
1.8 Add Amazon S3 site to Data_Docs_Site Section
`great-expectations.yml`
```
  s3_site:  # this is a user-selected name - you may select your own
    class_name: SiteBuilder
    store_backend:
      class_name: TupleS3StoreBackend
      bucket: data-docs.my_org  # UPDATE the bucket name here to match the bucket you configured above.
    site_index_builder:
      class_name: DefaultSiteIndexBuilder
      show_cta_footer: true
```
  1.8.1 Test Data Docs Configuration
  `Command`
  ```
  great_expectations docs build --site-name s3_site
  ```
  
  `Output`
  ```
  The following Data Docs sites will be built:

 - s3_site: https://s3.amazonaws.com/<your_s3_bucket_name>/<your_s3_bucket_folder_name>/index.html

Would you like to proceed? [Y/n]:Y
  ```
  ```
  Building Data Docs...

  Done building Data Docs
  ```

**2. Connect to Data**

Configured datasources in order to connect to `GOES18` and `NEXRAD` data in S3 Bucket.

2.1. Create datasource with CLI

```
great_expectations datasource new
```

2.2 Instantiate Project's Data Context
```
from ruamel import yaml

import great_expectations as gx
from great_expectations.core.batch import Batch, BatchRequest, RuntimeBatchRequest
context = gx.get_context()
```

2.3 Configure Datasource
```
datasource_config = {
    "name": "my_s3_datasource",
    "class_name": "Datasource",
    "execution_engine": {"class_name": "PandasExecutionEngine"},
    "data_connectors": {
        "default_runtime_data_connector_name": {
            "class_name": "RuntimeDataConnector",
            "batch_identifiers": ["default_identifier_name"],
        },
        "default_inferred_data_connector_name": {
            "class_name": "InferredAssetS3DataConnector",
            "bucket": "<your_s3_bucket_name>",
            "prefix": "<your_s3_bucket_folder_name>",
            "default_regex": {
                "pattern": "(.*)\\.csv",
                "group_names": ["data_asset_name"],
            },
        },
    },
}

```

- Save the datasource Configuration and close Jupyter notebook
- Test Configuration using `context.test_yaml_config(yaml.dump(datasource_config))` command

2.4 Save Datasource to DataContext

```
context.add_datasource(**datasource_config)
```

2.5 Test Datasource

`Repeat for both GOES18 and NEXRAD SUITES`

```
batch_request = RuntimeBatchRequest(
    datasource_name="my_s3_datasource",
    data_connector_name="default_runtime_data_connector_name",
    data_asset_name="",  # this can be anything that identifies this data_asset for you
    runtime_parameters={"path": ""},  # Add your S3 path here.
    batch_identifiers={"default_identifier_name": "default_identifier"},
)
```

2.6 Load Data into Validator
```
context.add_or_update_expectation_suite(expectation_suite_name="test_suite")
validator = context.get_validator(
    batch_request=batch_request, expectation_suite_name="test_suite"
)
print(validator.head())
```


**3. Expectations**

3.1 Use Validators to add Expectations to Suite

`Snippet`

```
validator.expect_column_values_to_not_be_null(column="day")

validator.expect_column_values_to_be_between(
    column="day", min_value=1, max_value=365
)
```

3.2 Save Expectation Suite

```
validator.save_expectation_suite(discard_failed_expectations=False)
```


**4. Data Validation**

4.1. Create Checkpoint 

`GOES18 Checkpoint`
```
my_checkpoint_name = "goes18_checkpoint_v0.1"
checkpoint_config = {
    "name": my_checkpoint_name,
    "config_version": 1.0,
    "class_name": "SimpleCheckpoint",
    "run_name_template": "%Y%m%d-%H%M%S-my-run-name-template",
}
```


`NEXRAD Checkpoint`
```
my_checkpoint_name = "nexrad_checkpoint_v0.1"
checkpoint_config = {
    "name": my_checkpoint_name,
    "config_version": 1.0,
    "class_name": "SimpleCheckpoint",
    "run_name_template": "%Y%m%d-%H%M%S-my-run-name-template",
}
```

4.2 Test and Save Checkpoint
```
my_checkpoint = context.test_yaml_config(yaml.dump(checkpoint_config))
```
```
context.add_or_update_checkpoint(**checkpoint_config)
```

4.3 Run Checkpoint
```
checkpoint_result = context.run_checkpoint(
    checkpoint_name=my_checkpoint_name,
    validations=[
        {
            "batch_request": batch_request,
            "expectation_suite_name": <your_expectation_suite_name>,
        }
    ],
)
```

4.4 Build and View Data Docs
```
context.open_data_docs()
```

**5. Great Expectations with Airflow**
5.1 Install GreatExpectationsOperator
```
pip install airflow-provider-great-expectations==0.1.1
```

5.2 Import GreatExpectationsOperator to DAG
```
from great_expectations_provider.operators.great_expectations import GreatExpectationsOperator
from great_expectations.core.batch import BatchRequest
from great_expectations.data_context.types.base import (
    DataContextConfig,
    CheckpointConfig
)
```

5.3 DAGS for GOES18 and NEXRAD Checkpoints
```
with dag:
    ge_goes18_checkpoint_pass = GreatExpectationsOperator(
        task_id="task_goes18_checkpoint",
        data_context_root_dir=ge_root_dir,
        checkpoint_name="goes18_checkpoint_v0.1"
    )
    ge_nexrad_checkpoint_pass = GreatExpectationsOperator(
        task_id="task_nexrad_checkpoint",
        data_context_root_dir=ge_root_dir,
        checkpoint_name="nexrad_checkpoint_v0.2",
        trigger_rule="all_done"
    )
```

5.4 Define Order of DAG Workflow

```
    ge_goes18_checkpoint_pass >> ge_nexrad_checkpoint_pass
```

-----
> WE ATTEST THAT WE HAVEN’T USED ANY OTHER STUDENTS’ WORK IN OUR ASSIGNMENT AND ABIDE BY THE POLICIES LISTED IN THE STUDENT HANDBOOK.
> 
> Vraj: 25%, Poojitha: 25%, Merwin: 25%, Anushka: 25%
-----


[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

