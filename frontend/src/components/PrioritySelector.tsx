import { Button } from "./ui/Button";
import type { TrackingPriority } from "../types";

interface PrioritySelectorProps {
  value: TrackingPriority | null;
  onChange: (value: TrackingPriority | null) => void;
}

export function PrioritySelector({ value, onChange }: PrioritySelectorProps) {
  const priorities: { value: TrackingPriority; label: string }[] = [
    { value: "low", label: "Low" },
    { value: "mid", label: "Mid" },
    { value: "high", label: "High" },
  ];

  return (
    <div className="flex gap-2">
      {priorities.map((p) => (
        <Button
          key={p.value}
          type="button"
          variant={value === p.value ? "default" : "outline"}
          size="sm"
          onClick={() => onChange(value === p.value ? null : p.value)}
        >
          {p.label}
        </Button>
      ))}
    </div>
  );
}
