# ATLAS PM HTML → NEXUS API Integration

## Overview

This guide shows how to optionally integrate your existing ATLAS PM HTML file with the NEXUS backend API, enabling cloud sync, AI features, and cross-system data sharing.

## Integration Options

### Option 1: API Bridge (Recommended)
Add the API bridge script to enable optional API connectivity while maintaining localStorage fallback.

### Option 2: Full Migration
Use the migration utility to move all data to Airtable and update HTML to use API-only mode.

## Option 1: API Bridge Integration

### Step 1: Add the Bridge Script

Add this script tag to your ATLAS PM HTML file, right after the Babel script:

```html
<!DOCTYPE html>
<html>
<head>
    <!-- ... existing scripts ... -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.23.5/babel.min.js"></script>

    <!-- 🔗 ADD THIS: NEXUS API Bridge -->
    <script src="atlas_api_bridge.js"></script>

    <style>
        <!-- ... existing styles ... -->
    </style>
</head>
```

### Step 2: Configure API URL (Optional)

Set the NEXUS API URL in your HTML (defaults to localhost):

```html
<script>
    // Set this before loading ATLAS PM
    window.NEXUS_API_BASE_URL = 'https://your-nexus-api.com';
</script>
```

### Step 3: Add Sync Buttons to UI

Add these buttons to your ATLAS PM interface for manual sync:

```javascript
// In your ATLAS PM React component, add these functions:

const syncFromNexus = async () => {
    const success = await window.syncAtlasWithNexus();
    if (success) {
        // Refresh your local data
        loadProjectsFromStorage();
        alert('✅ Data synced from NEXUS!');
    } else {
        alert('❌ Sync failed - check console');
    }
};

const uploadToNexus = async () => {
    const localData = {
        activeProjects: activeProjects,
        activeRFPs: activeRFPs,
        changeOrders: changeOrders
    };

    const success = await window.uploadAtlasToNexus(localData);
    if (success) {
        alert('✅ Data uploaded to NEXUS!');
    } else {
        alert('❌ Upload failed - check console');
    }
};

// Add buttons to your UI:
<button onClick={syncFromNexus} className="sync-button">
    🔄 Sync from NEXUS
</button>

<button onClick={uploadToNexus} className="upload-button">
    ☁️ Upload to NEXUS
</button>
```

### Step 4: Automatic API Detection

The bridge automatically detects if NEXUS API is available:

```javascript
// Check API status
const apiAvailable = window.AtlasNexusBridge.apiAvailable;

if (apiAvailable) {
    console.log('Running in integrated mode');
    // Show sync buttons, enable cloud features
} else {
    console.log('Running in standalone mode');
    // Hide sync buttons, use localStorage only
}
```

## Option 2: Full Migration

### Step 1: Migrate Data

Use the migration utility to move all data to Airtable:

```bash
# Extract from HTML
python atlas_migration.py --export-html-data ATLAS_PM_v2.1_COMPLETE.html

# Migrate to Airtable
python atlas_migration.py --migrate-to-airtable atlas_extracted_data.json \
  --airtable-key YOUR_KEY --airtable-base YOUR_BASE
```

### Step 2: Replace localStorage Calls

Update your ATLAS PM HTML to use API calls instead of localStorage:

```javascript
// BEFORE (localStorage)
const saveProjects = (projects) => {
    localStorage.setItem('atlas_pm_projects', JSON.stringify(projects));
};

const loadProjects = () => {
    const data = localStorage.getItem('atlas_pm_projects');
    return data ? JSON.parse(data) : [];
};

// AFTER (API calls)
const saveProjects = async (projects) => {
    for (const project of projects) {
        if (project.id) {
            await window.AtlasNexusBridge.updateProject(project.id, project);
        } else {
            await window.AtlasNexusBridge.createProject(project);
        }
    }
};

const loadProjects = async () => {
    const result = await window.AtlasNexusBridge.getProjects();
    return result ? result.projects : [];
};
```

## Enhanced Features with API Integration

### AI-Powered Analysis
```javascript
// RFP Analysis with Claude AI
const analyzeRFP = async (rfpContent) => {
    const analysis = await window.AtlasNexusBridge.analyzeRFP(rfpContent, projectId);
    if (analysis) {
        setRfpAnalysis(analysis);
        // Automatically save to Airtable
    }
};
```

### Automated WBS Generation
```javascript
// Generate Work Breakdown Structure
const generateProjectWBS = async (projectId) => {
    const wbs = await window.AtlasNexusBridge.generateWBS(projectId);
    if (wbs) {
        setProjectWBS(wbs);
        // WBS automatically saved to Airtable
    }
};
```

### Change Order Impact Analysis
```javascript
// Analyze change request impact
const analyzeChangeImpact = async (changeDescription, projectId) => {
    const analysis = await window.AtlasNexusBridge.analyzeChangeRequest(changeDescription, projectId);
    if (analysis) {
        // Automatically create change order in Airtable
        const coData = {
            project_id: projectId,
            title: 'Change Request',
            description: changeDescription,
            type: analysis.change_type,
            impact_scope: analysis.impact_assessment.scope_impact,
            impact_schedule: analysis.impact_assessment.schedule_impact,
            impact_budget: analysis.impact_assessment.budget_impact
        };
        await window.AtlasNexusBridge.createChangeOrder(coData);
    }
};
```

## Data Synchronization Strategy

### Bidirectional Sync
- **Upload**: Local changes → NEXUS API → Airtable
- **Download**: Airtable → NEXUS API → Local storage

### Conflict Resolution
- **Last-write-wins**: API timestamps determine precedence
- **Manual merge**: User chooses which version to keep
- **Field-level sync**: Only changed fields are updated

### Offline Mode
- **Detection**: API bridge tests connectivity
- **Fallback**: Automatically switches to localStorage
- **Sync on reconnect**: Queues changes for upload when online

## Testing Integration

### 1. Standalone Mode
```bash
# Open ATLAS PM HTML directly
# Should work without API (localStorage only)
# Check console: "NEXUS API not available - Running standalone"
```

### 2. Integrated Mode
```bash
# Start NEXUS backend
python api_server.py

# Open ATLAS PM HTML
# Should detect API and show sync options
# Check console: "NEXUS API connected - Running integrated"
```

### 3. Data Sync Test
1. Create project in standalone mode
2. Click "Upload to NEXUS"
3. Verify data appears in React dashboard
4. Make changes in dashboard
5. Click "Sync from NEXUS" in HTML
6. Verify changes appear in HTML

## Deployment Options

### Development
- API: `http://127.0.0.1:8000`
- HTML: Served from filesystem or local server

### Production
- API: `https://your-domain.com`
- HTML: Same file, just update `NEXUS_API_BASE_URL`

### Hybrid Deployment
- Keep HTML standalone for some users
- Enable API integration for power users
- Gradual migration path

## Troubleshooting

### API Connection Issues
```javascript
// Check API status
console.log('API Available:', window.AtlasNexusBridge.apiAvailable);

// Test connection manually
fetch('http://127.0.0.1:8000/health')
    .then(r => r.json())
    .then(d => console.log('API Status:', d));
```

### Data Sync Issues
- Check browser console for error messages
- Verify API endpoints are responding
- Check CORS settings if deploying to different domains
- Validate data formats match API expectations

### Performance Considerations
- Large datasets may cause sync delays
- Implement pagination for large project lists
- Use web workers for background sync operations
- Cache frequently accessed data locally

## Future Enhancements

### Real-time Sync
- WebSocket connections for live updates
- Real-time collaboration features
- Instant notifications for changes

### Advanced Features
- Automated backup and restore
- Data validation and integrity checks
- Audit trails for all changes
- Role-based access control

---

## Quick Integration Script

For rapid integration, add this script to your ATLAS PM HTML:

```html
<script src="atlas_api_bridge.js"></script>
<script>
    // Add to your existing script section
    const enableNexusIntegration = () => {
        // Add sync buttons to UI
        // Replace localStorage calls with API calls
        // Enable AI features
    };

    // Auto-enable if API available
    setTimeout(() => {
        if (window.AtlasNexusBridge?.apiAvailable) {
            enableNexusIntegration();
        }
    }, 1000);
</script>
```

This provides a seamless upgrade path from standalone HTML to full NEXUS integration! 🚀
