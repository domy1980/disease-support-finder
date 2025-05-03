import { 
  DiseaseInfo, 
  DiseaseWithOrganizations, 
  SearchRequest, 
  SearchResponse, 
  SupportOrganization,
  DiseaseListResponse,
  SearchStatsResponse,
  DiseaseSearchStats,
  OrganizationCollection,
  OrganizationCollectionResponse,
  ManualEntry,
  ManualEntryRequest,
  ManualOrganizationRequest,
  EnhancedSupportOrganization,
  WebsiteStatusResponse,
  AllWebsiteStatusResponse
} from "../types";

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const fetchDiseases = async (): Promise<DiseaseInfo[]> => {
  try {
    const response = await fetch(`${API_URL}/api/diseases`);
    if (!response.ok) {
      throw new Error(`Error fetching diseases: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching diseases:', error);
    throw error;
  }
};

export const searchDiseases = async (searchRequest: SearchRequest): Promise<SearchResponse> => {
  try {
    const response = await fetch(`${API_URL}/api/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(searchRequest),
    });
    if (!response.ok) {
      throw new Error(`Error searching diseases: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error searching diseases:', error);
    throw error;
  }
};

export const fetchDiseaseWithOrganizations = async (diseaseId: string): Promise<DiseaseWithOrganizations> => {
  try {
    const response = await fetch(`${API_URL}/api/disease/${diseaseId}`);
    if (!response.ok) {
      throw new Error(`Error fetching disease: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching disease:', error);
    throw error;
  }
};

export const fetchOrganizations = async (diseaseId: string): Promise<SupportOrganization[]> => {
  try {
    const response = await fetch(`${API_URL}/api/organizations/${diseaseId}`);
    if (!response.ok) {
      throw new Error(`Error fetching organizations: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching organizations:', error);
    throw error;
  }
};

export const fetchAllDiseases = async (): Promise<DiseaseListResponse> => {
  try {
    const response = await fetch(`${API_URL}/api/v2/diseases/all`);
    if (!response.ok) {
      throw new Error(`Error fetching all diseases: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching all diseases:', error);
    throw error;
  }
};

export const fetchAllStats = async (): Promise<SearchStatsResponse> => {
  try {
    const response = await fetch(`${API_URL}/api/v2/stats`);
    if (!response.ok) {
      throw new Error(`Error fetching stats: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching stats:', error);
    throw error;
  }
};

export const fetchDiseaseStats = async (diseaseId: string): Promise<DiseaseSearchStats> => {
  try {
    const response = await fetch(`${API_URL}/api/v2/stats/${diseaseId}`);
    if (!response.ok) {
      throw new Error(`Error fetching disease stats: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching disease stats:', error);
    throw error;
  }
};

export const fetchAllOrganizationCollections = async (): Promise<OrganizationCollectionResponse> => {
  try {
    const response = await fetch(`${API_URL}/api/v2/organizations/all`);
    if (!response.ok) {
      throw new Error(`Error fetching organization collections: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching organization collections:', error);
    throw error;
  }
};

export const fetchOrganizationCollection = async (diseaseId: string): Promise<OrganizationCollection> => {
  try {
    const response = await fetch(`${API_URL}/api/v2/organizations/collection/${diseaseId}`);
    if (!response.ok) {
      throw new Error(`Error fetching organization collection: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching organization collection:', error);
    throw error;
  }
};

export const runSearchForDisease = async (diseaseId: string): Promise<{ message: string }> => {
  try {
    const response = await fetch(`${API_URL}/api/v2/search/run/${diseaseId}`, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error(`Error running search: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error running search:', error);
    throw error;
  }
};

export const runSearchForAllDiseases = async (): Promise<{ message: string }> => {
  try {
    const response = await fetch(`${API_URL}/api/v2/search/run-all`, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error(`Error running search for all diseases: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error running search for all diseases:', error);
    throw error;
  }
};

export const getSearchStatus = async (): Promise<{ daily_search_running: boolean; stats_count: number; collections_count: number }> => {
  try {
    const response = await fetch(`${API_URL}/api/v2/search/status`);
    if (!response.ok) {
      throw new Error(`Error getting search status: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error getting search status:', error);
    throw error;
  }
};

export const addManualEntry = async (entry: ManualEntryRequest): Promise<ManualEntry> => {
  try {
    const response = await fetch(`${API_URL}/api/v2/manual/entry`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(entry),
    });
    if (!response.ok) {
      throw new Error(`Error adding manual entry: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error adding manual entry:', error);
    throw error;
  }
};

export const updateManualEntry = async (entryId: string, entry: ManualEntryRequest): Promise<ManualEntry> => {
  try {
    const response = await fetch(`${API_URL}/api/v2/manual/entry/${entryId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(entry),
    });
    if (!response.ok) {
      throw new Error(`Error updating manual entry: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error updating manual entry:', error);
    throw error;
  }
};

export const deleteManualEntry = async (entryId: string): Promise<{ message: string }> => {
  try {
    const response = await fetch(`${API_URL}/api/v2/manual/entry/${entryId}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error(`Error deleting manual entry: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error deleting manual entry:', error);
    throw error;
  }
};

export const addManualOrganization = async (org: ManualOrganizationRequest): Promise<EnhancedSupportOrganization> => {
  try {
    const response = await fetch(`${API_URL}/api/v2/manual/organization`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(org),
    });
    if (!response.ok) {
      throw new Error(`Error adding manual organization: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error adding manual organization:', error);
    throw error;
  }
};

export const deleteOrganization = async (diseaseId: string, orgUrl: string): Promise<{ message: string }> => {
  try {
    const response = await fetch(`${API_URL}/api/v2/manual/organization/${diseaseId}/${encodeURIComponent(orgUrl)}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error(`Error deleting organization: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error deleting organization:', error);
    throw error;
  }
};

export const getManualEntries = async (diseaseId: string): Promise<ManualEntry[]> => {
  try {
    const response = await fetch(`${API_URL}/api/v2/manual/entries/${diseaseId}`);
    if (!response.ok) {
      throw new Error(`Error getting manual entries: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error getting manual entries:', error);
    throw error;
  }
};

export const checkWebsitesForDisease = async (diseaseId: string): Promise<{ message: string }> => {
  try {
    const response = await fetch(`${API_URL}/api/v2/websites/check/${diseaseId}`, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error(`Error checking websites: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error checking websites:', error);
    throw error;
  }
};

export const checkAllWebsites = async (): Promise<{ message: string }> => {
  try {
    const response = await fetch(`${API_URL}/api/v2/websites/check-all`, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error(`Error checking all websites: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error checking all websites:', error);
    throw error;
  }
};

export const getWebsiteStatusForDisease = async (diseaseId: string): Promise<WebsiteStatusResponse> => {
  try {
    const response = await fetch(`${API_URL}/api/v2/websites/status/${diseaseId}`);
    if (!response.ok) {
      throw new Error(`Error getting website status: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error getting website status:', error);
    throw error;
  }
};

export const getAllWebsiteStatus = async (): Promise<AllWebsiteStatusResponse> => {
  try {
    const response = await fetch(`${API_URL}/api/v2/websites/status`);
    if (!response.ok) {
      throw new Error(`Error getting all website status: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error getting all website status:', error);
    throw error;
  }
};

export const getWebsiteHistory = async (url: string): Promise<{ url: string; name: string; disease_id: string; disease_name: string; is_available: boolean; last_checked: string | null; history: any[] }> => {
  try {
    const response = await fetch(`${API_URL}/api/v2/websites/history/${encodeURIComponent(url)}`);
    if (!response.ok) {
      throw new Error(`Error getting website history: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error getting website history:', error);
    throw error;
  }
};
