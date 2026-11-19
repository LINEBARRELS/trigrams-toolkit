"""Guide discovery retains current package and installed source ownership."""
from __future__ import annotations

from unittest.mock import patch

from support import RuntimeCase, write_json
from trigrams_toolkit.handbook.guides import GuideCatalog
from trigrams_toolkit.installation.installation_sources import read_installation
from trigrams_toolkit.handbook.location import project_provider_root, sources_for_project


class GuideSourceTests(RuntimeCase):
    def test_core_uses_two_global_skills_for_the_selected_agent(self) -> None:
        import os
        import shutil
        root, env = self.install_core()
        project_skills = self.project / ".agents/skills"
        shutil.copytree(root, project_skills)
        with patch.dict(os.environ, {**env, "CLAUDE_CONFIG_DIR": str(self.root / "claude")}):
            packages = sources_for_project(self.project, self.schemas)
            self.assertEqual(sources_for_project(self.project, self.schemas, "claude-code"), {})
        loaded = GuideCatalog.discover(list(packages.values()), self.project, self.schemas).load("research")
        self.assertEqual({item["source"] for item in loaded["resources"]},
                         {str(root / "principles"), str(root / "workbook")})

    def test_project_guides_use_the_docs_package_declaration(self) -> None:
        local = self.project / "docs"
        write_json(local / "resources.json", {**self.manifest, "source": "project", "resourceRoots": []})
        self.assertEqual(project_provider_root(self.project), local)
        import os
        _, env = self.install_core()
        with patch.dict(os.environ, env):
            packages = sources_for_project(self.project, self.schemas)
        self.assertEqual(set(packages), {"core", "project"})

    def test_installation_record_requires_current_structure(self) -> None:
        write_json(self.project / ".agents/harness.json", {"schemaVersion": 1, "extensions": []})
        error = self.assert_code("invalid_schema", lambda: read_installation(self.project, self.schemas))
        self.assertIn("Archive unsupported records", str(error))
