import apiService from "./index";
import { Type, plainToClass } from "class-transformer";
import { paths } from "./schema";

export type GetSelfResponse = paths["/api/v1/people/users/self/"]["get"]["responses"]["200"]["content"]["application/json"]
export type UpdateSelfResponse = paths["/api/v1/people/users/self/"]["patch"]["responses"]["200"]["content"]["application/json"]
export type UpdateSelfRequest = paths["/api/v1/people/users/self/"]["patch"]["requestBody"]["content"]["application/json"];


class UserSelf {
  id!: number;
  username!: string;
  approved!: boolean;
  first_name!: string;
  last_name!: string;
  is_superuser!: boolean;

  @Type(() => Date)
  date_joined!: Date;

  preferences!: Record<string, unknown>; // Adjust as needed
}

interface UserSelfResponse {
  id: number;
  username: string;
  approved: boolean;
  first_name: string;
  last_name: string;
  is_superuser: boolean;
  date_joined: string;
  preferences: Record<string, unknown>;
}

export const extendedApiService = apiService.injectEndpoints({
  endpoints: (builder) => ({
    sendOtp: builder.mutation<Record<string, string>, string>({
      query: (sub) => ({
        url: "/api/v1/auth/otp/send",
        method: "POST",
        body: {sub},
      }),
      transformResponse: (response: Record<string, string>) => {
        localStorage.setItem("houseworkApi.headers", JSON.stringify(response));
        return response;
      },
    }),
    respondOtp: builder.mutation<Record<string, string>, string>({
      query: (code) => ({
        url: "/api/v1/auth/otp/respond",
        method: "POST",
        body: {code},
      }),
      transformResponse: (response: Record<string, string>) => {
        localStorage.setItem("houseworkApi.headers", JSON.stringify(response));
        return response;
      },
      invalidatesTags: ["self"],
    }),
    getSelf: builder.query<GetSelfResponse, void>({
      query: () => "/api/v1/people/users/self/",
      providesTags: ["self"],
    }),
    updateSelf: builder.mutation<UpdateSelfResponse, UpdateSelfRequest>({
      query: (credentials) => ({
        url: "/api/v1/people/users/self/",
        method: "PATCH",
        body: credentials,
      }),
      invalidatesTags: ["self"],
    }),
    // Endpoint to login
    loginUser: builder.mutation({
      query: (credentials) => ({
        url: "/api/v1/auth/session",
        method: "POST",
        body: credentials,
      }),
      transformResponse: (response: Record<string, string>) => {
        localStorage.setItem("houseworkApi.headers", JSON.stringify(response));
        return response;
      },
      invalidatesTags: ["self"],
    }),
    logoutUser: builder.mutation({
      query: () => ({
        url: "/api/v1/auth/session",
        method: "DELETE",
      }),
      transformResponse: (response) => {
        localStorage.removeItem("houseworkApi.headers");
        return response;
      },
      invalidatesTags: ["self"],
    }),
  }),
});

export const { useUpdateSelfMutation, useSendOtpMutation, useRespondOtpMutation, useGetSelfQuery, useLoginUserMutation, useLogoutUserMutation } =
  extendedApiService;
