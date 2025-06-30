#!/usr/bin/env python3
"""
🧠 RAG Server for GopiAI
Retrieval-Augmented Generation service for context enrichment

Provides endpoints for:
- Health checking
- Document indexing  
- Context search

Usage:
    python rag_server.py
    
Server will be available at: http://127.0.0.1:5051
"""

import os
import sys
import time
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from flask import Flask, request, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Server configuration
HOST = "127.0.0.1"
PORT = 5051
DEBUG = False

# Environment variables
RAG_TIMEOUT = int(os.environ.get('GOPIAI_RAG_TIMEOUT', 4))
DATA_PATH = Path(__file__).parent / "data"
INDEX_PATH = Path(__file__).parent / "index"

# Ensure directories exist
DATA_PATH.mkdir(exist_ok=True)
INDEX_PATH.mkdir(exist_ok=True)

app = Flask(__name__)

# Global state
SERVER_STATUS = {
    "status": "initializing",
    "timestamp": time.time(),
    "indexed_documents": 0,
    "last_index_time": None
}

# Simple in-memory document store for demonstration
DOCUMENT_STORE = {}

@app.route('/', methods=['GET'])
def index():
    """Main page with API information"""
    SERVER_STATUS["timestamp"] = time.time()
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>GopiAI RAG Server</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; line-height: 1.6; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            h1 {{ color: #333; }}
            .status {{ padding: 10px; border-radius: 5px; margin-bottom: 20px; }}
            .online {{ background-color: #d4edda; color: #155724; }}
            .initializing {{ background-color: #fff3cd; color: #856404; }}
            .offline {{ background-color: #f8d7da; color: #721c24; }}
            .endpoint {{ background-color: #f8f9fa; padding: 15px; margin-bottom: 10px; border-radius: 5px; }}
            .method {{ display: inline-block; padding: 3px 6px; border-radius: 3px; font-size: 12px; margin-right: 10px; }}
            .get {{ background-color: #61affe; color: white; }}
            .post {{ background-color: #49cc90; color: white; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧠 GopiAI RAG Server</h1>
            
            <div class="status {SERVER_STATUS['status']}">
                <strong>Status:</strong> {SERVER_STATUS['status'].upper()}<br>
                <strong>Indexed Documents:</strong> {SERVER_STATUS['indexed_documents']}<br>
                <strong>RAG Timeout:</strong> {RAG_TIMEOUT} seconds<br>
                <strong>Last Updated:</strong> {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(SERVER_STATUS['timestamp']))}
            </div>
            
            <h2>Available Endpoints</h2>
            
            <div class="endpoint">
                <span class="method get">GET</span> <strong>/api/health</strong>
                <p>Check server health and status. Returns current server state and configuration.</p>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span> <strong>/api/index</strong>
                <p>Index documents for RAG retrieval. Processes and stores documents for context search.</p>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span> <strong>/api/search</strong>
                <p>Search for relevant context based on query. Returns contextual information for RAG enhancement.</p>
                <p><em>Parameters:</em> {{ "query": "search text", "max_results": 3 }}</p>
            </div>
            
            <hr>
            <p><small>GopiAI RAG Server - Started: {time.strftime('%Y-%m-%d %H:%M:%S')}</small></p>
        </div>
    </body>
    </html>
    """
    
    return html

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    SERVER_STATUS["timestamp"] = time.time()
    return jsonify({
        "status": "online",
        "timestamp": SERVER_STATUS["timestamp"],
        "indexed_documents": SERVER_STATUS["indexed_documents"],
        "rag_timeout": RAG_TIMEOUT,
        "server_version": "1.0.0",
        "capabilities": ["indexing", "search", "health_check"]
    })

@app.route('/api/index', methods=['POST'])
def index_documents():
    """Index documents for RAG retrieval"""
    try:
        start_time = time.time()
        
        # Check if request has data
        data = request.json if request.is_json else {}
        documents = data.get('documents', [])
        
        if not documents:
            # Default indexing - scan for CrewAI documentation or other relevant docs
            logger.info("Starting default document indexing...")
            indexed_count = index_default_documents()
        else:
            # Index provided documents
            logger.info(f"Indexing {len(documents)} provided documents...")
            indexed_count = len(documents)
            for i, doc in enumerate(documents):
                doc_id = doc.get('id', f'doc_{i}')
                content = doc.get('content', '')
                metadata = doc.get('metadata', {})
                DOCUMENT_STORE[doc_id] = {
                    'content': content,
                    'metadata': metadata,
                    'indexed_at': time.time()
                }
        
        SERVER_STATUS["indexed_documents"] = len(DOCUMENT_STORE)
        SERVER_STATUS["last_index_time"] = time.time()
        
        elapsed_time = time.time() - start_time
        
        logger.info(f"Indexing completed in {elapsed_time:.2f} seconds")
        
        return jsonify({
            "success": True,
            "message": f"Successfully indexed {indexed_count} documents",
            "indexed_documents": SERVER_STATUS["indexed_documents"],
            "indexing_time": elapsed_time
        })
        
    except Exception as e:
        logger.error(f"Error during indexing: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/search', methods=['POST'])
def search_context():
    """Search for relevant context"""
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
            
        data = request.json
        query = data.get('query', '')
        max_results = data.get('max_results', 3)
        
        if not query:
            return jsonify({"error": "Query parameter is required"}), 400
        
        logger.info(f"Searching for context: '{query[:50]}...'")
        
        # Simple search implementation
        results = search_documents(query, max_results)
        
        # Format context for response
        if results:
            context_parts = []
            for result in results:
                content = result.get('content', '')
                if content:
                    # Truncate long content
                    if len(content) > 500:
                        content = content[:497] + "..."
                    context_parts.append(content)
            
            context = "\n\n".join(context_parts) if context_parts else None
        else:
            context = None
        
        return jsonify({
            "query": query,
            "context": context,
            "results_count": len(results),
            "max_results": max_results
        })
        
    except Exception as e:
        logger.error(f"Error during search: {e}")
        return jsonify({
            "error": str(e),
            "context": None
        }), 500

def index_default_documents():
    """Index default documents (CrewAI docs, etc.)"""
    indexed_count = 0
    
    # Look for documentation files in common locations
    doc_paths = [
        Path(__file__).parent.parent / "GopiAI-CrewAI" / "README.md",
        Path(__file__).parent.parent / "02_DOCUMENTATION",
        Path(__file__).parent / "txtai" / "docs",
    ]
    
    for doc_path in doc_paths:
        if doc_path.exists():
            if doc_path.is_file():
                indexed_count += index_file(doc_path)
            elif doc_path.is_dir():
                indexed_count += index_directory(doc_path)
    
    # Add some sample contextual information
    sample_docs = {
        "crewai_basics": {
            "content": """CrewAI is a multi-agent AI framework that allows you to create teams of AI agents 
            that can work together to solve complex tasks. Key concepts include Agents, Tasks, and Crews.
            Agents have roles, goals, and backstories. Tasks define what needs to be done.
            Crews coordinate the agents and tasks.""",
            "metadata": {"type": "documentation", "topic": "crewai_basics"}
        },
        "gopiai_features": {
            "content": """GopiAI is a modular AI system with multiple components including:
            - GopiAI-Core: Core functionality
            - GopiAI-UI: User interface components  
            - GopiAI-CrewAI: Multi-agent integration
            - RAG memory system: Context and knowledge management
            The system supports multiple LLM providers and has intelligent routing capabilities.""",
            "metadata": {"type": "documentation", "topic": "gopiai_features"}
        }
    }
    
    for doc_id, doc_data in sample_docs.items():
        DOCUMENT_STORE[doc_id] = {
            **doc_data,
            'indexed_at': time.time()
        }
        indexed_count += 1
    
    return indexed_count

def index_file(file_path: Path):
    """Index a single file"""
    try:
        if file_path.suffix.lower() in ['.md', '.txt', '.rst']:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            doc_id = f"file_{file_path.stem}"
            DOCUMENT_STORE[doc_id] = {
                'content': content,
                'metadata': {
                    'file_path': str(file_path),
                    'file_type': file_path.suffix,
                    'file_size': len(content)
                },
                'indexed_at': time.time()
            }
            return 1
    except Exception as e:
        logger.warning(f"Could not index file {file_path}: {e}")
    
    return 0

def index_directory(dir_path: Path):
    """Index all suitable files in a directory"""
    indexed_count = 0
    
    for file_path in dir_path.rglob("*.md"):
        indexed_count += index_file(file_path)
        if indexed_count > 50:  # Limit to prevent excessive indexing
            break
    
    return indexed_count

def search_documents(query: str, max_results: int) -> List[Dict]:
    """Simple search implementation"""
    query_lower = query.lower()
    results = []
    
    for doc_id, doc_data in DOCUMENT_STORE.items():
        content = doc_data.get('content', '').lower()
        
        # Simple keyword matching
        relevance_score = 0
        query_words = query_lower.split()
        
        for word in query_words:
            if word in content:
                relevance_score += content.count(word)
        
        if relevance_score > 0:
            results.append({
                'doc_id': doc_id,
                'content': doc_data.get('content', ''),
                'metadata': doc_data.get('metadata', {}),
                'relevance_score': relevance_score
            })
    
    # Sort by relevance and return top results
    results.sort(key=lambda x: x['relevance_score'], reverse=True)
    return results[:max_results]

if __name__ == '__main__':
    print(f"🧠 Starting GopiAI RAG Server at http://{HOST}:{PORT}")
    print(f"RAG Timeout: {RAG_TIMEOUT} seconds")
    print("This server provides context enrichment for AI agents")
    
    # Initialize server
    SERVER_STATUS["status"] = "online"
    
    # Index default documents on startup
    try:
        logger.info("Indexing default documents...")
        indexed_count = index_default_documents()
        SERVER_STATUS["indexed_documents"] = len(DOCUMENT_STORE)
        logger.info(f"Indexed {indexed_count} documents on startup")
    except Exception as e:
        logger.error(f"Error during startup indexing: {e}")
    
    app.run(host=HOST, port=PORT, debug=DEBUG)
