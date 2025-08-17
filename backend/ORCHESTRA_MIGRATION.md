# Orchestra Framework Migration Guide

This document outlines the migration strategy from the custom agent framework to the Orchestra-powered system while maintaining backward compatibility.

## Migration Overview

The Orchestra integration has been designed to provide a smooth transition path:

1. **Backward Compatibility**: Existing agent APIs continue to work
2. **Gradual Migration**: Agents can be migrated one at a time
3. **Enhanced Features**: New Orchestra features are available immediately
4. **Data Preservation**: All existing agent data is preserved

## Migration Phases

### Phase 1: Foundation (✅ Complete)
- [x] Install Orchestra framework dependencies
- [x] Create Orchestra wrapper classes
- [x] Set up temporal intelligence database models
- [x] Implement knowledge graph storage
- [x] Add new API endpoints for Orchestra features

### Phase 2: Parallel Operation (Current)
- [x] Both systems running simultaneously
- [x] Orchestra manager initialized alongside legacy agent service
- [x] New endpoints available under `/api/orchestra/`
- [x] Legacy endpoints continue to work under `/api/agents/`

### Phase 3: Agent Migration (Future)
- [ ] Migrate demo agents to Orchestra framework
- [ ] Update frontend to use Orchestra endpoints
- [ ] Test all agent functionality with Orchestra
- [ ] Validate temporal intelligence features

### Phase 4: Legacy Deprecation (Future)
- [ ] Mark legacy endpoints as deprecated
- [ ] Provide migration warnings in API responses
- [ ] Set sunset timeline for legacy system

### Phase 5: Complete Migration (Future)
- [ ] Remove legacy agent framework
- [ ] Clean up deprecated code
- [ ] Update documentation

## API Migration Mapping

### Legacy to Orchestra Endpoint Mapping

| Legacy Endpoint | Orchestra Endpoint | Migration Status |
|----------------|-------------------|------------------|
| `POST /api/agents` | `POST /api/orchestra/agents/{agent_id}/start` | ✅ Available |
| `GET /api/agents` | `GET /api/orchestra/status` | ✅ Available |
| `GET /api/agents/{agent_id}` | `GET /api/orchestra/agents/{agent_id}/status` | ✅ Available |
| `POST /api/agents/{agent_id}/start` | `POST /api/orchestra/agents/{agent_id}/start` | ✅ Available |
| `POST /api/agents/{agent_id}/stop` | `POST /api/orchestra/agents/{agent_id}/stop` | ✅ Available |
| N/A | `POST /api/orchestra/orchestrate` | ✅ New Feature |
| N/A | `POST /api/orchestra/predictions` | ✅ New Feature |
| N/A | `POST /api/orchestra/temporal/query` | ✅ New Feature |

## New Orchestra Features

### 1. Multi-Agent Orchestration
```json
POST /api/orchestra/orchestrate
{
  "strategy": "collaborative",
  "agents": [
    {
      "agent_id": "procore_agent_1",
      "agent_type": "procore",
      "task_type": "extract_project_data",
      "parameters": {"project_id": "123"}
    },
    {
      "agent_id": "primavera_agent_1", 
      "agent_type": "primavera",
      "task_type": "analyze_schedule",
      "parameters": {"project_id": "123"}
    }
  ]
}
```

### 2. Predictive Analytics
```json
POST /api/orchestra/predictions
{
  "project_id": "123",
  "prediction_types": ["schedule_drift", "budget_variance"],
  "horizon_days": 30
}
```

### 3. Temporal Intelligence
```json
POST /api/orchestra/temporal/query
{
  "entity_id": "project_123",
  "entity_type": "project",
  "context_window_hours": 48
}
```

### 4. Knowledge Graph Insights
```json
GET /api/orchestra/collaboration/insights?project_id=123
```

## Frontend Migration

### Current State
- Frontend uses existing WebSocket connection to `ws://localhost:8080/ws`
- Agent management through `/api/agents` endpoints
- Real-time updates via WebSocket messages

### Migration Path
1. **Immediate**: New Orchestra features can be added to frontend
2. **Gradual**: Existing agent functionality continues to work
3. **Enhanced**: Add temporal intelligence visualizations
4. **Future**: Migrate to Orchestra endpoints when ready

### WebSocket Compatibility
The Orchestra framework integrates with the existing WebSocket system:
- Same connection endpoint: `ws://localhost:8080/ws`
- Enhanced message types for Orchestra events
- Backward compatible with existing message format

## Data Migration

### Temporal Intelligence Database
- New database: `temporal_knowledge.db`
- Existing agent data in `con_ai.db` remains unchanged
- Orchestra system can read existing data for context

### Knowledge Graph Population
- Historical events can be imported from existing database
- New events automatically stored in knowledge graph
- Pattern detection runs on combined historical + new data

## Testing Strategy

### 1. Parallel Testing
```bash
# Test legacy system
curl -X POST http://localhost:8080/api/agents/demo_agent/start

# Test Orchestra system  
curl -X POST http://localhost:8080/api/orchestra/agents/demo_agent/start \
  -H "Content-Type: application/json" \
  -d '{"agent_type": "demo", "task_type": "extract_project_data"}'
```

### 2. Feature Testing
```bash
# Test new orchestration
curl -X POST http://localhost:8080/api/orchestra/orchestrate \
  -H "Content-Type: application/json" \
  -d @orchestration_test.json

# Test predictions
curl -X POST http://localhost:8080/api/orchestra/predictions \
  -H "Content-Type: application/json"
  -d '{"project_id": "test_project", "prediction_types": ["schedule_drift"]}'
```

### 3. WebSocket Testing
```javascript
// Test enhanced WebSocket messages
const ws = new WebSocket('ws://localhost:8080/ws');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Orchestra update:', data);
};
```

## Rollback Strategy

If issues arise during migration:

1. **Immediate Rollback**: Disable Orchestra endpoints
2. **Partial Rollback**: Revert specific agents to legacy system  
3. **Data Safety**: Orchestra database is separate from legacy database
4. **Configuration**: Feature flags control Orchestra vs legacy usage

## Configuration

### Environment Variables
```bash
# Orchestra features
ORCHESTRA_ENABLED=true
TEMPORAL_DB_URL=sqlite:///temporal_knowledge.db
KNOWLEDGE_GRAPH_ENABLED=true
PREDICTIVE_ANALYTICS_ENABLED=true

# Legacy compatibility
LEGACY_AGENTS_ENABLED=true
LEGACY_DEPRECATION_WARNINGS=false
```

### Feature Flags
- `ORCHESTRA_ENABLED`: Enable/disable Orchestra framework
- `TEMPORAL_INTELLIGENCE_ENABLED`: Enable/disable temporal features
- `LEGACY_AGENTS_ENABLED`: Enable/disable legacy agent system

## Monitoring and Observability

### Orchestra Metrics
- Agent orchestration success rate
- Prediction accuracy over time
- Knowledge graph growth rate
- Temporal pattern detection frequency

### Migration Metrics
- Legacy vs Orchestra endpoint usage
- Error rates during migration
- Performance comparison between systems

## Timeline

### Immediate (Week 1)
- ✅ Orchestra framework deployed
- ✅ Parallel operation established
- ✅ Basic testing completed

### Short Term (Weeks 2-4)
- [ ] Frontend integration with Orchestra features
- [ ] Comprehensive testing of all agent types
- [ ] Performance optimization

### Medium Term (Weeks 5-8)
- [ ] Production deployment of Orchestra features
- [ ] User training on new capabilities
- [ ] Legacy deprecation planning

### Long Term (Weeks 9-12)
- [ ] Complete migration to Orchestra
- [ ] Legacy system removal
- [ ] Documentation updates

## Support

### During Migration
- Both systems monitored simultaneously
- Rollback procedures documented and tested
- Support team trained on both systems

### Post-Migration
- Orchestra-only operation
- Enhanced monitoring and alerting
- Temporal intelligence insights for operations

## Conclusion

The Orchestra migration provides:
1. **Zero Downtime**: Seamless transition with parallel operation
2. **Enhanced Capabilities**: Multi-agent orchestration and temporal intelligence
3. **Future Proof**: Modern, scalable architecture
4. **Risk Mitigation**: Comprehensive rollback and testing strategies

The migration can proceed at a comfortable pace, ensuring stability while gaining access to advanced AI orchestration capabilities.