import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import type { AIAnalysisResult } from "../../types/complaint";

interface AIState {
  analyzing: boolean;
  result: AIAnalysisResult | null;
  error: string | null;
}

const initialState: AIState = {
  analyzing: false,
  result: null,
  error: null,
};

const aiSlice = createSlice({
  name: "ai",
  initialState,
  reducers: {
    analysisStarted: (state) => {
      state.analyzing = true;
      state.error = null;
    },

    analysisSucceeded: (
      state,
      action: PayloadAction<AIAnalysisResult>
    ) => {
      state.analyzing = false;
      state.result = action.payload;
      state.error = null;
    },

    analysisFailed: (
      state,
      action: PayloadAction<string>
    ) => {
      state.analyzing = false;
      state.error = action.payload;
    },

    clearAnalysis: (state) => {
      state.analyzing = false;
      state.result = null;
      state.error = null;
    },
  },
});

export const {
  analysisStarted,
  analysisSucceeded,
  analysisFailed,
  clearAnalysis,
} = aiSlice.actions;

export default aiSlice.reducer;