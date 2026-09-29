"use client";

import { useEffect, useState, use, useCallback } from "react";
import { ArrowLeft, UserPlus, Trash2 } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

interface TeamMember {
  id: string;
  user_id: string;
  role: string;
  created_at: string;
  user: {
    email: string;
  };
}

interface TeamInvitation {
  id: string;
  email: string;
  role: string;
  status: string;
  expires_at: string;
}

export default function TeamDetailsPage({ params }: { params: Promise<{ teamId: string }> }) {
  const resolvedParams = use(params);
  const router = useRouter();
  const { activeOrg } = useAuth();
  const activeOrgSlug = activeOrg?.slug;
  
  const [team, setTeam] = useState<any>(null);
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [invitations, setInvitations] = useState<TeamInvitation[]>([]);
  
  const [loading, setLoading] = useState(true);
  
  // Invite Modal State
  const [isInviteOpen, setIsInviteOpen] = useState(false);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteLoading, setInviteLoading] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const [teamRes, membersRes, invitesRes] = await Promise.all([
        api.get(`/api/v1/teams/${resolvedParams.teamId}`),
        api.get(`/api/v1/teams/${resolvedParams.teamId}/members`),
        api.get(`/api/v1/teams/${resolvedParams.teamId}/invitations`)
      ]);
      setTeam(teamRes.data);
      setMembers(membersRes.data);
      setInvitations(invitesRes.data);
    } catch (error) {
      console.error("Failed to fetch team details", error);
      router.push("/dashboard/teams");
    } finally {
      setLoading(false);
    }
  }, [resolvedParams.teamId, router]);

  useEffect(() => {
    if (activeOrg?.slug) {
      fetchData();
    }
  }, [activeOrg?.slug, fetchData]);

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setInviteLoading(true);
      await api.post(`/api/v1/teams/${resolvedParams.teamId}/invitations`, {
        email: inviteEmail,
        role: "member"
      });
      setIsInviteOpen(false);
      setInviteEmail("");
      fetchData();
    } catch (error) {
      console.error("Failed to invite to team", error);
    } finally {
      setInviteLoading(false);
    }
  };

  const handleRemoveMember = async (userId: string) => {
    if (!confirm("Are you sure you want to remove this member from the team?")) return;
    try {
      await api.delete(`/api/v1/teams/${resolvedParams.teamId}/members/${userId}`);
      fetchData();
    } catch (error) {
      console.error("Failed to remove member", error);
    }
  };

  if (!activeOrg?.slug || loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      <div className="flex items-center space-x-4 mb-4">
        <Button variant="ghost" size="icon" asChild>
          <Link href="/dashboard/teams">
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        <h2 className="text-3xl font-bold tracking-tight">{team?.name}</h2>
      </div>
      
      {team?.description && (
        <p className="text-muted-foreground">{team.description}</p>
      )}

      <div className="flex items-center justify-between space-y-2 mt-8">
        <h3 className="text-xl font-bold">Members</h3>
        <Dialog open={isInviteOpen} onOpenChange={setIsInviteOpen}>
          <DialogTrigger asChild>
            <Button>
              <UserPlus className="mr-2 h-4 w-4" /> Invite Member
            </Button>
          </DialogTrigger>
          <DialogContent>
            <form onSubmit={handleInvite}>
              <DialogHeader>
                <DialogTitle>Invite to Team</DialogTitle>
                <DialogDescription>
                  Invite an existing organization member to this team.
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid gap-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={inviteEmail}
                    onChange={(e) => setInviteEmail(e.target.value)}
                    required
                  />
                </div>
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setIsInviteOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={inviteLoading}>
                  {inviteLoading ? "Inviting..." : "Send Invite"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Active Members</CardTitle>
          </CardHeader>
          <CardContent>
            {members.length === 0 ? (
              <div className="text-sm text-muted-foreground py-4">No active members.</div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>User</TableHead>
                    <TableHead>Role</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {members.map((member) => (
                    <TableRow key={member.id}>
                      <TableCell className="font-medium">{member.user?.email}</TableCell>
                      <TableCell className="capitalize">{member.role}</TableCell>
                      <TableCell className="text-right">
                        <Button 
                          variant="ghost" 
                          size="icon"
                          onClick={() => handleRemoveMember(member.user_id)}
                        >
                          <Trash2 className="h-4 w-4 text-red-500" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Pending Invitations</CardTitle>
          </CardHeader>
          <CardContent>
            {invitations.length === 0 ? (
              <div className="text-sm text-muted-foreground py-4">No pending invitations.</div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Email</TableHead>
                    <TableHead>Role</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {invitations.map((inv) => (
                    <TableRow key={inv.id}>
                      <TableCell className="font-medium">{inv.email}</TableCell>
                      <TableCell className="capitalize">{inv.role}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{inv.status}</Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
