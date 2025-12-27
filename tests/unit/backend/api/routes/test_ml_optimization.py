"""
Unit Tests for ML Optimization API Route
Tests ML optimization endpoints comprehensively.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import ml_optimization
except ImportError:
    pytest.skip(
        "Could not import ml_optimization route module", allow_module_level=True
    )


class TestMLOptimizationRouteImports:
    """Test ml_optimization route module can be imported."""

    def test_ml_optimization_module_imports(self):
        """Test ml_optimization module can be imported."""
        assert ml_optimization is not None, "Failed to import ml_optimization module"
        assert hasattr(
            ml_optimization, "router"
        ), "ml_optimization module missing router"
        assert hasattr(
            ml_optimization, "OptimizationRequest"
        ), "ml_optimization module missing OptimizationRequest model"
        assert hasattr(
            ml_optimization, "OptimizationResponse"
        ), "ml_optimization module missing OptimizationResponse model"
        assert hasattr(
            ml_optimization, "ExplainabilityRequest"
        ), "ml_optimization module missing ExplainabilityRequest model"

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert ml_optimization.router is not None, "Router should exist"
        assert hasattr(ml_optimization.router, "prefix"), "Router should have prefix"
        assert (
            ml_optimization.router.prefix == "/api/ml-optimization"
        ), "Router prefix should be /api/ml-optimization"

    def test_router_has_routes(self):
        """Test router has expected routes."""
        routes = [route.path for route in ml_optimization.router.routes]
        assert "/optimize" in routes, "Router should have /optimize route"
        assert "/explain" in routes, "Router should have /explain route"
        assert "/methods" in routes, "Router should have /methods route"


class TestMLOptimizationRouteHandlers:
    """Test ml_optimization route handlers exist."""

    def test_optimize_hyperparameters_handler_exists(self):
        """Test optimize_hyperparameters handler exists."""
        assert hasattr(
            ml_optimization, "optimize_hyperparameters"
        ), "optimize_hyperparameters handler should exist"
        assert callable(
            ml_optimization.optimize_hyperparameters
        ), "optimize_hyperparameters should be callable"

    def test_explain_model_handler_exists(self):
        """Test explain_model handler exists."""
        assert hasattr(
            ml_optimization, "explain_model"
        ), "explain_model handler should exist"
        assert callable(
            ml_optimization.explain_model
        ), "explain_model should be callable"

    def test_get_available_methods_handler_exists(self):
        """Test get_available_methods handler exists."""
        assert hasattr(
            ml_optimization, "get_available_methods"
        ), "get_available_methods handler should exist"
        assert callable(
            ml_optimization.get_available_methods
        ), "get_available_methods should be callable"


class TestMLOptimizationRouteFunctionality:
    """Test ml_optimization route functionality with mocks."""

    @patch("backend.api.routes.ml_optimization.HyperparameterOptimizer")
    def test_optimize_hyperparameters_optuna(self, mock_optimizer_class):
        """Test optimize_hyperparameters with optuna method."""
        # Mock optimizer
        mock_optimizer = MagicMock()
        mock_optimizer.get_available_methods.return_value = ["optuna", "hyperopt"]
        mock_result = MagicMock()
        mock_result.best_params = {"param1": 0.5, "param2": 1.0}
        mock_result.best_score = 0.25
        mock_result.n_trials = 100
        mock_result.method = "optuna"
        mock_result.trials = []
        mock_optimizer.optimize_with_optuna.return_value = mock_result
        mock_optimizer_class.return_value = mock_optimizer

        # Create request
        request = ml_optimization.OptimizationRequest(
            objective_function="test",
            search_space={"param1": [0, 1], "param2": [0, 2]},
            method="optuna",
            n_trials=100,
            direction="minimize",
        )

        # Test optimize_hyperparameters
        result = ml_optimization.optimize_hyperparameters(request)

        # Verify
        assert result.best_params == {"param1": 0.5, "param2": 1.0}
        assert result.best_score == 0.25
        assert result.n_trials == 100
        assert result.method == "optuna"
        mock_optimizer.optimize_with_optuna.assert_called_once()

    @patch("backend.api.routes.ml_optimization.HyperparameterOptimizer")
    def test_optimize_hyperparameters_hyperopt(self, mock_optimizer_class):
        """Test optimize_hyperparameters with hyperopt method."""
        # Mock optimizer
        mock_optimizer = MagicMock()
        mock_optimizer.get_available_methods.return_value = ["optuna", "hyperopt"]
        mock_result = MagicMock()
        mock_result.best_params = {"param1": 0.3}
        mock_result.best_score = 0.15
        mock_result.n_trials = 50
        mock_result.method = "hyperopt"
        mock_result.trials = []
        mock_optimizer.optimize_with_hyperopt.return_value = mock_result
        mock_optimizer_class.return_value = mock_optimizer

        # Create request
        request = ml_optimization.OptimizationRequest(
            objective_function="test",
            search_space={"param1": [0, 1]},
            method="hyperopt",
            n_trials=50,
            direction="minimize",
        )

        # Test optimize_hyperparameters
        result = ml_optimization.optimize_hyperparameters(request)

        # Verify
        assert result.method == "hyperopt"
        mock_optimizer.optimize_with_hyperopt.assert_called_once()

    @patch("backend.api.routes.ml_optimization.HyperparameterOptimizer")
    def test_optimize_hyperparameters_ray_not_implemented(self, mock_optimizer_class):
        """Test optimize_hyperparameters with ray method (not implemented)."""
        # Mock optimizer
        mock_optimizer = MagicMock()
        mock_optimizer.get_available_methods.return_value = [
            "optuna",
            "hyperopt",
            "ray",
        ]
        mock_optimizer_class.return_value = mock_optimizer

        # Create request
        request = ml_optimization.OptimizationRequest(
            objective_function="test",
            search_space={"param1": [0, 1]},
            method="ray",
            n_trials=100,
            direction="minimize",
        )

        # Test optimize_hyperparameters - should raise HTTPException
        with pytest.raises(Exception):  # Should raise HTTPException
            ml_optimization.optimize_hyperparameters(request)

    @patch("backend.api.routes.ml_optimization.ModelExplainer")
    @patch("backend.api.routes.ml_optimization.RandomForestRegressor")
    def test_explain_model_shap(self, mock_rf_class, mock_explainer_class):
        """Test explain_model with SHAP method."""
        # Mock explainer
        mock_explainer = MagicMock()
        mock_explainer.get_available_methods.return_value = ["shap", "lime"]
        mock_explainer.explain_with_shap.return_value = {
            "feature_importance": {"feature1": 0.5, "feature2": 0.3},
            "explanation": {"shap_values": [0.1, 0.2]},
        }
        mock_explainer_class.return_value = mock_explainer

        # Mock RandomForest
        mock_rf = MagicMock()
        mock_rf_class.return_value = mock_rf

        # Create request
        request = ml_optimization.ExplainabilityRequest(
            model_type="tree",
            features=[[0.1, 0.2], [0.3, 0.4]],
            method="shap",
            feature_names=["feature1", "feature2"],
        )

        # Test explain_model
        result = ml_optimization.explain_model(request)

        # Verify
        assert result.method == "shap"
        assert "feature_importance" in result.feature_importance
        mock_explainer.explain_with_shap.assert_called_once()

    @patch("backend.api.routes.ml_optimization.HyperparameterOptimizer")
    @patch("backend.api.routes.ml_optimization.ModelExplainer")
    def test_get_available_methods(self, mock_explainer_class, mock_optimizer_class):
        """Test get_available_methods."""
        # Mock optimizer
        mock_optimizer = MagicMock()
        mock_optimizer.get_available_methods.return_value = ["optuna", "hyperopt"]
        mock_optimizer_class.return_value = mock_optimizer

        # Mock explainer
        mock_explainer = MagicMock()
        mock_explainer.get_available_methods.return_value = ["shap", "lime"]
        mock_explainer_class.return_value = mock_explainer

        # Test get_available_methods
        result = ml_optimization.get_available_methods()

        # Verify
        assert "optimization_methods" in result
        assert "explainability_methods" in result
        assert "optuna" in result["optimization_methods"]
        assert "shap" in result["explainability_methods"]


class TestMLOptimizationRouteErrorHandling:
    """Test ml_optimization route error handling."""

    @patch("backend.api.routes.ml_optimization.HyperparameterOptimizer")
    def test_optimize_hyperparameters_invalid_method(self, mock_optimizer_class):
        """Test optimize_hyperparameters with invalid method."""
        # Mock optimizer
        mock_optimizer = MagicMock()
        mock_optimizer.get_available_methods.return_value = ["optuna", "hyperopt"]
        mock_optimizer_class.return_value = mock_optimizer

        # Create request with invalid method
        request = ml_optimization.OptimizationRequest(
            objective_function="test",
            search_space={"param1": [0, 1]},
            method="invalid_method",
            n_trials=100,
            direction="minimize",
        )

        # Test optimize_hyperparameters - should raise HTTPException
        with pytest.raises(Exception):  # Should raise HTTPException
            ml_optimization.optimize_hyperparameters(request)

    @patch("backend.api.routes.ml_optimization.ModelExplainer")
    def test_explain_model_invalid_method(self, mock_explainer_class):
        """Test explain_model with invalid method."""
        # Mock explainer
        mock_explainer = MagicMock()
        mock_explainer.get_available_methods.return_value = ["shap", "lime"]
        mock_explainer_class.return_value = mock_explainer

        # Create request with invalid method
        request = ml_optimization.ExplainabilityRequest(
            model_type="tree", features=[[0.1, 0.2]], method="invalid_method"
        )

        # Test explain_model - should raise HTTPException
        with pytest.raises(Exception):  # Should raise HTTPException
            ml_optimization.explain_model(request)

    @patch("backend.api.routes.ml_optimization.ModelExplainer")
    def test_explain_model_no_sklearn(self, mock_explainer_class):
        """Test explain_model when sklearn is not available."""
        # Mock explainer
        mock_explainer = MagicMock()
        mock_explainer.get_available_methods.return_value = ["shap", "lime"]
        mock_explainer_class.return_value = mock_explainer

        # Create request
        request = ml_optimization.ExplainabilityRequest(
            model_type="tree", features=[[0.1, 0.2]], method="shap"
        )

        # Mock ImportError for sklearn
        with patch(
            "builtins.__import__", side_effect=ImportError("No module named 'sklearn'")
        ):
            # Test explain_model - should raise HTTPException
            with pytest.raises(Exception):  # Should raise HTTPException
                ml_optimization.explain_model(request)
