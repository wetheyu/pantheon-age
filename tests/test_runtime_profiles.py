import os
import unittest
from unittest.mock import patch

from agentic_runtime.providers import build_agentic_providers_from_env
from agentic_runtime.runtime_profiles import (
    PLAY_PROFILE_ENV_VAR,
    active_runtime_profile,
    apply_runtime_profile,
    available_runtime_profiles,
)


class RuntimeProfileTests(unittest.TestCase):
    def test_available_profiles_include_expected_play_modes(self):
        names = {profile.name for profile in available_runtime_profiles()}

        self.assertEqual(names, {"local", "fast", "quality", "debug"})

    def test_active_runtime_profile_reads_environment_name(self):
        with patch.dict(os.environ, {PLAY_PROFILE_ENV_VAR: "fast"}, clear=False):
            profile = active_runtime_profile()

        self.assertEqual(profile.name, "fast")
        self.assertIn("真实试玩", profile.description)

    def test_apply_runtime_profile_sets_runtime_defaults(self):
        with patch.dict(os.environ, {PLAY_PROFILE_ENV_VAR: "quality"}, clear=False):
            profile = active_runtime_profile()
            apply_runtime_profile(profile)

            self.assertEqual(os.environ["PANTHEON_USE_AGENTIC_LLM"], "1")
            self.assertEqual(os.environ["PANTHEON_CREATIVE_GM_MODE"], "1")
            self.assertEqual(os.environ["PANTHEON_CANON_RETRIEVAL"], "vector_hybrid")
            self.assertEqual(os.environ["PANTHEON_OPENAI_MAX_OUTPUT_TOKENS"], "5000")

    def test_build_agentic_providers_uses_local_profile_without_llm(self):
        with patch.dict(
            os.environ,
            {
                PLAY_PROFILE_ENV_VAR: "local",
                "OPENAI_API_KEY": "",
                "PANTHEON_USE_AGENTIC_LLM": "1",
            },
            clear=False,
        ):
            providers = build_agentic_providers_from_env()

        self.assertFalse(providers.llm_enabled)
        self.assertEqual(providers.runtime_profile, "local")
        self.assertIn("Runtime profile local", providers.reason)

    def test_build_agentic_providers_keeps_profile_when_api_key_is_missing(self):
        with patch.dict(
            os.environ,
            {
                PLAY_PROFILE_ENV_VAR: "fast",
                "OPENAI_API_KEY": "",
                "PANTHEON_USE_AGENTIC_LLM": "0",
            },
            clear=False,
        ):
            providers = build_agentic_providers_from_env()

        self.assertFalse(providers.llm_enabled)
        self.assertEqual(providers.runtime_profile, "fast")
        self.assertIn("OPENAI_API_KEY is missing", providers.reason)

    def test_agentic_providers_report_openai_compatible_endpoint(self):
        with patch.dict(
            os.environ,
            {
                PLAY_PROFILE_ENV_VAR: "fast",
                "OPENAI_API_KEY": "",
                "PANTHEON_USE_AGENTIC_LLM": "1",
                "PANTHEON_OPENAI_PROVIDER": "lm_studio",
                "PANTHEON_OPENAI_BASE_URL": "http://localhost:1234/v1",
            },
            clear=False,
        ):
            providers = build_agentic_providers_from_env()

        endpoint = providers.to_dict()["provider_endpoint"]
        self.assertEqual(endpoint["provider"], "lm_studio")
        self.assertEqual(endpoint["endpoint"], "custom_openai_compatible")
        self.assertEqual(endpoint["base_url_origin"], "http://localhost:1234")


if __name__ == "__main__":
    unittest.main()
