import { configureStore } from '@reduxjs/toolkit';
import resourceSlice from './resourceSlice';

export const store = configureStore({
  reducer: {
    resources: resourceSlice,
  },
});

export default store;
