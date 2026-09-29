'use client';

import { useState, useEffect, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { format } from 'date-fns';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Loader2, ArrowLeft, Trash2, Edit2, Paperclip, Download } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import Link from 'next/link';

/* eslint-disable react-hooks/exhaustive-deps */
/* eslint-disable react-hooks/set-state-in-effect */
/* eslint-disable react-hooks/immutability */

export default function TaskDetailPage() {
  const { taskId } = useParams();
  const router = useRouter();
  const { activeOrg, user } = useAuth();
  
  const [task, setTask] = useState<any>(null);
  const [comments, setComments] = useState<any[]>([]);
  const [attachments, setAttachments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [newComment, setNewComment] = useState('');
  const [submitting, setSubmitting] = useState(false);
  
  const [editingCommentId, setEditingCommentId] = useState<string | null>(null);
  const [editContent, setEditContent] = useState('');
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    if (activeOrg && taskId) {
      fetchTaskData();
    }
  }, [activeOrg, taskId]);

  const fetchTaskData = async () => {
    try {
      setLoading(true);
      const [taskRes, commentsRes, attachmentsRes] = await Promise.all([
        api.get(`/api/v1/tasks/${taskId}`),
        api.get(`/api/v1/comments/tasks/${taskId}`),
        api.get(`/api/v1/attachments/tasks/${taskId}`)
      ]);
      setTask(taskRes.data);
      setComments(commentsRes.data);
      setAttachments(attachmentsRes.data);
    } catch (err) {
      console.error('Failed to fetch task data', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim()) return;
    
    try {
      setSubmitting(true);
      const res = await api.post('/api/v1/comments', {
        task_id: taskId,
        content: newComment.trim()
      });
      setComments([...comments, res.data]);
      setNewComment('');
    } catch (err) {
      console.error('Failed to add comment', err);
    } finally {
      setSubmitting(false);
    }
  };
  
  const handleDeleteComment = async (commentId: string) => {
    if (!confirm("Are you sure you want to delete this comment?")) return;
    try {
      await api.delete(`/api/v1/comments/${commentId}`);
      setComments(comments.filter(c => c.id !== commentId));
    } catch (err) {
      console.error('Failed to delete comment', err);
    }
  };

  const handleUpdateComment = async (commentId: string) => {
    if (!editContent.trim()) return;
    try {
      const res = await api.put(`/api/v1/comments/${commentId}`, {
        content: editContent.trim()
      });
      setComments(comments.map(c => c.id === commentId ? res.data : c));
      setEditingCommentId(null);
      setEditContent('');
    } catch (err) {
      console.error('Failed to update comment', err);
    }
  };
  
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !taskId) return;
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('task_id', taskId as string);
    
    try {
      setUploading(true);
      const res = await api.post('/api/v1/attachments', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setAttachments([res.data, ...attachments]);
      if (fileInputRef.current) fileInputRef.current.value = '';
    } catch (err) {
      console.error('Failed to upload attachment', err);
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteAttachment = async (attachmentId: string) => {
    if (!confirm("Are you sure you want to delete this attachment?")) return;
    try {
      await api.delete(`/api/v1/attachments/${attachmentId}`);
      setAttachments(attachments.filter(a => a.id !== attachmentId));
    } catch (err) {
      console.error('Failed to delete attachment', err);
    }
  };

  const handleDownloadAttachment = async (attachment: any) => {
    try {
      const res = await api.get(`/api/v1/attachments/${attachment.id}/download`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', attachment.filename);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
    } catch (err) {
      console.error('Failed to download attachment', err);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!task) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold mb-2">Task not found</h2>
        <Button onClick={() => router.push('/dashboard/tasks')}>Back to Tasks</Button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" asChild>
          <Link href="/dashboard/tasks">
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold tracking-tight">{task.title}</h1>
            <Badge variant="outline" className="capitalize">{task.status}</Badge>
            <Badge variant="secondary" className="capitalize">{task.priority}</Badge>
          </div>
          <p className="text-muted-foreground mt-1">
            Created on {format(new Date(task.created_at), 'PPP')}
          </p>
        </div>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Description</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="whitespace-pre-wrap">{task.description || 'No description provided.'}</p>
        </CardContent>
      </Card>
      
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">Attachments</h2>
          <div>
            <input 
              type="file" 
              ref={fileInputRef} 
              className="hidden" 
              onChange={handleFileUpload}
            />
            <Button 
              variant="outline" 
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
            >
              {uploading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Paperclip className="h-4 w-4 mr-2" />}
              {uploading ? 'Uploading...' : 'Attach File'}
            </Button>
          </div>
        </div>
        
        {attachments.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {attachments.map((att) => (
              <Card key={att.id} className="overflow-hidden group">
                <CardContent className="p-4 flex items-center justify-between">
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="bg-muted p-2 rounded-md">
                      <Paperclip className="h-5 w-5 text-muted-foreground" />
                    </div>
                    <div className="min-w-0">
                      <p className="text-sm font-medium truncate">{att.filename}</p>
                      <p className="text-xs text-muted-foreground">{formatFileSize(att.size)} • {format(new Date(att.created_at), 'MMM d, yyyy')}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Button 
                      variant="ghost" 
                      size="icon" 
                      className="h-8 w-8"
                      onClick={() => handleDownloadAttachment(att)}
                    >
                      <Download className="h-4 w-4 text-muted-foreground" />
                    </Button>
                    {(user?.id === att.uploader_id || user?.role === 'Owner' || user?.role === 'Admin') && (
                      <Button 
                        variant="ghost" 
                        size="icon" 
                        className="h-8 w-8 text-destructive hover:text-destructive hover:bg-destructive/10"
                        onClick={() => handleDeleteAttachment(att.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <div className="text-center py-6 bg-muted/50 rounded-lg border border-dashed">
            <p className="text-sm text-muted-foreground">No attachments yet</p>
          </div>
        )}
      </div>
      
      <div className="space-y-6">
        <h2 className="text-xl font-semibold">Activity & Comments</h2>
        
        <div className="space-y-4">
          {comments.map((comment) => (
            <Card key={comment.id} className="overflow-hidden group">
              <CardContent className="p-4 sm:p-6">
                <div className="flex items-start gap-4">
                  <Avatar className="h-10 w-10">
                    <AvatarFallback>{comment.author?.email?.charAt(0).toUpperCase() || 'U'}</AvatarFallback>
                  </Avatar>
                  
                  <div className="flex-1 space-y-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 text-sm">
                        <span className="font-medium text-foreground">
                          {comment.author?.full_name || comment.author?.email || 'Unknown User'}
                        </span>
                        <span className="text-muted-foreground">
                          {format(new Date(comment.created_at), 'MMM d, yyyy h:mm a')}
                        </span>
                        {comment.updated_at !== comment.created_at && (
                          <span className="text-muted-foreground text-xs">(edited)</span>
                        )}
                      </div>
                      
                      {/* Check if current user is the author */}
                      {user && comment.author?.id === user.id && (
                        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          <Button 
                            variant="ghost" 
                            size="icon" 
                            className="h-8 w-8 text-muted-foreground hover:text-foreground"
                            onClick={() => {
                              setEditingCommentId(comment.id);
                              setEditContent(comment.content);
                            }}
                          >
                            <Edit2 className="h-4 w-4" />
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="icon" 
                            className="h-8 w-8 text-destructive hover:text-destructive hover:bg-destructive/10"
                            onClick={() => handleDeleteComment(comment.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      )}
                    </div>
                    
                    {editingCommentId === comment.id ? (
                      <div className="pt-2 space-y-2">
                        <Textarea 
                          value={editContent}
                          onChange={(e) => setEditContent(e.target.value)}
                          className="min-h-[80px]"
                        />
                        <div className="flex gap-2 justify-end">
                          <Button 
                            variant="outline" 
                            size="sm" 
                            onClick={() => setEditingCommentId(null)}
                          >
                            Cancel
                          </Button>
                          <Button 
                            size="sm" 
                            onClick={() => handleUpdateComment(comment.id)}
                            disabled={!editContent.trim()}
                          >
                            Save
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <p className="text-sm pt-1 whitespace-pre-wrap">{comment.content}</p>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
        
        <Card>
          <CardContent className="p-4 sm:p-6">
            <form onSubmit={handleAddComment} className="space-y-4">
              <Textarea 
                placeholder="Leave a comment..." 
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                className="min-h-[100px]"
              />
              <div className="flex justify-end">
                <Button 
                  type="submit" 
                  disabled={!newComment.trim() || submitting}
                >
                  {submitting ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Posting...
                    </>
                  ) : (
                    'Comment'
                  )}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
        
      </div>
    </div>
  );
}
