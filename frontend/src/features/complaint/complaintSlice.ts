import {
  createAsyncThunk,
  createSlice,
  PayloadAction,
} from "@reduxjs/toolkit";
import axios from "axios";

import type { Complaint } from "../../types/complaint";
import { saveComplaint } from "../../services/api";

const initialComplaint: Complaint = {
  complaint_source: "",
  customer_name: "",
  product_name: "",
  product_strength: "",
  batch_number: "",
  manufacturing_date: "",
  expiry_date: "",
  quantity_affected: null,
  quantity_unit: "",
  complaint_type: "",
  complaint_date: "",
  description: "",
  initial_severity: "",
  priority: "",
};

interface ComplaintState {
  current: Complaint;
  saving: boolean;
  saved: boolean;
  savedComplaintNumber: string | null;
  error: string | null;
}

const initialState: ComplaintState = {
  current: { ...initialComplaint },
  saving: false,
  saved: false,
  savedComplaintNumber: null,
  error: null,
};

/* =========================
   SUBMIT COMPLAINT
   ========================= */

export const submitComplaint = createAsyncThunk<
  {
    id: number;
    complaint_number: string;
    status: string;
  },
  Complaint,
  { rejectValue: string }
>(
  "complaint/submitComplaint",

  async (complaint, { rejectWithValue }) => {
    try {
      console.log("========== SAVE COMPLAINT ==========");
      console.log("Payload:", complaint);

      const response = await saveComplaint(complaint);

      console.log("Save response:", response);

      return response;

    } catch (error: unknown) {
      console.error("========== SAVE ERROR ==========");
      console.error("Full error:", error);

      /* Axios error */
      if (axios.isAxiosError(error)) {
        console.error("Request URL:", error.config?.url);
        console.error("Request method:", error.config?.method);
        console.error("Status:", error.response?.status);
        console.error("Response data:", error.response?.data);
        console.error("Axios message:", error.message);

        /* Server returned an HTTP response */
        if (error.response) {
          const status = error.response.status;
          const data = error.response.data;

          if (
            data &&
            typeof data === "object" &&
            "detail" in data &&
            typeof data.detail === "string"
          ) {
            return rejectWithValue(
              `Server error ${status}: ${data.detail}`
            );
          }

          return rejectWithValue(
            `Server returned HTTP ${status}.`
          );
        }

        /* Request was sent but no response received */
        if (error.request) {
          return rejectWithValue(
            "No response from backend. Make sure FastAPI is running on http://localhost:8000."
          );
        }

        /* Axios configuration/request error */
        return rejectWithValue(
          error.message || "Unable to send save request."
        );
      }

      /* Normal JavaScript Error */
      if (error instanceof Error) {
        console.error("Error message:", error.message);

        return rejectWithValue(error.message);
      }

      return rejectWithValue(
        "Unknown error occurred while saving the complaint."
      );
    }
  }
);

/* =========================
   COMPLAINT SLICE
   ========================= */

const complaintSlice = createSlice({
  name: "complaint",

  initialState,

  reducers: {
    /* Update one form field */
    updateField: (
      state,
      action: PayloadAction<{
        field: keyof Complaint;
        value: string | number | null;
      }>
    ) => {
      state.current[action.payload.field] =
        action.payload.value as never;

      state.saved = false;
      state.savedComplaintNumber = null;
      state.error = null;
    },

    /* Populate form from AI */
   populateComplaint: (
  state,
  action: PayloadAction<Partial<Complaint>>
) => {
  const aiData = action.payload;

  const cleanedData = Object.fromEntries(
    Object.entries(aiData).filter(
      ([, value]) =>
        value !== null &&
        value !== undefined &&
        value !== ""
    )
  ) as Partial<Complaint>;

  state.current = {
    ...state.current,
    ...cleanedData,
  };

  state.saved = false;
  state.savedComplaintNumber = null;
  state.error = null;
},

    /* Reset complete form */
    resetComplaint: (state) => {
      state.current = { ...initialComplaint };

      state.saving = false;
      state.saved = false;
      state.savedComplaintNumber = null;
      state.error = null;
    },

    /* Clear success/error message */
    clearSaveStatus: (state) => {
      state.saved = false;
      state.error = null;
      state.savedComplaintNumber = null;
    },
  },

  /* =========================
     ASYNC STATES
     ========================= */

  extraReducers: (builder) => {
    builder

      /* Saving */
      .addCase(
        submitComplaint.pending,
        (state) => {
          state.saving = true;
          state.saved = false;
          state.savedComplaintNumber = null;
          state.error = null;
        }
      )

      /* Successfully saved */
      .addCase(
        submitComplaint.fulfilled,
        (state, action) => {
          state.saving = false;
          state.saved = true;
          state.error = null;

          state.savedComplaintNumber =
            action.payload.complaint_number;
        }
      )

      /* Failed */
      .addCase(
        submitComplaint.rejected,
        (state, action) => {
          state.saving = false;
          state.saved = false;
          state.savedComplaintNumber = null;

          state.error =
            action.payload ||
            action.error.message ||
            "Unable to save complaint.";
        }
      );
  },
});

/* =========================
   EXPORTS
   ========================= */

export const {
  updateField,
  populateComplaint,
  resetComplaint,
  clearSaveStatus,
} = complaintSlice.actions;

export default complaintSlice.reducer;