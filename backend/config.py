import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

    DATABASE_URL = os.getenv("DATABASE_URL")

    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

    MCP_FILE_SERVER = os.getenv("MCP_FILE_SERVER")
    MCP_WEB_SEARCH = os.getenv("MCP_WEB_SEARCH")
    MCP_KB_SERVER = os.getenv("MCP_KB_SERVER")
