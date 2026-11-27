## What does this change?

<!-- Briefly describe the change and why it is needed. -->

## Which part is affected?

- [ ] The image (`Dockerfile`)
- [ ] Repository, workflows or docs (everything outside the `Dockerfile`)

## Related issues

<!-- e.g. Closes #123 -->

## Checklist

- [ ] The change is focused on one thing
- [ ] The `[Unreleased]` section of `CHANGELOG.md` has a short entry
- [ ] README or docs are updated if behavior changed
- [ ] The image still builds and runs as a non-root user
- [ ] No secrets or personal data are in the change or baked into the image
- [ ] Dockerfile changes: `pytest -m integration` passes
- [ ] Workflow changes: `actionlint` passes
- [ ] A new `rayohx-cli` version: the pin in `requirements.txt` and the `CHANGELOG.md` entry both say which version
- [ ] A release: `VERSION` and the `CHANGELOG.md` heading both match the tag you will publish
