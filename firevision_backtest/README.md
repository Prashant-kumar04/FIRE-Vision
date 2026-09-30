# FIRE-Vision
### Forensic Intelligence & Reconstruction Engine

> Don’t just recover the footage. Reconstruct the evidence.

FIRE-Vision is a **working MVP/prototype** for SIH 2026 Problem Statement 26150. It implements a defensible evidence workflow: import-copy, MD5/SHA-256 integrity, generic/Demo DVR identification, FFprobe metadata extraction, controlled recovery fixture carving, transparent recovery confidence, timestamp normalization, AI analysis fallback, evidence graph, evidence passport, hash-chained audit, replay, PDF reporting, and automated tests.

## Important scope
This is a research prototype. It does **not** claim proprietary OEM DVR/NVR support, universal deleted-video recovery, automatic court admissibility, or 100% recovery. Proprietary formats require representative OEM samples and validation.

## Architecture
```text
React/Vite UI
      |
 FastAPI REST API
      |
+-----+-----------------------------+
| SQLite / SQLAlchemy               |
|                                  |
| Evidence -> Hash -> Identify     |
|             -> FFprobe           |
|             -> Controlled Carve  |
|             -> Timeline           |
|             -> AI Analysis        |
|             -> Graph/Passport     |
|             -> Audit Chain        |
|             -> Report             |
+----------------------------------+
      |
 Evidence Store (immutable-by-convention working master)
```
See `docs/architecture.svg`.

## Requirements
- Python 3.11+ (tested with Python 3.13)
- Node.js 20+
- FFmpeg + FFprobe on PATH

## Install
### Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173.

## Seed the default demo case
From project root after generating fixtures:
```bash
python scripts/seed_demo.py
```
This creates `FV-2026-0001` and imports the controlled Demo-DVR evidence copy.

## Generate controlled test evidence
From project root:
```bash
python scripts/generate_test_evidence.py
```
This creates genuine short MP4 recordings and a separate controlled recovery fixture. The recovery fixture is deliberately **not** presented as a proprietary DVR image.

## Demo workflow
1. Create case `FV-2026-0001`.
2. Import `test_evidence/demo_dvr_evidence.bin` to demonstrate the Demo DVR signature. For FFprobe metadata, import a generated MP4 as well.
3. Verify MD5/SHA-256.
4. Identify DVR profile.
5. Extract metadata from a valid MP4.
6. Run controlled recovery on `controlled_recovery_fixture.bin`.
7. Add a normalized timeline event.
8. Run AI analysis on a valid video. If no person is detected, the UI explicitly reports that no validated detection was found.
9. Open graph/passport/replay.
10. Generate PDF and verify the audit chain.

## API
- `POST /api/cases`
- `GET /api/cases`
- `POST /api/evidence/upload`
- `GET /api/evidence/{id}`
- `POST /api/evidence/{id}/hash`
- `POST /api/evidence/{id}/verify`
- `POST /api/identify/{id}`
- `POST /api/parse/{id}`
- `POST /api/recovery/{id}`
- `GET /api/recovery/{id}/results`
- `POST /api/timeline/{case_id}`
- `GET /api/timeline/{case_id}`
- `POST /api/analytics/{artifact_id}`
- `GET /api/graph/{case_id}`
- `GET /api/passport/{artifact_id}`
- `GET /api/replay/{case_id}`
- `POST /api/audit/verify?case_id={id}`
- `POST /api/report/{case_id}`

## Security controls
Path basename sanitization, extension allowlist, upload size limit, UUID-backed controlled paths, no shell execution from user input, subprocess argument arrays for FFmpeg/FFprobe, no arbitrary evidence download endpoint, and audit logging.

## AI limitations
The base install uses OpenCV HOG as an offline person-detection fallback. It is not a general vehicle/object classifier. To add YOLO, configure a locally available YOLO-family model and add the model adapter; the application must continue to label the model/version used for each finding.

## Validation
Run:
```bash
cd backend
pytest -q
```
Tests cover hashing/change detection, filename/path hardening, audit-chain tamper detection, and the controlled recovery fixture. Additional API/integration tests can be extended against the generated fixtures.

## Final validation note

The included backend regression suite and end-to-end workflow have been executed against the packaged source, including case creation, evidence import, MD5/SHA-256 verification, Demo DVR identification, FFprobe parsing, media delivery, controlled recovery, timestamp normalization, AI execution, graph/passport/replay generation, PDF reporting, and audit-chain tamper detection.

The frontend source was statically checked for component references, package JSON validity, accessibility-oriented navigation structure, and the light institutional theme. A production Vite build requires the frontend npm dependencies to be installed (`npm install`); the validation environment could not complete npm dependency installation within its network/time limit, so the frontend production bundle is not represented as independently build-verified here.
