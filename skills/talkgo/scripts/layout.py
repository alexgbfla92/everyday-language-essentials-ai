"""Localized layout of a Central: folder and file names, prefixes, tabs and status labels.

Every Central has a fixed manifest at its root, `talkgo.json`, with the learner's native language and
the names used in that Central. Scripts and the skill find every folder and file through it, never
through hard-coded names, so a Central in English and another in Portuguese work with the same code.
Record fields (`status:`, `mission_id:`, `lab_*`...) and status values are machine keys in English.
"""
import json
from pathlib import Path, PurePosixPath

ASSETS = Path(__file__).resolve().parents[1] / "assets"
LOCALES = ASSETS / "locales"
TEMPLATES = "templates"
MANIFEST = "talkgo.json"
TARGETS = ("en-US", "es-ES", "fr-FR", "pt-BR", "zh-CN", "it-IT", "ja-JP", "de-DE", "ko-KR", "hi-IN", "ar")
PRACTICE_STATUS = ("prepared", "running", "paused", "completed")
MISSION_STATUS = ("active", "paused", "completed")


def available_locales():
    return sorted(p.name for p in LOCALES.iterdir() if (p / "locale.json").is_file())


def locale_code(native):
    """Locale whose names are used for a native language; unknown languages fall back to `en`."""
    native = (native or "en").strip()
    codes = {code.lower(): code for code in available_locales()}
    if native.lower() in codes:
        return codes[native.lower()]
    base = native.split("-")[0].split("_")[0].lower()
    for code in codes.values():
        if code.split("-")[0].lower() == base:
            return code
    return "en"


def load_locale(native):
    code = locale_code(native)
    return json.loads((LOCALES / code / "locale.json").read_text(encoding="utf-8"))


def template_path(native, name):
    return LOCALES / locale_code(native) / TEMPLATES / f"{name}.md"


def build_manifest(native):
    """Content of talkgo.json for a new Central."""
    data = load_locale(native)
    return {
        "talkgo": 1,
        "native_language": native,
        "locale": data["code"],
        "paths": data["paths"],
        "prefixes": data["prefixes"],
        "targets": {tag: data["targets"][tag]["folder"] for tag in TARGETS},
        "target_names": {tag: data["targets"][tag]["name"] for tag in TARGETS},
        "tabs": data["tabs"],
        "labels": {"completed_practices": data["text"]["label_completed_practices"],
                   "observed_duration": data["text"]["label_observed_duration"]},
        "status": data["status"],
        "mission_status": data["mission_status"],
        "stage_status": data["stage_status"],
    }


class Layout:
    """Logical paths (POSIX, relative to the Central root) for one Central."""

    def __init__(self, manifest):
        self.m = manifest
        self.p = manifest["paths"]

    @classmethod
    def for_native(cls, native):
        return cls(build_manifest(native))

    @classmethod
    def read(cls, root):
        path = Path(root) / MANIFEST
        if not path.is_file():
            raise ValueError(f"{root} is not a TalkGo Central ({MANIFEST} not found).")
        return cls(json.loads(path.read_text(encoding="utf-8")))

    @property
    def native(self):
        return self.m["native_language"]

    # Central level
    def config(self):
        return self.p["config"]

    def central_state(self):
        return f"{self.p['config']}/{self.p['central_state']}"

    def learner_profile(self):
        return f"{self.p['config']}/{self.p['learner_profile']}"

    def languages(self):
        return self.p["languages"]

    # Language level
    def language(self, tag):
        return f"{self.p['languages']}/{self.m['targets'][tag]}"

    def lang_state(self, tag):
        return f"{self.language(tag)}/{self.p['lang_state']}"

    def active_session(self, tag):
        return f"{self.lang_state(tag)}/{self.p['active_session']}"

    def recent_context(self, tag):
        return f"{self.lang_state(tag)}/{self.p['recent_context']}"

    def current_profile(self, tag):
        return f"{self.lang_state(tag)}/{self.p['current_profile']}"

    def diagnostics(self, tag):
        return f"{self.language(tag)}/{self.p['diagnostics']}"

    def practices(self, tag):
        return f"{self.language(tag)}/{self.p['practices']}"

    def missions(self, tag):
        return f"{self.language(tag)}/{self.p['missions']}"

    def progress(self, tag):
        return f"{self.language(tag)}/{self.p['progress']}"

    def progress_log(self, tag):
        return f"{self.progress(tag)}/{self.p['progress_log']}"

    def history(self, tag):
        return f"{self.progress(tag)}/{self.p['history']}"

    def history_readme(self, tag):
        return f"{self.history(tag)}/{self.p['history_readme']}"

    def prefix(self, kind):
        return self.m["prefixes"][kind]

    def target_name(self, tag):
        return self.m["target_names"][tag]

    def tag_of_folder(self, folder):
        return next((tag for tag, name in self.m["targets"].items() if name == folder), None)

    def status_label(self, code):
        return self.m["status"].get(code, code)

    def stage_status_label(self, code):
        """Label of a practice stage state; Centrals created before stage states fall back to their locale."""
        labels = self.m.get("stage_status") or load_locale(self.m.get("locale", "en")).get("stage_status", {})
        return labels.get(code, code)

    def mission_status_label(self, code):
        return self.m["mission_status"].get(code, code)

    def specification(self, languages):
        """Ordered {logical path: (kind, template or None, tag)} of everything provisioned.

        kind: folder | manifest | markdown | google-doc | google-sheet (the Drive format)."""
        spec = {MANIFEST: ("manifest", None, None), self.config(): ("folder", None, None),
                self.central_state(): ("google-doc", "central-state", None),
                self.learner_profile(): ("google-doc", "learner-profile", None),
                self.languages(): ("folder", None, None)}
        for tag in languages:
            spec[self.language(tag)] = ("folder", None, tag)
            spec[self.lang_state(tag)] = ("folder", None, tag)
            spec[self.active_session(tag)] = ("google-doc", "active-session", tag)
            spec[self.recent_context(tag)] = ("google-doc", "recent-context", tag)
            spec[self.current_profile(tag)] = ("google-doc", "current-profile", tag)
            for folder in (self.diagnostics(tag), self.practices(tag), self.missions(tag), self.progress(tag),
                           self.history(tag)):
                spec[folder] = ("folder", None, tag)
            spec[self.progress_log(tag)] = ("google-sheet", "progress-log", tag)
            spec[self.history_readme(tag)] = ("markdown", "history-readme", tag)
        return dict(sorted(spec.items(), key=lambda pair: (pair[0].count("/"), pair[0])))

    def classify(self, path):
        """Drive format of any logical path, including records created during use."""
        posix = PurePosixPath(path)
        parent, name = str(posix.parent), posix.name
        for tag in TARGETS:
            if parent == self.practices(tag) and name.startswith(self.prefix("practice") + "-"):
                return "google-doc"
            if parent == self.diagnostics(tag) and name.startswith(self.prefix("diagnostic") + "-"):
                return "google-doc"
            if parent == self.missions(tag):
                return "google-doc"
        spec = self.specification(TARGETS)
        return spec[path][0] if path in spec else "markdown"

    def render(self, template, tag=None):
        text = template_path(self.native, template).read_text(encoding="utf-8")
        values = {"native": self.native, "tag": tag or "", "target_name": self.target_name(tag) if tag else ""}
        for key, value in values.items():
            text = text.replace("{{" + key + "}}", value)
        return text
