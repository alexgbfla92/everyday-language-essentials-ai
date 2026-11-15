# Guidelines for working in this repository

The root README is the public manifesto of the product. The skill lives entirely in skills/talkgo/ and only references files inside that folder; platform manifests live at the root. Keep development documentation in docs/. Every PR bumps VERSION with tools/bump_version.py. See START-HERE.md to find the project decisions.

The repository is written in English. Learner-facing text in other languages lives only in skills/talkgo/assets/locales/ (Central names and record templates per native language), in skills/talkgo/assets/targets/ (target-language material) and in the translated READMEs (README-<language>.md). After changing a template in assets/templates/ or a locale.json, run python tools/render_locales.py.

Distinguish the author's decisions, implementation proposals and capabilities proven by tests. Use fictional data in demonstrations. Keep learner files, credentials, personal folder links and backups out of Git. EnglishMission and EverydayEssentials are independent projects and their references are read-only.
