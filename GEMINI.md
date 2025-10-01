# Conversational Analytics API Demo Boilerplate

This boilerplate provides a complete solution for creating conversational analytics demos using Google's Conversational Analytics API, BigQuery, and a React-based frontend.

## 🚀 Project Overview

The project is divided into three main parts:

*   **`frontend`**: A React web application that provides the user interface for the chatbot.
*   **`backend`**: A Python FastAPI server that acts as a bridge between the frontend and the Google Conversational Analytics API.
*   **`scripts`**: A Python script to generate synthetic data for the demo.

### Architecture

```
[React Frontend] --HTTP--> [Python Backend] --Google API--> [Conversational Analytics API] --SQL--> [BigQuery]
```

## ⚙️ Prerequisites

Before you begin, you will need:

*   A Google Cloud project with the Conversational Analytics API enabled.
*   The `gcloud` CLI installed and authenticated.
*   Node.js 18+ and npm.
*   Python 3.11+.

## 🚀 Step-by-Step Guide

### Step 1: Configuration

1.  **Set your Google Cloud project ID:**
    The `billing_project` variable in `backend/api.py` is automatically set from the `DEVSHELL_PROJECT_ID` environment variable. If you are not in Cloud Shell, you can set it manually or through the `GOOGLE_CLOUD_PROJECT` environment variable.

2.  **Configure the Data Agent:**
    The data agent's configuration (ID, dataset, table names, system instruction, and display name) can be set using environment variables. If not set, default values will be used.

    Create a `.env` file in the `backend` directory with the following variables:
    ```env
    DATA_AGENT_ID=your_agent_id
    DATASET_ID=your_bigquery_dataset_id
    TABLE_NAMES=table1,table2,table3
    SYSTEM_INSTRUCTION="Your custom system instruction for the agent."
    DISPLAY_NAME="Your Agent Display Name"
    ```
    *   `DATA_AGENT_ID`: A unique identifier for your data agent (e.g., `my_new_demo_agent`).
    *   `DATASET_ID`: The ID of your BigQuery dataset (e.g., `my_demo_dataset`).
    *   `TABLE_NAMES`: A comma-separated list of table names in your dataset (e.g., `users,products,orders`).
    *   `SYSTEM_INSTRUCTION`: A description of the agent's persona and expected behavior.
    *   `DISPLAY_NAME`: A user-friendly name for your agent.

    **Example for Klick Health Demo:**
    ```env
    DATA_AGENT_ID=klick_agent
    DATASET_ID=klick_demo
    TABLE_NAMES=clients,campaigns,leads,opportunities,deals
    SYSTEM_INSTRUCTION="You are a helpful assistant for Klick Health, a marketing agency for life sciences companies."
    DISPLAY_NAME="Klick Health Demo Agent"
    ```

    **Example for LeagueApps Demo (Default):**
    ```env
    DATA_AGENT_ID=leagueapps_agent
    DATASET_ID=leagueapps_demo
    TABLE_NAMES=facilities,organizations,payments,programs,registrations,roles,schedule,team_members,teams,user_roles,users
    SYSTEM_INSTRUCTION="You are a helpful assistant for a youth sports organization."
    DISPLAY_NAME="LeagueApps Demo Agent"
    ```

### Step 2: Data Generation

1.  **Run the data generation script:**
    ```bash
    cd scripts
    pip install faker
    python generate_synthetic_data.py
    ```
    This will create a set of CSV files in the `scripts` directory.

### Step 3: BigQuery Setup

1.  **Create a BigQuery dataset:**
    ```bash
    bq --location=US mk -d --project_id YOUR_PROJECT_ID YOUR_DATASET_NAME
    ```

2.  **Load the data into BigQuery:**
    Run the `bq load` command for each of the CSV files generated in the previous step. You will need to define the schema for each table.

### Step 4: Running the Backend and Frontend

To run the application, you will need to open two separate terminals.

**Terminal 1: Start the Backend Server**

In your first terminal, run the following command to start the backend server in the background.

```bash
cd /home/admin_/final_demo/capi/demo-gen-capi/backend
uvicorn api:app --reload --port 8000 &
```

To verify that the backend server has started correctly, you can view the logs in the `backend.log` file:
```bash
tail -f /home/admin_/final_demo/capi/demo-gen-capi/backend/backend.log
```
You should see a line that says `Application startup complete.`

**Terminal 2: Start the Frontend Server**

In your second terminal, run the following command to start the frontend server in the background.

```bash
cd /home/admin_/final_demo/capi/demo-gen-capi/frontend/web-app
npm run dev &
```

To verify that the frontend server has started correctly, you can view the output of the command. You should see something like this:
```
  VITE v5.4.19  ready in 321 ms

  ➜  Local:   http://localhost:8084/
  ➜  Network: http://10.88.0.4:8084/
  ➜  press h + enter to show help
```

### Step 6: Testing the Demo

1.  **Open your browser** to the URL provided by the `npm run dev` command (usually `http://localhost:5173`).

2.  **Ask a question:**
    Try asking one of the "golden" queries from the `DEMO_SCRIPT.md` file.

### Step 7: Deployment

*   **Backend:** The backend can be deployed to a serverless platform like Google Cloud Run. You will need to create a `Dockerfile` and use `gcloud` to deploy it.
*   **Frontend:** The frontend can be deployed to any static hosting provider, such as Netlify, Vercel, or Firebase Hosting.
