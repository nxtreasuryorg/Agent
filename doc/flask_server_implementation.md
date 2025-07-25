# Treasury Agent - Flask Server

## Overview
Production-ready Flask server for treasury payment workflows with AI-powered analysis and approval processing.

**Status**: ✅ **PRODUCTION READY**
**Version**: 1.0.0
**Environment**: Conda `agent`
**Server**: `http://localhost:5001`
**Safety**: All transactions simulated by default

## Core Workflow

### 1. Request Submission (`POST /submit_request`)
- **Input**: Excel file + JSON metadata
- **Process**: Validates, processes payments, generates proposal
- **Output**: `{proposal_id, status}`

### 2. Proposal Review (`GET /get_proposal/<id>`)
- **Input**: Proposal ID
- **Output**: Complete payment proposal with risk assessment

### 3. Approval Submission (`POST /submit_approval`)
- **Input**: Approval decision + payment list
- **Process**: Validates, processes payments, updates status
- **Output**: Execution ID and status

### 4. Results Retrieval (`GET /execution_result/<id>`)
- **Input**: Proposal ID
- **Output**: Complete execution details and status

## Architecture

### Components
- **API Layer**: RESTful endpoints with validation
- **Processing**: Async task processing
- **State**: In-memory storage (dev) / Database (prod)
- **Security**: Input validation, rate limiting

### Data Flow
1. Client submits request → Server validates → Processes → Returns ID
2. Client reviews → Submits approval → Server executes → Returns result

## Security
- Input validation
- Rate limiting
- Secure file handling
- Error handling

## Development

### Setup
```bash
# Create environment
conda create -n agent python=3.9
conda activate agent

# Install dependencies
pip install -r requirements.txt

# Run server
python flask_server.py
```

### Testing
```bash
pytest tests/
```

## Deployment

### Production
1. Use Gunicorn/Uvicorn
2. Set up Nginx
3. Configure HTTPS
4. Enable monitoring

### Environment
| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | `development` | Runtime env |
| `PORT` | `5001` | Server port |
| `LOG_LEVEL` | `INFO` | Logging level |
| `RATE_LIMIT` | `100/hour` | Rate limiting |

## Maintenance
- Regular backups
- Dependency updates
- Security patches
- Performance monitoring

## Troubleshooting
- Check server logs
- Verify file permissions
- Monitor resources