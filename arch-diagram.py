from diagrams import Diagram, Edge, Cluster
from diagrams.onprem.client import User, Users
from diagrams.onprem.container import Docker
from diagrams.onprem.workflow import Airflow
from diagrams.aws.storage import SimpleStorageServiceS3 as S3
from diagrams.onprem.network import Nginx
from diagrams.onprem.database import Postgresql as PostgreSQL
from diagrams.oci.monitoring import Telemetry

with Diagram("Architectural Diagram for Assignment 2", show=False,direction="LR"):
    #Define Nodes
    ingress = Users("User")
    with Cluster("Compute Instance"):  
        with Cluster("Applications"): #Cluster for Streamlit and API 
            userfacing = Docker("Streamlit")
            backend = Docker("FastAPI")
            userfacing - Edge(label = "API Calls", color = "red", style = "dashed") - backend

        with Cluster("Database"):  #A cluster with single node for Databse
            db = PostgreSQL("IAM")  #SQLIte database unavailable, substituting with PostGRESql for Diagram

        with Cluster("Batch Process"):     #Creating a cluster for Airflow and Hosting Great Expectations
            airflow = Airflow("Streamlit")
            GE = Telemetry("Data Quality Check")
            hosting = Nginx("Reports")

    backend << Edge(label = "Verify Login") << db   #FAST API interaction with db to verify login
    developers = User("Developers")  #developer accessing Airflow instance
    dataset = S3("Open Dataset")   #dataset storing the file transfers from public bucket

    airflow << Edge(label = "metadata collection") << dataset   #airflow scrapes metadata from dataset
    airflow >> Edge(label = "Update AWS bucket metadata") >> db  #scraped data stored in db

    GE << Edge(label = "CSV of metadata") << db   #extract csv file from db
    GE >> Edge(label = "Host the static HTML report") >> hosting #host static html
    airflow >> Edge(label = "Run Great Expectations") >> GE #running great expectations

    ingress >> Edge(label = "Login to dashboard", color="darkgreen") << userfacing  #user logging in to dashboard
    developers << Edge(label = "View Reports", color="darkgreen") << hosting  #developer using hosting
    developers << Edge(label = "View Dashboard", color="darkgreen") << airflow  #developer accessing airflow