import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ExternalLink, MoreVertical, CheckCircle2, XCircle, Clock } from "lucide-react";
import { cn } from "@/lib/utils";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface ProvisionJob {
  id: string;
  url: string;
  status: "complete" | "failed" | "running";
  duration: string;
  date: string;
  mode: "default" | "advanced";
}

interface JobHistoryTableProps {
  jobs: ProvisionJob[];
}

const StatusBadge = ({ status }: { status: ProvisionJob["status"] }) => {
  const variants = {
    complete: {
      icon: <CheckCircle2 className="h-3 w-3" />,
      className: "bg-green-500/10 text-green-700 dark:text-green-400 border-green-500/20",
      label: "Complete"
    },
    failed: {
      icon: <XCircle className="h-3 w-3" />,
      className: "bg-red-500/10 text-red-700 dark:text-red-400 border-red-500/20",
      label: "Failed"
    },
    running: {
      icon: <Clock className="h-3 w-3 animate-pulse" />,
      className: "bg-blue-500/10 text-blue-700 dark:text-blue-400 border-blue-500/20",
      label: "Running"
    }
  };

  const variant = variants[status];

  return (
    <Badge variant="outline" className={cn("gap-1.5 font-medium", variant.className)}>
      {variant.icon}
      {variant.label}
    </Badge>
  );
};

export const JobHistoryTable = ({ jobs }: JobHistoryTableProps) => {
  const handleViewDetails = (jobId: string) => {
    console.log("View details for job:", jobId);
    // TODO: Navigate to job details page or open modal
  };

  const handleRetry = (jobId: string) => {
    console.log("Retry job:", jobId);
    // TODO: Implement retry logic
  };

  const handleDelete = (jobId: string) => {
    console.log("Delete job:", jobId);
    // TODO: Implement delete logic
  };

  return (
    <div className="rounded-lg border bg-card shadow-sm overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow className="hover:bg-muted/50">
            <TableHead className="font-semibold">URL</TableHead>
            <TableHead className="font-semibold">Status</TableHead>
            <TableHead className="font-semibold">Mode</TableHead>
            <TableHead className="font-semibold">Duration</TableHead>
            <TableHead className="font-semibold">Date</TableHead>
            <TableHead className="text-right font-semibold">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {jobs.map((job) => (
            <TableRow
              key={job.id}
              className="cursor-pointer hover:bg-muted/30 transition-colors"
              onClick={() => handleViewDetails(job.id)}
            >
              <TableCell className="font-medium">
                <div className="flex items-center gap-2">
                  <ExternalLink className="h-3.5 w-3.5 text-muted-foreground" />
                  <span className="truncate max-w-[200px]">{job.url}</span>
                </div>
              </TableCell>
              <TableCell>
                <StatusBadge status={job.status} />
              </TableCell>
              <TableCell>
                <Badge
                  variant={job.mode === "advanced" ? "default" : "secondary"}
                  className={cn(
                    "capitalize font-medium",
                    job.mode === "advanced" && "bg-gradient-button"
                  )}
                >
                  {job.mode}
                </Badge>
              </TableCell>
              <TableCell className="text-muted-foreground">
                {job.duration}
              </TableCell>
              <TableCell className="text-muted-foreground">
                {job.date}
              </TableCell>
              <TableCell className="text-right">
                <DropdownMenu>
                  <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                    <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                      <MoreVertical className="h-4 w-4" />
                      <span className="sr-only">Open menu</span>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={(e) => {
                      e.stopPropagation();
                      handleViewDetails(job.id);
                    }}>
                      View Details
                    </DropdownMenuItem>
                    {job.status === "failed" && (
                      <DropdownMenuItem onClick={(e) => {
                        e.stopPropagation();
                        handleRetry(job.id);
                      }}>
                        Retry
                      </DropdownMenuItem>
                    )}
                    <DropdownMenuItem
                      className="text-destructive focus:text-destructive"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(job.id);
                      }}
                    >
                      Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
};
