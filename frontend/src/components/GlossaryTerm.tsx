import * as Popover from '@radix-ui/react-popover';

interface GlossaryTermProps {
  term: string;
  definition: string;
  children: React.ReactNode;
}

export function GlossaryTerm({ term, definition, children }: GlossaryTermProps) {
  return (
    <Popover.Root>
      <Popover.Trigger asChild>
        <button 
          className="underline decoration-dotted underline-offset-4 decoration-brand/50 hover:decoration-brand focus:outline-none focus:ring-2 focus:ring-focus rounded px-0.5"
          aria-haspopup="dialog"
          aria-expanded={false}
        >
          {children}
        </button>
      </Popover.Trigger>
      <Popover.Portal>
        <Popover.Content 
          className="w-64 rounded bg-white p-4 shadow-md border border-gray-200 focus:outline-none focus:ring-2 focus:ring-focus z-50 text-sm"
          sideOffset={5}
        >
          <div className="font-bold mb-1">{term}</div>
          <p className="text-gray-700">{definition}</p>
          <Popover.Arrow className="fill-white" />
        </Popover.Content>
      </Popover.Portal>
    </Popover.Root>
  );
}
