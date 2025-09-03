# 📄 Intelligent Document Summarization & Q&A Platform

An AI-powered document processing platform that provides intelligent summarization, entity extraction, and question-answering capabilities using Azure OpenAI. The platform supports multiple document formats and offers both API and web interfaces for seamless document analysis.

## 🌟 Features

### Core Capabilities
- **Multi-format Document Parsing**: Support for PDF, DOCX, and HTML documents
- **AI-Powered Summarization**: Section-wise, document-level, and corpus-level summaries
- **Named Entity Extraction**: Automatic identification of names, dates, and organizations
- **Intelligent Q&A**: Context-aware question answering based on document content
- **Human-in-the-Loop**: Edit and refine summaries through the web interface

### Technical Features
- **RESTful API**: FastAPI-based backend with comprehensive endpoints
- **Interactive Web UI**: Streamlit-based user interface with real-time processing
- **Global Error Handling**: Comprehensive error boundaries and user-friendly error messages
- **Observability**: Integrated logging with LangSmith for monitoring and debugging
- **Agent-Based Architecture**: Modular design with specialized agents for different tasks
- **Validation & Rollback**: Quality checks with automatic rollback for low-quality outputs


## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Azure OpenAI API access
- Git (for cloning the repository)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Python\ \&\ Gen-AI
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**

   Create a `.env` file in the root directory:
   ```env
   # Azure OpenAI Configuration
   AZURE_OPENAI_API_KEY=your_azure_openai_api_key
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
   AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name

   # Optional: Database Configuration
   DATABASE_URL=sqlite:///./documents.db

   # Optional: LangSmith for Observability
   LANGCHAIN_API_KEY=your_langsmith_api_key

   # Optional: MCP Server Configuration
   MCP_FILE_SERVER=http://localhost:3001
   MCP_WEB_SEARCH=http://localhost:3002
   MCP_KB_SERVER=http://localhost:3003
   ```

### Running the Application

1. **Start the FastAPI backend**
   ```bash
   cd backend
   uvicorn main:app --reload --port 8000
   ```

2. **Start the Streamlit frontend** (in a new terminal)
   ```bash
   cd ui
   streamlit run app.py --server.port 8501
   ```

3. **Access the application**
   - Web Interface: http://localhost:8501
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## 📖 Usage Guide

### Web Interface

1. **Upload Documents**
   - Navigate to the "Upload" tab
   - Select a PDF, DOCX, or HTML file (max 10MB)
   - Click "Process Document" to analyze

2. **Review Summaries**
   - Go to the "Summary" tab
   - Edit the generated summary if needed
   - Save changes to update the document

3. **Ask Questions**
   - Use the "Q&A" tab
   - Enter questions about your document
   - Get AI-powered answers based on the content

4. **Monitor Progress**
   - Check the "Monitor" tab for document status
   - View all processed documents
   - Switch between different documents

5. **Export Results**
   - Use the "Export" tab
   - Download summaries and entities as JSON

### API Usage

#### Upload a Document
```bash
curl -X POST "http://localhost:8000/documents/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@document.pdf"
```

#### Get Summary
```bash
curl -X GET "http://localhost:8000/summary/{doc_id}" \
     -H "accept: application/json"
```

#### Ask a Question
```bash
curl -X GET "http://localhost:8000/qa/?doc_id={doc_id}&question=What is this document about?" \
     -H "accept: application/json"
```

#### Update Summary
```bash
curl -X POST "http://localhost:8000/summary/{doc_id}/update" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{"updated_summary": "New summary content"}'
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test files
pytest tests/test_parser.py
pytest tests/test_summarizer.py
pytest tests/test_entity.py
pytest tests/test_qa.py
pytest tests/test_agents.py
pytest tests/test_api.py
```

### Test Coverage

The test suite includes:
- **Unit Tests**: Individual agent functionality
- **Integration Tests**: API endpoint testing
- **Error Handling Tests**: Exception and edge case coverage
- **Validation Tests**: Input validation and error responses

## 📁 Project Structure

```
Desktop/Python & Gen-AI/
├── backend/                    # FastAPI backend
│   ├── agents/                # AI agents
│   │   ├── parser_agent.py    # Document parsing
│   │   ├── summarizer_agent.py # Text summarization
│   │   ├── entity_agent.py    # Entity extraction
│   │   ├── qa_agent.py        # Question answering
│   │   ├── critic_agent.py    # Content review
│   │   └── validation_agent.py # Output validation
│   ├── routes/                # API endpoints
│   │   ├── documents.py       # Document operations
│   │   ├── summary.py         # Summary management
│   │   ├── qa.py             # Q&A endpoints
│   │   └── mcp.py            # MCP server endpoints
│   ├── utils/                 # Utilities
│   │   ├── exceptions.py      # Custom exceptions
│   │   └── helpers.py         # Helper functions
│   ├── agent_registry.py      # Agent management
│   ├── config.py             # Configuration
│   ├── logging_config.py     # Logging setup
│   ├── main.py               # FastAPI app
│   └── db.py                 # Database models
├── ui/                        # Streamlit frontend
│   ├── components/           # UI components
│   │   ├── upload_component.py
│   │   ├── summary_component.py
│   │   ├── qa_component.py
│   │   ├── monitor_component.py
│   │   ├── history_component.py
│   │   └── export_component.py
│   ├── error_handler.py      # UI error handling
│   ├── app.py               # Main Streamlit app
│   └── utils.py             # UI utilities
├── tests/                    # Test suite
│   ├── test_parser.py
│   ├── test_summarizer.py
│   ├── test_entity.py
│   ├── test_qa.py
│   ├── test_agents.py
│   └── test_api.py
├── uploaded_docs/           # Document storage
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key | Yes | - |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL | Yes | - |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Deployment name | Yes | - |
| `DATABASE_URL` | Database connection string | No | In-memory |
| `LANGCHAIN_API_KEY` | LangSmith API key for observability | No | - |
| `MCP_FILE_SERVER` | MCP file server URL | No | - |
| `MCP_WEB_SEARCH` | MCP web search server URL | No | - |
| `MCP_KB_SERVER` | MCP knowledge base server URL | No | - |

### Agent Configuration

Each agent can be configured through the `Config` class:

- **ParserAgent**: Supports PDF, DOCX, and HTML parsing
- **SummarizerAgent**: Configurable token limits and prompt templates
- **EntityAgent**: Regex patterns for entity extraction
- **QAAgent**: Context-aware question answering
- **CriticAgent**: Content review and bias detection
- **ValidationAgent**: Quality checks and rollback mechanisms

## 🚨 Error Handling

The platform includes comprehensive error handling:

### Backend Error Handling
- **Global Exception Handlers**: Catch and format all API errors
- **Custom Exceptions**: Specific error types for different failure modes
- **Graceful Degradation**: Fallback responses when services are unavailable
- **Request Validation**: Input validation with detailed error messages

### Frontend Error Handling
- **Error Boundaries**: Prevent UI crashes from component errors
- **User-Friendly Messages**: Convert technical errors to readable messages
- **Retry Mechanisms**: Automatic retry for transient failures
- **Offline Support**: Graceful handling of network connectivity issues

## 📊 Monitoring & Observability

### Logging
- **Structured Logging**: JSON-formatted logs with contextual information
- **Agent Actions**: All agent operations are logged for debugging
- **Performance Metrics**: Response times and success rates
- **Error Tracking**: Detailed error logs with stack traces

### LangSmith Integration
- **Request Tracing**: Track all LLM requests and responses
- **Performance Analytics**: Monitor token usage and latency
- **Quality Metrics**: Track summary quality and user feedback
- **Debugging Tools**: Inspect agent decision-making processes

## 🔒 Security Considerations

- **API Key Management**: Secure storage of Azure OpenAI credentials
- **Input Validation**: Comprehensive validation of all user inputs
- **File Upload Security**: Size limits and type validation for uploads
- **Error Information**: Sanitized error messages to prevent information leakage
- **Rate Limiting**: Built-in protection against abuse (when deployed)

## 🚀 Deployment

### Local Development
```bash
# Development mode with hot reload
uvicorn backend.main:app --reload --port 8000
streamlit run ui/app.py --server.port 8501
```

### Production Deployment
```bash
# Production mode
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
streamlit run ui/app.py --server.port 8501 --server.address 0.0.0.0
```

### Docker Support (Future Enhancement)
```dockerfile
# Example Dockerfile structure
FROM python:3.9-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000 8501
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add comprehensive docstrings to all functions and classes
- Include unit tests for new functionality
- Update documentation for API changes
- Test error handling scenarios

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Azure OpenAI**: For providing the language model capabilities
- **FastAPI**: For the high-performance API framework
- **Streamlit**: For the intuitive web interface framework
- **LangSmith**: For observability and monitoring tools
- **PyMuPDF**: For PDF parsing capabilities
- **python-docx**: For DOCX document processing
- **BeautifulSoup**: For HTML parsing and text extraction

## 📞 Support

For support, please:
1. Check the [documentation](#-usage-guide)
2. Review [common issues](#-error-handling)
3. Open an issue on GitHub
4. Contact the development team

---

**Built with ❤️ using Azure OpenAI, FastAPI, and Streamlit**#   G e n - A I 
 
 