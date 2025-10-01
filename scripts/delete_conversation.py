
import os
from google.cloud import geminidataanalytics

location = "global"
billing_project = os.environ.get('DEVSHELL_PROJECT_ID')
if not billing_project:
    billing_project = "bq-demos-469816"

data_chat_client = geminidataanalytics.DataChatServiceClient()

conversation_name = f"projects/{billing_project}/locations/{location}/conversations/my_first_conversation"

try:
    data_chat_client.delete_conversation(name=conversation_name)
    print(f"Conversation '{conversation_name}' deleted successfully.")
except Exception as e:
    print(f"Error deleting conversation '{conversation_name}': {e}")
