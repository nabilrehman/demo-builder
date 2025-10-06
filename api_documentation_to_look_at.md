Skip to main content
Google Cloud
Documentation
Technology areas

Cross-product tools

Related sites


Search
/


English
Console

Gemini for Google Cloud
Overview
Conversational Analytics API
Contact Us
Filter

Gemini for Google Cloud 
Documentation 
Conversational Analytics API
Was this helpful?

Send feedbackConversational Analytics API architecture and key concepts

bookmark_border

This product or feature is subject to the "Pre-GA Offerings Terms" in the General Service Terms section of the Service Specific Terms. Pre-GA products and features are available "as is" and might have limited support. For more information, see the launch stage descriptions.

This document describes the key concepts for using the Conversational Analytics API (geminidataanalytics.googleapis.com), which lets you create and interact with data agents that use natural language to answer questions about your structured data. This document describes how agents work, typical workflows, conversation modes, Identity and Access Management (IAM) roles, and how to design systems with multiple agents.

How data agents work
Conversational Analytics API data agents use context that you provide (business information and data) and tools (such as SQL and Python) to interpret natural language questions and generate responses from your structured data.

The following diagram illustrates the stages of an agent's workflow when a user asks a question:

Conversational Analytics API architecture diagram, showing the flow from user input through a reasoning engine, to the final output.


As shown in the diagram, when a user asks a question, the agent processes the request in the following stages:

User input: The user submits a question in natural language, along with any additional context you provide.
Data sources: The agent connects to your data in Looker, BigQuery, and Looker Studio to retrieve the necessary information.
Reasoning engine: The core of the agent processes the user's question by using available tools to generate an answer.
Agent output: The agent generates a response, which can include text, data tables, or specifications for charts.
Workflows for designing and using agents
The Conversational Analytics API supports workflows for agent creators (who build and configure agents) and for agent consumers (who interact with agents).

The following diagram illustrates the end-to-end process, from the initial setup by an agent creator to the final interactions from an agent consumer:

The end-to-end workflow for agent design and use, from creator tasks like creating and sharing to data user tasks like interacting with an agent.


The following sections describe the workflows for agent creators and agent consumers in more detail.

The agent creator workflow
The agent creator is responsible for setting up and configuring agents. This workflow involves the following steps:

Create agent: The creator starts by creating a new agent and providing the necessary context, including system instructions and connections to data sources. This step is crucial for enabling the agent to understand and respond to user questions effectively.
Share the agent: Once the agent is configured, the creator shares it with other users and sets the appropriate role-based access controls to manage permissions.
The agent consumer workflow
The agent consumer is typically a business user who needs to get answers from a configured agent. This workflow involves the following steps:

Find an agent: The user starts by finding an agent that has been shared with them.
Ask a question: The user asks a question in natural language. This question can be a single query or part of a multi-turn conversation.
Agent "thinks": The agent's reasoning engine processes the question. The reasoning engine uses the agent's predefined knowledge and available agent tools (like SQL, Python, and charts) in a "reasoning loop" to determine the best way to answer the question.
Agent responds: The agent returns an answer, which can include text, data tables, or charts.
Conversation modes
Conversational Analytics API agents support different conversation modes that determine how an agent handles conversation history and the persistence of context across interactions. The following conversation modes are available:

Stateless mode: The agent doesn't store conversation history. Each interaction is treated independently. This mode is useful for applications where you don't need to maintain context across multiple turns.
Stateful mode: The agent retains context and conversation history, allowing for more contextualized interactions. This mode is useful for applications where you need to maintain context across multiple turns. Using stateful mode is recommended for better accuracy and personalized responses.
Choose a conversation mode based on your application's requirements for conversation history and context persistence.

The different modes of chat for a Conversational Analytics API agent.


IAM roles
IAM roles control who can create, manage, share, and interact with Conversational Analytics API agents. The following table describes the key IAM roles for the Conversational Analytics API:

Role	Typical scope	What the role enables	Who might use this role
Gemini Data Analytics Data Agent Creator (roles/geminidataanalytics.dataAgentCreator)	Project	Create agents and inherit owner permissions on the agent.	Any data analyst
Gemini Data Analytics Data Agent Owner (roles/geminidataanalytics.dataAgentOwner)	Project, Agent	Edit, share, or delete agents with other users.	Senior data analyst
Gemini Data Analytics Data Agent Editor (roles/geminidataanalytics.dataAgentEditor)	Agent, Project	Update an agent's configuration or context.	Junior data analyst
Gemini Data Analytics Data Agent User (roles/geminidataanalytics.dataAgentUser)	Agent, Project	Chat with an agent.	Marketer, store owner
Gemini Data Analytics Data Agent Viewer (roles/geminidataanalytics.dataAgentViewer)	Project, Agent	List agents and get their details.	Any user
Gemini Data Analytics Data Agent Stateless User (roles/geminidataanalytics.dataAgentStatelessUser)	Project	Chat with an agent without storage of context or conversation history.	Any user
Systems with multiple agents
You can design complex systems by integrating multiple Conversational Analytics API agents. A common pattern is to use a primary "orchestrator" agent that delegates tasks to one or more specialized agents that handle specific domains, such as sales or marketing data. This approach lets you build a system that can handle a wide range of questions by combining the strengths of multiple agents.

The following diagram illustrates this multi-agent pattern and shows how a primary agent can delegate a data question to a specialized Conversational Analytics agent:

A primary orchestrator agent delegates a data question to a specialized sales agent, which then returns an answer to the user.


The typical workflow for a multi-agent system involves the following steps:

A business user or data analyst asks a question in natural language, such as "Show me the top three stores by revenue."
A primary "orchestrator" agent delegates the request to the appropriate specialized agent.
A specialized agent receives the delegated request, connects to the relevant data sources, uses its tools to generate the necessary SQL queries and charts, and generates a response.
The specialized agent's response is returned to the user, such as "Stores 4, 9, and 3 have the highest revenue. Here's a chart."
What's next
After understanding the core concepts of the Conversational Analytics API, explore how to implement these features:

Explore how to authenticate and connect to a data source.
Learn how to create and configure an agent with HTTP.
Learn how to create and configure an agent with Python.
Learn more about guiding an agent's behavior with authored context.
Understand access control with IAM for the Conversational Analytics API.
Was this helpful?

Send feedback
Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2025-10-02 UTC.

Why Google
Choosing Google Cloud
Trust and security
Modern Infrastructure Cloud
Multicloud
Global infrastructure
Customers and case studies
Analyst reports
Whitepapers
Products and pricing
See all products
See all solutions
Google Cloud for Startups
Google Cloud Marketplace
Google Cloud pricing
Contact sales
Support
Community forums
Support
Release Notes
System status
Resources
GitHub
Getting Started with Google Cloud
Google Cloud documentation
Code samples
Cloud Architecture Center
Training and Certification
Developer Center
Engage
Blog
Events
X (Twitter)
Google Cloud on YouTube
Google Cloud Tech on YouTube
Become a Partner
Google Cloud Affiliate Program
Press Corner
About Google
Privacy
Site terms
Google Cloud terms
Our third decade of climate action: join us
Sign up for the Google Cloud newsletter
Subscribe

English
The new page has loaded..





Skip to main content
Google Cloud
Documentation
Technology areas

Cross-product tools

Related sites


Search
/


English
Console

Gemini for Google Cloud
Overview
Conversational Analytics API
Contact Us
Filter

Gemini for Google Cloud 
Documentation 
Conversational Analytics API
Was this helpful?

Send feedbackMigrate from the Data QnA API to the Conversational Analytics API

bookmark_border

This product or feature is subject to the "Pre-GA Offerings Terms" in the General Service Terms section of the Service Specific Terms. Pre-GA products and features are available "as is" and might have limited support. For more information, see the launch stage descriptions.

This guide describes key differences and steps for migrating your applications from the Data QnA API (dataqna.googleapis.com) to the Conversational Analytics API (geminidataanalytics.googleapis.com).

Note: If you haven't previously enabled the Data QnA API (dataqna.googleapis.com), you can skip this page and go directly to the documentation on setup and authentication.
Provide feedback
If you encounter any discrepancies during the migration process, contact conversational-analytics-api-feedback@google.com.

Overview of key changes
The Conversational Analytics API introduces changes to the API endpoint, the service that the API uses, and the structure of API requests. The following table summarizes the key differences between the Data QnA API and the Conversational Analytics API and lists the required steps for migration.

Data QnA API	Conversational Analytics API	Required change
dataqna.googleapis.com endpoint	geminidataanalytics.googleapis.com endpoint	Update the API endpoint in your requests.
DataQuestionService service	DataChatService service	Update the service name in your requests.
project field in the AskQuestionRequest message	parent field in the ChatRequest message	Replace the project field with the parent field in your requests. For more information, see Replace project with parent for request routing.
datasource_ids field	studio_references field	Replace the datasource_ids field with the studio_references field in your requests. For more information, see Update references to Looker Studio data source IDs.
AgentConfig object	ConversationOptions object	Replace the AgentConfig object with the ConversationOptions object in your requests. For more information, see Enable Python analysis with ConversationOptions.
context field in the AskQuestionRequest message	inline_context field in the ChatRequest message	Replace the context field with the inline_context field in your requests. For more information, see Replace context with inline_context.
For examples of how to update your API request structures, see Examples: Update your API request structures.

Replace project with parent for request routing
In the Data QnA API, you use the project field within the AskQuestionRequest message to specify the Google Cloud project. In the Conversational Analytics API, the project field is deprecated within the ChatRequest message. Instead, you use the parent field to specify both the project and the location.

The following example shows the format for specifying the parent field:



parent: "projects/your_project_name/locations/global"
In the previous example, replace your_project_name with the name of your Google Cloud project.

Update references to Looker Studio data source IDs
In the Data QnA API, you use the datasource_ids field to provide a list of Looker Studio data source IDs. In the Conversational Analytics API, you use the studio_references field to provide a list of StudioDatasourceReference objects, each containing a single data source ID. For more information, see StudioDatasourceReferences.

Enable Python analysis with ConversationOptions
The AgentConfig object, which is used in the Data QnA API to enable tools, is not used by the DataChatService service in the Conversational Analytics API. To enable features such as Python analysis in the Conversational Analytics API, use the ConversationOptions object when you create or configure a data agent. For more information, see ConversationOptions.

Replace context with inline_context
In the Data QnA API, the AskQuestionRequest message includes a context field for inline contextual information. In the Conversational Analytics API, the context field is renamed to inline_context in the ChatRequest message. This change helps to distinguish inline context from other types of context that can be provided through data agents.

Examples: Update your API request structures
The following examples show how to adapt your requests to the new API structure when you migrate from the Data QnA API to the Conversational Analytics API. These examples cover BigQuery, Looker, and Looker Studio data sources.

BigQuery data source
This section provides an example of how to update your API requests for BigQuery data sources. The example shows how to update a request that asks for a bar graph that shows the top five states by the total number of airports.

The following code sample shows the request structure for the Data QnA API:



project: "projects/your_project_name"
messages {
  user_message {
    text: "Create a bar graph showing the top 5 states by the total number of airports."
  }
}
context {
  datasource_references {
    bq {
      table_references {
        project_id: "your_project_id"
        dataset_id: "your_dataset_id"
        table_id: "your_table_id"
      }
    }
  }
}
The following code sample shows the updated request structure for the Conversational Analytics API:



messages {
  user_message {
    text: "Create a bar graph showing the top 5 states by the total number of airports."
  }
}
parent: "projects/your_project_name/locations/global"
inline_context {
  datasource_references {
    bq {
      table_references {
        project_id: "your_project_id"
        dataset_id: "your_dataset_id"
        table_id: "your_table_id"
      }
    }
  }
For the previous examples, you can replace the sample values as follows:

your_project_name: The name of your Google Cloud project.
your_project_id: The ID of your BigQuery project. To connect to a public dataset, specify bigquery-public-data.
your_dataset_id: The ID of the BigQuery dataset. For example, faa.
your_table_id: The ID of the BigQuery table. For example, us_airports.
Looker data source
This section provides an example of how to update your API requests for Looker data sources. The example shows how to update a request that asks for the count of orders by order status.

The following code sample shows the request structure for the Data QnA API:



project: "projects/your_project_name"
messages {
  user_message {
    text: "Show the count of orders by order status."
  }
}
context {
  datasource_references {
    looker {
      explore_references {
        looker_instance_uri: "https://your_company.looker.com"
        lookml_model: "your_model"
        explore: "your_explore"
      }
      credentials {
        oauth {
          secret {
            client_id: "your_looker_client_id"
            client_secret: "your_looker_client_secret"
          }
        }
      }
    }
  }
}

The following code sample shows the updated request structure for the Conversational Analytics API:



messages {
  user_message {
    text: "Show the count of orders by order status."
  }
}
parent: "projects/your_project_name/locations/global"
inline_context {
  datasource_references {
    looker {
      explore_references {
        lookml_model: "your_model"
        explore: "your_explore"
        looker_instance_uri: "https://your_company.looker.com"
      }
      credentials {
        oauth {
          secret {
            client_id: "your_looker_client_id"
            client_secret: "your_looker_client_secret"
          }
        }
      }
    }
  }
}
For the previous examples, you can replace the sample values as follows:

your_project_name: The name of your Google Cloud project
https://your_company.looker.com: The URI of your Looker instance
your_model: The name of your LookML model
your_explore: The name of your LookML Explore
your_looker_client_id: Your Looker client ID
your_looker_client_secret: Your Looker client secret
Looker Studio data source
This section provides an example of how to update your API requests for Looker Studio data sources. The example shows how to update a request that asks for a bar graph that shows the top five carriers.

The following code sample shows the request structure for the Data QnA API:



project: "projects/your_project_name"
messages {
  user_message {
    text: "Create a bar graph showing the top 5 carriers."
  }
}
context {
  datasource_references {
    studio {
      datasource_ids: "your_data_source_id"
    }
  }
}
The following code sample shows the updated request structure for the Conversational Analytics API:



messages {
  user_message {
    text: "Create a bar graph showing the top 5 carriers."
  }
}
parent: "projects/your_project_name/locations/global"
inline_context {
  datasource_references {
    studio {
      datasource_ids: "your_data_source_id"
    }
  }
}
For the previous examples, you can replace the sample values as follows:

your_project_name: The name of your Google Cloud project
your_data_source_id: The ID of your Looker Studio data source
Was this helpful?

Send feedback
Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2025-10-02 UTC.

Why Google
Choosing Google Cloud
Trust and security
Modern Infrastructure Cloud
Multicloud
Global infrastructure
Customers and case studies
Analyst reports
Whitepapers
Products and pricing
See all products
See all solutions
Google Cloud for Startups
Google Cloud Marketplace
Google Cloud pricing
Contact sales
Support
Community forums
Support
Release Notes
System status
Resources
GitHub
Getting Started with Google Cloud
Google Cloud documentation
Code samples
Cloud Architecture Center
Training and Certification
Developer Center
Engage
Blog
Events
X (Twitter)
Google Cloud on YouTube
Google Cloud Tech on YouTube
Become a Partner
Google Cloud Affiliate Program
Press Corner
About Google
Privacy
Site terms
Google Cloud terms
Our third decade of climate action: join us
Sign up for the Google Cloud newsletter
Subscribe

English
The new page has loaded.



Skip to main content
Google Cloud
Documentation
Technology areas

Cross-product tools

Related sites


Search
/


English
Console

Gemini for Google Cloud
Overview
Conversational Analytics API
Contact Us
Filter

Gemini for Google Cloud 
Documentation 
Conversational Analytics API
Was this helpful?

Send feedbackAuthenticate and connect to a data source with the Conversational Analytics API

bookmark_border

This product or feature is subject to the "Pre-GA Offerings Terms" in the General Service Terms section of the Service Specific Terms. Pre-GA products and features are available "as is" and might have limited support. For more information, see the launch stage descriptions.

Developers can use the Conversational Analytics API, accessed through geminidataanalytics.googleapis.com, to build an artificial intelligence (AI)-powered chat interface, or data agent, that answers questions about structured data in BigQuery, Looker, and Looker Studio using natural language.

This page describes how to authenticate to the Conversational Analytics API and configure connections to your data in Looker, BigQuery, and Looker Studio by using either direct HTTP requests or the SDK. The Conversational Analytics API uses standard Google Cloud authentication methods.

Before you begin
Before you can authenticate to the Conversational Analytics API and configure connections to your data, you must complete the prerequisites and enable the required APIs for your Google Cloud project, as described in Enable the Conversational Analytics API.

Authenticate to the Conversational Analytics API
This section describes how to authenticate to the Conversational Analytics API (through geminidataanalytics.googleapis.com) by using HTTP and Python methods to obtain the necessary authorization tokens.

HTTP curl
HTTP using Python
Python SDK
The following sample curl command sends a request to the Conversational Analytics API. The gcloud auth print-identity-token command provides an access token that is used for authorization. In the code sample, replace  with the appropriate API resource path.



curl  -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
https://geminidataanalytics.googleapis.com/
Connect to Looker with the Conversational Analytics API
To connect to Looker with the Conversational Analytics API, you must provide the following information:

The URL of your Looker instance
The specific LookML model and Looker Explore that you want to use as a data source
Additionally, the authenticating user or service account must have the required Looker permissions.

Choose the appropriate authentication method
You can then choose to authenticate using either Looker API keys (client ID and client secret) or an access token. Customers who use Looker (Google Cloud core) with only private connections must authenticate with an access token.

Important: You can connect to only one Looker Explore at a time with the Conversational Analytics API.
Use the following table to choose the appropriate authentication method.

User type	Authentication method	For Looker (original)	For Looker (Google Cloud core)	For Looker (Google Cloud core) that uses only private connections	Description
Embed users	Access token	login_user	login_user	N/A	Respects LookML row and column level permissions (for example, access_filters, access_grants, sql_always_where) of the target user's access_token.
Standard users	Access token	
login_user

Or

OAuth client

OAuth client	OAuth client	Respects LookML row and column level permissions (for example, access_filters, access_grants, sql_always_where) of the target user's access_token.
Looker API-only service account	API key	Client ID and secret	Client ID and secret	N/A	All users share the same level of access to Looker.
API keys use the permissions and access levels of the user. API keys can be useful if you are building an application where everyone shares the same level of access.

An access token lets you use LookML row and column level permissions (for example,access_filters, access_grants, sql_always_where) of the target user's access_token. An access token is useful for a multi-tenant application.

Required Looker permissions
The user or service account whose credentials are used for authentication must be granted a Looker role that includes the following permissions for the models that you want to query:

access_data
gemini_in_looker
You can configure these permissions in the Admin > Roles section of your Looker instance.

Authenticate with Looker API keys
This section describes how to generate the API keys and configure the Conversational Analytics API to connect to Looker by using either direct HTTP requests or the SDK.

Important: Customers who use the Looker (Google Cloud core) private connections option cannot use this method and should authenticate with an access token.
To establish a connection with a Looker instance, you need valid Looker API keys, which are created by Looker and consist of a client ID and a client secret. Looker uses these keys to authorize requests to the Looker API.

To learn more about generating new Looker API keys, see Admin settings - Users. To learn more about authentication methods and managing Looker API keys, see Looker API authentication.

HTTP using Python
Python SDK
After you generate the API keys (client ID and secret), you can configure the Conversational Analytics API to connect to Looker by making direct HTTP requests. The following sample code demonstrates how to specify your Looker data source details and your API keys within the body of your HTTP request.


looker_credentials = {
  "oauth": {
      "secret": {
        "client_id": "your_looker_client_id",
        "client_secret": "your_looker_client_secret",
      }
  }
}

looker_data_source = {
  "looker": {
    "explore_references": {
        "looker_instance_uri": "https://your_company.looker.com",
        "lookml_model": "your_model",
        "explore": "your_explore",
    }
  }
}

Replace the sample values as follows:

your_looker_client_id: The client ID of your generated Looker API key
your_looker_client_secret: The client secret of your generated Looker API key
https://your_company.looker.com: The complete URL of your Looker instance
your_model: The name of the LookML model that you want to use
your_explore: The name of the Explore within the specified model that you want to use
Authenticate with an access token
This section describes how to configure the Conversational Analytics API to connect to Looker using an access token.

Note: An admin user must generate the access_token value. The user that the access_token is created for must have the permissions for the Get LookML Model Explore and Run Inline Query Looker endpoints. The develop permission is a minimum requirement.
To establish a connection with a Looker instance, you need a valid OAuth2 access_token value, which is created by a successful request to the login Looker API endpoint.

To learn more about generating an access token, see Looker API authentication and how to present client credentials to obtain an authorization token.

Using a public IP Using a private connection
HTTP using Python
Python SDK
HTTP using JavaScript
The following sample code demonstrates how to specify your Looker data source details and your access token within the body of your HTTP request.

We suggest storing the Looker access token (access_token) as an environment variable for improved security.

looker_credentials = {
  "oauth": {
    "token": {
      "access_token": "YOUR-TOKEN",
    }
  }
}

looker_data_source = {
  "looker": {
    "explore_references": {
        "looker_instance_uri": "https://your_company.looker.com",
        "lookml_model": "your_model",
        "explore": "your_explore",
    }
  }
}
Replace the sample values as follows:

YOUR-TOKEN: The access_token value you generate to authenticate to Looker.
https://your_company.looker.com: The complete URL of your Looker instance
your_model: The name of the LookML model that you want to use
your_explore: The name of the Explore within the specified model that you want to use
Connect to BigQuery with the Conversational Analytics API
To connect to one or more BigQuery tables with the Conversational Analytics API, you must authenticate to the relevant BigQuery project for each table. For each table, provide the following information:

The BigQuery project ID
The BigQuery dataset ID
The BigQuery table ID
With the Conversational Analytics API, there are no hard limits on the number of BigQuery tables that you can connect to. However, connecting to a large number of tables can reduce accuracy or cause you to exceed Gemini's input token limit. Queries that require complex joins across multiple tables might also result in less accurate responses.

This section describes how to configure the Conversational Analytics API to connect to BigQuery by using either direct HTTP requests or an SDK.

HTTP using Python
Python SDK
The following sample code defines a connection to multiple BigQuery tables.

bigquery_data_sources = {
    "bq": {
      "tableReferences": [
        {
          "projectId": "my_project_id",
          "datasetId": "my_dataset_id",
          "tableId": "my_table_id"
        },
        {
          "projectId": "my_project_id_2",
          "datasetId": "my_dataset_id_2",
          "tableId": "my_table_id_2"
        },
        {
          "projectId": "my_project_id_3",
          "datasetId": "my_dataset_id_3",
          "tableId": "my_table_id_3"
        },
      ]
    }
}
Replace the sample values as follows:

my_project_id: The ID of the Google Cloud project that contains the BigQuery dataset and table that you want to connect to. To connect to a public dataset, specify bigquery-public-data.
my_dataset_id: The ID of the BigQuery dataset.
my_table_id: The ID of the BigQuery table.
Connect to Looker Studio with the Conversational Analytics API
To connect to Looker Studio with the Conversational Analytics API, you must first enable the Looker Studio API. This section describes how to configure the Conversational Analytics API to connect to Looker Studio by using either direct HTTP requests or an SDK.

Enable Looker Studio API
To enable the Looker Studio API, follow the instructions in Enable the API.

Authenticate to Looker Studio
To connect to Looker Studio with the Conversational Analytics API, you must authenticate to Looker Studio and provide the Looker Studio data source ID.

HTTP using Python
Python SDK
After you enable the Looker Studio API, you can authenticate to Looker Studio by making HTTP curl requests with Python. The following sample code demonstrates how to specify your Looker data source details within the body of your HTTP request.

You can authenticate to Looker Studio by making direct HTTP requests. A sample HTTP call is shown in the following code block.

looker_studio_data_source = {
    "studio":{
        "studio_references":
        [
            {
              "datasource_id": "your_studio_datasource_id"
            }
        ]
    }
}

Replace your_studio_datasource_id with the actual data source ID of the Looker Studio data source that you want to use.

Was this helpful?

Send feedback
Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2025-10-02 UTC.

Why Google
Choosing Google Cloud
Trust and security
Modern Infrastructure Cloud
Multicloud
Global infrastructure
Customers and case studies
Analyst reports
Whitepapers
Products and pricing
See all products
See all solutions
Google Cloud for Startups
Google Cloud Marketplace
Google Cloud pricing
Contact sales
Support
Community forums
Support
Release Notes
System status
Resources
GitHub
Getting Started with Google Cloud
Google Cloud documentation
Code samples
Cloud Architecture Center
Training and Certification
Developer Center
Engage
Blog
Events
X (Twitter)
Google Cloud on YouTube
Google Cloud Tech on YouTube
Become a Partner
Google Cloud Affiliate Program
Press Corner
About Google
Privacy
Site terms
Google Cloud terms
Our third decade of climate action: join us
Sign up for the Google Cloud newsletter
Subscribe

English
The new page has loaded..



Skip to main content
Google Cloud
Documentation
Technology areas

Cross-product tools

Related sites


Search
/


English
Console

Gemini for Google Cloud
Overview
Conversational Analytics API
Contact Us
Filter

Gemini for Google Cloud 
Documentation 
Conversational Analytics API
Was this helpful?

Send feedbackGuide agent behavior with authored context

bookmark_border

This product or feature is subject to the "Pre-GA Offerings Terms" in the General Service Terms section of the Service Specific Terms. Pre-GA products and features are available "as is" and might have limited support. For more information, see the launch stage descriptions.

This page describes the recommended structure for writing effective prompts for your Conversational Analytics API data agents. These prompts are authored context that you define as strings by using the system_instruction parameter. Well-structured system instructions can improve the accuracy and relevance of the responses that the API provides.

For examples of authored context in different environments, see the following documentation pages:

Define data agent context for BigQuery data sources
Define data agent context for Looker data sources
What are system instructions?
System instructions are user-defined guidance that developers can provide to shape the behavior of a data agent and to refine the API's responses. System instructions are part of the context that the API uses to answer questions. This context also includes connected data sources (BigQuery tables, Looker Explores, Looker Studio data sources), and conversation history (for multi-turn conversations).

By providing clear, structured guidance through system instructions, you can improve the agent's ability to interpret user questions and generate useful and accurate responses. Well-defined system instructions are especially useful if you're connecting to data such as BigQuery tables, where there may not be a predefined semantic layer like there is with a Looker Explore.

For example, you can use system instructions to provide the following types of guidance to an agent:

Business-specific logic: Define a "loyal" customer as one who has made more than five purchases within a certain timeframe.
Response formatting: Summarize all responses from your data agent in 20 words or fewer to save your users time.
Data presentation: Format all numbers to match the company's style guide.
Provide system instructions
You can provide system instructions to the Conversational Analytics API as a YAML-formatted string by using the system_instruction parameter. Although the system_instruction parameter is optional and the structure is up to your discretion, providing well-structured system instructions is recommended for accurate and relevant responses.

You can define the YAML-formatted string in your code during initial setup, as shown in Configure initial settings and authentication (HTTP) or Specify the billing project and system instructions (Python SDK). You can then include the system_instruction parameter in the following API calls:

Creating a persistent data agent: Include the system_instruction string within the published_context object in the request body to configure agent behavior that persists across multiple conversations. For more information, see Create a data agent (HTTP) or Set up context for stateful or stateless chat (Python SDK).
Sending a stateless request: Provide the system_instruction string within the inline_context object in the chat request to define the agent's behavior and context for the duration of that specific API call. For more information, see Create a stateless multi-turn conversation (HTTP) or Send a stateless chat request with inline context (Python SDK).
Related resources
Define data agent context for BigQuery data sources
Define data agent context for Looker data sources
Was this helpful?

Send feedback
Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2025-10-02 UTC.

Why Google
Choosing Google Cloud
Trust and security
Modern Infrastructure Cloud
Multicloud
Global infrastructure
Customers and case studies
Analyst reports
Whitepapers
Products and pricing
See all products
See all solutions
Google Cloud for Startups
Google Cloud Marketplace
Google Cloud pricing
Contact sales
Support
Community forums
Support
Release Notes
System status
Resources
GitHub
Getting Started with Google Cloud
Google Cloud documentation
Code samples
Cloud Architecture Center
Training and Certification
Developer Center
Engage
Blog
Events
X (Twitter)
Google Cloud on YouTube
Google Cloud Tech on YouTube
Become a Partner
Google Cloud Affiliate Program
Press Corner
About Google
Privacy
Site terms
Google Cloud terms
Our third decade of climate action: join us
Sign up for the Google Cloud newsletter
Subscribe

English
The new page has loaded.



Skip to main content
Google Cloud
Documentation
Technology areas

Cross-product tools

Related sites


Search
/


English
Console

Gemini for Google Cloud
Overview
Conversational Analytics API
Contact Us
Filter

Gemini for Google Cloud 
Documentation 
Conversational Analytics API
Was this helpful?

Send feedbackDefine data agent context for BigQuery data sources

bookmark_border

This product or feature is subject to the "Pre-GA Offerings Terms" in the General Service Terms section of the Service Specific Terms. Pre-GA products and features are available "as is" and might have limited support. For more information, see the launch stage descriptions.

Writing effective system instructions can provide your Conversational Analytics API data agents with useful context for answering questions about your data sources. System instructions are a kind of authored context that data agent owners can provide to shape the behavior of a data agent and to refine the API's responses.

This page describes the recommended structure for writing effective prompts for your Conversational Analytics API data agents that connect to BigQuery data. These prompts are authored context that you define as strings by using the system_instruction parameter.

This page describes how to write system instructions for BigQuery data sources, which are based on BigQuery databases.

Define context in system instructions
System instructions consist of a series of key components and objects that provide the data agent with details about the data source and guidance about the agent's role when answering questions. You can provide system instructions to the data agent in the system_instruction parameter as a YAML-formatted string.

Important: Although the system_instruction parameter is optional and the structure is up to your discretion, we recommend that you provide well-structured system instructions to enable the agent to give more accurate and relevant responses.
The following template shows a suggested YAML structure for the string that you provide to the system_instruction parameter, including the available keys and expected data types.

The following YAML template shows an example of how you might structure system instructions for a BigQuery data source.

- system_instruction: str # A description of the expected behavior of the agent. For example: You are a sales agent.
- tables: # A list of tables to describe for the agent.
    - table: # Details about a single table that is relevant for the agent.
        - name: str # The name of the table.
        - description: str # A description of the table.
        - synonyms: list[str] # Alternative terms for referring to the table.
        - tags: list[str] # Keywords or tags that are associated with the table.
        - fields: # Details about columns (fields) within the table.
            - field: # Details about a single column within the current table.
                - name: str # The name of the column.
                - description: str # A description of the column.
                - synonyms: list[str] # Alternative terms for referring to the column.
                - tags: list[str] # Keywords or tags that are associated with the column.
                - sample_values: list[str] # Sample values that are present within the column.
                - aggregations: list[str] # Commonly used or default aggregations for the column.
        - measures: # A list of calculated metrics (measures) for the table.
            - measure: # Details about a single measure within the table.
                - name: str # The name of the measure.
                - description: str # A description of the measure.
                - exp: str # The expression that is used to construct the measure.
                - synonyms: list[str] # Alternative terms for referring to the measure.
        - golden_queries: # A list of important or popular ("golden") queries for the table.
            - golden_query: # Details about a single golden query.
                - natural_language_query: str # The natural language query.
                - sql_query: str # The SQL query that corresponds to the natural language query.
        - golden_action_plans: # A list of suggested multi-step plans for answering specific queries.
            - golden_action_plan: # Details about a single action plan.
                - natural_language_query: str # The natural language query.
                - action_plan: # A list of the steps for this action plan.
                    - step: str # A single step within the action plan.
    - relationships: # A list of join relationships between tables.
        - relationship: # Details about a single join relationship.
            - name: str # The name of this join relationship.
            - description: str # A description of the relationship.
            - relationship_type: str # The join relationship type: one-to-one, one-to-many, many-to-one, or many-to-many.
            - join_type: str # The join type: inner, outer, left, right, or full.
            - left_table: str # The name of the left table in the join.
            - right_table: str # The name of the right table in the join.
            - relationship_columns: # A list of columns that are used for the join.
                - left_column: str # The join column from the left table.
                - right_column: str # The join column from the right table.
- glossaries: # A list of definitions for glossary business terms, jargon, and abbreviations.
    - glossary: # The definition for a single glossary item.
        - term: str # The term, phrase, or abbreviation to define.
        - description: str # A description or definition of the term.
        - synonyms: list[str] # Alternative terms for the glossary entry.
- additional_descriptions: # A list of any other general instructions or content.
    - text: str # Any additional general instructions or context not covered elsewhere.
Examples of key components of system instructions using BigQuery data sources
The following sections contain examples of key components of system instructions in BigQuery. These keys include the following:

system_instruction
tables
fields
measures
golden_queries
golden_action_plans
relationships
glossaries
additional_descriptions
system_instruction
Use the system_instruction key to define the agent's role and persona. This initial instruction sets the tone and style for the API's responses and helps the agent understand its core purpose.

For example, you can define an agent as a sales analyst for a fictitious ecommerce store as follows:

- system_instruction: >-
    You are an expert sales analyst for a fictitious ecommerce store. You will answer questions about sales, orders, and customer data. Your responses should be concise and data-driven.
tables
The tables key contains a list of table descriptions for the agent and provides details about the specific data that is available to the agent for answering questions. Each table object within this list contains the metadata for a specific table, including that table's name, description, synonyms, tags, fields, measures, golden queries, and golden action plans. The following YAML code block shows the basic structure for the tables key for the table bigquery-public-data.thelook_ecommerce.orders:

- tables:
    - table:
        - name: bigquery-public-data.thelook_ecommerce.orders
        - description: Data for customer orders in The Look fictitious e-commerce store.
        - synonyms:
            - sales
            - orders_data
        - tags:
            - ecommerce
            - transaction
fields
The fields key, which is nested within a table object, takes a list of field objects to describe individual columns. Not all fields need additional context; however, for commonly used fields, including additional details can help improve the agent's performance.

The following sample YAML code describes key fields such as order_id, status, created_at, num_of_items, and earnings for the orders table:

- tables:
    - table:
        - name: bigquery-public-data.thelook_ecommerce.orders
        - fields:
            - field:
                - name: order_id
                - description: The unique identifier for each customer order.
            - field:
                - name: user_id
                - description: The unique identifier for each customer.
            - field:
                - name: status
                - description: The current status of the order.
                - sample_values:
                    - complete
                    - shipped
                    - returned
            - field:
                - name: created_at
                - description: The timestamp when the order was created.
            - field:
                - name: num_of_items
                - description: The total number of items in the order.
                - aggregations:
                    - sum
                    - avg
            - field:
                - name: earnings
                - description: The sales amount for the order.
                - aggregations:
                    - sum
                    - avg
measures
The measures key, which is nested within a table object, defines custom business metrics or calculations that aren't directly present as columns in your tables. Providing context for measures helps the agent answer questions about key performance indicators (KPIs) or other calculated values.

As an example, you can define a profit measure as a calculation of the earnings minus the cost as follows:

- tables:
    - table:
        - name: bigquery-public-data.thelook_ecommerce.orders
        - measures:
            - measure:
                - name: profit
                - description: Raw profit (earnings minus cost).
                - exp: earnings - cost
                - synonyms: gains
golden_queries
The golden_queries key, which is nested within a table object, takes a list of golden_query objects. Golden queries help the agent provide more accurate and relevant responses to common or important questions that you can define.

As an example, you can define golden queries for common analyses for the data in the orders table as follows:

- tables:
    - table:
        - golden_queries:
            - golden_query:
                - natural_language_query: How many orders are there?
                - sql_query: SELECT COUNT(*) FROM sqlgen-testing.thelook_ecommerce.orders
            - golden_query:
                - natural_language_query: How many orders were shipped?
                - sql_query: >-
                    SELECT COUNT(*) FROM sqlgen-testing.thelook_ecommerce.orders
                    WHERE status = 'shipped'
golden_action_plans
The golden_action_plans key, which is nested within a table object, takes a list of golden_action_plan objects. You can use golden action plans to provide the agent with examples of how to handle multi-step requests, such as to fetch data and then create a visualization.

As an example, you can define an action plan for showing order breakdowns by age group and include details about the SQL query and visualization-related steps:

- tables:
    - table:
        - golden_action_plans:
            - golden_action_plan:
                - natural_language_query: Show me the number of orders broken down by age group.
                - action_plan:
                    - step: >-
                        Run a SQL query that joins the table
                        sqlgen-testing.thelook_ecommerce.orders and
                        sqlgen-testing.thelook_ecommerce.users to get a
                        breakdown of order count by age group.
                    - step: >-
                        Create a vertical bar plot using the retrieved data,
                        with one bar per age group.
relationships
The relationships key contains a list of join relationships between tables. By defining join relationships, you can help the agent understand how to join data from multiple tables when answering questions.

As an example, you can define an orders_to_user relationship between the bigquery-public-data.thelook_ecommerce.orders table and the bigquery-public-data.thelook_ecommerce.users table as follows:

- relationships:
    - relationship:
        - name: orders_to_user
        - description: >-
            Connects customer order data to user information with the user_id and id fields to allow an aggregated view of sales by customer demographics.
        - relationship_type: many-to-one
        - join_type: left
        - left_table: bigquery-public-data.thelook_ecommerce.orders
        - right_table: bigquery-public-data.thelook_ecommerce.users
        - relationship_columns:
            - left_column: user_id
            - right_column: id
glossaries
The glossaries key lists definitions for business terms, jargon, and abbreviations that are relevant to your data and use case. By providing glossary definitions, you can help the agent accurately interpret and answer questions that use specific business language.

As an example, you can define terms like common business statuses and "OMPF" according to your specific business context as follows:

- glossaries:
    - glossary:
        - term: complete
        - description: Represents an order status where the order has been completed.
        - synonyms: 'finish, done, fulfilled'
    - glossary:
        - term: shipped
        - description: Represents an order status where the order has been shipped to the customer.
    - glossary:
        - term: returned
        - description: Represents an order status where the customer has returned the order.
    - glossary:
        - term: OMPF
        - description: Order Management and Product Fulfillment
additional_descriptions
The additional_descriptions key lists any additional general instructions or context that is not covered elsewhere in the system instructions. By providing additional descriptions, you can help the agent better understand the context of your data and use case.

As an example, you can use the additional_descriptions key to provide information about your organization as follows:

- additional_descriptions:
    - text: All the sales data pertains to The Look, a fictitious ecommerce store.
    - text: 'Orders can be of three categories: food, clothes, and electronics.'
Example: System instructions in BigQuery
The following example shows sample system instructions for a fictitious sales analyst agent:

- system_instruction: >-
    You are an expert sales analyst for a fictitious ecommerce store. You will answer questions about sales, orders, and customer data. Your responses should be concise and data-driven.
- tables:
    - table:
        - name: bigquery-public-data.thelook_ecommerce.orders
        - description: Data for orders in The Look, a fictitious ecommerce store.
        - synonyms: sales
        - tags: 'sale, order, sales_order'
        - fields:
            - field:
                - name: order_id
                - description: The unique identifier for each customer order.
            - field:
                - name: user_id
                - description: The unique identifier for each customer.
            - field:
                - name: status
                - description: The current status of the order.
                - sample_values:
                    - complete
                    - shipped
                    - returned
            - field:
                - name: created_at
                - description: >-
                    The date and time at which the order was created in timestamp
                    format.
            - field:
                - name: returned_at
                - description: >-
                    The date and time at which the order was returned in timestamp
                    format.
            - field:
                - name: num_of_items
                - description: The total number of items in the order.
                - aggregations: 'sum, avg'
            - field:
                - name: earnings
                - description: The sales revenue for the order.
                - aggregations: 'sum, avg'
            - field:
                - name: cost
                - description: The cost for the items in the order.
                - aggregations: 'sum, avg'
        - measures:
            - measure:
                - name: profit
                - description: Raw profit (earnings minus cost).
                - exp: earnings - cost
                - synonyms: gains
        - golden_queries:
            - golden_query:
                - natural_language_query: How many orders are there?
                - sql_query: SELECT COUNT(*) FROM sqlgen-testing.thelook_ecommerce.orders
            - golden_query:
                - natural_language_query: How many orders were shipped?
                - sql_query: >-
                    SELECT COUNT(*) FROM sqlgen-testing.thelook_ecommerce.orders
                    WHERE status = 'shipped'
        - golden_action_plans:
            - golden_action_plan:
                - natural_language_query: Show me the number of orders broken down by age group.
                - action_plan:
                    - step: >-
                        Run a SQL query that joins the table
                        sqlgen-testing.thelook_ecommerce.orders and
                        sqlgen-testing.thelook_ecommerce.users to get a
                        breakdown of order count by age group.
                    - step: >-
                        Create a vertical bar plot using the retrieved data,
                        with one bar per age group.
    - table:
        - name: bigquery-public-data.thelook_ecommerce.users
        - description: Data for users in The Look, a fictitious ecommerce store.
        - synonyms: customers
        - tags: 'user, customer, buyer'
        - fields:
            - field:
                - name: id
                - description: The unique identifier for each user.
            - field:
                - name: first_name
                - description: The first name of the user.
                - tag: person
                - sample_values: 'alex, izumi, nur'
            - field:
                - name: last_name
                - description: The first name of the user.
                - tag: person
                - sample_values: 'warmer, stilles, smith'
            - field:
                - name: age_group
                - description: The age demographic group of the user.
                - sample_values:
                    - 18-24
                    - 25-34
                    - 35-49
                    - 50+
            - field:
                - name: email
                - description: The email address of the user.
                - tag: contact
                - sample_values: '222larabrown@gmail.com, cloudysanfrancisco@gmail.com'
        - golden_queries:
            - golden_query:
                - natural_language_query: How many unique customers are there?
                - sql_query: >-
                    SELECT COUNT(DISTINCT id) FROM
                    bigquery-public-data.thelook_ecommerce.users
            - golden_query:
                - natural_language_query: How many users in the 25-34 age group have a cymbalgroup email address?
                - sql_query: >-
                    SELECT COUNT(DISTINCT id) FROM
                    bigquery-public-data.thelook_ecommerce.users WHERE users.age_group =
                    '25-34' AND users.email LIKE '%@cymbalgroup.com';
    - relationships:
        - relationship:
            - name: orders_to_user
            - description: >-
                Connects customer order data to user information with the user_id and id fields to allow an aggregated view of sales by customer demographics.
            - relationship_type: many-to-one
            - join_type: left
            - left_table: bigquery-public-data.thelook_ecommerce.orders
            - right_table: bigquery-public-data.thelook_ecommerce.users
            - relationship_columns:
                - left_column: user_id
                - right_column: id
- glossaries:
    - glossary:
        - term: complete
        - description: Represents an order status where the order has been completed.
        - synonyms: 'finish, done, fulfilled'
    - glossary:
        - term: shipped
        - description: Represents an order status where the order has been shipped to the customer.
    - glossary:
        - term: returned
        - description: Represents an order status where the customer has returned the order.
    - glossary:
        - term: OMPF
        - description: Order Management and Product Fulfillment
- additional_descriptions:
    - text: All the sales data pertains to The Look, a fictitious ecommerce store.
    - text: 'Orders can be of three categories: food, clothes, and electronics.'
Was this helpful?

Send feedback
Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2025-10-02 UTC.

Why Google
Choosing Google Cloud
Trust and security
Modern Infrastructure Cloud
Multicloud
Global infrastructure
Customers and case studies
Analyst reports
Whitepapers
Products and pricing
See all products
See all solutions
Google Cloud for Startups
Google Cloud Marketplace
Google Cloud pricing
Contact sales
Support
Community forums
Support
Release Notes
System status
Resources
GitHub
Getting Started with Google Cloud
Google Cloud documentation
Code samples
Cloud Architecture Center
Training and Certification
Developer Center
Engage
Blog
Events
X (Twitter)
Google Cloud on YouTube
Google Cloud Tech on YouTube
Become a Partner
Google Cloud Affiliate Program
Press Corner
About Google
Privacy
Site terms
Google Cloud terms
Our third decade of climate action: join us
Sign up for the Google Cloud newsletter
Subscribe

English
The new page has loaded..




Skip to main content
Google Cloud
Documentation
Technology areas

Cross-product tools

Related sites


Search
/


English
Console

Gemini for Google Cloud
Overview
Conversational Analytics API
Contact Us
Filter

Gemini for Google Cloud 
Documentation 
Conversational Analytics API
Was this helpful?

Send feedbackDefine data agent context for Looker data sources

bookmark_border

This product or feature is subject to the "Pre-GA Offerings Terms" in the General Service Terms section of the Service Specific Terms. Pre-GA products and features are available "as is" and might have limited support. For more information, see the launch stage descriptions.

Writing effective system instructions can provide your Conversational Analytics API data agents with useful context for answering questions about your data sources. System instructions are a kind of authored context that data agent owners can provide to shape the behavior of a data agent and to refine the API's responses.

This page describes how to write system instructions for Looker data sources, which are based on Looker Explores.

Define context in system instructions
System instructions consist of a series of key components and objects that provide the data agent with details about the data source and guidance about the agent's role when answering questions. You can provide system instructions to the data agent in the system_instruction parameter as a YAML-formatted string.

Important: Although the system_instruction parameter is optional and the structure is up to your discretion, we recommend that you provide well-structured system instructions to enable the agent to give more accurate and relevant responses.
The following YAML template shows an example of how you might structure system instructions for a Looker data source:



- system_instruction: str # Describe the expected behavior of the agent
  - golden_queries: # Define queries for common analyses of your Explore data
    - golden_query:
      - natural_language_query: str
      - looker_query: str
        - model: string
        - view: string
        - fields: list[str]
        - filters: list[str]
        - sorts: list[str]
        - limit: str
        - query_timezone: str
  - golden_action_plans: # Provide the agent with guidance on how to respond to queries that might require multiple steps to answer
    - golden_action_plan:
      - natural_language_query: str
        - action_plan:
          - step: str
- glossaries: # Define business terms, jargon, and abbreviations that are relevant to your use case
    - glossary:
        - term: str
        - description: str
        - synonyms: list[str]
- additional_descriptions: # List any additional general instructions
    - text: str
Descriptions of key components of system instructions
The following sections contain examples of key components of system instructions in Looker. These keys include the following:

system_instruction
golden_queries
golden_action_plans
glossaries
additional_descriptions
system_instruction
Use the system_instruction key to define the agent's role and persona. This initial instruction sets the tone and style for the API's responses and helps the agent understand its core purpose.

For example, you can define an agent as a sales analyst for a fictitious ecommerce store as follows:



- system_instruction: >-
    You are an expert sales analyst for a fictitious ecommerce store. You will answer questions about sales, orders, and customer data. Your responses should be concise and data-driven.
golden_queries
The golden_queries key takes a list of golden_query objects. Golden queries help the agent provide more accurate and relevant responses to common or important questions that you can define. By providing the agent with both a natural language query and the corresponding Looker query and LookML information for each golden query, you can guide the agent to provide higher quality and more consistent results. As an example, you can define golden queries for common analyses for the data in the order_items table as follows:



- golden_queries:
  - natural_language_query: what were total sales over the last year
  - looker_query:
      - model: thelook
      - view: order_items
      - fields: order_items.total_sale_price
      - filters: order_items.created_date: last year
      - sorts: order_items.total_sale_price desc 0
      - limit: null
      - query_timezone: America/Los_Angeles
golden_action_plans
The golden_action_plans key lets you define a series of golden_action_plan objects. Each golden action plan provides the agent with guidance on how to respond questions that might require multiple steps to answer, such as to fetch data and then create a visualization. As an example, you can define an action plan for showing order breakdowns by age group and include details about the Looker query and visualization-related steps as follows:

- golden_action_plans:
  - golden_action_plan:
    - natural_language_query: What is the correlation between customer age cohort and buying propensity?
    - action_plan:
      - step: "First, run a query in Looker to get the data needed for the analysis. You need to group by `users.age` (NOT AGE TIER) and calculate the average `order_items.30_day_repeat_purchase_rate` for each age."
      - step: "Then, pass the resulting data table to the Python tool. Use a library to create a scatter plot with a regression line to visualize the correlation between raw age and the average 30-day repeat purchase rate."
glossaries
The glossaries key lists definitions for business terms, jargon, and abbreviations that are relevant to your data and use case but that don't already appear in your data. As an example, you can define terms like common business statuses and "Loyal Customer" according to your specific business context as follows:

- glossaries:
  - glossary:
      - term: Loyal Customer
      - description: A customer who has made more than one purchase. Maps to the dimension 'user_order_facts.repeat_customer' being 'Yes'. High value loyal customers are those with high 'user_order_facts.lifetime_revenue'.
      - synonyms:
        - repeat customer
        - returning customer
additional_descriptions
The additional_descriptions key lists any additional general instructions or context that is not covered elsewhere in the system instructions. As an example, you can use the additional_descriptions key to provide information about your agent as follows:

- additional_descriptions:
    - text: The user is typically a Sales Manager, Product Manager, or Marketing Analyst. They need to understand performance trends, build customer lists for campaigns, and analyze product sales.
Example: System instructions in Looker using YAML
The following example shows sample system instructions for a fictitious sales analyst agent.

- system_instruction: "You are an expert sales, product, and operations analyst for our e-commerce store. Your primary function is to answer questions by querying the 'Order Items' Explore. Always be concise and data-driven. When asked about 'revenue' or 'sales', use 'order_items.total_sale_price'. For 'profit' or 'margin', use 'order_items.total_gross_margin'. For 'customers' or 'users', use 'users.count'. The default date for analysis is 'order_items.created_date' unless specified otherwise. For advanced statistical questions, such as correlation or regression analysis, use the Python tool to fetch the necessary data, perform the calculation, and generate a plot (like a scatter plot or heatmap)."
  - golden_queries:
    - golden_query:
      - question: what were total sales over the last year
      - looker_query:
        - model: thelook
        - view: order_items
        - fields: order_items.total_sale_price
          - filters: order_items.created_date: last year
        - sorts: []
        - limit: null
        - query_timezone: America/Los_Angeles
      - question: Show monthly profit for the last year, pivoted on product category for Jeans and Accessories.
      - looker_query:
        - model: thelook
        - view: order_items
        - fields:
          - name: products.category
          - name: order_items.total_gross_margin
          - name: order_items.created_month_name
        - filters:
          - products.category: Jeans,Accessories
          - order_items.created_date: last year
        - pivots: products.category
        - sorts:
          - order_items.created_month_name asc
          - order_items.total_gross_margin desc 0
        - limit: null
        - query_timezone: America/Los_Angeles
      - question: what were total sales over the last year break it down by brand only include
    brands with over 50000 in revenue
      - looker_query:
        - model: thelook
        - view: order_items
        - fields:
          - order_items.total_sale_price
          - products.brand
        - filters:
          - order_items.created_date: last year
          - order_items.total_sale_price: '>50000'
        - sorts: order_items.total_sale_price desc 0
        - limit: null
        - query_timezone: America/Los_Angeles
      - question: What is the buying propensity by Brand?
      - looker_query:
          - model: thelook
          - view: order_items
          - fields:
            - order_items.30_day_repeat_purchase_rate
            - products.brand
          - filters: {}
          - sorts: order_items.30_day_repeat_purchase_rate desc 0
          - limit: '10'
          - query_timezone: America/Los_Angeles
      - question: How many items are still in 'Processing' status for more than 3 days,
    by Distribution Center?
      - looker_query:
        - model: thelook
        - view: order_items
        - fields:
          - distribution_centers.name
          - order_items.count
        - filters:
            - order_items.created_date: before 3 days ago
            - order_items.status: Processing
        - sorts: order_items.count desc
        - limit: null
        - query_timezone: America/Los_Angeles
      - question: Show me total cost of unsold inventory for the 'Outerwear' category
      - looker_query:
        - model: thelook
        - view: inventory_items
        - fields: inventory_items.total_cost
        - filters:
          - inventory_items.is_sold: No
          - products.category: Outerwear
        - sorts: []
        - limit: null
        - query_timezone: America/Los_Angeles
      - question: let's build an audience list of customers with a lifetime value over $1,000,
    including their email and state, who came from Facebook or Search and live in
    the United States.
      - looker_query:
        - model: thelook
        - view: users
        - fields:
          - users.email
          - users.state
          - user_order_facts.lifetime_revenue
        - filters:
          - user_order_facts.lifetime_revenue: '>1000'
          - users.country: United States
          - users.traffic_source: Facebook,Search
        - sorts: user_order_facts.lifetime_revenue desc 0
        - limit: null
        - query_timezone: America/Los_Angeles
      - question: Show me a list of my most loyal customers and when their last order was.
      - looker_query:
        - model: thelook
        - view: users
        - fields:
          - users.id
          - users.email
          - user_order_facts.lifetime_revenue
          - user_order_facts.lifetime_orders
          - user_order_facts.latest_order_date
        - filters: user_order_facts.repeat_customer: Yes
        - sorts: user_order_facts.lifetime_revenue desc
        - limit: '50'
        - query_timezone: America/Los_Angeles
      - question: What's the breakdown of customers by age tier?
      - looker_query:
        - model: thelook
        - view: users
        - fields:
          - users.age_tier
          - users.count
        - filters: {}
        - sorts: users.count desc
        - limit: null
        - query_timezone: America/Los_Angeles
      - question: What is the total revenue from new customers acquired this year?
      - looker_query:
        - model: thelook
        - view: order_items
        - fields: order_items.total_sale_price
        - filters: user_order_facts.first_order_year: this year
        - sorts: []
        - limit: null
        - query_timezone: America/Los_Angeles
- golden_action_plans:
  - golden_action_plan:
    - natural_language_query: whats the correlation between customer age cohort and buying propensity.
    - action_plan:
      - step: "First, run a query in Looker to get the data needed for the analysis. You need to group by `users.age` (NOT AGE TIER) and calculate the average `order_items.30_day_repeat_purchase_rate` for each age."
      - step: "Then, pass the resulting data table to the Python tool. Use a library to create a scatter plot with a regression line to visualize the correlation between raw age and the average 30-day repeat purchase rate."
- glossaries:
  - term: Revenue
  - description: The total monetary value from items sold. Maps to the measure 'order_items.total_sale_price'.
  - synonyms:
    - sales
    - total sales
    - income
    - turnover
  - term: Profit
  - description: Revenue minus the cost of goods sold. Maps to the measure 'order_items.total_gross_margin'.
  - synonyms:
    - margin
    - gross margin
    - contribution
  - term: Buying Propensity
  - description: Measures the likelihood of a customer to purchase again soon. Primarily maps to the 'order_items.30_day_repeat_purchase_rate' measure.
  - synonyms:
    - repeat purchase rate
    - repurchase likelihood
    - customer velocity
  - term: Customer Lifetime Value
  - description: The total revenue a customer has generated over their entire history with us. Maps to 'user_order_facts.lifetime_revenue'.
  - synonyms:
    - CLV
    - LTV
    - lifetime spend
    - lifetime value
  - term: Loyal Customer
  - description: "A customer who has made more than one purchase. Maps to the dimension 'user_order_facts.repeat_customer' being 'Yes'. High value loyal customers are those with high 'user_order_facts.lifetime_revenue'."
  - synonyms:
    - repeat customer
    - returning customer
  - term: Active Customer
  - description: "A customer who is currently considered active based on their recent purchase history. Mapped to 'user_order_facts.currently_active_customer' being 'Yes'."
  - synonyms:
    - current customer
    - engaged shopper
  - term: Audience
  - description: A list of customers, typically identified by their email address, for marketing or analysis purposes.
  - synonyms:
    - audience list
    - customer list
    - segment
  - term: Return Rate
  - description: The percentage of items that are returned by customers after purchase. Mapped to 'order_items.return_rate'.
  - synonyms:
    - returns percentage
    - RMA rate
  - term: Processing Time
  - description: The time it takes to prepare an order for shipment from the moment it is created. Maps to 'order_items.average_days_to_process'.
  - synonyms:
    - fulfillment time
    - handling time
  - term: Inventory Turn
  - description: "A concept related to how quickly stock is sold. This can be analyzed using 'inventory_items.days_in_inventory' (lower days means higher turn)."
  - synonyms:
    - stock turn
    - inventory turnover
    - sell-through
  - term: New vs Returning Customer
  - description: "A classification of whether a purchase was a customer's first ('order_facts.is_first_purchase' is Yes) or if they are a repeat buyer ('user_order_facts.repeat_customer' is Yes)."
  - synonyms:
    - customer type
    - first-time buyer
- additional_descriptions:
  - text: The user is typically a Sales Manager, Product Manager, or Marketing Analyst. They need to understand performance trends, build customer lists for campaigns, and analyze product sales.
  - text: This agent can answer complex questions by joining data about sales line items, products, users, inventory, and distribution centers.
Related resource
Guide agent behavior with authored context
Was this helpful?

Send feedback
Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2025-10-02 UTC.

Why Google
Choosing Google Cloud
Trust and security
Modern Infrastructure Cloud
Multicloud
Global infrastructure
Customers and case studies
Analyst reports
Whitepapers
Products and pricing
See all products
See all solutions
Google Cloud for Startups
Google Cloud Marketplace
Google Cloud pricing
Contact sales
Support
Community forums
Support
Release Notes
System status
Resources
GitHub
Getting Started with Google Cloud
Google Cloud documentation
Code samples
Cloud Architecture Center
Training and Certification
Developer Center
Engage
Blog
Events
X (Twitter)
Google Cloud on YouTube
Google Cloud Tech on YouTube
Become a Partner
Google Cloud Affiliate Program
Press Corner
About Google
Privacy
Site terms
Google Cloud terms
Our third decade of climate action: join us
Sign up for the Google Cloud newsletter
Subscribe

English
The new page has loaded.



Skip to main content
Google Cloud
Documentation
Technology areas

Cross-product tools

Related sites


Search
/


English
Console

Gemini for Google Cloud
Overview
Conversational Analytics API
Contact Us
Filter

Gemini for Google Cloud 
Documentation 
Conversational Analytics API
Was this helpful?

Send feedbackBuild a data agent using HTTP and Python

bookmark_border

This product or feature is subject to the "Pre-GA Offerings Terms" in the General Service Terms section of the Service Specific Terms. Pre-GA products and features are available "as is" and might have limited support. For more information, see the launch stage descriptions.

This page guides you through using Python to make HTTP requests to the Conversational Analytics API (accessed through geminidataanalytics.googleapis.com).

The sample Python code on this page shows how to complete the following tasks:

Configure initial settings and authentication
Connect to a Looker, BigQuery, or Looker Studio data source
Create a data agent
Create a conversation
Manage data agents and conversations
Use the API to ask questions
Create a stateless multi-turn conversation
A complete version of the sample code is included at the end of the page, along with the helper functions that are used to stream the API response.

Tip: You can run the code samples on this page in the interactive Conversational Analytics API HTTP Colaboratory notebook.
Configure initial settings and authentication
The following sample Python code performs these tasks:

Imports the required Python libraries
Obtains an access token for HTTP authentication by using the Google Cloud CLI
Defines variables for the billing project and system instructions


from pygments import highlight, lexers, formatters
import pandas as pd
import json as json_lib
import requests
import json
import altair as alt
import IPython
from IPython.display import display, HTML
import google.auth
from google.auth.transport.requests import Request

from google.colab import auth
auth.authenticate_user()

access_token = !gcloud auth application-default print-access-token
headers = {
        "Authorization": f"Bearer {access_token[0]}",
        "Content-Type": "application/json",
        "x-server-timeout": "300", # Custom timeout up to 600s
}

billing_project = 'YOUR-BILLING-PROJECT'
system_instruction = 'YOUR-SYSTEM-INSTRUCTIONS'
Replace the sample values as follows:

YOUR-BILLING-PROJECT: The ID of the billing project where you've enabled the required APIs.
YOUR-SYSTEM-INSTRUCTIONS: System instructions to guide the agent's behavior and customize it for your data needs. For example, you can use system instructions to define business terms, control response length, or set data formatting. Ideally, define system instructions by using the recommended YAML format in Write effective system instructions to provide detailed and structured guidance.
Authenticate to Looker
If you plan to connect to a Looker data source, you will need to authenticate to the Looker instance.

Using API keys
Using access tokens
The following Python code sample demonstrates how to authenticate your agent to a Looker instance using API keys.



looker_credentials = {
    "oauth": {
        "secret": {
            "client_id": "YOUR-LOOKER-CLIENT-ID",
            "client_secret": "YOUR-LOOKER-CLIENT-SECRET",
        }
    }
}
Replace the sample values as follows:

YOUR-LOOKER-CLIENT-ID: The client ID of your generated Looker API key.
YOUR-LOOKER-CLIENT-SECRET: The client secret of your generated Looker API key.
Connect to a data source
The following sections show how to define the connection details for your agent's data sources. Your agent can connect to data in Looker, BigQuery, or Looker Studio.

Connect to Looker data
The following sample code defines a connection to a Looker Explore. To establish a connection with a Looker instance, verify that you've generated Looker API keys, as described in Authenticate and connect to a data source with the Conversational Analytics API. You can connect to up to five Looker Explores at a time with the Conversational Analytics API.

When you connect to a Looker data source, note the following:

You can query any included Explore in a conversation.
An agent can only query one Explore at a time. It is not possible to perform queries across multiple Explores simultaneously.
An agent can query multiple Explores in the same conversation.
An agent can query multiple Explores in a conversation that includes questions with multiple parts, or in conversations that include follow-up questions.

For example: A user connects two Explores, one called cat-explore and one called dog-explore. The user inputs the question "What's greater: the count of cats or the count of dogs?" This would create two queries: one to count the number of cats in cat-explore and one to count the number of dogs in dog-explore. The agent compares the number from both queries after completing both queries.

Note: Don't include credentials in the data source during agent creation.
looker_instance_uri = "https://my_company.looker.com"
looker_data_source = {
    "looker": {
        "explore_references": {
            "looker_instance_uri": "https://your_company.looker.com"
            "lookml_model": "your_model",
            "explore": "your_explore",
       },
       {
            "looker_instance_uri": looker_instance_uri,
            "lookml_model": "your_model_2",
            "explore": "your_explore_2",
       },
       # Do not include the following line during agent creation
       "credentials": looker_credentials
    }
}
Replace the sample values as follows:

https://your_company.looker.com: The complete URL of your Looker instance.
your_model: The name of the LookML model that includes the Explore that you want to connect to.
your_explore: The name of the Looker Explore that you want the data agent to query.
my_model_2: The name of the second LookML model that includes the Explore that you want to connect to. You can repeat this variable for additional models for up to five Explores.
my_explore_2: The name of the additional Looker Explore that you want the data agent to query. You can repeat this variable to include up to five Explores.
Connect to BigQuery data
With the Conversational Analytics API, there are no hard limits on the number of BigQuery tables that you can connect to. However, connecting to a large number of tables can reduce accuracy or cause you to exceed the model's input token limit.

Note: Queries that require complex joins across multiple tables might result in less accurate responses.
The following sample code defines a connection to multiple BigQuery tables.

Important: Make sure you have the necessary Identity and Access Management (IAM) permissions to query any BigQuery tables that you're connecting to.
bigquery_data_sources = {
    "bq": {
        "tableReferences": [
            {
                "projectId": "my_project_id",
                "datasetId": "my_dataset_id",
                "tableId": "my_table_id"
            },
            {
                "projectId": "my_project_id_2",
                "datasetId": "my_dataset_id_2",
                "tableId": "my_table_id_2"
            },
            {
                "projectId": "my_project_id_3",
                "datasetId": "my_dataset_id_3",
                "tableId": "my_table_id_3"
            },
        ]
    }
}
Replace the sample values as follows:

my_project_id: The ID of the Google Cloud project that contains the BigQuery dataset and table that you want to connect to. To connect to a public dataset, specify bigquery-public-data.
my_dataset_id: The ID of the BigQuery dataset.
my_table_id: The ID of the BigQuery table.
Connect to Looker Studio data
The following sample code defines a connection to a Looker Studio data source.

looker_studio_data_source = {
    "studio":{
        "studio_references": [
            {
              "studio_datasource_id": "studio_datasource_id"
            }
        ]
    }
}
Replace studio_datasource_id with the data source ID.

Create a data agent
The following sample code demonstrates how to create the data agent by sending an HTTP POST request to the data agent creation endpoint. The request payload includes the following details:

The full resource name for the agent. This value includes the project ID, location, and a unique identifier for the agent.
The data agent's description.
The data agent's context, including the system description (defined in Configure initial settings and authentication) and the data source that the agent uses (defined in Connect to a data source).
You can also optionally enable advanced analysis with Python by including the options parameter in the request payload. See the REST Resource: projects.locations.dataAgents for more information about the options parameter, and options that you can configure for the conversation.

The following example uses the bigquery_data_sources variable that was created in the section on connecting to BigQuery to configure the data agent to connect to a BigQuery table.

To use Looker data instead, replace bigquery_data_sources with looker_data_source.

To use Looker Studio data instead, replace bigquery_data_sources with looker_studio_data_source.

data_agent_url = f"https://geminidataanalytics.googleapis.com/v1beta/projects/{billing_project}/locations/{location}/dataAgents"

data_agent_id = "data_agent_1"

data_agent_payload = {
      "name": f"projects/{billing_project}/locations/{location}/dataAgents/{data_agent_id}", # Optional
      "description": "This is the description of data_agent_1.", # Optional

      "data_analytics_agent": {
          "published_context": {
              "datasource_references": bigquery_data_sources,
              "system_instruction": system_instruction,
              # Optional: To enable advanced analysis with Python, include the following options block:
              "options": {
                  "analysis": {
                      "python": {
                          "enabled": True
                      }
                  }
              }
          }
      }
  }

params = {"data_agent_id": data_agent_id} # Optional

data_agent_response = requests.post(
    data_agent_url, params=params, json=data_agent_payload, headers=headers
)

if data_agent_response.status_code == 200:
    print("Data Agent created successfully!")
    print(json.dumps(data_agent_response.json(), indent=2))
else:
    print(f"Error creating Data Agent: {data_agent_response.status_code}")
    print(data_agent_response.text)
Replace the sample values as follows:

data_agent_1: A unique identifier for the data agent. This value is used in the agent's resource name and as the data_agent_id URL query parameter.
This is the description of data_agent_1.: A description for the data agent.
Create a conversation
The following sample code demonstrates how to create a conversation with your data agent.

conversation_url = f"https://geminidataanalytics.googleapis.com/v1beta/projects/{billing_project}/locations/{location}/conversations"

data_agent_id = "data_agent_1"
conversation_id = "conversation_1"

conversation_payload = {
    "agents": [
        f"projects/{billing_project}/locations/{location}/dataAgents/{data_agent_id}"
    ],
    "name": f"projects/{billing_project}/locations/{location}/conversations/{conversation_id}"
}
params = {
    "conversation_id": conversation_id
}

conversation_response = requests.post(conversation_url, headers=headers, params=params, json=conversation_payload)

if conversation_response.status_code == 200:
    print("Conversation created successfully!")
    print(json.dumps(conversation_response.json(), indent=2))
else:
    print(f"Error creating Conversation: {conversation_response.status_code}")
    print(conversation_response.text)

Replace the sample values as follows:

data_agent_1: The ID of the data agent, as defined in the sample code block in Create a data agent.
conversation_1: A unique identifier for the conversation.
Manage data agents and conversations
The following code samples show how to manage your data agents and conversations by using the Conversational Analytics API. You can perform the following tasks:

Get a data agent
List data agents
List accessible data agents
Update a data agent
Set the IAM policy for a data agent
Get the IAM policy for a data agent
Delete a data agent
Get a conversation
List conversations
List messages in a conversation
Get a data agent
The following sample code demonstrates how to fetch an existing data agent by sending an HTTP GET request to the data agent resource URL.

data_agent_id = "data_agent_1"
data_agent_url = f"{base_url}/v1beta/projects/{billing_project}/locations/{location}/dataAgents/{data_agent_id}"

data_agent_response = requests.get(
    data_agent_url, headers=headers
)

if data_agent_response.status_code == 200:
    print("Fetched Data Agent successfully!")
    print(json.dumps(data_agent_response.json(), indent=2))
else:
    print(f"Error: {data_agent_response.status_code}")
    print(data_agent_response.text)
In the previous example, replace data_agent_1 with the ID of the data agent that you want to fetch.

List data agents
The following code demonstrates how to list all the data agents for a given project by sending an HTTP GET request to the dataAgents endpoint.

To list all agents, you must have the geminidataanalytics.dataAgents.list permission on the project. For more information on which IAM roles include this permission, see the list of predefined roles.

billing_project = "YOUR-BILLING-PROJECT"
location = "global"
data_agent_url = f"{base_url}/v1beta/projects/{billing_project}/locations/{location}/dataAgents"

data_agent_response = requests.get(
    data_agent_url, headers=headers
)

if data_agent_response.status_code == 200:
    print("Data Agents Listed successfully!")
    print(json.dumps(data_agent_response.json(), indent=2))
else:
    print(f"Error Listing Data Agents: {data_agent_response.status_code}")
Replace YOUR-BILLING-PROJECT with the ID of your billing project.

List accessible data agents
The following code demonstrates how to list all the accessible data agents for a given project by sending an HTTP GET request to the dataAgents:listAccessible endpoint.

billing_project = "YOUR-BILLING-PROJECT"
creator_filter = "YOUR-CREATOR-FILTER"
location = "global"
data_agent_url = f"{base_url}/v1beta/projects/{billing_project}/locations/{location}/dataAgents:listAccessible"

params = {
    "creator_filter": creator_filter
}

data_agent_response = requests.get(
    data_agent_url, headers=headers, params=params
)

if data_agent_response.status_code == 200:
    print("Accessible Data Agents Listed successfully!")
    print(json.dumps(data_agent_response.json(), indent=2))
else:
    print(f"Error Listing Accessible Data Agents: {data_agent_response.status_code}")
Replace the sample values as follows:

YOUR-BILLING-PROJECT: The ID of your billing project.
YOUR-CREATOR-FILTER: The filter to apply based on the creator of the data agent. Possible values include NONE (default), CREATOR_ONLY, and NOT_CREATOR_ONLY.
Update a data agent
The following sample code demonstrates how to update a data agent by sending an HTTP PATCH request to the data agent resource URL. The request payload includes the new values for the fields that you want to change, and the request parameters include an updateMask parameter, which specifies the fields to be updated.

data_agent_id = "data_agent_1"
billing_project = "YOUR-BILLING-PROJECT"
location = "global"

data_agent_url = f"{base_url}/v1beta/projects/{billing_project}/locations/{location}/dataAgents/{data_agent_id}"

payload = {
    "description": "Updated description of the data agent.",
    "data_analytics_agent": {
        "published_context": {
            "datasource_references": bigquery_data_sources,
            "system_instruction": system_instruction
        }
    },
}

fields = ["description", "data_analytics_agent"]
params = {
    "updateMask": ",".join(fields)
}

data_agent_response = requests.patch(
    data_agent_url, headers=headers, params=params, json=payload
)

if data_agent_response.status_code == 200:
    print("Data Agent updated successfully!")
    print(json.dumps(data_agent_response.json(), indent=2))
else:
    print(f"Error Updating Data Agent: {data_agent_response.status_code}")
    print(data_agent_response.text)
Replace the sample values as follows:

data_agent_1: The ID of the data agent that you want to update.
YOUR-BILLING-PROJECT: The ID of your billing project.
Updated description of the data agent.: A new description for the data agent.
Set the IAM policy for a data agent
To share an agent, you can use the setIamPolicy method to assign IAM roles to users on a specific agent. The following sample code demonstrates how to make a POST call to the data agent URL with a payload that includes bindings. The binding specifies which roles should be assigned to which users.

Important: The setIamPolicy API call overrides existing permissions for the resource. To preserve existing policies, call the Get IAM policy API to fetch the existing policy, and then pass the existing policy along with any additional changes in the call to SetIamPolicy.
billing_project = "YOUR-BILLING-PROJECT"
location = "global"
data_agent_id = "data_agent_1"
role = "roles/geminidataanalytics.dataAgentEditor"
users = "222larabrown@gmail.com, cloudysanfrancisco@gmail.com"

data_agent_url = f"{base_url}/v1beta/projects/{billing_project}/locations/{location}/dataAgents/{data_agent_id}:setIamPolicy"

# Request body
payload = {
    "policy": {
        "bindings": [
            {
                "role": role,
                "members": [
                    f"user:{i.strip()}" for i in users.split(",")
                ]
            }
        ]
    }
}

data_agent_response = requests.post(
    data_agent_url, headers=headers, json=payload
)

if data_agent_response.status_code == 200:
    print("IAM Policy set successfully!")
    print(json.dumps(data_agent_response.json(), indent=2))
else:
    print(f"Error setting IAM policy: {data_agent_response.status_code}")
    print(data_agent_response.text)
Replace the sample values as follows:

YOUR-BILLING-PROJECT: The ID of your billing project.
data_agent_1: The ID of the data agent for which you want to set the IAM policy.
222larabrown@gmail.com, cloudysanfrancisco@gmail.com: A comma-separated list of user emails to which you want to grant the specified role.
Get the IAM policy for a data agent
The following sample code demonstrates how to fetch the IAM policy for a data agent by sending an HTTP POST request to the data agent URL. The request payload includes the data agent path.

billing_project = "YOUR-BILLING-PROJECT"
location = "global"
data_agent_id = "data_agent_1"

data_agent_url = f"{base_url}/v1beta/projects/{billing_project}/locations/{location}/dataAgents/{data_agent_id}:getIamPolicy"

# Request body
payload = {
    "resource": f"projects/{billing_project}/locations/{location}/dataAgents/{data_agent_id}"
}

data_agent_response = requests.post(
    data_agent_url, headers=headers, json=payload
)

if data_agent_response.status_code == 200:
    print("IAM Policy fetched successfully!")
    print(json.dumps(data_agent_response.json(), indent=2))
else:
    print(f"Error fetching IAM policy: {data_agent_response.status_code}")
    print(data_agent_response.text)
Replace the sample values as follows:

YOUR-BILLING-PROJECT: The ID of your billing project.
data_agent_1: The ID of the data agent for which you want to get the IAM policy.
Delete a data agent
The following sample code demonstrates how to soft delete a data agent by sending an HTTP DELETE request to the data agent resource URL. Soft deleting means that the agent is deleted but can still be retrieved within 30 days.

billing_project = "YOUR-BILLING-PROJECT"
location = "global"
data_agent_id = "data_agent_1"

data_agent_url = f"{base_url}/v1beta/projects/{billing_project}/locations/{location}/dataAgents/{data_agent_id}"

data_agent_response = requests.delete(
    data_agent_url, headers=headers
)

if data_agent_response.status_code == 200:
    print("Data Agent deleted successfully!")
    print(json.dumps(data_agent_response.json(), indent=2))
else:
    print(f"Error Deleting Data Agent: {data_agent_response.status_code}")
    print(data_agent_response.text)
Replace the sample values as follows:

YOUR-BILLING-PROJECT: The ID of your billing project.
data_agent_1: The ID of the data agent that you want to delete.
Get a conversation
The following sample code demonstrates how to fetch an existing conversation by sending an HTTP GET request to the conversation resource URL.

billing_project = "YOUR-BILLING-PROJECT"
location = "global"
conversation_id = "conversation_1"

conversation_url = f"{base_url}/v1beta/projects/{billing_project}/locations/{location}/conversations/{conversation_id}"

conversation_response = requests.get(conversation_url, headers=headers)

# Handle the response
if conversation_response.status_code == 200:
    print("Conversation fetched successfully!")
    print(json.dumps(conversation_response.json(), indent=2))
else:
    print(f"Error while fetching conversation: {conversation_response.status_code}")
    print(conversation_response.text)
Replace the sample values as follows:

YOUR-BILLING-PROJECT: The ID of your billing project.
conversation_1: The ID of the conversation that you want to fetch.
List conversations
The following sample code demonstrates how to list conversations for a given project by sending an HTTP GET request to the conversations endpoint.

By default, this method returns the conversations that you created. Admins (users with the cloudaicompanion.topicAdmin IAM role) can see all conversations within the project.

billing_project = "YOUR-BILLING-PROJECT"
location = "global"
conversation_url = f"{base_url}/v1beta/projects/{billing_project}/locations/{location}/conversations"

conversation_response = requests.get(conversation_url, headers=headers)

# Handle the response
if conversation_response.status_code == 200:
    print("Conversation fetched successfully!")
    print(json.dumps(conversation_response.json(), indent=2))
else:
    print(f"Error while fetching conversation: {conversation_response.status_code}")
    print(conversation_response.text)
Replace YOUR-BILLING-PROJECT with the ID of the billing project where you've enabled the required APIs.

List messages in a conversation
The following sample code demonstrates how to list all the messages in a conversation by sending an HTTP GET request to the conversation's messages endpoint.

To list messages, you must have the cloudaicompanion.topics.get permission on the conversation.

Note: This list operation also supports pagination.
billing_project = "YOUR-BILLING-PROJECT"
location = "global"

conversation_id = "conversation_1"

conversation_url = f"{base_url}/v1beta/projects/{billing_project}/locations/{location}/conversations/{conversation_id}/messages"

conversation_response = requests.get(conversation_url, headers=headers)

# Handle the response
if conversation_response.status_code == 200:
    print("Conversation fetched successfully!")
    print(json.dumps(conversation_response.json(), indent=2))
else:
    print(f"Error while fetching conversation: {conversation_response.status_code}")
    print(conversation_response.text)
Replace the sample values as follows:

YOUR-BILLING-PROJECT: The ID of your billing project.
conversation_1: The ID of the conversation for which you want to list messages.
Use the API to ask questions
After you've created a data agent and a conversation, you can ask questions of your data.

The Conversational Analytics API supports multi-turn conversations, which let users ask follow-up questions that build on previous context. The API provides the following methods for managing conversation history:

Stateful chat: Google Cloud stores and manages the conversation history. Stateful chat is inherently multi-turn, as the API retains context from previous messages. You only need to send the current message for each turn.
Stateless chat: Your application manages the conversation history. You must include the relevant previous messages with each new message. For detailed examples of how to manage multi-turn conversations in stateless mode, see Create a stateless multi-turn conversation.

Stateful chat
Stateless chat
Send a stateful chat request with a conversation reference
The following sample code demonstrates how to ask the API questions using the conversation that you defined in previous steps. This sample uses a get_stream helper function to stream the response.

Note: If your agent uses a Looker data source, you must uncomment the "credentials": looker_credentials line.
chat_url = f"https://geminidataanalytics.googleapis.com/v1beta/projects/{billing_project}/locations/{location}:chat"

data_agent_id = "data_agent_1"
conversation_id = "conversation_1"

# Construct the payload
chat_payload = {
    "parent": f"projects/{billing_project}/locations/global",
    "messages": [
        {
            "userMessage": {
                "text": "Make a bar graph for the top 5 states by the total number of airports"
            }
        }
    ],
    "conversation_reference": {
        "conversation": f"projects/{billing_project}/locations/{location}/conversations/{conversation_id}",
        "data_agent_context": {
            "data_agent": f"projects/{billing_project}/locations/{location}/dataAgents/{data_agent_id}",
            # "credentials": looker_credentials
        }
    }
}

# Call the get_stream function to stream the response
get_stream(chat_url, chat_payload)

Replace the sample values as follows:

data_agent_1: The ID of the data agent, as defined in the sample code block in Create a data agent.
conversation_1: A unique identifier for the conversation.
Make a bar graph for the top 5 states by the total number of airports was used as the sample prompt.
Create a stateless multi-turn conversation
To ask follow-up questions in a stateless conversation, your application must manage the conversation's context by sending the entire message history with each new request. The following sections show how to define and call helper functions to create a multi-turn conversation:

Send multi-turn requests
Process responses
Send multi-turn requests
The following multi_turn_Conversation helper function manages conversation context by storing messages in a list. This lets you send follow-up questions that build on previous turns. In the function's payload, you can reference a data agent or provide the data source directly by using inline context.

The following code sample uses a data agent reference. To use inline context instead, uncomment the inline_context block and comment out the data_agent_context block. The inline context sample uses a BigQuery data source.

If your agent uses a Looker data source and you're using a data agent reference, uncomment the "credentials": looker_credentials line.

chat_url = f"https://geminidataanalytics.googleapis.com/v1beta/projects/{billing_project}/locations/global:chat"

# List that is used to track previous turns and is reused across requests
conversation_messages = []

data_agent_id = "data_agent_1"

# Helper function for calling the API
def multi_turn_Conversation(msg):

  userMessage = {
      "userMessage": {
          "text": msg
      }
  }

  # Send a multi-turn request by including previous turns and the new message
  conversation_messages.append(userMessage)

  # Construct the payload
  chat_payload = {
      "parent": f"projects/{billing_project}/locations/global",
      "messages": conversation_messages,
      # Use a data agent reference
      "data_agent_context": {
          "data_agent": f"projects/{billing_project}/locations/{location}/dataAgents/{data_agent_id}",
          # "credentials": looker_credentials
      },
      # Use inline context
      # "inline_context": {
      #     "datasource_references": bigquery_data_sources,
      # }
  }

  # Call the get_stream_multi_turn helper function to stream the response
  get_stream_multi_turn(chat_url, chat_payload, conversation_messages)
In the previous example, replace data_agent_1 with the ID of the data agent, as defined in the sample code block in Create a data agent.

You can call the multi_turn_Conversation helper function for each turn of the conversation. The following sample code shows how to send an initial request and then a follow-up request that builds on the previous response.

# Send first-turn request
multi_turn_Conversation("Which species of tree is most prevalent?")

# Send follow-up-turn request
multi_turn_Conversation("Can you show me the results as a bar chart?")
In the previous example, replace the sample values as follows:

Which species of tree is most prevalent?: A natural language question to send to the data agent.
Can you show me the results as a bar chart?: A follow-up question that builds on or refines the previous question.
Process responses
The following get_stream_multi_turn function processes the streaming API response. This function is similar to the get_stream helper function, but it stores the response in the conversation_messages list to save the conversation context for the next turn.

def get_stream_multi_turn(url, json, conversation_messages):
    s = requests.Session()

    acc = ''

    with s.post(url, json=json, headers=headers, stream=True) as resp:
        for line in resp.iter_lines():
            if not line:
                continue

            decoded_line = str(line, encoding='utf-8')

            if decoded_line == '[{':
                acc = '{'
            elif decoded_line == '}]':
                acc += '}'
            elif decoded_line == ',':
                continue
            else:
                acc += decoded_line

            if not is_json(acc):
                continue

            data_json = json_lib.loads(acc)
            # Store the response that will be used in the next iteration
            conversation_messages.append(data_json)

            if not 'systemMessage' in data_json:
                if 'error' in data_json:
                    handle_error(data_json['error'])
                continue

            if 'text' in data_json['systemMessage']:
                handle_text_response(data_json['systemMessage']['text'])
            elif 'schema' in data_json['systemMessage']:
                handle_schema_response(data_json['systemMessage']['schema'])
            elif 'data' in data_json['systemMessage']:
                handle_data_response(data_json['systemMessage']['data'])
            elif 'chart' in data_json['systemMessage']:
                handle_chart_response(data_json['systemMessage']['chart'])
            else:
                colored_json = highlight(acc, lexers.JsonLexer(), formatters.TerminalFormatter())
                print(colored_json)
            print('\n')
            acc = ''
End-to-end code sample
The following expandable code sample contains all the tasks that are covered in this guide.

Build a data agent using HTTP and Python

The following expandable code sample contains the Python helper functions used to stream chat responses.

Helper Python functions to stream chat responses
Was this helpful?

Send feedback
Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2025-10-02 UTC.

Why Google
Choosing Google Cloud
Trust and security
Modern Infrastructure Cloud
Multicloud
Global infrastructure
Customers and case studies
Analyst reports
Whitepapers
Products and pricing
See all products
See all solutions
Google Cloud for Startups
Google Cloud Marketplace
Google Cloud pricing
Contact sales
Support
Community forums
Support
Release Notes
System status
Resources
GitHub
Getting Started with Google Cloud
Google Cloud documentation
Code samples
Cloud Architecture Center
Training and Certification
Developer Center
Engage
Blog
Events
X (Twitter)
Google Cloud on YouTube
Google Cloud Tech on YouTube
Become a Partner
Google Cloud Affiliate Program
Press Corner
About Google
Privacy
Site terms
Google Cloud terms
Our third decade of climate action: join us
Sign up for the Google Cloud newsletter
Subscribe

English
The new page has loaded.



Skip to main content
Google Cloud
Documentation
Technology areas

Cross-product tools

Related sites


Search
/


English
Console

Gemini for Google Cloud
Overview
Conversational Analytics API
Contact Us
Filter

Gemini for Google Cloud 
Documentation 
Conversational Analytics API
Was this helpful?

Send feedbackBuild a data agent using the Python SDK

bookmark_border

This product or feature is subject to the "Pre-GA Offerings Terms" in the General Service Terms section of the Service Specific Terms. Pre-GA products and features are available "as is" and might have limited support. For more information, see the launch stage descriptions.

This page shows you how to use the Python SDK to make requests to the Conversational Analytics API. The sample Python code demonstrates how to complete the following tasks:

Authenticate and set up your environment
Specify the billing project and system instructions
Connect to a Looker, BigQuery, or Looker Studio data source
Set up context for stateful or stateless chat
Create a data agent
Create a conversation
Manage data agents and conversations
Use the API to ask questions
Create a stateless multi-turn conversation
Define helper functions
Tip: To run the code samples on this page in an interactive environment, see the Conversational Analytics API SDK Colaboratory notebook.
Authenticate and set up your environment
To use the Python SDK for the Conversational Analytics API, follow the instructions in the Conversational Analytics API SDK Colaboratory notebook to download and install the SDK. Note that the download method and the contents of the SDK Colab are subject to change.

After you've completed the setup instructions in the notebook, you can use the following code to import the required SDK libraries, authenticate your Google Account within a Colaboratory environment, and initialize a client for making API requests:

from google.colab import auth
auth.authenticate_user()

from google.cloud import geminidataanalytics

data_agent_client = geminidataanalytics.DataAgentServiceClient()
data_chat_client = geminidataanalytics.DataChatServiceClient()
Specify the billing project and system instructions
The following sample Python code defines the billing project and system instructions that are used throughout your script:

# Billing project
billing_project = "my_project_name"

# System instructions
system_instruction = "Help the user analyze their data."
Replace the sample values as follows:

my_project_name: The ID of your billing project that has the required APIs enabled.
Help the user analyze their data.: System instructions to guide the agent's behavior and customize it for your data needs. For example, you can use system instructions to define business terms, control response length, or set data formatting. Ideally, define system instructions by using the recommended YAML format in Write effective system instructions to provide detailed and structured guidance.
Connect to a data source
The following sections show how to define the connection details for your agent's data sources. Your agent can connect to data in Looker, BigQuery, or Looker Studio.

Connect to Looker data
The following code examples show how to define the details for a connection to a Looker Explore with either API keys or an access token. You can connect up to five Looker Explores at a time with the Conversational Analytics API.

When you connect to a Looker data source, note the following:

You can query any included Explore in a conversation.
An agent can only query one Explore at a time. It is not possible to perform queries across multiple Explores simultaneously.
An agent can query multiple Explores in the same conversation.
An agent can query multiple Explores in a conversation that includes questions with multiple parts, or in conversations that include follow-up questions.

For example: A user connects two Explores, one called cat-explore and one called dog-explore. The user inputs the question "What's greater: the count of cats or the count of dogs?" This would create two queries: one to count the number of cats in cat-explore and one to count the number of dogs in dog-explore. The agent compares the number from both queries after completing both queries.

Note: Don't include credentials in the data source during agent creation.
API keys
Access token
You can establish a connection with a Looker instance with generated Looker API keys, as described in Authenticate and connect to a data source with the Conversational Analytics API.

looker_client_id = "my_looker_client_id"
looker_client_secret = "my_looker_client_secret"
looker_instance_uri = "https://my_company.looker.com"
lookml_model_1 = "my_model"
explore_1 = "my_explore"
lookml_model_2 = "my_model_2"
explore_2 = "my_explore_2"

looker_explore_reference = geminidataanalytics.LookerExploreReference()
looker_explore_reference.looker_instance_uri = looker_instance_uri
looker_explore_reference.lookml_model = "my_model"
looker_explore_reference.explore = "my_explore"

looker_explore_reference2 = geminidataanalytics.LookerExploreReference()
looker_explore_reference2.looker_instance_uri = looker_instance_uri
looker_explore_reference2.lookml_model = "my_model_2"
looker_explore_reference2.explore = "my_explore_2"

credentials = geminidataanalytics.Credentials()
credentials.oauth.secret.client_id = looker_client_id
credentials.oauth.secret.client_secret = looker_client_secret

datasource_references = geminidataanalytics.DatasourceReferences()
datasource_references.looker.explore_references = [looker_explore_reference, looker_explore_reference2]

# Do not include the following line during agent creation
datasource_references.credentials = credentials
Replace the sample values as follows:

my_looker_client_id: The client ID of your generated Looker API key.
my_looker_client_secret: The client secret of your generated Looker API key.
https://my_company.looker.com: The complete URL of your Looker instance.
my_model: The name of the LookML model that includes the Explore that you want to connect to.
my_explore: The name of the Looker Explore that you want the data agent to query.
my_model_2: The name of the second LookML model that includes the Explore that you want to connect to. You can repeat this variable for additional models for up to five Explores.
my_explore_2: The name of the additional Looker Explore that you want the data agent to query. You can repeat this variable to include up to five Explores.
Connect to BigQuery data
With the Conversational Analytics API, there are no hard limits on the number of BigQuery tables that you can connect to. However, connecting to a large number of tables can reduce accuracy or cause you to exceed the model's input token limit.

Note: Queries that require complex joins across multiple tables might result in less accurate responses.
The following sample code defines a connection to multiple BigQuery tables.

Important: Make sure you have the necessary Identity and Access Management (IAM) permissions to query any BigQuery tables that you specify.
bigquery_table_reference = geminidataanalytics.BigQueryTableReference()
bigquery_table_reference.project_id = "my_project_id"
bigquery_table_reference.dataset_id = "my_dataset_id"
bigquery_table_reference.table_id = "my_table_id"

bigquery_table_reference_2 = geminidataanalytics.BigQueryTableReference()
bigquery_table_reference_2.project_id = "my_project_id_2"
bigquery_table_reference_2.dataset_id = "my_dataset_id_2"
bigquery_table_reference_2.table_id = "my_table_id_2"

bigquery_table_reference_3 = geminidataanalytics.BigQueryTableReference()
bigquery_table_reference_3.project_id = "my_project_id_3"
bigquery_table_reference_3.dataset_id = "my_dataset_id_3"
bigquery_table_reference_3.table_id = "my_table_id_3"

# Connect to your data source
datasource_references = geminidataanalytics.DatasourceReferences()
datasource_references.bq.table_references = [bigquery_table_reference, bigquery_table_reference_2, bigquery_table_reference_3]
Replace the sample values as follows:

my_project_id: The ID of the Google Cloud project that contains the BigQuery dataset and table that you want to connect to. To connect to a public dataset, specify bigquery-public-data.
my_dataset_id: The ID of the BigQuery dataset. For example, san_francisco.
my_table_id: The ID of the BigQuery table. For example, street_trees.
Connect to Looker Studio data
The following sample code defines a connection to a Looker Studio data source.

studio_datasource_id = "my_datasource_id"

studio_references = geminidataanalytics.StudioDatasourceReference()
studio_references.datasource_id = studio_datasource_id

## Connect to your data source
datasource_references.studio.studio_references = [studio_references]
In the previous example, replace my_datasource_id with the data source ID.

Set up context for stateful or stateless chat
The Conversational Analytics API supports multi-turn conversations, which let users ask follow-up questions that build on previous context. The following sample Python code demonstrates how to set up context for either stateful or stateless chat:

Stateful chat: Google Cloud stores and manages the conversation history. Stateful chat is inherently multi-turn, as the API retains context from previous messages. You only need to send the current message for each turn.
Stateless chat: Your application manages the conversation history. You must include the entire conversation history with each new message. For detailed examples on how to manage multi-turn conversations in stateless mode, see Create a stateless multi-turn conversation.
Note: Whether you set up published_context for stateful chat or inline_context for stateless chat, you use the system_instruction variable that you defined in Specify the billing project and system instructions to effectively guide the agent's responses. For details on the recommended YAML format for these instructions, see Write effective system instructions.
Stateful chat
Stateless chat
The following code sample sets up context for stateful chat, where Google Cloud stores and manages the conversation history. You can also optionally enable advanced analysis with Python by including the line published_context.options.analysis.python.enabled = True in the following sample code.

# Set up context for stateful chat
published_context = geminidataanalytics.Context()
published_context.system_instruction = system_instruction
published_context.datasource_references = datasource_references
# Optional: To enable advanced analysis with Python, include the following line:
published_context.options.analysis.python.enabled = True
Create a data agent
The following sample Python code makes an API request to create a data agent, which you can then use to have a conversation about your data. The data agent is configured with the specified data source, system instructions, and context.

data_agent_id = "data_agent_1"

data_agent = geminidataanalytics.DataAgent()
data_agent.data_analytics_agent.published_context = published_context
data_agent.name = f"projects/{billing_project}/locations/global/dataAgents/{data_agent_id}" # Optional

request = geminidataanalytics.CreateDataAgentRequest(
    parent=f"projects/{billing_project}/locations/global",
    data_agent_id=data_agent_id, # Optional
    data_agent=data_agent,
)

try:
    data_agent_client.create_data_agent(request=request)
    print("Data Agent created")
except Exception as e:
    print(f"Error creating Data Agent: {e}")
In the previous example, replace the value data_agent_1 with a unique identifier for the data agent.

Create a conversation
The following sample Python code makes an API request to create a conversation.

# Initialize request arguments
data_agent_id = "data_agent_1"
conversation_id = "conversation_1"

conversation = geminidataanalytics.Conversation()
conversation.agents = [f'projects/{billing_project}/locations/global/dataAgents/{data_agent_id}']
conversation.name = f"projects/{billing_project}/locations/global/conversations/{conversation_id}"

request = geminidataanalytics.CreateConversationRequest(
    parent=f"projects/{billing_project}/locations/global",
    conversation_id=conversation_id,
    conversation=conversation,
)

# Make the request
response = data_chat_client.create_conversation(request=request)

# Handle the response
print(response)
Replace the sample values as follows:

data_agent_1: The ID of the data agent, as defined in the sample code block in Create a data agent.
conversation_1: A unique identifier for the conversation.
Manage data agents and conversations
The following code samples show how to manage your data agents and conversations by using the Conversational Analytics API. You can perform the following tasks:

Get a data agent
List data agents
List accessible data agents
Update a data agent
Set the IAM policy for a data agent
Get the IAM policy for a data agent
Delete a data agent
Get a conversation
List conversations
List messages in a conversation
Get a data agent
The following sample Python code demonstrates how to make an API request to retrieve a data agent that you previously created.

# Initialize request arguments
data_agent_id = "data_agent_1"
request = geminidataanalytics.GetDataAgentRequest(
    name=f"projects/{billing_project}/locations/global/dataAgents/{data_agent_id}",
)

# Make the request
response = data_agent_client.get_data_agent(request=request)

# Handle the response
print(response)
In the previous example, replace the value data_agent_1 with the unique identifier for the data agent that you want to retrieve.

List data agents
The following code demonstrates how to list all the data agents for a given project by calling the list_data_agents method. To list all agents, you must have the geminidataanalytics.dataAgents.list permission on the project. For more information on which IAM roles include this permission, see the list of predefined roles.

billing_project = "YOUR-BILLING-PROJECT"
location = "global"
request = geminidataanalytics.ListDataAgentsRequest(
    parent=f"projects/{billing_project}/locations/global",
)

# Make the request
page_result = data_agent_client.list_data_agents(request=request)

# Handle the response
for response in page_result:
    print(response)
Replace YOUR-BILLING-PROJECT with the ID of your billing project.

List accessible data agents
The following code demonstrates how to list all the accessible data agents for a given project by calling the list_accessible_data_agents method.

billing_project = "YOUR-BILLING-PROJECT"
creator_filter = "YOUR-CREATOR-FILTER"
location = "global"
request = geminidataanalytics.ListAccessibleDataAgentsRequest(
    parent=f"projects/{billing_project}/locations/global",
    creator_filter=creator_filter
)

# Make the request
page_result = data_agent_client.list_accessible_data_agents(request=request)

# Handle the response
for response in page_result:
    print(response)
Replace the sample values as follows:

YOUR-BILLING-PROJECT: The ID of your billing project.
YOUR-CREATOR-FILTER: The filter to apply based on the creator of the data agent. Possible values include NONE (default), CREATOR_ONLY, and NOT_CREATOR_ONLY.
Update a data agent
The following sample code demonstrates how to update a data agent by calling the update_data_agent method on the data agent resource. The request requires a DataAgent object that includes the new values for the fields that you want to change, and an update_mask parameter that takes a FieldMask object to specify which fields to update.

To update a data agent, you must have the geminidataanalytics.dataAgents.update IAM permission on the agent. For more information on which IAM roles include this permission, see the list of predefined roles.

data_agent_id = "data_agent_1"
billing_project = "YOUR-BILLING-PROJECT"
data_agent = geminidataanalytics.DataAgent()
data_agent.data_analytics_agent.published_context = published_context
data_agent.name = f"projects/{billing_project}/locations/global/dataAgents/{data_agent_id}"
data_agent.description = "Updated description of the data agent."

update_mask = field_mask_pb2.FieldMask(paths=['description', 'data_analytics_agent.published_context'])

request = geminidataanalytics.UpdateDataAgentRequest(
    data_agent=data_agent,
    update_mask=update_mask,
)

try:
    # Make the request
    data_agent_client.update_data_agent(request=request)
    print("Data Agent Updated")
except Exception as e:
    print(f"Error updating Data Agent: {e}")
Replace the sample values as follows:

data_agent_1: The ID of the data agent that you want to update.
YOUR-BILLING-PROJECT: The ID of your billing project.
Updated description of the data agent.: A description of the updated data agent.
Set the IAM policy for a data agent
To share an agent, you can use the set_iam_policy method to assign IAM roles to users on a specific agent. The request includes bindings that specify which roles should be assigned to which users.

Important: This API call overrides existing permissions for the resource. To preserve existing policies, call the get_iam_policy method to fetch the existing policy, and then pass the existing policy along with any additional changes in the call to set_iam_policy.
billing_project = "YOUR-BILLING-PROJECT"
location = "global"
data_agent_id = "data_agent_1"
role = "roles/geminidataanalytics.dataAgentEditor"
users = "222larabrown@gmail.com, cloudysanfrancisco@gmail.com"

resource = f"projects/{billing_project}/locations/global/dataAgents/{data_agent_id}"

# Construct the IAM policy
binding = policy_pb2.Binding(
    role=role,
    members= [f"user:{i.strip()}" for i in users.split(",")]
)

policy = policy_pb2.Policy(bindings=[binding])

# Create the request
request = iam_policy_pb2.SetIamPolicyRequest(
    resource=resource,
    policy=policy
)

# Send the request
try:
    response = data_agent_client.set_iam_policy(request=request)
    print("IAM Policy set successfully!")
    print(f"Response: {response}")
except Exception as e:
    print(f"Error setting IAM policy: {e}")
Replace the sample values as follows:

YOUR-BILLING-PROJECT: The ID of your billing project.
data_agent_1: The ID of the data agent for which you want to set the IAM policy.
222larabrown@gmail.com, cloudysanfrancisco@gmail.com: A comma-separated list of user emails to which you want to grant the specified role.
Get the IAM policy for a data agent
The following sample code demonstrates how to use the get_iam_policy method to fetch the IAM policy for a data agent. The request specifies the data agent resource path.

billing_project = "YOUR-BILLING-PROJECT"
location = "global"
data_agent_id = "data_agent_1"

resource = f"projects/{billing_project}/locations/global/dataAgents/{data_agent_id}"
request = iam_policy_pb2.GetIamPolicyRequest(
            resource=resource,
        )
try:
    response = data_agent_client.get_iam_policy(request=request)
    print("IAM Policy fetched successfully!")
    print(f"Response: {response}")
except Exception as e:
    print(f"Error setting IAM policy: {e}")
Replace the sample values as follows:

YOUR-BILLING-PROJECT: The ID of your billing project.
data_agent_1: The ID of the data agent for which you want to get the IAM policy.
Delete a data agent
The following sample code demonstrates how to use the delete_data_agent method to soft delete a data agent. When you soft delete an agent, that agent is deleted but can still be retrieved within 30 days. The request specifies the data agent resource URL.

billing_project = "YOUR-BILLING-PROJECT"
location = "global"
data_agent_id = "data_agent_1"

request = geminidataanalytics.DeleteDataAgentRequest(
    name=f"projects/{billing_project}/locations/global/dataAgents/{data_agent_id}",
)

try:
    # Make the request
    data_agent_client.delete_data_agent(request=request)
    print("Data Agent Deleted")
except Exception as e:
    print(f"Error deleting Data Agent: {e}")
Replace the sample values as follows:

YOUR-BILLING-PROJECT: The ID of your billing project.
data_agent_1: The ID of the data agent that you want to delete.
Get a conversation
The following sample code demonstrates how to use the get_conversation method to fetch information about an existing conversation. The request specifies the conversation resource path.

billing_project = "YOUR-BILLING-PROJECT"
location = "global"
conversation_id = "conversation_1"

request = geminidataanalytics.GetConversationRequest(
    name = f"projects/{billing_project}/locations/global/conversations/{conversation_id}"
)

# Make the request
response = data_chat_client.get_conversation(request=request)

# Handle the response
print(response)
Replace the sample values as follows:

YOUR-BILLING-PROJECT: The ID of your billing project.
conversation_1: The ID of the conversation that you want to fetch.
List conversations
The following sample code demonstrates how to list conversations for a given project by calling the list_conversations method. The request specifies the parent resource URL, which is the project and location (for example, projects/my-project/locations/global).

By default, this method returns the conversations that you created. Admins (users with the cloudaicompanion.topicAdmin IAM role) can see all conversations within the project.

billing_project = "YOUR-BILLING-PROJECT"
location = "global"
request = geminidataanalytics.ListConversationsRequest(
    parent=f"projects/{billing_project}/locations/global",
)

# Make the request
response = data_chat_client.list_conversations(request=request)

# Handle the response
print(response)
Replace YOUR-BILLING-PROJECT with the ID of the billing project where you've enabled the required APIs.

List messages in a conversation
The following sample code demonstrates how to use the list_messages method to fetch all the messages in a conversation. The request specifies the conversation resource path.

To list messages, you must have the cloudaicompanion.topics.get permission on the conversation.

Note: This list operation also supports pagination.
billing_project = "YOUR-BILLING-PROJECT"
location = "global"

conversation_id = "conversation_1"

request = geminidataanalytics.ListMessagesRequest(
    parent=f"projects/{billing_project}/locations/global/conversations/{conversation_id}",
)

# Make the request
response = data_chat_client.list_messages(request=request)

# Handle the response
print(response)
Replace the sample values as follows:

YOUR-BILLING-PROJECT: The ID of your billing project.
conversation_1: The ID of the conversation for which you want to list messages.
Use the API to ask questions
After you create a data agent and a conversation, the following sample Python code sends a query to the agent. The code uses the context that you set up for stateful or stateless chat. The API returns a stream of messages that represent the steps that the agent takes to answer the query.

Stateful chat
Stateless chat
Send a stateful chat request with a Conversation reference
You can send a stateful chat request to the data agent by referencing a Conversation resource that you previously created.

Note: If you're using a Looker data source, uncomment the line conversation_reference.data_agent_context.credentials = credentials in the following sample code.
# Create a request that contains a single user message (your question)
question = "Which species of tree is most prevalent?"
messages = [geminidataanalytics.Message()]
messages[0].user_message.text = question

data_agent_id = "data_agent_1"
conversation_id = "conversation_1"

# Create a conversation_reference
conversation_reference = geminidataanalytics.ConversationReference()
conversation_reference.conversation = f"projects/{billing_project}/locations/global/conversations/{conversation_id}"
conversation_reference.data_agent_context.data_agent = f"projects/{billing_project}/locations/global/dataAgents/{data_agent_id}"
# conversation_reference.data_agent_context.credentials = credentials

# Form the request
request = geminidataanalytics.ChatRequest(
    parent = f"projects/{billing_project}/locations/global",
    messages = messages,
    conversation_reference = conversation_reference
)

# Make the request
stream = data_chat_client.chat(request=request, timeout=300 #custom timeout up to 600s)

# Handle the response
for response in stream:
    show_message(response)
Replace the sample values as follows:

Which species of tree is most prevalent?: A natural language question to send to the data agent.
data_agent_1: The unique identifier for the data agent, as defined in Create a data agent.
conversation_1: The unique identifier for the conversation, as defined in Create a conversation.
Create a stateless multi-turn conversation
To ask follow-up questions in a stateless conversation, your application must manage the conversation's context by sending the entire message history with each new request. The following example shows how to create a multi-turn conversation by referencing a data agent or by using inline context to provide the data source directly.

The following code sample uses data agent context. To use inline context instead, uncomment the line inline_context=inline_context.

If your agent uses a Looker data source and you're using data agent context, uncomment the line data_agent_context.credentials = credentials.

# List that is used to track previous turns and is reused across requests
conversation_messages = []

data_agent_id = "data_agent_1"

# Use data agent context
data_agent_context = geminidataanalytics.DataAgentContext()
data_agent_context.data_agent = f"projects/{billing_project}/locations/global/dataAgents/{data_agent_id}"
# data_agent_context.credentials = credentials

# Helper function for calling the API
def multi_turn_Conversation(msg):

    message = geminidataanalytics.Message()
    message.user_message.text = msg

    # Send a multi-turn request by including previous turns and the new message
    conversation_messages.append(message)

    request = geminidataanalytics.ChatRequest(
        parent=f"projects/{billing_project}/locations/global",
        messages=conversation_messages,
        # Use data agent context
        data_agent_context=data_agent_context,
        # Use inline context
        # inline_context=inline_context,
    )

    # Make the request
    stream = data_chat_client.chat(request=request, timeout=300 #custom timeout up to 600s)

    # Handle the response
    for response in stream:
      show_message(response)
      conversation_messages.append(response)

# Send the first turn request
multi_turn_Conversation("Which species of tree is most prevalent?")

# Send follow-up turn request
multi_turn_Conversation("Can you show me the results as a bar chart?")
In the previous example, replace the sample values as follows:

data_agent_1: The unique identifier for the data agent, as defined in the sample code block in Create a data agent.
Which species of tree is most prevalent?: A natural language question to send to the data agent.
Can you show me the results as a bar chart?: A follow-up question that builds on or refines the previous question.
Define helper functions
The following sample code contains helper function definitions that are used in the previous code samples. These functions help to parse the response from the API and display the results.

from pygments import highlight, lexers, formatters
import pandas as pd
import requests
import json as json_lib
import altair as alt
import IPython
from IPython.display import display, HTML

import proto
from google.protobuf.json_format import MessageToDict, MessageToJson

def handle_text_response(resp):
  parts = getattr(resp, 'parts')
  print(''.join(parts))

def display_schema(data):
  fields = getattr(data, 'fields')
  df = pd.DataFrame({
    "Column": map(lambda field: getattr(field, 'name'), fields),
    "Type": map(lambda field: getattr(field, 'type'), fields),
    "Description": map(lambda field: getattr(field, 'description', '-'), fields),
    "Mode": map(lambda field: getattr(field, 'mode'), fields)
  })
  display(df)

def display_section_title(text):
  display(HTML('<h2>{}</h2>'.format(text)))

def format_looker_table_ref(table_ref):
 return 'lookmlModel: {}, explore: {}, lookerInstanceUri: {}'.format(table_ref.lookml_model, table_ref.explore, table_ref.looker_instance_uri)

def format_bq_table_ref(table_ref):
  return '{}.{}.{}'.format(table_ref.project_id, table_ref.dataset_id, table_ref.table_id)

def display_datasource(datasource):
  source_name = ''
  if 'studio_datasource_id' in datasource:
   source_name = getattr(datasource, 'studio_datasource_id')
  elif 'looker_explore_reference' in datasource:
   source_name = format_looker_table_ref(getattr(datasource, 'looker_explore_reference'))
  else:
    source_name = format_bq_table_ref(getattr(datasource, 'bigquery_table_reference'))

  print(source_name)
  display_schema(datasource.schema)

def handle_schema_response(resp):
  if 'query' in resp:
    print(resp.query.question)
  elif 'result' in resp:
    display_section_title('Schema resolved')
    print('Data sources:')
    for datasource in resp.result.datasources:
      display_datasource(datasource)

def handle_data_response(resp):
  if 'query' in resp:
    query = resp.query
    display_section_title('Retrieval query')
    print('Query name: {}'.format(query.name))
    print('Question: {}'.format(query.question))
    print('Data sources:')
    for datasource in query.datasources:
      display_datasource(datasource)
  elif 'generated_sql' in resp:
    display_section_title('SQL generated')
    print(resp.generated_sql)
  elif 'result' in resp:
    display_section_title('Data retrieved')

    fields = [field.name for field in resp.result.schema.fields]
    d = {}
    for el in resp.result.data:
      for field in fields:
        if field in d:
          d[field].append(el[field])
        else:
          d[field] = [el[field]]

    display(pd.DataFrame(d))

def handle_chart_response(resp):
  def _value_to_dict(v):
    if isinstance(v, proto.marshal.collections.maps.MapComposite):
      return _map_to_dict(v)
    elif isinstance(v, proto.marshal.collections.RepeatedComposite):
      return [_value_to_dict(el) for el in v]
    elif isinstance(v, (int, float, str, bool)):
      return v
    else:
      return MessageToDict(v)

  def _map_to_dict(d):
    out = {}
    for k in d:
      if isinstance(d[k], proto.marshal.collections.maps.MapComposite):
        out[k] = _map_to_dict(d[k])
      else:
        out[k] = _value_to_dict(d[k])
    return out

  if 'query' in resp:
    print(resp.query.instructions)
  elif 'result' in resp:
    vegaConfig = resp.result.vega_config
    vegaConfig_dict = _map_to_dict(vegaConfig)
    alt.Chart.from_json(json_lib.dumps(vegaConfig_dict)).display();

def show_message(msg):
  m = msg.system_message
  if 'text' in m:
    handle_text_response(getattr(m, 'text'))
  elif 'schema' in m:
    handle_schema_response(getattr(m, 'schema'))
  elif 'data' in m:
    handle_data_response(getattr(m, 'data'))
  elif 'chart' in m:
    handle_chart_response(getattr(m, 'chart'))
  print('\n')
Was this helpful?

Send feedback
Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2025-10-02 UTC.

Why Google
Choosing Google Cloud
Trust and security
Modern Infrastructure Cloud
Multicloud
Global infrastructure
Customers and case studies
Analyst reports
Whitepapers
Products and pricing
See all products
See all solutions
Google Cloud for Startups
Google Cloud Marketplace
Google Cloud pricing
Contact sales
Support
Community forums
Support
Release Notes
System status
Resources
GitHub
Getting Started with Google Cloud
Google Cloud documentation
Code samples
Cloud Architecture Center
Training and Certification
Developer Center
Engage
Blog
Events
X (Twitter)
Google Cloud on YouTube
Google Cloud Tech on YouTube
Become a Partner
Google Cloud Affiliate Program
Press Corner
About Google
Privacy
Site terms
Google Cloud terms
Our third decade of climate action: join us
Sign up for the Google Cloud newsletter
Subscribe

English
The new page has loaded..




Skip to main content
Google Cloud
Documentation
Technology areas

Cross-product tools

Related sites


Search
/


English
Console

Gemini for Google Cloud
Overview
Conversational Analytics API
Contact Us
Filter

Gemini for Google Cloud 
Documentation 
Conversational Analytics API
Was this helpful?

Send feedbackRender an agent response as a visualization

bookmark_border

This product or feature is subject to the "Pre-GA Offerings Terms" in the General Service Terms section of the Service Specific Terms. Pre-GA products and features are available "as is" and might have limited support. For more information, see the launch stage descriptions.

This page shows how to use the Python SDK to render a visualization from the chart specifications that are provided within a Conversational Analytics API response. The sample code extracts the chart specification (in the Vega-Lite format) from the response's chart field and uses the Vega-Altair library to render the chart, save it as an image, and display it.

Note: This guide assumes that you're working in an environment like Colaboratory. This guide also builds on the setup in Build a data agent using the Python SDK, which shows how to authenticate and initialize the required client, inline_context, and messages variables.
Example: Render a bar chart from an API
This example shows how to render a bar chart from a Conversational Analytics API agent response. The example sends a request with the following prompt:


"Create a bar graph that shows the top five states by the total number of airports."
The sample code defines the following helper functions:

render_chart_response: Extracts the Vega-Lite configuration from the chart message, converts it to a format that can be used by the Vega-Altair library, renders the chart, saves it to chart.png, and displays it.
chat: Sends a request to the Conversational Analytics API using the inline_context variable and the current messages list, processes the streaming response, and if a chart is returned, calls render_chart_response to display it.
To use the following sample code, replace the following:

sqlgen-testing: The ID of your billing project that has the required APIs enabled.
Create a bar graph that shows the top five states by the total number of airports: The prompt that you want to send to the Conversational Analytics API.
from google.cloud import geminidataanalytics
from google.protobuf.json_format import MessageToDict
import altair as alt
import proto

# Helper function for rendering chart response
def render_chart_response(resp):
  def _convert(v):
    if isinstance(v, proto.marshal.collections.maps.MapComposite):
      return {k: _convert(v) for k, v in v.items()}
    elif isinstance(v, proto.marshal.collections.RepeatedComposite):
      return [_convert(el) for el in v]
    elif isinstance(v, (int, float, str, bool)):
      return v
    else:
      return MessageToDict(v)

  vega_config = _convert(resp.result.vega_config)
  chart = alt.Chart.from_dict(vega_config)
  chart.save('chart.png')
  chart.display()

# Helper function for calling the API
def chat(q: str):
  billing_project = "sqlgen-testing"

  input_message = geminidataanalytics.Message(
      user_message=geminidataanalytics.UserMessage(text=q)
  )

  client = geminidataanalytics.DataChatServiceClient()
  request = geminidataanalytics.ChatRequest(
      inline_context=inline_context,
      parent=f"projects/{billing_project}/locations/global",
      messages=messages,
  )

  # Make the request
  stream = client.chat(request=request)

  for reply in stream:
    if "chart" in reply.system_message:
      # ChartMessage includes `query` for generating a chart and `result` with the generated chart.
      if "result" in reply.system_message.chart:
        render_chart_response(reply.system_message.chart)

# Send the prompt to make a bar graph
chat("Create a bar graph that shows the top five states by the total number of airports.")
Was this helpful?

Send feedback
Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2025-10-02 UTC.

Why Google
Choosing Google Cloud
Trust and security
Modern Infrastructure Cloud
Multicloud
Global infrastructure
Customers and case studies
Analyst reports
Whitepapers
Products and pricing
See all products
See all solutions
Google Cloud for Startups
Google Cloud Marketplace
Google Cloud pricing
Contact sales
Support
Community forums
Support
Release Notes
System status
Resources
GitHub
Getting Started with Google Cloud
Google Cloud documentation
Code samples
Cloud Architecture Center
Training and Certification
Developer Center
Engage
Blog
Events
X (Twitter)
Google Cloud on YouTube
Google Cloud Tech on YouTube
Become a Partner
Google Cloud Affiliate Program
Press Corner
About Google
Privacy
Site terms
Google Cloud terms
Our third decade of climate action: join us
Sign up for the Google Cloud newsletter
Subscribe

English
The new page has loaded.
