import asyncio
import random
from typing import Dict, Any
import logging

from .base_agent import BaseAgent
from models.agent import AgentType, AgentState

logger = logging.getLogger(__name__)


class DemoAgent(BaseAgent):
    """Demo agent for testing and development purposes."""

    def __init__(self, agent_id: str, config: Dict[str, Any] = None):
        super().__init__(agent_id, AgentType.DEMO, config)

        # Demo-specific configuration
        self.simulation_duration = (
            config.get("simulation_duration", 10) if config else 10
        )
        self.step_count = config.get("step_count", 5) if config else 5
        self.should_fail = config.get("should_fail", False) if config else False

        logger.info(
            f"Demo agent {agent_id} initialized with duration={self.simulation_duration}s, steps={self.step_count}"
        )

    async def _execute_task(
        self, task_type: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute demo task with simulated work."""
        logger.info(f"Demo agent {self.agent_id} starting task: {task_type}")

        if task_type == "simulate_data_extraction":
            return await self._simulate_data_extraction(parameters)
        elif task_type == "simulate_platform_integration":
            return await self._simulate_platform_integration(parameters)
        elif task_type == "test_error_handling":
            return await self._test_error_handling(parameters)
        else:
            raise NotImplementedError(
                f"Task type '{task_type}' not supported by demo agent"
            )

    async def _simulate_data_extraction(
        self, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simulate extracting data from a construction platform."""
        await self._update_status(
            AgentState.RUNNING, 0, "Connecting to demo platform..."
        )
        await self._sleep_with_stop_check(1)

        # Simulate authentication
        await self._update_status(
            AgentState.RUNNING, 10, "Authenticating with demo platform..."
        )
        if not await self._authenticate():
            raise Exception("Demo authentication failed")
        await self._sleep_with_stop_check(1)

        # Simulate data extraction steps
        extracted_data = {"projects": [], "rfis": [], "budget_items": []}

        steps = [
            (20, "Extracting project list..."),
            (40, "Processing project data..."),
            (60, "Extracting RFIs..."),
            (80, "Processing budget information..."),
            (100, "Data extraction completed"),
        ]

        for progress, message in steps:
            await self._check_should_stop()
            await self._update_status(AgentState.RUNNING, progress, message)

            # Generate demo data based on current step
            if "project" in message.lower():
                extracted_data["projects"] = await self._generate_demo_projects()
            elif "rfi" in message.lower():
                extracted_data["rfis"] = await self._generate_demo_rfis()
            elif "budget" in message.lower():
                extracted_data["budget_items"] = (
                    await self._generate_demo_budget_items()
                )

            await self._sleep_with_stop_check(self.simulation_duration / len(steps))

        return {
            "task_completed": True,
            "data_extracted": extracted_data,
            "total_projects": len(extracted_data["projects"]),
            "total_rfis": len(extracted_data["rfis"]),
            "total_budget_items": len(extracted_data["budget_items"]),
            "extraction_time_seconds": self.simulation_duration,
        }

    async def _simulate_platform_integration(
        self, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simulate integrating with multiple construction platforms."""
        platforms = parameters.get("platforms", ["procore", "autodesk", "primavera"])

        await self._update_status(
            AgentState.RUNNING, 0, "Starting multi-platform integration..."
        )

        results = {}
        step_size = 100 // len(platforms)

        for i, platform in enumerate(platforms):
            await self._check_should_stop()
            progress = i * step_size

            await self._update_status(
                AgentState.RUNNING, progress, f"Connecting to {platform}..."
            )
            await self._sleep_with_stop_check(1)

            await self._update_status(
                AgentState.RUNNING,
                progress + step_size // 2,
                f"Extracting data from {platform}...",
            )
            await self._sleep_with_stop_check(2)

            # Simulate platform-specific data
            results[platform] = {
                "status": "connected",
                "projects_found": random.randint(1, 10),
                "last_sync": "2025-08-14T04:59:33Z",
                "data_quality": random.choice(["excellent", "good", "fair"]),
            }

        await self._update_status(
            AgentState.RUNNING, 100, "Integration completed successfully"
        )

        return {
            "task_completed": True,
            "platforms_integrated": len(platforms),
            "platform_results": results,
            "integration_time_seconds": self.simulation_duration,
        }

    async def _test_error_handling(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Test error handling and recovery scenarios."""
        error_type = parameters.get("error_type", "network_timeout")

        await self._update_status(
            AgentState.RUNNING, 0, "Starting error handling test..."
        )
        await self._sleep_with_stop_check(1)

        await self._update_status(
            AgentState.RUNNING, 30, "Simulating normal operation..."
        )
        await self._sleep_with_stop_check(2)

        # Simulate different error types
        if error_type == "network_timeout":
            await self._update_status(
                AgentState.RUNNING, 50, "Network timeout occurred, retrying..."
            )
            await self._sleep_with_stop_check(2)
            await self._update_status(
                AgentState.RUNNING, 75, "Retry successful, continuing..."
            )
        elif error_type == "authentication_failure":
            await self._update_status(
                AgentState.RUNNING,
                50,
                "Authentication failed, refreshing credentials...",
            )
            await self._sleep_with_stop_check(2)
            await self._update_status(
                AgentState.RUNNING, 75, "Credentials refreshed, continuing..."
            )
        elif error_type == "critical_failure":
            await self._update_status(
                AgentState.RUNNING, 50, "Critical error encountered..."
            )
            await self._sleep_with_stop_check(1)
            raise Exception(f"Simulated critical failure: {error_type}")

        await self._update_status(
            AgentState.RUNNING, 100, "Error handling test completed"
        )

        return {
            "task_completed": True,
            "error_type_tested": error_type,
            "recovery_successful": True,
            "test_duration_seconds": self.simulation_duration,
        }

    async def _authenticate(self) -> bool:
        """Simulate authentication with demo platform."""
        await self._sleep_with_stop_check(0.5)

        # Simulate authentication failure for testing
        if self.should_fail:
            return False

        return True

    async def _extract_data(
        self, data_type: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simulate data extraction from demo platform."""
        await self._update_status(
            AgentState.RUNNING, 50, f"Extracting {data_type} data..."
        )
        await self._sleep_with_stop_check(1)

        if data_type == "projects":
            return {"projects": await self._generate_demo_projects()}
        elif data_type == "rfis":
            return {"rfis": await self._generate_demo_rfis()}
        elif data_type == "budget_items":
            return {"budget_items": await self._generate_demo_budget_items()}
        else:
            return {"message": f"Demo data extraction for {data_type}"}

    async def _generate_demo_projects(self) -> list:
        """Generate demo project data."""
        projects = []
        for i in range(random.randint(2, 5)):
            projects.append(
                {
                    "id": f"demo-project-{i+1}",
                    "name": f"Demo Construction Project {i+1}",
                    "status": random.choice(
                        ["planning", "active", "delayed", "completed"]
                    ),
                    "budget": random.randint(100000, 5000000),
                    "progress": random.randint(0, 100),
                }
            )
        return projects

    async def _generate_demo_rfis(self) -> list:
        """Generate demo RFI data."""
        rfis = []
        for i in range(random.randint(1, 8)):
            rfis.append(
                {
                    "id": f"demo-rfi-{i+1}",
                    "title": f"Demo RFI {i+1}",
                    "status": random.choice(["open", "pending", "closed"]),
                    "priority": random.choice(["low", "medium", "high", "critical"]),
                    "submitted_date": "2025-08-14",
                }
            )
        return rfis

    async def _generate_demo_budget_items(self) -> list:
        """Generate demo budget item data."""
        budget_items = []
        categories = ["Labor", "Materials", "Equipment", "Subcontractors", "Other"]

        for i, category in enumerate(categories):
            budget_items.append(
                {
                    "id": f"demo-budget-{i+1}",
                    "category": category,
                    "budgeted_amount": random.randint(10000, 500000),
                    "actual_amount": random.randint(8000, 520000),
                    "variance_percentage": random.randint(-25, 15),
                }
            )
        return budget_items
