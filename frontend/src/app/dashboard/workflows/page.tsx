"use client";

import { useEffect, useState } from "react";
import { format } from "date-fns";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/contexts/AuthContext";
import { api } from "@/lib/api";

interface WorkflowAction {
  id: string;
  action_type: string;
  config: Record<string, any>;
}

interface Workflow {
  id: string;
  name: string;
  description: string;
  trigger_type: string;
  is_active: boolean;
  created_at: string;
  actions: WorkflowAction[];
}

export default function WorkflowsPage() {
  const { activeOrg } = useAuth();
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (activeOrg) {
      loadWorkflows();
    }
  }, [activeOrg]);

  const loadWorkflows = async () => {
    try {
      const res = await api.get("/api/v1/workflows");
      setWorkflows(res.data);
    } catch (error) {
      console.error("Failed to load workflows", error);
    } finally {
      setLoading(false);
    }
  };

  const createExampleWorkflow = async () => {
    try {
      await api.post("/api/v1/workflows", {
        name: "Auto Webhook on Task",
        description: "Sends a webhook payload whenever a task is created",
        trigger_type: "task.created",
        is_active: true,
        actions: [
          {
            action_type: "webhook",
            config: { url: "https://example.com/hook" },
            order: 0,
          },
        ],
      });
      loadWorkflows();
    } catch (error) {
      console.error("Failed to create workflow", error);
    }
  };

  if (!activeOrg) return null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Workflows</h2>
          <p className="text-muted-foreground">
            Automate actions across your organization.
          </p>
        </div>
        <Button onClick={createExampleWorkflow}>Create Example Workflow</Button>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {loading ? (
          <p>Loading...</p>
        ) : workflows.length === 0 ? (
          <p>No workflows found.</p>
        ) : (
          workflows.map((workflow) => (
            <Card key={workflow.id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base">{workflow.name}</CardTitle>
                  <Badge variant={workflow.is_active ? "default" : "secondary"}>
                    {workflow.is_active ? "Active" : "Inactive"}
                  </Badge>
                </div>
                <CardDescription>{workflow.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Trigger</span>
                    <span className="font-mono bg-muted px-1 py-0.5 rounded text-xs">
                      {workflow.trigger_type}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Actions</span>
                    <span>{workflow.actions.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Created</span>
                    <span>
                      {format(new Date(workflow.created_at), "MMM d, yyyy")}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
