import { configureStore } from '@reduxjs/toolkit';
import exportsReducer from './exportsSlice';

export const store = configureStore({
  reducer: {
    exports: exportsReducer,
  },
});
