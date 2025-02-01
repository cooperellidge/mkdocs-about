# mkdocs-about

Generate an About page for MkDocs based on GitHub repos

## Future work

- CLI to simply generate the `about.md` without MkDocs plugin
- repos outside the given username, e.g. from organisations
- repos from outside github
- bug: mkdocs serve goes into infinite loop if mkdocs.yml config is changed, or if about.md is changed
  - [relevant issue](https://github.com/mkdocs/mkdocs/issues/1479)
- cleanup about.md after a build (likely related to above)
