import apiService from "./index";
import { components, paths } from "./schema";

export type SubscribeResponse =
paths["/api/v1/notifications/subscribe"]["post"]["responses"][200]["content"]["application/json"];

export type SubscribeRequest =
paths["/api/v1/notifications/subscribe"]["post"]["requestBody"]["content"]["application/json"];

export type Notification = components["schemas"]["NotificationSchema"];

export const extendedApiService = apiService.injectEndpoints({
  endpoints: (builder) => ({
    subscribe: builder.mutation<SubscribeResponse, SubscribeRequest>({
      query: body => ({
       url: "/api/v1/notifications/subscribe",
       method: "POST",
       body,
    }),
      invalidatesTags: ["subscriptions"],
    }),
    markNotificationAsRead: builder.mutation<string, number>({
      query: id => ({
        url: `/api/v1/notifications/${id}/read`,
        method: "POST"
      }),
      invalidatesTags: ["notifications"]
    }),
    markAllNotificationsAsRead: builder.mutation<void, void>({
      query: id => ({
        url: `/api/v1/notifications/all/read`,
        method: "POST"
      }),
      invalidatesTags: ["notifications"]
    }),
    getUnreadNotifications: builder.query<Notification[], void>({
      query: () => '/api/v1/notifications/unread',
      providesTags: ["notifications"]
    })
  }),
});

export const { useSubscribeMutation, useGetUnreadNotificationsQuery, useMarkNotificationAsReadMutation, useMarkAllNotificationsAsReadMutation } = extendedApiService;
