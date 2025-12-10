import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export const createExport = createAsyncThunk(
  'exports/create',
  async (exportData) => {
    const response = await axios.post(`${API_BASE}/exports`, exportData);
    return response.data;
  }
);

export const fetchExports = createAsyncThunk(
  'exports/fetchAll',
  async (userId) => {
    const response = await axios.get(`${API_BASE}/exports?user_id=${userId}&limit=50`);
    return response.data;
  }
);

export const fetchExportStatus = createAsyncThunk(
  'exports/fetchStatus',
  async (jobId) => {
    const response = await axios.get(`${API_BASE}/exports/${jobId}`);
    return response.data;
  }
);

export const cancelExport = createAsyncThunk(
  'exports/cancel',
  async (jobId) => {
    await axios.delete(`${API_BASE}/exports/${jobId}`);
    return jobId;
  }
);

export const createSchedule = createAsyncThunk(
  'exports/createSchedule',
  async (scheduleData) => {
    const response = await axios.post(`${API_BASE}/schedules`, scheduleData);
    return response.data;
  }
);

export const fetchSchedules = createAsyncThunk(
  'exports/fetchSchedules',
  async (userId) => {
    const response = await axios.get(`${API_BASE}/schedules?user_id=${userId}`);
    return response.data;
  }
);

export const fetchPreview = createAsyncThunk(
  'exports/fetchPreview',
  async (format) => {
    const response = await axios.get(`${API_BASE}/preview?format_type=${format}`);
    return response.data;
  }
);

const exportsSlice = createSlice({
  name: 'exports',
  initialState: {
    exports: [],
    schedules: [],
    currentExport: null,
    preview: null,
    loading: false,
    error: null,
  },
  reducers: {
    updateExportProgress: (state, action) => {
      const { job_id, progress, status, stage, download_url, file_size, row_count } = action.payload;
      const exportJob = state.exports.find(e => e.job_id === job_id);
      if (exportJob) {
        exportJob.progress = progress;
        exportJob.status = status || exportJob.status;
        if (download_url) exportJob.download_url = download_url;
        if (file_size) exportJob.file_size = file_size;
        if (row_count) exportJob.row_count = row_count;
      }
    },
    clearPreview: (state) => {
      state.preview = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(createExport.fulfilled, (state, action) => {
        state.exports.unshift({
          job_id: action.payload.job_id,
          status: action.payload.status,
          progress: 0,
          created_at: new Date().toISOString(),
        });
      })
      .addCase(fetchExports.fulfilled, (state, action) => {
        state.exports = action.payload;
      })
      .addCase(fetchExportStatus.fulfilled, (state, action) => {
        const index = state.exports.findIndex(e => e.job_id === action.payload.job_id);
        if (index !== -1) {
          state.exports[index] = action.payload;
        }
      })
      .addCase(cancelExport.fulfilled, (state, action) => {
        const exportJob = state.exports.find(e => e.job_id === action.payload);
        if (exportJob) {
          exportJob.status = 'CANCELLED';
        }
      })
      .addCase(fetchSchedules.fulfilled, (state, action) => {
        state.schedules = action.payload;
      })
      .addCase(fetchPreview.fulfilled, (state, action) => {
        state.preview = action.payload;
      });
  },
});

export const { updateExportProgress, clearPreview } = exportsSlice.actions;
export default exportsSlice.reducer;
