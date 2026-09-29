 
'use client';

import * as React from 'react';
import { useRouter } from 'next/navigation';
import { Search, Loader2 } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command';
import { api } from '@/lib/api';
import { useDebounce } from '@/hooks/use-debounce';

interface SearchResult {
  id: string;
  type: 'project' | 'task' | 'user';
  title: string;
  description?: string;
  url: string;
}

interface SearchResponse {
  query: string;
  results: SearchResult[];
  total: number;
}

export function GlobalSearch() {
  const [open, setOpen] = React.useState(false);
  const [search, setSearch] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const [results, setResults] = React.useState<SearchResult[]>([]);
  const router = useRouter();
  const { activeOrg } = useAuth();
  
  const debouncedSearch = useDebounce(search, 300);

  React.useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((open) => !open);
      }
    };

    document.addEventListener('keydown', down);
    return () => document.removeEventListener('keydown', down);
  }, []);

  React.useEffect(() => {
    async function performSearch() {
      if (!debouncedSearch || debouncedSearch.length < 2 || !activeOrg) {
        setResults([]);
        return;
      }

      setLoading(true);
      try {
        const res = await api.get<SearchResponse>(
          `/api/v1/search?q=${encodeURIComponent(debouncedSearch)}`,
          { headers: { 'X-Organization-Slug': activeOrg.slug } }
        );
        setResults(res.data.results);
      } catch (error) {
        console.error('Search error', error);
        setResults([]);
      } finally {
        setLoading(false);
      }
    }

    performSearch();
  }, [debouncedSearch, activeOrg]);

  const runCommand = React.useCallback((command: () => unknown) => {
    setOpen(false);
    command();
  }, []);

  const projects = results.filter((r) => r.type === 'project');
  const tasks = results.filter((r) => r.type === 'task');
  const users = results.filter((r) => r.type === 'user');

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="flex items-center gap-2 px-3 py-1.5 text-sm text-muted-foreground bg-muted/50 hover:bg-muted rounded-md transition-colors w-full md:w-64"
      >
        <Search className="w-4 h-4" />
        <span>Search...</span>
        <kbd className="ml-auto pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground opacity-100">
          <span className="text-xs">⌘</span>K
        </kbd>
      </button>

      <CommandDialog open={open} onOpenChange={setOpen}>
        <CommandInput
          placeholder="Type a command or search..."
          value={search}
          onValueChange={setSearch}
        />
        <CommandList>
          <CommandEmpty>
            {loading ? (
              <div className="flex items-center justify-center p-4">
                <Loader2 className="w-4 h-4 animate-spin mr-2" />
                <span>Searching...</span>
              </div>
            ) : (
              'No results found.'
            )}
          </CommandEmpty>

          {projects.length > 0 && (
            <CommandGroup heading="Projects">
              {projects.map((project) => (
                <CommandItem
                  key={project.id}
                  value={project.id}
                  onSelect={() => runCommand(() => router.push(project.url))}
                >
                  <div className="flex flex-col">
                    <span>{project.title}</span>
                    {project.description && (
                      <span className="text-xs text-muted-foreground line-clamp-1">
                        {project.description}
                      </span>
                    )}
                  </div>
                </CommandItem>
              ))}
            </CommandGroup>
          )}

          {tasks.length > 0 && (
            <CommandGroup heading="Tasks">
              {tasks.map((task) => (
                <CommandItem
                  key={task.id}
                  value={task.id}
                  onSelect={() => runCommand(() => router.push(task.url))}
                >
                  <div className="flex flex-col">
                    <span>{task.title}</span>
                    {task.description && (
                      <span className="text-xs text-muted-foreground line-clamp-1">
                        {task.description}
                      </span>
                    )}
                  </div>
                </CommandItem>
              ))}
            </CommandGroup>
          )}

          {users.length > 0 && (
            <CommandGroup heading="Users">
              {users.map((user) => (
                <CommandItem
                  key={user.id}
                  value={user.id}
                  onSelect={() => runCommand(() => router.push(user.url))}
                >
                  <div className="flex flex-col">
                    <span>{user.title}</span>
                    {user.description && (
                      <span className="text-xs text-muted-foreground line-clamp-1">
                        {user.description}
                      </span>
                    )}
                  </div>
                </CommandItem>
              ))}
            </CommandGroup>
          )}
        </CommandList>
      </CommandDialog>
    </>
  );
}
