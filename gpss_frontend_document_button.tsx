/**
 * GPSS Frontend - Document Package Assembly Button
 * 
 * Add this code to GPSSSystem.tsx to enable document assembly from the dashboard
 * Location: /Users/deedavis/NEXUS BACKEND/nexus-frontend/src/components/systems/GPSSSystem.tsx
 */

// ============================================================================
// STEP 1: Add state variable for package assembly (around line 100-120)
// ============================================================================

const [assemblingPackage, setAssemblingPackage] = useState<string | null>(null); // Track which opportunity is being assembled

// ============================================================================
// STEP 2: Add the assemblePackage function (around line 300-400, with other functions)
// ============================================================================

const assemblePackageForOpportunity = async (opportunityId: string, opportunityTitle: string) => {
  try {
    setAssemblingPackage(opportunityId);
    setNotification({ message: `Assembling package for ${opportunityTitle}...`, type: 'success' });
    
    const response = await api.post(`/api/gpss/opportunities/${opportunityId}/assemble-package`);
    
    if (response.data.success) {
      setNotification({ 
        message: `✅ Package assembled! ${response.data.documents.length} documents included. Location: ${response.data.packagePath}`, 
        type: 'success' 
      });
      
      // Refresh opportunities to show updated package status
      fetchOpportunities();
    } else {
      const missingDocs = response.data.missing.join(', ');
      setNotification({ 
        message: `⚠️ Package incomplete. Missing: ${missingDocs}. Package saved at: ${response.data.packagePath}`, 
        type: 'error' 
      });
    }
  } catch (error: any) {
    console.error('Error assembling package:', error);
    setNotification({ 
      message: error.response?.data?.error || 'Failed to assemble package. Make sure documents are uploaded to COMPANY_DOCUMENTS/', 
      type: 'error' 
    });
  } finally {
    setAssemblingPackage(null);
  }
};

// ============================================================================
// STEP 3: Add Package Status Badge Component (around line 500-600)
// ============================================================================

const PackageStatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const statusColors = {
    'Attached': 'bg-green-100 text-green-800 border-green-300',
    'Ready': 'bg-blue-100 text-blue-800 border-blue-300',
    'Incomplete': 'bg-yellow-100 text-yellow-800 border-yellow-300',
    'Not Needed': 'bg-gray-100 text-gray-600 border-gray-300'
  };
  
  const color = statusColors[status as keyof typeof statusColors] || statusColors['Not Needed'];
  
  return (
    <span className={`px-2 py-1 text-xs font-medium rounded-full border ${color}`}>
      {status || 'Not Set'}
    </span>
  );
};

// ============================================================================
// STEP 4: Add the button to Opportunities table
// This goes in the table rendering section (around line 1200-1400)
// Look for where actions/buttons are rendered for each opportunity row
// ============================================================================

/*
In the opportunities table, find the row rendering section and add this button:
*/

<button
  onClick={() => assemblePackageForOpportunity(opp.id, opp.title)}
  disabled={assemblingPackage === opp.id}
  className={`
    px-3 py-1 rounded-lg text-sm font-medium transition-all
    ${assemblingPackage === opp.id 
      ? 'bg-gray-300 text-gray-600 cursor-not-allowed' 
      : 'bg-blue-600 text-white hover:bg-blue-700 hover:shadow-md'
    }
  `}
  title="Assemble bid documents package"
>
  {assemblingPackage === opp.id ? (
    <>
      <span className="animate-spin inline-block mr-1">⏳</span>
      Assembling...
    </>
  ) : (
    <>
      📦 Assemble Package
    </>
  )}
</button>

// ============================================================================
// STEP 5: Add Package Status column to table (optional)
// Add this as a new column in the opportunities table
// ============================================================================

/*
In the table header (around line 1100-1200):
*/
<th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
  Package Status
</th>

/*
In the table body (for each row):
*/
<td className="px-6 py-4 whitespace-nowrap">
  <PackageStatusBadge status={opp.packageStatus} />
  {opp.documentsChecklist && opp.documentsChecklist.length > 0 && (
    <div className="text-xs text-gray-500 mt-1">
      {opp.documentsChecklist.length} docs: {opp.documentsChecklist.slice(0, 3).join(', ')}
      {opp.documentsChecklist.length > 3 && '...'}
    </div>
  )}
</td>

// ============================================================================
// STEP 6: Update the Opportunity interface to include new fields
// Add these fields to the Opportunity interface (around line 13-30)
// ============================================================================

interface Opportunity {
  id: string;
  title: string;
  rfpNumber: string;
  agency: string;
  value: number;
  dueDate: string;
  source: 'Federal' | 'State' | 'Local' | 'Cooperative';
  sourcePortal: string;
  state: string;
  setAsideType: string;
  edwsbEligible: boolean;
  priorityScore: number;
  urgency: 'Critical' | 'High' | 'Medium' | 'Low';
  category: string;
  homeStatePriority: boolean;
  internalStatus: string;
  
  // NEW: Document package fields
  packageStatus?: 'Not Needed' | 'Incomplete' | 'Ready' | 'Attached';
  documentsChecklist?: string[]; // ['W-9', 'EDWOSB', 'WOSB', etc.]
  packageAssembledDate?: string;
  packageAssembledBy?: string;
}

// ============================================================================
// STEP 7: Add Documents Status Dashboard Widget (optional)
// Add this to the Dashboard tab to show document repository status
// ============================================================================

const DocumentsStatusWidget: React.FC = () => {
  const [documentsStatus, setDocumentsStatus] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    const fetchDocumentsStatus = async () => {
      try {
        setLoading(true);
        const response = await api.get('/api/gpss/documents/status');
        setDocumentsStatus(response.data);
      } catch (error) {
        console.error('Error fetching documents status:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchDocumentsStatus();
  }, []);
  
  if (loading) return <div>Loading documents status...</div>;
  if (!documentsStatus) return null;
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">📁 Company Documents Status</h3>
      
      <div className="grid grid-cols-3 gap-4 mb-4">
        <div className="text-center">
          <div className="text-3xl font-bold text-blue-600">{documentsStatus.totalFound}</div>
          <div className="text-sm text-gray-600">Documents Found</div>
        </div>
        <div className="text-center">
          <div className="text-3xl font-bold text-gray-600">{documentsStatus.totalRequired}</div>
          <div className="text-sm text-gray-600">Required</div>
        </div>
        <div className="text-center">
          <div className={`text-3xl font-bold ${documentsStatus.ready ? 'text-green-600' : 'text-red-600'}`}>
            {documentsStatus.ready ? '✅' : '❌'}
          </div>
          <div className="text-sm text-gray-600">
            {documentsStatus.ready ? 'Ready' : 'Incomplete'}
          </div>
        </div>
      </div>
      
      {!documentsStatus.ready && (
        <div className="bg-yellow-50 border border-yellow-200 rounded p-3 text-sm text-yellow-800">
          ⚠️ Upload required documents to COMPANY_DOCUMENTS/ folder to enable package assembly
        </div>
      )}
    </div>
  );
};

/*
Add this widget to the dashboard grid (around line 600-800):
*/
<DocumentsStatusWidget />

// ============================================================================
// COMPLETE EXAMPLE: How it looks in the Opportunities table
// ============================================================================

/*
Example of a complete opportunities table row with the new button:
*/

<tr key={opp.id} className="hover:bg-gray-50">
  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
    {opp.title}
  </td>
  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
    {opp.agency}
  </td>
  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
    ${opp.value.toLocaleString()}
  </td>
  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
    {opp.dueDate}
  </td>
  <td className="px-6 py-4 whitespace-nowrap">
    <PackageStatusBadge status={opp.packageStatus} />
  </td>
  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
    <div className="flex gap-2">
      <button
        onClick={() => assemblePackageForOpportunity(opp.id, opp.title)}
        disabled={assemblingPackage === opp.id}
        className={`
          px-3 py-1 rounded-lg text-sm font-medium transition-all
          ${assemblingPackage === opp.id 
            ? 'bg-gray-300 text-gray-600 cursor-not-allowed' 
            : 'bg-blue-600 text-white hover:bg-blue-700'
          }
        `}
        title="Assemble bid documents package"
      >
        {assemblingPackage === opp.id ? '⏳ Assembling...' : '📦 Assemble'}
      </button>
      
      <button
        onClick={() => viewOpportunityDetails(opp.id)}
        className="px-3 py-1 rounded-lg text-sm bg-gray-200 hover:bg-gray-300"
      >
        View
      </button>
    </div>
  </td>
</tr>

// ============================================================================
// USAGE NOTES
// ============================================================================

/*
1. Make sure the backend API endpoint is added to api_server.py first
2. Ensure COMPANY_DOCUMENTS folder has required documents uploaded
3. Test with one opportunity before rolling out to all
4. The package will be created at: 
   /Users/deedavis/NEXUS BACKEND/photos_and_videos/{OPPORTUNITY_TITLE}/BID_PACKAGE/

5. Future enhancement: Auto-upload attachments to Airtable (requires additional Airtable API work)
*/

export { PackageStatusBadge, DocumentsStatusWidget };
