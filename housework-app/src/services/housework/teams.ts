import apiService from "./index";
import { paths } from './schema';

type GetTeamsResponse = paths["/api/v1/teams/"]["get"]["responses"]["200"]["content"]["application/json"];
type GetInvitationsResponse = paths["/api/v1/teams/invitations"]["get"]["responses"]["200"]["content"]["application/json"];
type RespondInvitationRequest = paths["/api/v1/teams/invitations/{invitation_id}/{action}"]["post"]["parameters"]["path"];

export const extendedApiService = apiService.injectEndpoints({
  endpoints: (builder) => ({
    getTeams: builder.query<GetTeamsResponse, void>({
      query: () => "/api/v1/teams/",
      providesTags: ["teams"],
    }),
    getInvitations: builder.query<GetInvitationsResponse, void>({
      query: () => "/api/v1/teams/invitations",
      providesTags: ["invites"],
    }),
    respondInvitation: builder.mutation<boolean, RespondInvitationRequest>({
      query: (req) => ({
        url: `/api/v1/teams/invitations/${req.invitation_id}/${req.action}/`,
        method: "POST",
      }),
      invalidatesTags: ["invites", "self", "teams", "jobs"],
    }),
  }),
});

export const { useRespondInvitationMutation, useGetInvitationsQuery, useGetTeamsQuery } = extendedApiService;
