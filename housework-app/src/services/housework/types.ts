export type PaginatedResponse<T> = {
  items: T[];
  count: number;
};

export interface Job {
  id: number;
  team: string;
  name: string;
  default_credit: number;
  is_priority: boolean;
  assignee: number;
  due_date: string;
  status: "Scheduled" | "Open" | "Overdue" | "Complete" | "Cancelled";
}
