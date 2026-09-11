import { configureStore } from "@reduxjs/toolkit";
import complaintReducer from "../features/complaint/complaintSlice";
import aiReducer from "../features/ai/aiSlice";

export const store = configureStore({
  reducer: {
    complaint: complaintReducer,
    ai: aiReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;