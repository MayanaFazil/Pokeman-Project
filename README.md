# Pokemon Gateway API

A robust, publicly accessible **REST API microservice** that acts as a simplified gateway to the official [PokéAPI](https://pokeapi.co/).

This project was built using **FastAPI** and provides two endpoints:

- `GET /health` → Service health check  
- `GET /pokemon-info?name={pokemon_name}` → Retrieve simplified Pokemon data  

> **Note:** No authentication or API keys are required.

---

## 🚀 Features
- Health check endpoint  
- Fetch Pokémon details by name (case-insensitive)  
- Returns `name`, `type`, `height`, `weight`, and `first_ability`  
- Proper error handling (400, 404, 502)  
- Retries upstream API failures with exponential backoff  
- JSON responses with correct `Content-Type` headers  

---

## 📋 Endpoints

### 1. Health Check
**Request:**  
http
GET /health
```
{
  "status": "ok"
}
```

### 2. Pokemon Information
**Request:** 
http
GET /pokemon-info?name=ditto
```
Response (200 OK):

{
  "name": "ditto",
  "type": "normal",
  "height": 3,
  "weight": 40,
  "first_ability": "limber"
}
```

```
Error Response (404 Not Found):

{
  "error": "Pokemon not found"
}
```
```
Error Response (400 Bad Request):

{
  "error": "missing 'name' query parameter"
}
```
```
Error Response (502 Bad Gateway):

{
  "error": "upstream service unavailable"
}
```

## 🛠️ Tech Stack
Python 3.12 <br>
FastAPI (REST API framework) <br>
httpx (async HTTP client) <br>

### 1. Clone Repository
```
git clone https://github.com/your-username/pokemon-gateway.git
cd pokemon-gateway
```

### 2. Create Virtual Environment & Install Dependencies
```
python -m venv venv
source venv/bin/activate   # On Linux / Mac
venv\Scripts\activate      # On Windows

pip install -r requirements.txt
```

### 3. Run Locally
```
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Now visit:
```
http://127.0.0.1:8000/health

http://127.0.0.1:8000/pokemon-info?name=ditto
```
## 🌐 Deployment
You can deploy the service to any hosting provider.
Recommended options:
- Vercel
- Render
- Railway

Example with Vercel:
- Add a vercel.json config file
- Push repo to GitHub
- Import project in Vercel → Deploy

## ✅ Acceptance Criteria (Met)
- GET /health implemented
- GET /pokemon-info?name={pokemon_name} implemented
- No authentication required
- Returns valid JSON with correct HTTP status codes
- Handles upstream errors gracefully

## 🤖 AI Usage
- This project was built with the help of AI assistants (ChatGPT & others) for:
- Researching FastAPI best practices
- Debugging async requests
- Writing clean, production-ready code
