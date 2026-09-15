# Postman Testing Suite for Clauneck

This folder contains Postman collections and environments for end-to-end testing of the clauneck scientific prototyping platform.

## Files

- **Clauneck_Complete_Flow.postman_collection.json** — Main test collection (20+ test cases)
- **Clauneck_Local.postman_environment.json** — Environment variables for local testing
- **POSTMAN_TESTING_GUIDE.md** — Detailed guide for running and understanding tests

## Quick Start

### 1. Import into Postman

Open Postman (desktop or web) and:
1. Click **Import** (top left)
2. Upload both `.json` files from this folder
3. Select **Clauneck Local** environment (top right dropdown)

### 2. Start Services

```bash
# Terminal 1: Engine
cd engine && python -m uvicorn app.main:app --port 8001

# Terminal 2: Web
export ANTHROPIC_API_KEY="sk-ant-..."
export CLAUNECK_ENGINE_URL="http://localhost:8001"
./gradlew :web:bootRun
```

### 3. Run Tests

In Postman, run any request. Start with:
- **Setup → Health Check - Web**
- **Setup → Health Check - Engine**
- **Happy Path → Simple Projectile - 45° Launch**

## Test Coverage

✅ **Happy Path**: 3 projectile motion scenarios  
✅ **Statistics**: `mathematics.statistics` translation and direct-engine support
✅ **Input Validation**: Empty/null/too-long queries  
✅ **Error Cases**: Unsupported domains, service unavailable  
✅ **Direct Engine**: Bypass translator, test determinism  

Example statistics query: `Compute the mean of [1, 2, 3, 4, 5].`

## Documentation

See **POSTMAN_TESTING_GUIDE.md** for:
- Full setup instructions
- Response structure documentation
- Troubleshooting guide
- Performance benchmarks
- How to add custom tests

## Environment Variables

Edit **Clauneck_Local.postman_environment.json** to change:
- `web_url`: Spring Boot API gateway (default: `http://localhost:8080`)
- `engine_url`: Python FastAPI engine (default: `http://localhost:8001`)
- `anthropic_api_key`: Your API key (leave disabled unless needed)

## Next Steps

1. Read **POSTMAN_TESTING_GUIDE.md**
2. Start both services
3. Import collection and run health checks
4. Run the complete test suite via **Run collection** button

---

*Last updated: 2026-09-15*
