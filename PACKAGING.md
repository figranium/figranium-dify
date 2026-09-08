# Dify Marketplace packaging

Marketplace packages are built and validated by `.github/workflows/validate-package.yml`.

The workflow creates a clean source tree from `git archive`, removes development-only metadata, packages with the official Dify plugin daemon, and validates the exact resulting `.difypkg` with Dify's official Marketplace toolkit before uploading it as an artifact.

Do not package directly from a Git working tree for Marketplace submission.
