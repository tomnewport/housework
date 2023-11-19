import apiService from "./index";
import { Job, PaginatedResponse } from "./types";

import { paths, operations } from "./schema";

export type GetJobByIDResponse =
  paths["/api/v1/jobs/{job_id}"]["get"]["responses"][200]["content"]["application/json"];
export type GetJobDryRunResponse =
  paths["/api/v1/jobs/{job_id}/dry_run/{action}"]["get"]["responses"][200]["content"]["application/json"];

export type JobDryRunRequest =
  operations["hwk_apps_api_v1_job_dry_run_job"]["parameters"];

export type JobCloseRequest = Pick<
  paths["/api/v1/jobs/{job_id}/status/{status}"]["post"],
  "parameters" | "requestBody"
>;
export type JobCloseResponse =
  paths["/api/v1/jobs/{job_id}/status/{status}"]["post"]["responses"]["200"]["content"]["application/json"];

export const extendedApiService = apiService.injectEndpoints({
  endpoints: (builder) => ({
    // Endpoint to get the current user's information
    getOwnOpenJobs: builder.query<PaginatedResponse<Job>, unknown>({
      query: () =>
        "/api/v1/jobs/?only_self=true&status=Scheduled&status=Open&limit=300&offset=0",
      providesTags: ["jobs"],
    }),
    getOverdueJobs: builder.query<PaginatedResponse<Job>, unknown>({
      query: () =>
        "/api/v1/jobs/?only_self=false&status=Overdue&limit=300&offset=0",
      providesTags: ["jobs"],
    }),
    getJobById: builder.query<GetJobByIDResponse, number>({
      query: (jobId) => `/api/v1/jobs/${jobId}`,
      providesTags: ["jobs"],
    }),
    getJobDryRun: builder.query<GetJobDryRunResponse, JobDryRunRequest>({
      query: (params) =>
        `/api/v1/jobs/${params.path.job_id}/dry_run/${
          params.path.action
        }?delay=${params.query?.delay || 0}`,
      providesTags: ["jobs"],
    }),
    jobClose: builder.mutation<JobCloseResponse, JobCloseRequest>({
      query: (params) => ({
        url: `/api/v1/jobs/${params.parameters.path.job_id}/status/${params.parameters.path.status}`,
        method: "POST",
        body: params.requestBody.content["application/json"],
      }),
      invalidatesTags: ["jobs"],
    }),
  }),
});

export const {
  useGetOwnOpenJobsQuery,
  useGetOverdueJobsQuery,
  useGetJobByIdQuery,
  useGetJobDryRunQuery,
  useJobCloseMutation,
} = extendedApiService;
