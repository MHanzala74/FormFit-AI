# Security Policy

## Privacy by design

FormFit AI runs **entirely on your machine**. Camera frames and videos are processed locally, voice feedback uses offline
text-to-speech, and nothing is uploaded anywhere. The only network access is downloading model weights (for example
`yolov8n-pose.pt` on first use of the YOLO backend) through the libraries you install.

## Reporting a vulnerability

Please do **not** open a public issue for security problems. Use GitHub's
[private vulnerability reporting](https://github.com/MHanzala74/FormFit-AI/security/advisories/new) for this repository
and include steps to reproduce. You can expect an initial response within a few days.

## Supported versions

Only the latest release on `main` receives fixes.
