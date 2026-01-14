/**
 * ATLAS PM ↔ NEXUS API Bridge
 *
 * Optional integration layer that allows ATLAS PM HTML to use NEXUS API
 * instead of localStorage. Include this script in ATLAS PM HTML for API connectivity.
 *
 * Usage:
 * 1. Include this script in ATLAS PM HTML
 * 2. Set window.NEXUS_API_BASE_URL
 * 3. ATLAS PM will automatically detect and use API when available
 */

(function(window) {
    'use strict';

    // Configuration
    const NEXUS_API_BASE_URL = window.NEXUS_API_BASE_URL || 'http://127.0.0.1:8000';

    // API Bridge Class
    class AtlasNexusBridge {
        constructor() {
            this.apiAvailable = false;
            this.testConnection();
        }

        async testConnection() {
            try {
                const response = await fetch(`${NEXUS_API_BASE_URL}/health`);
                const data = await response.json();
                this.apiAvailable = data.status === 'healthy';
                if (this.apiAvailable) {
                    console.log('🔗 NEXUS API connected - ATLAS PM running in integrated mode');
                }
            } catch (error) {
                console.log('📦 NEXUS API not available - ATLAS PM running in standalone mode');
                this.apiAvailable = false;
            }
        }

        // Project CRUD operations
        async getProjects() {
            if (!this.apiAvailable) return null;
            try {
                const response = await fetch(`${NEXUS_API_BASE_URL}/atlas/projects`);
                return await response.json();
            } catch (error) {
                console.error('API Error - getProjects:', error);
                return null;
            }
        }

        async createProject(projectData) {
            if (!this.apiAvailable) return null;
            try {
                const response = await fetch(`${NEXUS_API_BASE_URL}/atlas/projects`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(projectData)
                });
                return await response.json();
            } catch (error) {
                console.error('API Error - createProject:', error);
                return null;
            }
        }

        async updateProject(projectId, projectData) {
            if (!this.apiAvailable) return null;
            try {
                const response = await fetch(`${NEXUS_API_BASE_URL}/atlas/projects/${projectId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(projectData)
                });
                return await response.json();
            } catch (error) {
                console.error('API Error - updateProject:', error);
                return null;
            }
        }

        // RFP operations
        async getRFPs(projectId = null) {
            if (!this.apiAvailable) return null;
            try {
                const url = projectId
                    ? `${NEXUS_API_BASE_URL}/atlas/rfps?project_id=${projectId}`
                    : `${NEXUS_API_BASE_URL}/atlas/rfps`;
                const response = await fetch(url);
                return await response.json();
            } catch (error) {
                console.error('API Error - getRFPs:', error);
                return null;
            }
        }

        async createRFP(rfpData) {
            if (!this.apiAvailable) return null;
            try {
                const response = await fetch(`${NEXUS_API_BASE_URL}/atlas/rfps`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(rfpData)
                });
                return await response.json();
            } catch (error) {
                console.error('API Error - createRFP:', error);
                return null;
            }
        }

        async analyzeRFP(rfpContent, projectId = null) {
            if (!this.apiAvailable) return null;
            try {
                const response = await fetch(`${NEXUS_API_BASE_URL}/atlas/analyze-rfp`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        rfp_content: rfpContent,
                        project_id: projectId
                    })
                });
                return await response.json();
            } catch (error) {
                console.error('API Error - analyzeRFP:', error);
                return null;
            }
        }

        // Change Order operations
        async getChangeOrders(projectId = null) {
            if (!this.apiAvailable) return null;
            try {
                const url = projectId
                    ? `${NEXUS_API_BASE_URL}/atlas/change-orders?project_id=${projectId}`
                    : `${NEXUS_API_BASE_URL}/atlas/change-orders`;
                const response = await fetch(url);
                return await response.json();
            } catch (error) {
                console.error('API Error - getChangeOrders:', error);
                return null;
            }
        }

        async createChangeOrder(changeOrderData) {
            if (!this.apiAvailable) return null;
            try {
                const response = await fetch(`${NEXUS_API_BASE_URL}/atlas/change-orders`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(changeOrderData)
                });
                return await response.json();
            } catch (error) {
                console.error('API Error - createChangeOrder:', error);
                return null;
            }
        }

        async analyzeChangeRequest(changeDescription, projectId) {
            if (!this.apiAvailable) return null;
            try {
                const response = await fetch(`${NEXUS_API_BASE_URL}/atlas/analyze-change-request`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        change_description: changeDescription,
                        project_id: projectId
                    })
                });
                return await response.json();
            } catch (error) {
                console.error('API Error - analyzeChangeRequest:', error);
                return null;
            }
        }

        // WBS operations
        async generateWBS(projectId) {
            if (!this.apiAvailable) return null;
            try {
                const response = await fetch(`${NEXUS_API_BASE_URL}/atlas/generate-wbs`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ project_id: projectId })
                });
                return await response.json();
            } catch (error) {
                console.error('API Error - generateWBS:', error);
                return null;
            }
        }

        // Data synchronization utilities
        async syncFromAPI() {
            if (!this.apiAvailable) return false;

            try {
                // Sync projects
                const projectsData = await this.getProjects();
                if (projectsData && projectsData.projects) {
                    localStorage.setItem('atlas_pm_projects_api', JSON.stringify(projectsData.projects));
                }

                // Sync RFPs
                const rfpsData = await this.getRFPs();
                if (rfpsData && rfpsData.rfps) {
                    localStorage.setItem('atlas_pm_rfps_api', JSON.stringify(rfpsData.rfps));
                }

                // Sync change orders
                const coData = await this.getChangeOrders();
                if (coData && coData.change_orders) {
                    localStorage.setItem('atlas_pm_change_orders_api', JSON.stringify(coData.change_orders));
                }

                console.log('✅ ATLAS PM data synced from NEXUS API');
                return true;
            } catch (error) {
                console.error('❌ Failed to sync data from API:', error);
                return false;
            }
        }

        async syncToAPI(localData) {
            if (!this.apiAvailable) return false;

            try {
                let syncCount = 0;

                // Sync projects
                if (localData.activeProjects) {
                    for (const project of localData.activeProjects) {
                        const apiProject = await this.createProject({
                            name: project.name,
                            client: project.client,
                            type: project.type,
                            industry: project.industry,
                            scope: project.scope,
                            budget: project.budget,
                            timeline: project.timeline,
                            status: project.status,
                            priority: project.priority
                        });
                        if (apiProject) syncCount++;
                    }
                }

                // Sync RFPs
                if (localData.activeRFPs) {
                    for (const rfp of localData.activeRFPs) {
                        const apiRfp = await this.createRFP({
                            name: rfp.name,
                            client: rfp.client,
                            rfp_number: rfp.rfpNumber,
                            value: rfp.value,
                            due_date: rfp.dueDate,
                            industry: rfp.industry,
                            description: rfp.description,
                            contact_name: rfp.contact,
                            probability: rfp.probability
                        });
                        if (apiRfp) syncCount++;
                    }
                }

                console.log(`✅ Synced ${syncCount} items to NEXUS API`);
                return true;
            } catch (error) {
                console.error('❌ Failed to sync data to API:', error);
                return false;
            }
        }
    }

    // Create global instance
    const atlasBridge = new AtlasNexusBridge();

    // Expose to window for ATLAS PM HTML to use
    window.AtlasNexusBridge = atlasBridge;

    // Utility functions for easy integration
    window.syncAtlasWithNexus = async () => {
        return await atlasBridge.syncFromAPI();
    };

    window.uploadAtlasToNexus = async (localData) => {
        return await atlasBridge.syncToAPI(localData);
    };

    console.log('🔗 ATLAS PM ↔ NEXUS API Bridge loaded');

})(window);
