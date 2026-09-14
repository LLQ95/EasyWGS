# Contributing

This repository contains both an executable workflow (numbered folders) and the guidebook
(docs/). Read the root CONTRIBUTING.md before submitting.

The documentation uses MkDocs Material with the mkdocs-static-i18n plugin. English is the
default language and Simplified Chinese is provided alongside it; when you add or change a
page, update both the English (`name.md`) and Chinese (`name.zh.md`) files so the two stay in
sync.

Preview locally:

```bash
pip install -r requirements-doc.txt
mkdocs serve
```

When adding a tool or changing parameters, update the corresponding script, the install
script and the tool map together, and add a changelog entry. Chinese pages give the English
term on first use to ease comparison with upstream documentation.
