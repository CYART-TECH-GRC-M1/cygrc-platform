import { z } from "zod";

export const riskSchema = z.object({
  name: z.string().min(5, "Risk name must be at least 5 characters"),
  category: z.enum(["Operational", "Financial", "Cyber", "Compliance", "Strategic"]),
  likelihood: z.number().min(1).max(5),
  impact: z.number().min(1).max(5),
  owner: z.string().min(2, "Owner is required"),
  dueDate: z.string().optional(),
});

export type RiskFormValues = z.infer<typeof riskSchema>;
