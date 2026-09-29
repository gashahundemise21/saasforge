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
  const [activeTab, setActiveTab] = useState('profile');
  const [invoices, setInvoices] = useState<any[]>([]);
  const [subscription, setSubscription] = useState<any>(null);
  
  // API Keys state
  const [apiKeys, setApiKeys] = useState<any[]>([]);
  const [newKeyName, setNewKeyName] = useState('');
  const [isKeyDialogOpen, setIsKeyDialogOpen] = useState(false);
  const [generatedKey, setGeneratedKey] = useState<string | null>(null);
  const [generatedWebhookSecret, setGeneratedWebhookSecret] = useState<string | null>(null);
  const [keyLogs, setKeyLogs] = useState<any[]>([]);
  const [isLogsDialogOpen, setIsLogsDialogOpen] = useState(false);
  const [selectedKeyForLogs, setSelectedKeyForLogs] = useState<string | null>(null);


  // Integrations state
  const [integrations, setIntegrations] = useState<any[]>([]);
  const [isIntegrationDialogOpen, setIsIntegrationDialogOpen] = useState(false);
  const [integrationProvider, setIntegrationProvider] = useState('slack');
  const [integrationToken, setIntegrationToken] = useState('');

  // Webhooks state
  const [webhooks, setWebhooks] = useState<any[]>([]);
  const [newWebhookUrl, setNewWebhookUrl] = useState('');
  const [selectedEvents, setSelectedEvents] = useState<string[]>([]);
  const [isWebhookDialogOpen, setIsWebhookDialogOpen] = useState(false);
  const [webhookDeliveries, setWebhookDeliveries] = useState<any[]>([]);
  const [isDeliveriesDialogOpen, setIsDeliveriesDialogOpen] = useState(false);
  const [selectedEndpointForDeliveries, setSelectedEndpointForDeliveries] = useState<string | null>(null);

  const availableEvents = ['task.created', 'task.updated', 'task.deleted'];

  useEffect(() => {
    if (activeOrg) {
      fetchApiKeys();
      fetchWebhooks();
      fetchIntegrations();
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


  const fetchIntegrations = async () => {
    try {
      const res = await api.get('/api/v1/integrations');
      setIntegrations(res.data);
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


  const handleCreateIntegration = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/api/v1/integrations', {
        provider: integrationProvider,
        credentials: { token: integrationToken },
        settings: {},
      });
      setIsIntegrationDialogOpen(false);
      setIntegrationToken('');
      fetchIntegrations();
    } catch (err) {
      console.error(err);
    }
  };


  const fetchKeyLogs = async (keyId: string) => {
    try {
      const res = await api.get(`/api/v1/api-keys/${keyId}/logs`);
      setKeyLogs(res.data);
      setSelectedKeyForLogs(keyId);
      setIsLogsDialogOpen(true);
    } catch (err) {
      console.error(err);
    }
  };

  const rotateKey = async (keyId: string) => {
    if (!confirm('Are you sure you want to rotate this key? The old key will stop working immediately.')) return;
    try {
      const res = await api.post(`/api/v1/api-keys/${keyId}/rotate`);
      setGeneratedKey(res.data.raw_key);
      setIsKeyDialogOpen(true);
      fetchApiKeys();
    } catch (err) {
      console.error(err);
    }
  };


  const fetchWebhookDeliveries = async (endpointId: string) => {
    try {
      const res = await api.get(`/api/v1/webhooks/${endpointId}/deliveries`);
      setWebhookDeliveries(res.data);
      setSelectedEndpointForDeliveries(endpointId);
      setIsDeliveriesDialogOpen(true);
    } catch (err) {
      console.error(err);
    }
  };

  const replayDelivery = async (deliveryId: string) => {
    if (!selectedEndpointForDeliveries) return;
    try {
      await api.post(`/api/v1/webhooks/${selectedEndpointForDeliveries}/deliveries/${deliveryId}/retry`);
      // Refresh deliveries
      fetchWebhookDeliveries(selectedEndpointForDeliveries);
    } catch (err) {
      console.error(err);
    }
  };



  const fetchBillingData = async () => {
    if (!activeOrg) return;
    try {
      const invRes = await api.get('/api/v1/billing/invoices');
      setInvoices(invRes.data);
    } catch (err) {
      console.error('Failed to load invoices', err);
    }
    try {
      const subRes = await api.get('/api/v1/billing/subscription');
      setSubscription(subRes.data);
    } catch (err) {
      console.error('Failed to load subscription details', err);
    }
  };

  useEffect(() => {
    if (activeTab === 'billing' && activeOrg) {
      fetchBillingData();
    }
  }, [activeTab, activeOrg]);

  const handleCreateWebhook = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await api.post('/api/v1/webhooks', {
        url: newWebhookUrl,
        events: selectedEvents,
      });
      // setIsWebhookDialogOpen(false); // We keep it open to show secret
      setGeneratedWebhookSecret(res.data.secret);
      setNewWebhookUrl('');
      setSelectedEvents([]);
      fetchWebhooks();
      fetchIntegrations();
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
          <TabsTrigger value="integrations">Integrations</TabsTrigger>
        </TabsList>
        
        {/* API KEYS TAB */}
        <TabsContent value="api-keys" className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold tracking-tight">Active API Keys</h2>
            <Dialog open={isKeyDialogOpen} onOpenChange={setIsKeyDialogOpen}>
              <DialogTrigger render={<Button />}>Generate Key</DialogTrigger>
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
                  <TableHead className="text-right">Actions</TableHead>
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
                      <TableCell className="text-right">
                        <Button variant="ghost" size="sm" onClick={() => fetchKeyLogs(key.id)}>Logs</Button>
                        <Button variant="outline" size="sm" onClick={() => rotateKey(key.id)}>Rotate</Button>
                      </TableCell>
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
              <DialogTrigger render={<Button />}>Register Endpoint</DialogTrigger>
              <DialogContent className="sm:max-w-[425px]">
                
                {generatedWebhookSecret ? (
                  <div className="space-y-4">
                    <DialogHeader>
                      <DialogTitle>Save your Webhook Secret</DialogTitle>
                      <DialogDescription>
                        Use this secret to verify signatures (X-SaaSForge-Signature) of incoming payloads using HMAC-SHA256.
                      </DialogDescription>
                    </DialogHeader>
                    <div className="flex items-center space-x-2 bg-muted p-4 rounded-md">
                      <code className="text-sm flex-1 break-all">{generatedWebhookSecret}</code>
                      <Button variant="ghost" size="icon" onClick={() => navigator.clipboard.writeText(generatedWebhookSecret)}>
                        <Copy className="h-4 w-4" />
                      </Button>
                    </div>
                    <DialogFooter>
                      <Button onClick={() => { setIsWebhookDialogOpen(false); setGeneratedWebhookSecret(null); }}>
                        Done
                      </Button>
                    </DialogFooter>
                  </div>
                ) : (
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
                )}
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
                  <TableHead className="text-right">Actions</TableHead>
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
                      <TableCell className="text-right">
                        <Button variant="ghost" size="sm" onClick={() => fetchWebhookDeliveries(wh.id)}>Deliveries</Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </TabsContent>
      </Tabs>

      <Dialog open={isLogsDialogOpen} onOpenChange={setIsLogsDialogOpen}>
        <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>API Request Logs</DialogTitle>
            <DialogDescription>Recent API requests made with this key</DialogDescription>
          </DialogHeader>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Time</TableHead>
                <TableHead>Method</TableHead>
                <TableHead>Endpoint</TableHead>
                <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                <TableHead>Duration</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {keyLogs.length === 0 ? (
                <TableRow><TableCell colSpan={5} className="text-center">No requests logged yet.</TableCell></TableRow>
              ) : (
                keyLogs.map((log: any) => (
                  <TableRow key={log.id}>
                    <TableCell className="text-xs">{new Date(log.created_at).toLocaleString()}</TableCell>
                    <TableCell><Badge variant="outline">{log.method}</Badge></TableCell>
                    <TableCell className="font-mono text-xs">{log.endpoint}</TableCell>
                    <TableCell>
                      <Badge variant={log.status_code >= 400 ? 'destructive' : 'default'}>{log.status_code}</Badge>
                    </TableCell>
                    <TableCell className="text-xs">{log.duration_ms}ms</TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </DialogContent>
      </Dialog>

      <Dialog open={isDeliveriesDialogOpen} onOpenChange={setIsDeliveriesDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Webhook Deliveries</DialogTitle>
            <DialogDescription>Recent deliveries for this endpoint</DialogDescription>
          </DialogHeader>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Time</TableHead>
                <TableHead>Event</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {webhookDeliveries.length === 0 ? (
                <TableRow><TableCell colSpan={4} className="text-center">No deliveries found.</TableCell></TableRow>
              ) : (
                webhookDeliveries.map((deliv: any) => (
                  <TableRow key={deliv.id}>
                    <TableCell className="text-xs">{new Date(deliv.created_at).toLocaleString()}</TableCell>
                    <TableCell><Badge variant="outline">{deliv.event_type}</Badge></TableCell>
                    <TableCell>
                      <Badge variant={deliv.success ? 'default' : 'destructive'}>
                        {deliv.status_code || 'Err'}
                      </Badge>
                      {!deliv.success && deliv.error_message && (
                        <p className="text-xs text-destructive mt-1 truncate max-w-[200px]">{deliv.error_message}</p>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button variant="outline" size="sm" onClick={() => replayDelivery(deliv.id)}>Retry</Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </DialogContent>
      </Dialog>
    </div>
  );
}
