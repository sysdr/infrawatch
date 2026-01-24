import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { resourcesAPI, topologyAPI, costsAPI } from '../services/api';

export const fetchTopology = createAsyncThunk(
  'resources/fetchTopology',
  async (filters) => {
    const response = await topologyAPI.getTopology(filters);
    return response.data;
  }
);

export const fetchResources = createAsyncThunk(
  'resources/fetchResources',
  async (params) => {
    const response = await resourcesAPI.listResources(params);
    return response.data;
  }
);

export const fetchCostSummary = createAsyncThunk(
  'resources/fetchCostSummary',
  async (days) => {
    const response = await costsAPI.getSummary(days);
    return response.data;
  }
);

const resourceSlice = createSlice({
  name: 'resources',
  initialState: {
    topology: { nodes: [], edges: [], stats: {} },
    resources: { items: [], total: 0 },
    costs: null,
    loading: false,
    error: null,
  },
  reducers: {
    updateMetric: (state, action) => {
      // Update real-time metric
      const { resource_id, data } = action.payload;
      const node = state.topology.nodes.find(n => n.id === resource_id);
      if (node) {
        node.metrics = data;
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchTopology.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchTopology.fulfilled, (state, action) => {
        state.loading = false;
        state.topology = action.payload;
      })
      .addCase(fetchTopology.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })
      .addCase(fetchResources.fulfilled, (state, action) => {
        state.resources = action.payload;
      })
      .addCase(fetchCostSummary.fulfilled, (state, action) => {
        state.costs = action.payload;
      });
  },
});

export const { updateMetric } = resourceSlice.actions;
export default resourceSlice.reducer;
