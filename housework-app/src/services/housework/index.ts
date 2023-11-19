import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

// Define the base API service
const apiService = createApi({
  reducerPath: "api",
  tagTypes: [
    "self",
    "jobs",
    "teams",
    "subscriptions",
    "notifications",
    "invites",
  ],
  baseQuery: fetchBaseQuery({
    baseUrl: process.env.REACT_APP_HOUSEWORK_API_ROOT,
    prepareHeaders: (headers, { getState }) => {
      const houseworkApiHeadersJSON = localStorage.getItem(
        "houseworkApi.headers",
      );

      if (houseworkApiHeadersJSON) {
        const houseworkApiHeaders: Record<string, string> = JSON.parse(
          houseworkApiHeadersJSON,
        );
        try {
          Object.entries(houseworkApiHeaders).forEach(([key, value]) =>
            headers.set(key, value),
          );
        } catch (e) {}
      }
      return headers;
    },
    mode: "cors",
  }),
  endpoints: (builder) => ({}),
});

export default apiService;
