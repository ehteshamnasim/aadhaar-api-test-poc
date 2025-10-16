# AI-Powered API Test Automation POC

Proof of Concept for automated API test generation using Ollama Llama3:70b.

## 🎯 Features

- ✅ Parse OpenAPI specifications
- ✅ AI-powered test generation using **Ollama Llama3:70b**
- ✅ Contract testing (spec vs implementation)
- ✅ Code validation (syntax, imports, compilation)
- ✅ Automated test execution
- ✅ Coverage calculation (target: ≥85%)
- ✅ Git auto-commit
- ✅ CI/CD integration (GitHub Actions)
- ✅ Real-time dashboard with SSE

## 📋 Prerequisites

- Python 3.8+
- **Ollama** (with llama3:70b model)
- Git

## 🚀 Quick Start

### 1. Install Ollama

**macOS/Linux:**
```bash
curl https://ollama.ai/install.sh | sh
```

**Windows:**
Download from https://ollama.ai

### 2. Pull Llama3:70b Model
```bash
ollama pull llama3:70b
```

**Note:** This model is ~40GB. Make sure you have enough disk space and RAM (32GB+ recommended).

### 3. Start Ollama Server
```bash
ollama serve
```

Leave this running in a separate terminal.

### 4. Clone and Setup
```bash
git clone <repo-url>
cd aadhaar-api-test-poc
chmod +x setup.sh
./setup.sh
```

### 5. Start Dummy API (Terminal 2)
```bash
python api/dummy_aadhaar_api.py
```

### 6. Run POC (Terminal 3)
```bash
python main.py
```

### 7. Open Dashboard

Open browser: http://localhost:8080

## 🔧 Configuration

### Ollama Settings

Default Ollama endpoint: `http://localhost:11434`

To change, modify `src/test_generator.py`:
```python
def __init__(self, ollama_url: str = "http://your-ollama-server:11434"):
```

### Use Different Model

To use a different Ollama model:
```python
self.model = "codellama:34b"  # or another model
```

Available code models:
- `llama3:70b` (Best quality, needs 32GB+ RAM)
- `codellama:34b` (Good quality, needs 16GB+ RAM)
- `codellama:13b` (Faster, needs 8GB+ RAM)
- `llama3:8b` (Fastest, needs 4GB+ RAM)

## 🐛 Troubleshooting

### Ollama not found?
```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Verify installation
ollama --version
```

### Ollama not running?
```bash
# Start Ollama server
ollama serve

# In another terminal, check if it's running
curl http://localhost:11434/api/tags
```

### Model not found?
```bash
# Pull the model
ollama pull llama3:70b

# List installed models
ollama list
```

### Out of memory?
If you get OOM errors, use a smaller model:
```bash
ollama pull codellama:13b
```

Then update `src/test_generator.py`:
```python
self.model = "codellama:13b"
```

### Generation too slow?
- Use a smaller model (codellama:13b or llama3:8b)
- Or use GPU acceleration if available
- Increase timeout in `test_generator.py` if needed

## 📊 Performance

| Model | RAM Required | Generation Time | Quality |
|-------|--------------|-----------------|---------|
| llama3:70b | 32GB+ | ~60-120s | Excellent |
| codellama:34b | 16GB+ | ~30-60s | Good |
| codellama:13b | 8GB+ | ~15-30s | Decent |
| llama3:8b | 4GB+ | ~10-20s | Basic |

## 🎓 POC vs OpenAI

| Aspect | Ollama (Local) | OpenAI API |
|--------|---------------|------------|
| Cost | Free | ~$0.01-0.10 per run |
| Privacy | Data stays local | Data sent to cloud |
| Speed | Depends on hardware | Usually faster |
| Quality | Good (llama3:70b) | Excellent (GPT-4) |
| Setup | Needs installation | Just API key |
| Hardware | Needs GPU/RAM | No local requirements |

## 📝 Customization

### Switch Back to OpenAI

If you want to use OpenAI instead:

1. Install openai package:
```bash
pip install openai
```

2. Replace `src/test_generator.py` with OpenAI version (provided earlier)

3. Set API key:
```bash
export OPENAI_API_KEY='your-key'
```

