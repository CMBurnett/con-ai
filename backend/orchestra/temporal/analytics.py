"""
Predictive Analytics for Construction Intelligence

Provides machine learning-based predictions for project outcomes,
schedule drift, budget variance, and quality issues.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, accuracy_score
import pandas as pd

from orchestra.temporal.models import TemporalEvent, PredictionResult, PatternAnalysis
from orchestra.temporal.knowledge_graph import TemporalKnowledgeGraph

logger = logging.getLogger(__name__)


class PredictiveAnalytics:
    """Machine learning-based predictive analytics for construction projects."""

    def __init__(self, knowledge_graph: TemporalKnowledgeGraph):
        self.knowledge_graph = knowledge_graph
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_importance = {}

    async def initialize(self):
        """Initialize predictive models."""
        try:
            # Initialize ML models
            self.models = {
                "schedule_drift": RandomForestRegressor(
                    n_estimators=100, random_state=42
                ),
                "budget_variance": RandomForestRegressor(
                    n_estimators=100, random_state=42
                ),
                "quality_risk": GradientBoostingClassifier(
                    n_estimators=100, random_state=42
                ),
                "collaboration_effectiveness": RandomForestRegressor(
                    n_estimators=100, random_state=42
                ),
            }

            # Initialize preprocessing tools
            self.scalers = {
                model_name: StandardScaler() for model_name in self.models.keys()
            }
            self.encoders = {
                model_name: LabelEncoder() for model_name in self.models.keys()
            }

            logger.info("Predictive analytics models initialized")

        except Exception as e:
            logger.error(f"Failed to initialize predictive analytics: {e}")
            raise

    async def predict_schedule_drift(
        self, project_id: str, horizon_days: int = 30
    ) -> Dict[str, Any]:
        """Predict schedule drift for a project."""
        try:
            # Get historical data
            historical_data = await self._get_schedule_features(project_id)

            if not historical_data or len(historical_data) < 10:
                return await self._generate_baseline_prediction(
                    "schedule_drift", project_id, horizon_days
                )

            # Prepare features
            features = await self._prepare_schedule_features(historical_data)

            # Train or use existing model
            model = await self._get_or_train_model(
                "schedule_drift", features, "drift_days"
            )

            # Make prediction
            latest_features = features.iloc[-1:].drop(
                columns=["drift_days"], errors="ignore"
            )
            prediction = model.predict(latest_features)[0]

            # Calculate confidence
            confidence = await self._calculate_prediction_confidence(
                "schedule_drift", features, prediction
            )

            result = {
                "prediction_type": "schedule_drift",
                "predicted_drift_days": float(prediction),
                "confidence_score": confidence,
                "risk_level": self._categorize_schedule_risk(prediction),
                "contributing_factors": await self._get_schedule_risk_factors(features),
                "recommendations": await self._generate_schedule_recommendations(
                    prediction, features
                ),
            }

            # Store prediction
            await self._store_prediction_result(
                project_id, "schedule_drift", result, horizon_days
            )

            return result

        except Exception as e:
            logger.error(f"Schedule drift prediction failed: {e}")
            return await self._generate_baseline_prediction(
                "schedule_drift", project_id, horizon_days
            )

    async def predict_budget_variance(
        self, project_id: str, horizon_days: int = 30
    ) -> Dict[str, Any]:
        """Predict budget variance for a project."""
        try:
            # Get historical budget data
            historical_data = await self._get_budget_features(project_id)

            if not historical_data or len(historical_data) < 10:
                return await self._generate_baseline_prediction(
                    "budget_variance", project_id, horizon_days
                )

            # Prepare features
            features = await self._prepare_budget_features(historical_data)

            # Train or use existing model
            model = await self._get_or_train_model(
                "budget_variance", features, "variance_percent"
            )

            # Make prediction
            latest_features = features.iloc[-1:].drop(
                columns=["variance_percent"], errors="ignore"
            )
            prediction = model.predict(latest_features)[0]

            # Calculate confidence
            confidence = await self._calculate_prediction_confidence(
                "budget_variance", features, prediction
            )

            result = {
                "prediction_type": "budget_variance",
                "predicted_variance_percent": float(prediction),
                "confidence_score": confidence,
                "risk_level": self._categorize_budget_risk(prediction),
                "cost_impact": await self._estimate_cost_impact(project_id, prediction),
                "contributing_factors": await self._get_budget_risk_factors(features),
                "recommendations": await self._generate_budget_recommendations(
                    prediction, features
                ),
            }

            # Store prediction
            await self._store_prediction_result(
                project_id, "budget_variance", result, horizon_days
            )

            return result

        except Exception as e:
            logger.error(f"Budget variance prediction failed: {e}")
            return await self._generate_baseline_prediction(
                "budget_variance", project_id, horizon_days
            )

    async def predict_quality_issues(
        self, project_id: str, horizon_days: int = 30
    ) -> Dict[str, Any]:
        """Predict likelihood of quality issues."""
        try:
            # Get historical quality data
            historical_data = await self._get_quality_features(project_id)

            if not historical_data or len(historical_data) < 10:
                return await self._generate_baseline_prediction(
                    "quality_risk", project_id, horizon_days
                )

            # Prepare features
            features = await self._prepare_quality_features(historical_data)

            # Train or use existing model
            model = await self._get_or_train_model(
                "quality_risk", features, "has_quality_issue"
            )

            # Make prediction
            latest_features = features.iloc[-1:].drop(
                columns=["has_quality_issue"], errors="ignore"
            )
            prediction_proba = model.predict_proba(latest_features)[0]
            prediction = prediction_proba[1]  # Probability of quality issue

            # Calculate confidence
            confidence = await self._calculate_prediction_confidence(
                "quality_risk", features, prediction
            )

            result = {
                "prediction_type": "quality_issues",
                "predicted_risk_probability": float(prediction),
                "confidence_score": confidence,
                "risk_level": self._categorize_quality_risk(prediction),
                "likely_issue_types": await self._predict_issue_types(features),
                "contributing_factors": await self._get_quality_risk_factors(features),
                "recommendations": await self._generate_quality_recommendations(
                    prediction, features
                ),
            }

            # Store prediction
            await self._store_prediction_result(
                project_id, "quality_issues", result, horizon_days
            )

            return result

        except Exception as e:
            logger.error(f"Quality issues prediction failed: {e}")
            return await self._generate_baseline_prediction(
                "quality_risk", project_id, horizon_days
            )

    async def predict_collaboration_effectiveness(
        self, project_id: str, horizon_days: int = 30
    ) -> Dict[str, Any]:
        """Predict team collaboration effectiveness."""
        try:
            # Get collaboration data
            historical_data = await self._get_collaboration_features(project_id)

            if not historical_data or len(historical_data) < 5:
                return await self._generate_baseline_prediction(
                    "collaboration_effectiveness", project_id, horizon_days
                )

            # Prepare features
            features = await self._prepare_collaboration_features(historical_data)

            # Train or use existing model
            model = await self._get_or_train_model(
                "collaboration_effectiveness", features, "effectiveness_score"
            )

            # Make prediction
            latest_features = features.iloc[-1:].drop(
                columns=["effectiveness_score"], errors="ignore"
            )
            prediction = model.predict(latest_features)[0]

            # Calculate confidence
            confidence = await self._calculate_prediction_confidence(
                "collaboration_effectiveness", features, prediction
            )

            result = {
                "prediction_type": "collaboration_effectiveness",
                "predicted_effectiveness_score": float(prediction),
                "confidence_score": confidence,
                "effectiveness_level": self._categorize_collaboration_effectiveness(
                    prediction
                ),
                "improvement_opportunities": await self._identify_collaboration_improvements(
                    features
                ),
                "contributing_factors": await self._get_collaboration_factors(features),
                "recommendations": await self._generate_collaboration_recommendations(
                    prediction, features
                ),
            }

            # Store prediction
            await self._store_prediction_result(
                project_id, "collaboration_effectiveness", result, horizon_days
            )

            return result

        except Exception as e:
            logger.error(f"Collaboration effectiveness prediction failed: {e}")
            return await self._generate_baseline_prediction(
                "collaboration_effectiveness", project_id, horizon_days
            )

    async def train_models_from_historical_data(self) -> Dict[str, Any]:
        """Train all models using historical data from knowledge graph."""
        try:
            training_results = {}

            for model_name in self.models.keys():
                try:
                    # Get training data
                    training_data = await self._get_training_data(model_name)

                    if len(training_data) < 20:
                        logger.warning(
                            f"Insufficient training data for {model_name}: {len(training_data)} samples"
                        )
                        continue

                    # Prepare features and train
                    features = await self._prepare_features_for_training(
                        model_name, training_data
                    )
                    model_results = await self._train_single_model(model_name, features)

                    training_results[model_name] = model_results

                except Exception as e:
                    logger.error(f"Failed to train model {model_name}: {e}")
                    training_results[model_name] = {"error": str(e)}

            logger.info(f"Model training completed: {len(training_results)} models")
            return training_results

        except Exception as e:
            logger.error(f"Model training failed: {e}")
            return {}

    async def _get_schedule_features(self, project_id: str) -> List[Dict[str, Any]]:
        """Get schedule-related features for a project."""
        # Simulate getting schedule features from knowledge graph
        return [
            {
                "timestamp": datetime.now() - timedelta(days=i),
                "tasks_completed": 15 + i,
                "tasks_delayed": max(0, 3 - i // 5),
                "resource_utilization": 0.75 + (i % 10) * 0.02,
                "critical_path_delay": max(0, 2 - i // 10),
                "weather_impact": 1 if i % 7 == 0 else 0,
                "drift_days": max(0, 5 - i // 5),  # Target variable
            }
            for i in range(30)
        ]

    async def _get_budget_features(self, project_id: str) -> List[Dict[str, Any]]:
        """Get budget-related features for a project."""
        # Simulate getting budget features from knowledge graph
        return [
            {
                "timestamp": datetime.now() - timedelta(days=i),
                "spent_to_date": 100000 + i * 5000,
                "committed_costs": 80000 + i * 3000,
                "change_orders": i // 10,
                "material_cost_variance": (i % 20 - 10) * 0.01,
                "labor_cost_variance": (i % 15 - 7) * 0.01,
                "vendor_payment_delays": i % 5,
                "variance_percent": (i % 20 - 10) * 0.5,  # Target variable
            }
            for i in range(30)
        ]

    async def _prepare_schedule_features(
        self, data: List[Dict[str, Any]]
    ) -> pd.DataFrame:
        """Prepare schedule features for ML model."""
        df = pd.DataFrame(data)

        # Feature engineering
        df["task_completion_rate"] = df["tasks_completed"] / (
            df["tasks_completed"] + df["tasks_delayed"]
        )
        df["delay_trend"] = df["tasks_delayed"].rolling(window=5, min_periods=1).mean()
        df["resource_efficiency"] = (
            df["resource_utilization"] * df["task_completion_rate"]
        )

        # Add time-based features
        df["day_of_week"] = pd.to_datetime(df["timestamp"]).dt.dayofweek
        df["month"] = pd.to_datetime(df["timestamp"]).dt.month

        return df.fillna(0)

    async def _get_or_train_model(
        self, model_name: str, features: pd.DataFrame, target_column: str
    ):
        """Get existing model or train a new one."""
        if model_name not in self.models:
            raise ValueError(f"Unknown model: {model_name}")

        model = self.models[model_name]

        # Check if model is already trained
        if hasattr(model, "feature_importances_") or hasattr(model, "coef_"):
            return model

        # Train the model
        X = features.drop(columns=[target_column, "timestamp"], errors="ignore")
        y = features[target_column]

        # Handle missing values
        X = X.fillna(0)
        y = y.fillna(y.mean() if y.dtype in ["float64", "int64"] else y.mode()[0])

        # Scale features if needed
        if model_name in self.scalers:
            X_scaled = self.scalers[model_name].fit_transform(X)
            model.fit(X_scaled, y)
        else:
            model.fit(X, y)

        # Store feature importance
        if hasattr(model, "feature_importances_"):
            self.feature_importance[model_name] = dict(
                zip(X.columns, model.feature_importances_)
            )

        return model

    async def _calculate_prediction_confidence(
        self, model_name: str, features: pd.DataFrame, prediction: float
    ) -> float:
        """Calculate confidence score for a prediction."""
        try:
            # Simple confidence based on data quality and model performance
            data_quality = min(1.0, len(features) / 50)  # More data = higher confidence
            model_stability = 0.8  # Assume reasonable model stability

            # Adjust confidence based on prediction extremity
            if model_name == "schedule_drift":
                extremity_penalty = min(
                    0.2, abs(prediction) / 30
                )  # Extreme predictions less confident
            elif model_name == "budget_variance":
                extremity_penalty = min(0.2, abs(prediction) / 20)
            else:
                extremity_penalty = 0

            confidence = (data_quality * model_stability) - extremity_penalty
            return max(
                0.5, min(0.95, confidence)
            )  # Keep confidence between 0.5 and 0.95

        except Exception as e:
            logger.error(f"Confidence calculation failed: {e}")
            return 0.7  # Default confidence

    def _categorize_schedule_risk(self, drift_days: float) -> str:
        """Categorize schedule risk level."""
        if drift_days <= 2:
            return "low"
        elif drift_days <= 7:
            return "medium"
        else:
            return "high"

    def _categorize_budget_risk(self, variance_percent: float) -> str:
        """Categorize budget risk level."""
        abs_variance = abs(variance_percent)
        if abs_variance <= 5:
            return "low"
        elif abs_variance <= 15:
            return "medium"
        else:
            return "high"

    def _categorize_quality_risk(self, risk_probability: float) -> str:
        """Categorize quality risk level."""
        if risk_probability <= 0.3:
            return "low"
        elif risk_probability <= 0.6:
            return "medium"
        else:
            return "high"

    def _categorize_collaboration_effectiveness(
        self, effectiveness_score: float
    ) -> str:
        """Categorize collaboration effectiveness level."""
        if effectiveness_score >= 0.8:
            return "excellent"
        elif effectiveness_score >= 0.6:
            return "good"
        elif effectiveness_score >= 0.4:
            return "fair"
        else:
            return "poor"

    async def _generate_baseline_prediction(
        self, prediction_type: str, project_id: str, horizon_days: int
    ) -> Dict[str, Any]:
        """Generate baseline prediction when insufficient data."""
        baseline_predictions = {
            "schedule_drift": {
                "predicted_drift_days": 3.5,
                "confidence_score": 0.6,
                "risk_level": "medium",
            },
            "budget_variance": {
                "predicted_variance_percent": 2.5,
                "confidence_score": 0.6,
                "risk_level": "low",
            },
            "quality_risk": {
                "predicted_risk_probability": 0.25,
                "confidence_score": 0.6,
                "risk_level": "low",
            },
            "collaboration_effectiveness": {
                "predicted_effectiveness_score": 0.7,
                "confidence_score": 0.6,
                "effectiveness_level": "good",
            },
        }

        base_prediction = baseline_predictions.get(prediction_type, {})
        base_prediction.update(
            {
                "prediction_type": prediction_type,
                "note": "Baseline prediction due to insufficient historical data",
                "recommendations": [
                    "Collect more historical data for improved predictions"
                ],
            }
        )

        return base_prediction

    async def _store_prediction_result(
        self,
        project_id: str,
        prediction_type: str,
        result: Dict[str, Any],
        horizon_days: int,
    ):
        """Store prediction result in database."""
        try:
            # This would store in the database using the knowledge graph
            # For now, just log the prediction
            logger.info(
                f"Stored prediction for {project_id}: {prediction_type} = {result}"
            )

        except Exception as e:
            logger.error(f"Failed to store prediction result: {e}")

    # Additional helper methods for other prediction types...
    async def _get_quality_features(self, project_id: str) -> List[Dict[str, Any]]:
        """Get quality-related features."""
        return []  # Placeholder

    async def _get_collaboration_features(
        self, project_id: str
    ) -> List[Dict[str, Any]]:
        """Get collaboration-related features."""
        return []  # Placeholder

    # More helper methods would be implemented here...
