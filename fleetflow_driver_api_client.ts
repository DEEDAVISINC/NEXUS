/**
 * Driver OTR Flow API Client
 *
 * Use this client to connect external systems (TMS, dispatch, ERP, mobile apps)
 * to FleetFlow's Driver OTR Flow platform.
 *
 * @example
 * const client = new DriverOTRFlowClient('https://your-fleetflow.com');
 * const loads = await client.getInstantLoads('driver-1');
 * await client.updateDriverLocation('driver-1', { lat: 32.7767, lng: -96.797 });
 * await client.acceptLoad('driver-1', 'GWF-LOAD-001');
 */

// --- Types ---

export interface DriverLocation {
  lat: number;
  lng: number;
}

export interface Load {
  id: string;
  origin: { lat: number; lng: number; address: string };
  destination: { lat: number; lng: number; address: string };
  pickupTime: string;
  deliveryTime: string;
  weight: number;
  equipmentType: string;
  rate: number;
  status: string;
  urgency?: string;
}

export interface DriverEarnings {
  totalEarnings: number;
  tripHistory?: Array<{
    loadId: string;
    amount: number;
    date: string;
  }>;
}

export interface DriverDashboard {
  instantLoads: Load[];
  earnings: DriverEarnings;
  recentActivity: unknown[];
  loadCount: number;
  status: 'online' | 'offline' | 'on-load';
}

export interface LoadRequest {
  origin: string;
  destination: string;
  equipmentType: string;
  weight: number;
  urgency: 'low' | 'medium' | 'high';
  pickupDate: string;
  deliveryDate: string;
  shipperId: string;
}

export interface ApiResponse<T> {
  success: boolean;
  error?: string;
  message?: string;
  [key: string]: T | boolean | string | undefined;
}

// --- Client ---

export class DriverOTRFlowClient {
  private baseUrl: string;
  private apiKey?: string;

  constructor(baseUrl: string, apiKey?: string) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.apiKey = apiKey;
  }

  private async request<T>(
    path: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${path}`;
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.apiKey) {
      (headers as Record<string, string>)['Authorization'] = `Bearer ${this.apiKey}`;
      (headers as Record<string, string>)['X-API-Key'] = this.apiKey;
    }

    const response = await fetch(url, { ...options, headers });
    const data = (await response.json().catch(() => ({}))) as ApiResponse<T>;

    if (!response.ok) {
      throw new Error(data.error || data.message || `HTTP ${response.status}`);
    }

    return data;
  }

  // --- Driver API ---

  async getDriverDashboard(driverId: string): Promise<ApiResponse<{ dashboard: DriverDashboard }>> {
    return this.request(
      `/api/go-with-the-flow/driver?action=dashboard&driverId=${encodeURIComponent(driverId)}`
    );
  }

  async getInstantLoads(driverId: string): Promise<ApiResponse<{ loads: Load[]; count: number }>> {
    return this.request(
      `/api/go-with-the-flow/driver?action=instant-loads&driverId=${encodeURIComponent(driverId)}`
    );
  }

  async getDriverEarnings(driverId: string): Promise<ApiResponse<{ earnings: DriverEarnings }>> {
    return this.request(
      `/api/go-with-the-flow/driver?action=earnings&driverId=${encodeURIComponent(driverId)}`
    );
  }

  async toggleAvailability(
    driverId: string,
    status: 'online' | 'offline'
  ): Promise<ApiResponse<{ newStatus: string }>> {
    return this.request('/api/go-with-the-flow/driver', {
      method: 'POST',
      body: JSON.stringify({ action: 'toggle-availability', driverId, status }),
    });
  }

  async updateDriverLocation(
    driverId: string,
    location: DriverLocation
  ): Promise<ApiResponse<unknown>> {
    return this.request('/api/go-with-the-flow/driver', {
      method: 'POST',
      body: JSON.stringify({ action: 'update-location', driverId, location }),
    });
  }

  async acceptLoad(driverId: string, loadId: string): Promise<ApiResponse<{ message: string }>> {
    return this.request('/api/go-with-the-flow/driver', {
      method: 'POST',
      body: JSON.stringify({ action: 'accept-load', driverId, loadId }),
    });
  }

  // TODO: Add remaining methods when full code is provided
  // - declineLoad
  // - completeLoad
  // - updateLoadStatus
  // - getLoadDetails
}
