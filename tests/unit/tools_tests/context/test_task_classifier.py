"""
Unit tests for TaskClassifier.
"""


class TestTaskClassifierBasic:
    """Basic tests for TaskClassifier."""

    def test_import(self):
        """TaskClassifier should be importable."""
        from tools.context.classifier.task_classifier import TaskClassifier

        assert TaskClassifier is not None

    def test_init_default(self):
        """Should initialize with default config."""
        from tools.context.classifier.task_classifier import TaskClassifier

        classifier = TaskClassifier()
        assert len(classifier.get_all_roles()) > 0

    def test_classify_build_keywords(self):
        """Should classify build-related prompts."""
        from tools.context.classifier.task_classifier import TaskClassifier

        classifier = TaskClassifier()
        result = classifier.classify("Fix the build error in the csproj file")

        assert result.role_profile == "build-tooling"
        assert result.confidence > 0

    def test_classify_ui_keywords(self):
        """Should classify UI-related prompts."""
        from tools.context.classifier.task_classifier import TaskClassifier

        classifier = TaskClassifier()
        result = classifier.classify("Update the XAML layout for the panel")

        assert result.role_profile == "ui-engineer"

    def test_classify_engine_keywords(self):
        """Should classify engine-related prompts."""
        from tools.context.classifier.task_classifier import TaskClassifier

        classifier = TaskClassifier()
        result = classifier.classify("Add support for the new TTS engine with CUDA")

        assert result.role_profile == "engine-engineer"

    def test_classify_debug_keywords(self):
        """Should classify debug-related prompts."""
        from tools.context.classifier.task_classifier import TaskClassifier

        classifier = TaskClassifier()
        result = classifier.classify("Debug the crash in the exception handler")

        assert result.role_profile == "debug-agent"

    def test_classification_result_has_fields(self):
        """ClassificationResult should have required fields."""
        from tools.context.classifier.task_classifier import TaskClassifier

        classifier = TaskClassifier()
        result = classifier.classify("Test prompt")

        assert hasattr(result, "role_profile")
        assert hasattr(result, "role_id")
        assert hasattr(result, "display_name")
        assert hasattr(result, "task_type")
        assert hasattr(result, "confidence")
        assert hasattr(result, "keywords_matched")

    def test_to_dict(self):
        """ClassificationResult.to_dict should work."""
        from tools.context.classifier.task_classifier import TaskClassifier

        classifier = TaskClassifier()
        result = classifier.classify("Build the solution")
        d = result.to_dict()

        assert isinstance(d, dict)
        assert "role_profile" in d
        assert "confidence" in d


class TestMCPSelector:
    """Tests for MCPSelector."""

    def test_import(self):
        """MCPSelector should be importable."""
        from tools.context.mcp_selector import MCPSelector

        assert MCPSelector is not None

    def test_recommend_mcps_function(self):
        """recommend_mcps function should work."""
        from tools.context.mcp_selector import recommend_mcps

        mcps = recommend_mcps("Build the CI pipeline", "build-tooling")

        assert isinstance(mcps, list)
        assert len(mcps) > 0

    def test_role_mcps(self):
        """Should return MCPs for a role."""
        from tools.context.mcp_selector import MCPSelector

        selector = MCPSelector()
        mcps = selector.get_role_mcps("build-tooling")

        assert isinstance(mcps, list)

    def test_recommendation_structure(self):
        """MCPRecommendation should have correct structure."""
        from tools.context.mcp_selector import MCPSelector

        selector = MCPSelector()
        rec = selector.recommend("Fix the build", "build-tooling")

        assert hasattr(rec, "mcps")
        assert hasattr(rec, "confidence")
        assert hasattr(rec, "reasoning")

    def test_to_preamble(self):
        """MCPRecommendation.to_preamble should format correctly."""
        from tools.context.mcp_selector import MCPSelector

        selector = MCPSelector()
        rec = selector.recommend("Test", "debug-agent")
        preamble = rec.to_preamble()

        assert isinstance(preamble, str)
        if rec.mcps:
            assert "MCP" in preamble or "mcp" in preamble.lower()


class TestClassifyFromPrompt:
    """Tests for the classify_from_prompt adapter."""

    def test_import(self):
        """classify_from_prompt should be importable."""
        from tools.context.sources.task_classifier import classify_from_prompt

        assert classify_from_prompt is not None

    def test_empty_prompt_returns_none(self):
        """Empty prompt should return None."""
        from tools.context.sources.task_classifier import classify_from_prompt

        result = classify_from_prompt("")
        assert result is None

    def test_valid_prompt_returns_result(self):
        """Valid prompt should return ClassificationResult."""
        from tools.context.sources.task_classifier import classify_from_prompt

        result = classify_from_prompt("Build the project and fix errors")

        if result:
            assert result.role_profile is not None
            assert result.confidence >= 0.2
