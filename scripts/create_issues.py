#!/usr/bin/env python3
"""
Bulk issue creation script for CMBurnett/con-ai repository
Creates all 13 issues with proper milestones and labels
"""

import subprocess
import json
import time

# Issue definitions
issues = [
    {
        "title": "FastAPI Backend Setup",
        "milestone": "Core Infrastructure",
        "labels": ["backend", "infrastructure", "priority:high"],
        "body": """## Description
Set up FastAPI backend with WebSocket support for real-time agent communication.

## ClaudeCode Implementation Notes
- [ ] Database changes needed: SQLAlchemy models for agents, tasks, and results
- [ ] API endpoints required: /agents, /tasks, /ws websocket endpoint
- [ ] Frontend components needed: None (backend only)
- [ ] Tests to write: WebSocket connection tests, API endpoint tests, database model tests

## Acceptance Criteria
- [ ] FastAPI app with CORS configuration
- [ ] WebSocket endpoint for real-time updates
- [ ] Basic API endpoints for agent management
- [ ] SQLite database integration
- [ ] Environment configuration management
- [ ] Basic error handling and logging

**Tasks:**
- Set up FastAPI project structure
- Implement WebSocket handler
- Create database models with SQLAlchemy
- Add configuration management
- Write basic tests

**Estimate:** 3 days"""
    },
    {
        "title": "React PWA Frontend Foundation",
        "milestone": "Core Infrastructure",
        "labels": ["frontend", "infrastructure", "priority:high"],
        "body": """## Description
Create React PWA with TypeScript, real-time WebSocket integration, and basic UI components.

## ClaudeCode Implementation Notes
- [ ] Database changes needed: None (frontend only)
- [ ] API endpoints required: None (consumes existing WebSocket)
- [ ] Frontend components needed: AgentDashboard, WebSocket hook, routing, state management
- [ ] Tests to write: Component tests, WebSocket hook tests, integration tests

## Acceptance Criteria
- [ ] React app with TypeScript and PWA manifest
- [ ] WebSocket hook for real-time communication
- [ ] Basic routing and navigation
- [ ] Agent dashboard component
- [ ] State management with Zustand
- [ ] Responsive design with Tailwind CSS

**Tasks:**
- Initialize React app with PWA template
- Set up TypeScript and development tools
- Implement WebSocket custom hook
- Create basic component structure
- Add state management

**Estimate:** 4 days"""
    },
    {
        "title": "Agent Framework Architecture",
        "milestone": "Core Infrastructure",
        "labels": ["backend", "agents", "priority:high"],
        "body": """## Description
Build base agent architecture with browser-use integration and common functionality.

## ClaudeCode Implementation Notes
- [ ] Database changes needed: Agent configuration tables, execution logs
- [ ] API endpoints required: /agents/start, /agents/stop, /agents/status
- [ ] Frontend components needed: None (backend framework)
- [ ] Tests to write: BaseAgent tests, browser-use integration tests, agent manager tests

## Acceptance Criteria
- [ ] BaseAgent abstract class
- [ ] Browser-use library integration
- [ ] Agent lifecycle management
- [ ] Progress tracking and status updates
- [ ] Error handling and recovery
- [ ] Configuration management

**Tasks:**
- Design BaseAgent interface
- Integrate browser-use library
- Implement agent manager service
- Add progress tracking
- Create demo "hello world" agent

**Estimate:** 3 days"""
    },
    {
        "title": "Demo Agent Implementation",
        "milestone": "Core Infrastructure",
        "labels": ["backend", "agents"],
        "body": """## Description
Create a simple demo agent that navigates to a website and extracts basic information.

## ClaudeCode Implementation Notes
- [ ] Database changes needed: Demo agent results table
- [ ] API endpoints required: None (uses existing agent framework)
- [ ] Frontend components needed: Demo agent tile in dashboard
- [ ] Tests to write: Demo agent execution tests, data extraction validation

## Acceptance Criteria
- [ ] Demo agent extends BaseAgent
- [ ] Successfully navigates to test website
- [ ] Extracts and returns structured data
- [ ] Sends real-time progress updates
- [ ] Handles basic error scenarios

**Tasks:**
- Implement demo agent class
- Test browser automation workflow
- Add progress reporting
- Test error scenarios

**Estimate:** 2 days"""
    },
    {
        "title": "Procore Agent Development",
        "milestone": "First Construction Integration",
        "labels": ["backend", "agents", "priority:high"],
        "body": """## Description
Develop Procore agent for extracting project data, RFIs, and budget information.

## ClaudeCode Implementation Notes
- [ ] Database changes needed: Procore project data tables, RFI tracking, budget variance storage
- [ ] API endpoints required: /agents/procore/configure, /procore/projects, /procore/rfis
- [ ] Frontend components needed: Procore configuration form, project data visualization
- [ ] Tests to write: Procore login tests, data extraction validation, error handling tests

## Acceptance Criteria
- [ ] Procore login automation
- [ ] Project data extraction
- [ ] RFI status and details retrieval
- [ ] Budget vs actual cost tracking
- [ ] Schedule milestone extraction
- [ ] Data validation and error handling

**Tasks:**
- Research Procore UI navigation patterns
- Implement login automation
- Build data extraction workflows
- Add data validation
- Test with multiple Procore instances

**Estimate:** 5 days"""
    },
    {
        "title": "Data Visualization Dashboard",
        "milestone": "First Construction Integration",
        "labels": ["frontend", "priority:medium"],
        "body": """## Description
Create dashboard components to visualize extracted construction data.

## ClaudeCode Implementation Notes
- [ ] Database changes needed: None (reads existing agent data)
- [ ] API endpoints required: /dashboard/data, /export/csv, /export/pdf
- [ ] Frontend components needed: Chart components, data filters, export buttons, real-time updates
- [ ] Tests to write: Chart rendering tests, data filtering tests, export functionality tests

## Acceptance Criteria
- [ ] Project overview cards
- [ ] RFI status charts
- [ ] Budget variance visualizations
- [ ] Schedule progress indicators
- [ ] Real-time data updates
- [ ] Export functionality

**Tasks:**
- Design dashboard layout
- Implement chart components with Recharts
- Add data filtering and sorting
- Create export functionality
- Test with Procore data

**Estimate:** 4 days"""
    },
    {
        "title": "Autodesk Construction Cloud Agent",
        "milestone": "Multi-Agent Orchestration",
        "labels": ["backend", "agents", "priority:high"],
        "body": """## Description
Develop agent for Autodesk Construction Cloud data extraction and BIM integration.

## ClaudeCode Implementation Notes
- [ ] Database changes needed: ACC project tables, BIM model metadata, issue tracking
- [ ] API endpoints required: /agents/autodesk/configure, /autodesk/projects, /autodesk/models
- [ ] Frontend components needed: Autodesk configuration form, BIM data visualization
- [ ] Tests to write: ACC login tests, BIM data extraction, cross-platform correlation tests

## Acceptance Criteria
- [ ] ACC login and navigation
- [ ] Project and model data extraction
- [ ] Issue and RFI synchronization
- [ ] Document management integration
- [ ] Progress tracking with BIM data

**Tasks:**
- Map ACC UI navigation flows
- Implement data extraction workflows
- Add BIM-specific data handling
- Test cross-platform data correlation

**Estimate:** 4 days"""
    },
    {
        "title": "Oracle Primavera Agent",
        "milestone": "Multi-Agent Orchestration",
        "labels": ["backend", "agents", "priority:medium"],
        "body": """## Description
Build agent for Oracle Primavera P6 schedule and resource data extraction.

## ClaudeCode Implementation Notes
- [ ] Database changes needed: P6 schedule tables, resource allocation data, critical path analysis
- [ ] API endpoints required: /agents/primavera/configure, /primavera/schedules, /primavera/resources
- [ ] Frontend components needed: Primavera configuration form, schedule visualization, resource charts
- [ ] Tests to write: P6 login tests, schedule extraction validation, resource tracking tests

## Acceptance Criteria
- [ ] P6 web interface automation
- [ ] Schedule data extraction
- [ ] Resource allocation tracking
- [ ] Critical path analysis
- [ ] Progress measurement
- [ ] Integration with other agents

**Tasks:**
- Research P6 web interface patterns
- Implement schedule extraction
- Add resource tracking
- Build cross-platform correlation

**Estimate:** 5 days"""
    },
    {
        "title": "Multi-Agent Coordination System",
        "milestone": "Multi-Agent Orchestration",
        "labels": ["backend", "priority:high"],
        "body": """## Description
Build system for coordinating multiple agents and correlating data across platforms.

## ClaudeCode Implementation Notes
- [ ] Database changes needed: Agent coordination tables, scheduling queue, data correlation mappings
- [ ] API endpoints required: /orchestration/schedule, /orchestration/status, /correlation/sync
- [ ] Frontend components needed: Agent coordination dashboard, scheduling interface, conflict resolution UI
- [ ] Tests to write: Multi-agent coordination tests, data correlation validation, conflict resolution tests

## Acceptance Criteria
- [ ] Agent scheduling and queuing
- [ ] Data correlation between platforms
- [ ] Conflict detection and resolution
- [ ] Batch processing capabilities
- [ ] Performance monitoring

**Tasks:**
- Design agent coordination workflows
- Implement data correlation logic
- Add scheduling system
- Build monitoring dashboard

**Estimate:** 4 days"""
    },
    {
        "title": "PyInstaller Distribution Package",
        "milestone": "Production-Ready Package",
        "labels": ["backend", "priority:high"],
        "body": """## Description
Create distributable package using PyInstaller for easy user installation.

## ClaudeCode Implementation Notes
- [ ] Database changes needed: None (packaging only)
- [ ] API endpoints required: None (packaging only)
- [ ] Frontend components needed: None (packaging only)
- [ ] Tests to write: Installation tests, cross-platform compatibility tests, auto-updater tests

## Acceptance Criteria
- [ ] Single executable creation
- [ ] Frontend assets bundled correctly
- [ ] Python dependencies included
- [ ] Cross-platform compatibility (Windows/macOS)
- [ ] Installation wizard/script
- [ ] Auto-updater integration

**Tasks:**
- Configure PyInstaller specifications
- Bundle React build assets
- Test on multiple platforms
- Create installation scripts
- Add auto-update mechanism

**Estimate:** 3 days"""
    },
    {
        "title": "User Onboarding System",
        "milestone": "Production-Ready Package",
        "labels": ["frontend", "priority:medium"],
        "body": """## Description
Build guided onboarding flow for new users to configure their first agents.

## ClaudeCode Implementation Notes
- [ ] Database changes needed: User onboarding progress tracking, configuration templates
- [ ] API endpoints required: /onboarding/progress, /onboarding/complete, /templates/agent
- [ ] Frontend components needed: Welcome wizard, step-by-step forms, progress indicators, help tooltips
- [ ] Tests to write: Onboarding flow tests, wizard navigation tests, configuration validation tests

## Acceptance Criteria
- [ ] Welcome screen and tutorial
- [ ] Software connection wizard
- [ ] Agent configuration guidance
- [ ] Test agent execution
- [ ] Help documentation integration

**Tasks:**
- Design onboarding flow
- Create step-by-step wizard components
- Add help system
- Test user experience

**Estimate:** 3 days"""
    },
    {
        "title": "Documentation and Help System",
        "milestone": "Production-Ready Package",
        "labels": ["priority:medium"],
        "body": """## Description
Create comprehensive documentation for users and developers.

## ClaudeCode Implementation Notes
- [ ] Database changes needed: None (documentation only)
- [ ] API endpoints required: None (documentation only)
- [ ] Frontend components needed: In-app help system, documentation viewer
- [ ] Tests to write: Documentation completeness tests, help system navigation tests

## Acceptance Criteria
- [ ] User installation guide
- [ ] Agent configuration documentation
- [ ] Troubleshooting guide
- [ ] Developer API documentation
- [ ] Video tutorials (optional)

**Tasks:**
- Write user documentation
- Create developer guides
- Add in-app help system
- Record demonstration videos

**Estimate:** 2 days"""
    },
    {
        "title": "Beta Testing Framework",
        "milestone": "Production-Ready Package",
        "labels": ["backend", "priority:medium"],
        "body": """## Description
Set up beta testing program with feedback collection and analytics.

## ClaudeCode Implementation Notes
- [ ] Database changes needed: Beta user tracking, usage analytics, feedback storage
- [ ] API endpoints required: /analytics/track, /feedback/submit, /beta/users
- [ ] Frontend components needed: Feedback forms, analytics dashboard, beta user portal
- [ ] Tests to write: Analytics tracking tests, feedback submission tests, user management tests

## Acceptance Criteria
- [ ] Beta user management system
- [ ] Usage analytics collection
- [ ] Feedback submission system
- [ ] Error reporting and logging
- [ ] Performance monitoring

**Tasks:**
- Implement analytics tracking
- Create feedback forms
- Set up error reporting
- Build beta user portal

**Estimate:** 2 days"""
    }
]

def create_issue(issue_data):
    """Create a single issue using GitHub CLI"""
    labels_str = ",".join(issue_data["labels"])
    
    cmd = [
        "gh", "issue", "create",
        "--repo", "CMBurnett/con-ai",
        "--title", issue_data["title"],
        "--body", issue_data["body"],
        "--milestone", issue_data["milestone"],
        "--label", labels_str
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Created: {issue_data['title']}")
        print(f"   URL: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create: {issue_data['title']}")
        print(f"   Error: {e.stderr}")
        return False

def main():
    """Create all issues"""
    print(f"Creating {len(issues)} issues for CMBurnett/con-ai...")
    print("=" * 50)
    
    successful = 0
    failed = 0
    
    for i, issue in enumerate(issues, 1):
        print(f"\n[{i}/{len(issues)}] Creating issue...")
        
        if create_issue(issue):
            successful += 1
        else:
            failed += 1
            
        # Small delay to avoid rate limiting
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print(f"Summary: {successful} created, {failed} failed")
    
    if failed > 0:
        print("\nIf any issues failed, you can run this script again")
        print("It will only create issues that don't already exist")

if __name__ == "__main__":
    main()