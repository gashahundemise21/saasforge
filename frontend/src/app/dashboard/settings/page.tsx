'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Copy } from 'lucide-react';
import { Checkbox } from '@/components/ui/checkbox';

export default function SettingsPage() {
  const { activeOrg } = useAuth();
  
  // API Keys state
  const [apiKeys, setApiKeys] = useState<any[]>([]);
  const [newKeyName, setNewKeyName] = useState('');
  const [isKeyDialogOpen, setIsKeyDialogOpen] = useState(false);
  const [generatedKey, setGeneratedKey] = useState<string | null>(null);

  // Webhooks state
  const [webhooks, setWebhooks] = useState<any[]>([]);
  const [newWebhookUrl, setNewWebhookUrl] = useState('');
  const [selectedEvents, setSelectedEvents] = useState<string[]>([]);
  const [isWebhookDialogOpen, setIsWebhookDialogOpen] = useState(false);

  const availableEvents = ['task.created', 'task.updated', 'task.deleted'];

  useEffect(() => {
    if (activeOrg) {
      fetchApiKeys();
      fetchWebhooks();
    }
  }, [activeOrg]);

  const fetchApiKeys = async () => {
    try {
      const res = await api.get('/api/v1/api-keys');
      setApiKeys(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchWebhooks = async () => {
    try {
      const res = await api.get('/api/v1/webhooks');
      setWebhooks(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleCreateApiKey = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await api.post('/api/v1/api-keys', { name: newKeyName });
      setGeneratedKey(res.data.key); // Show secret once
      setNewKeyName('');
      fetchApiKeys();
    } catch (err) {
      console.error(err);
    }
  };

  const handleCreateWebhook = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/api/v1/webhooks', {
        url: newWebhookUrl,
        events: selectedEvents,
      });
      setIsWebhookDialogOpen(false);
      setNewWebhookUrl('');
      setSelectedEvents([]);
      fetchWebhooks();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Developer Settings</h1>
        <p className="text-muted-foreground">
          Manage API keys and Webhook endpoints for {activeOrg?.name}
        </p>
      </div>

      <Tabs defaultValue="api-keys" className="space-y-4">
        <TabsList>
          <TabsTrigger value="api-keys">API Keys</TabsTrigger>
          <TabsTrigger value="webhooks">Webhooks</TabsTrigger>
        </TabsList>
        
        {/* API KEYS TAB */}
        <TabsContent value="api-keys" className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold tracking-tight">Active API Keys</h2>
            <Dialog open={isKeyDialogOpen} onOpenChange={setIsKeyDialogOpen}>
              <DialogTrigger asChild>
                <Button>Generate Key</Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-[425px]">
                {generatedKey ? (
                  <div className="space-y-4">
                    <DialogHeader>
                      <DialogTitle>Save your secret key</DialogTitle>
                      <DialogDescription>
                        Please copy this key and save it somewhere secure. You will not be able to see it again.
                      </DialogDescription>
                    </DialogHeader>
                    <div className="flex items-center space-x-2 bg-muted p-4 rounded-md">
                      <code className="text-sm flex-1 break-all">{generatedKey}</code>
                      <Button variant="ghost" size="icon" onClick={() => navigator.clipboard.writeText(generatedKey)}>
                        <Copy className="h-4 w-4" />
                      </Button>
                    </div>
                    <DialogFooter>
                      <Button onClick={() => { setIsKeyDialogOpen(false); setGeneratedKey(null); }}>
                        Done
                      </Button>
                    </DialogFooter>
                  </div>
                ) : (
                  <form onSubmit={handleCreateApiKey}>
                    <DialogHeader>
                      <DialogTitle>Generate new API Key</DialogTitle>
                      <DialogDescription>
                        API keys grant full access to your organization's resources.
                      </DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                      <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="name" className="text-right">Name</Label>
                        <Input
                          id="name"
                          value={newKeyName}
                          onChange={(e) => setNewKeyName(e.target.value)}
                          className="col-span-3"
                          required
                          placeholder="e.g. Production Backend"
                        />
                      </div>
                    </div>
                    <DialogFooter>
                      <Button type="submit">Generate</Button>
                    </DialogFooter>
                  </form>
                )}
              </DialogContent>
            </Dialog>
          </div>
          
          <div className="rounded-md border bg-card">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Prefix</TableHead>
                  <TableHead>Created At</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {apiKeys.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={3} className="text-center text-muted-foreground h-24">No API keys found.</TableCell>
                  </TableRow>
                ) : (
                  apiKeys.map(key => (
                    <TableRow key={key.id}>
                      <TableCell className="font-medium">{key.name}</TableCell>
                      <TableCell><code className="bg-muted px-1.5 py-0.5 rounded text-xs">{key.prefix}</code></TableCell>
                      <TableCell className="text-muted-foreground">{new Date(key.created_at).toLocaleDateString()}</TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </TabsContent>

        {/* WEBHOOKS TAB */}
        <TabsContent value="webhooks" className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold tracking-tight">Webhook Endpoints</h2>
            <Dialog open={isWebhookDialogOpen} onOpenChange={setIsWebhookDialogOpen}>
              <DialogTrigger asChild>
                <Button>Register Endpoint</Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-[425px]">
                <form onSubmit={handleCreateWebhook}>
                  <DialogHeader>
                    <DialogTitle>Register Webhook</DialogTitle>
                    <DialogDescription>
                      We will send POST requests to this URL when the selected events occur.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="grid gap-4 py-4">
                    <div className="space-y-2">
                      <Label htmlFor="url">Payload URL</Label>
                      <Input
                        id="url"
                        type="url"
                        placeholder="https://example.com/webhook"
                        value={newWebhookUrl}
                        onChange={(e) => setNewWebhookUrl(e.target.value)}
                        required
                      />
                    </div>
                    <div className="space-y-3 mt-2">
                      <Label>Events to send</Label>
                      <div className="space-y-2">
                        {availableEvents.map(event => (
                          <div key={event} className="flex items-center space-x-2">
                            <Checkbox 
                              id={event} 
                              checked={selectedEvents.includes(event)}
                              onCheckedChange={(checked) => {
                                if (checked) {
                                  setSelectedEvents([...selectedEvents, event]);
                                } else {
                                  setSelectedEvents(selectedEvents.filter(e => e !== event));
                                }
                              }}
                            />
                            <Label htmlFor={event} className="font-normal">{event}</Label>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                  <DialogFooter>
                    <Button type="submit" disabled={selectedEvents.length === 0}>
                      Register
                    </Button>
                  </DialogFooter>
                </form>
              </DialogContent>
            </Dialog>
          </div>

          <div className="rounded-md border bg-card">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>URL</TableHead>
                  <TableHead>Events</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {webhooks.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={3} className="text-center text-muted-foreground h-24">No webhooks registered.</TableCell>
                  </TableRow>
                ) : (
                  webhooks.map(wh => (
                    <TableRow key={wh.id}>
                      <TableCell className="font-medium max-w-[200px] truncate">{wh.url}</TableCell>
                      <TableCell>
                        <div className="flex flex-wrap gap-1">
                          {wh.events.map((e: string) => (
                            <Badge key={e} variant="outline" className="text-xs">{e}</Badge>
                          ))}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant={wh.is_active ? 'default' : 'secondary'}>
                          {wh.is_active ? 'Active' : 'Inactive'}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
