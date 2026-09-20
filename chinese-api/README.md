# Private Chinese photo task API

Python web service for the existing Star Island Chinese PWA. Build: `pip install -r requirements.txt`. Start: `python server.py`. Health: `/health`.

Requires a Render managed Secret File `/etc/secrets/chinese-ai.json` containing `provider` (the GLM vision API credential) and `signing` (a random service signing secret). Never commit these values. The public frontend does not include either secret.

`POST /activate` exchanges a private, signed, expiring family ticket for a device token. `/access`, `POST /jobs`, and `GET /jobs/:id` require the device token. Photo requests accept only inline JPEG/PNG/WebP data URLs; no arbitrary remote URLs. The service normalizes images, strips metadata, performs two model passes and validates source-aligned cards. Results expire after one hour; a restart loses pending jobs. Pairing credentials survive because the signing key is a managed secret.

No student history, handwriting or audio is uploaded. No photo/body logs or photo files are written. In-memory per-instance daily limits reduce accidental repetition and reset when the instance restarts; they are not a billing cap. Only paired family devices should have access.

Run validation with `python -m unittest discover -s . -v`. See the private source project's CHINESE.md for client storage, version migration and deployment details.
