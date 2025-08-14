"""
Demo setup script to register demo agent and create sample data.
Run this script to set up the backend for testing.
"""

import asyncio
import logging
from sqlalchemy.orm import Session

from database import SessionLocal, create_tables
from services.agent_service import agent_service
from agents.demo_agent import DemoAgent
from models.agent import AgentType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def setup_demo():
    """Set up demo environment with sample agents."""
    logger.info("Setting up demo environment...")

    # Ensure database tables exist
    create_tables()

    # Register demo agent class
    agent_service.register_agent_class(AgentType.DEMO, DemoAgent)
    logger.info("Registered DemoAgent class")

    # Create demo agents in database
    db = SessionLocal()
    try:
        # Demo agent 1 - Basic data extraction
        demo_agent_1 = {
            "agent_id": "demo-agent-1",
            "name": "Demo Data Extraction Agent",
            "agent_type": "demo",
            "config": {"simulation_duration": 8, "step_count": 5, "should_fail": False},
            "is_enabled": True,
        }

        # Demo agent 2 - Multi-platform integration
        demo_agent_2 = {
            "agent_id": "demo-agent-2",
            "name": "Demo Multi-Platform Agent",
            "agent_type": "demo",
            "config": {
                "simulation_duration": 12,
                "step_count": 8,
                "should_fail": False,
            },
            "is_enabled": True,
        }

        # Demo agent 3 - Error handling test
        demo_agent_3 = {
            "agent_id": "demo-agent-3",
            "name": "Demo Error Handling Agent",
            "agent_type": "demo",
            "config": {"simulation_duration": 6, "step_count": 4, "should_fail": False},
            "is_enabled": True,
        }

        # Create agents if they don't exist
        for agent_data in [demo_agent_1, demo_agent_2, demo_agent_3]:
            existing = await agent_service.get_agent(agent_data["agent_id"], db)
            if not existing:
                await agent_service.create_agent(agent_data, db)
                logger.info(f"Created demo agent: {agent_data['agent_id']}")
            else:
                logger.info(f"Demo agent already exists: {agent_data['agent_id']}")

    finally:
        db.close()

    logger.info("Demo setup completed successfully!")
    logger.info("\nAvailable demo agents:")
    logger.info("- demo-agent-1: Basic data extraction simulation")
    logger.info("- demo-agent-2: Multi-platform integration simulation")
    logger.info("- demo-agent-3: Error handling test simulation")
    logger.info("\nExample tasks:")
    logger.info("- simulate_data_extraction")
    logger.info("- simulate_platform_integration")
    logger.info("- test_error_handling")


if __name__ == "__main__":
    asyncio.run(setup_demo())
