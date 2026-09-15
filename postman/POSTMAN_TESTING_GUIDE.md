# Clauneck Postman Testing Guide

## Quick Start

### 1. Import Files into Postman

**Option A: Using Postman UI**
1. Open Postman desktop or web (postman.com)
2. Click **Import** (top left)
3. Select **File** tab
4. Upload `Clauneck_Complete_Flow.postman_collection.json`
5. Click **Import**
6. Repeat for `Clauneck_Local.postman_environment.json`

**Option B: Using Postman CLI**
```bash
postman collection import Clauneck_Complete_Flow.postman_collection.json
postman environment import Clauneck_Local.postman_environment.json
```

### 2. Start the Services

Open three terminal tabs:

**Terminal 1: Python Engine**
```bash
cd engine
python -m uvicorn app.main:app --port 8001
```
✓ Should see: `Uvicorn running on http://0.0.0.0:8001`

**Terminal 2: Spring Boot Web**
```bash
export ANTHROPIC_API_KEY="sk-ant-YOUR-KEY-HERE"
export CLAUDE_MODEL="claude-haiku-4-5"
export CLAUNECK_ENGINE_URL="http://localhost:8001"
./gradlew :web:bootRun
```
✓ Should see: `Tomcat started on port(s): 8080`

**Terminal 3: Postman (this tab)**

### 3. Select Environment in Postman

1. Top right of Postman, click **Environment** dropdown
2. Select **Clauneck Local**
3. You should see `web_url` and `engine_url` populated

### 4. Run Tests

## Test Collections

### A. Setup (Quick Health Checks)

Run these first to verify both services are online:

1. **Health Check - Web** → GET `/actuator/health` on web module
2. **Health Check - Engine** → GET `/health` on engine

Both should return `200 OK`.

### B. Happy Path (Success Cases)

Complete end-to-end translator → engine flow:

1. **Simple Projectile - 45° Launch**
   - Tests: Translator converts natural language → Model
   - Engine solves and returns trajectory
   - **Validates**: Full pipeline works

2. **Projectile with 30° Angle**
   - Tests: Different angle, different initial height
   - Confirms robustness

3. **Vertical Launch (90°)**
   - Tests: Edge case—pure vertical motion
   - Confirms solver handles degenerate cases

**Expected Response (all succeed):**
```json
{
  "model": {
    "domain": "physics.mechanics",
    "quantities": [...],
    "equations": [...],
    "initialConditions": {...},
    "solver": {...}
  },
  "result": {
    "success": true,
    "message": "Solved successfully",
    "trajectory": {
      "time": [0.0, 0.1, 0.2, ...],
      "x": [0.0, 1.41, 2.82, ...],
      "y": [0.0, 1.36, 2.65, ...]
    },
    "summary": {
      "maxHeight": 10.2,
      "range": 40.8,
      "timeOfFlight": 2.87
    }
  },
  "message": "OK"
}
```

### C. Error Cases - Input Validation

Test query validation (should return `400 Bad Request`):

1. **Empty Query** → `query: ""`
2. **Query Too Long** → `query: "[long string > 1000 chars]"`
3. **Null Query** → `query: null`

**Expected Error Response:**
```json
{
  "error": "TRANSLATION_FAILED",
  "message": "Could not translate query",
  "details": "Query must not be empty",
  "suggestion": "Provide a natural language physics query..."
}
```

### D. Error Cases - Domain & Translation

Test unsupported domains and ambiguous queries (may return `400` or `501`):

1. **Unsupported Domain (Chemistry)** → `query: "[chemistry problem]"`
   - **Expected**: `501 Not Implemented` with `"error": "DOMAIN_NOT_SUPPORTED"`

2. **Ambiguous Query** → `query: "Something goes up and down. How much?"`
   - **Expected**: `400 Bad Request` with `"error": "TRANSLATION_FAILED"`
   - Claude cannot extract structured model from vague query

### E. Error Cases - Service Unavailable

These requests are skipped during normal collection runs. Set the Postman environment
variable `run_manual_infrastructure_cases` to `true` and run them individually after
restarting Web with the explicitly required environment state:

1. **Engine Down (Wrong Port)**
   - Start Web with both variables set: `ANTHROPIC_API_KEY=... CLAUNECK_ENGINE_URL=http://localhost:9999 ./gradlew :web:bootRun`
   - Run any happy-path query
   - **Expected**: `502 Bad Gateway` with `"error": "ENGINE_UNAVAILABLE"`

2. **Missing ANTHROPIC_API_KEY**
   - Set `CLAUNECK_ENGINE_URL=http://localhost:8001`, unset `ANTHROPIC_API_KEY`, and restart Spring Boot
   - Run any query
   - **Expected**: `503 Service Unavailable` with `"error": "SERVICE_UNAVAILABLE"`

### F. Direct Engine Testing

Bypass the translator and test the engine directly:

1. **Engine Health** → GET `/health`
   - Validates Python service is running

2. **Direct Engine Solve (Raw Model)**
   - POST complete `ScientificModel` JSON to `/api/solve`
   - Tests engine determinism independent of translator
   - **Expected**: `200 OK` with trajectory

**Use case**: If translator changes, this verifies the engine hasn't regressed.

## Request/Response Structure

### Request Format (PrototypeRequest)
```json
{
  "query": "A projectile is launched at 45 degrees with initial velocity 20 m/s. How far does it travel?",
  "parameterOverrides": null
}
```

### Response Format (PrototypeResponse)
```json
{
  "model": {
    "id": "model-uuid",
    "domain": "physics.mechanics",
    "description": "Translated by Claude",
    "quantities": [
      {
        "name": "v0",
        "description": "Initial velocity",
        "value": 20.0,
        "siUnit": "m/s",
        "isKnown": true,
        "dimensionVector": {
          "length": 1,
          "mass": 0,
          "time": -1,
          "electricCurrent": 0,
          "temperature": 0,
          "amountOfSubstance": 0,
          "luminousIntensity": 0
        }
      }
    ],
    "equations": [
      {
        "lhs": "x",
        "rhs": "v0 * cos(theta * pi / 180) * t",
        "type": "algebraic",
        "description": "Horizontal position"
      }
    ],
    "initialConditions": {
      "t": 0.0,
      "x": 0.0,
      "y": 0.0
    },
    "boundaryConditions": [],
    "solver": {
      "method": "RK45",
      "tolerance": 1e-6,
      "timeSpan": {
        "start": 0.0,
        "end": 3.0,
        "numPoints": 100
      }
    },
    "metadata": {
      "createdAt": "2026-09-15T...",
      "source": "translator",
      "originalQuery": "A projectile is launched...",
      "validationErrors": []
    }
  },
  "result": {
    "success": true,
    "message": "Solved successfully",
    "trajectory": {
      "time": [0.0, 0.03, 0.06, ...],
      "x": [0.0, 0.42, 0.85, ...],
      "y": [0.0, 0.38, 0.74, ...]
    },
    "summary": {
      "maxHeight": 10.2,
      "range": 40.8,
      "timeOfFlight": 2.87
    }
  },
  "message": "OK"
}
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Postman can't connect to web** | Verify `./gradlew :web:bootRun` is running. Check `http://localhost:8080/actuator/health` in browser. |
| **Postman can't connect to engine** | Verify `python -m uvicorn app.main:app --port 8001` is running. Check `http://localhost:8001/health` in browser. |
| **Translation fails** | Ensure `ANTHROPIC_API_KEY` is set and valid. Check Spring Boot logs for Claude API errors. |
| **"DOMAIN_NOT_SUPPORTED"** | Supported domains are `physics.mechanics` and `mathematics.statistics`. |
| **"VALIDATION_FAILED"** | Query may be too ambiguous. Try: "Ball at 45°, 20 m/s" (explicit, numeric). |
| **Engine returns wrong values** | Run "Direct Engine Solve" test with same model twice—should be byte-for-byte identical (determinism). |

## Advanced Usage

### Running the Full Test Suite

In Postman:
1. Open collection sidebar (left panel)
2. Click three-dot menu next to "Clauneck Complete Flow"
3. Select **Run collection**
4. Choose environment: "Clauneck Local"
5. Click **Run**

Postman will execute all requests in order and show pass/fail for each test.

### Adding Custom Test Cases

To add a new query:
1. In Postman, right-click **Happy Path - Projectile Motion**
2. Select **Add Request**
3. Set **Method** to `POST`
4. Set **URL** to `{{web_url}}/api/prototype`
5. Set **Body** (raw JSON):
   ```json
   {
     "query": "Your natural language physics query here"
   }
   ```
6. Add **Tests** (validate response):
   ```javascript
   pm.test('Status code is 200', function () {
       pm.response.to.have.status(200);
   });
   
   pm.test('Response has model and result', function () {
       var jsonData = pm.response.json();
       pm.expect(jsonData).to.have.property('model');
       pm.expect(jsonData).to.have.property('result');
   });
   ```

### Monitoring Performance

1. In Postman, run a happy-path query
2. Click **Response** → **Timeline** tab
3. See breakdown: DNS, TCP, Request, Response, Total time

For the complete flow (translator → validation → engine):
- Typical latency: **200–500 ms** (dominated by Claude API call)
- Engine solve only: **50–100 ms** (SymPy + SciPy)

---

## File Locations

| File | Purpose |
|------|---------|
| `Clauneck_Complete_Flow.postman_collection.json` | Main test collection (import this) |
| `Clauneck_Local.postman_environment.json` | Environment variables (import this) |
| `POSTMAN_TESTING_GUIDE.md` | This guide |

The files are already checkout-relative under `postman/`. Validate them from the repository root:

```bash
python -m json.tool postman/Clauneck_Complete_Flow.postman_collection.json >/dev/null
```

Then add to `.gitignore` if you don't want the collection version-controlled, or commit them if you want to version control test cases.

---

## Next Steps

1. ✅ Import collection and environment
2. ✅ Start Python engine
3. ✅ Start Spring Boot web
4. ✅ Run "Health Check - Web" and "Health Check - Engine"
5. ✅ Run "Simple Projectile - 45° Launch"
6. ✅ Run full error test suite
7. 🔄 Iterate: Modify queries, add domain support, watch determinism

Happy testing! 🚀
