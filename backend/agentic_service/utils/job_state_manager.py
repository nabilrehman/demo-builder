"""
Job State Manager - In-memory state management for provisioning jobs.

This module manages the state of provisioning jobs, including progress tracking,
logs, and artifacts. Uses in-memory storage for now (can be upgraded to database).
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Literal
from dataclasses import dataclass, field, asdict
import threading
import json

JobStatus = Literal["pending", "running", "completed", "failed", "cancelled"]
AgentPhase = Literal[
    "research", "demo_story", "data_modeling", "synthetic_data",
    "infrastructure", "capi_instruction", "validation"
]


@dataclass
class LogEntry:
    """Single log entry for a provisioning job."""
    timestamp: str
    phase: str
    level: str  # INFO, WARNING, ERROR
    message: str


@dataclass
class AgentProgress:
    """Progress tracking for individual agent."""
    name: str
    status: JobStatus
    progress_percentage: int
    elapsed_seconds: int
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class JobState:
    """Complete state of a provisioning job."""
    job_id: str
    customer_url: str
    status: JobStatus
    created_at: str
    updated_at: str
    current_phase: str = "pending"
    overall_progress: int = 0

    # Mode: "default" or "crazy_frog"
    mode: str = "default"
    crazy_frog_context: Optional[Dict[str, Any]] = None

    # Agent progress tracking
    agents: List[AgentProgress] = field(default_factory=list)

    # Logs
    logs: List[LogEntry] = field(default_factory=list)

    # Results
    dataset_id: Optional[str] = None
    dataset_full_name: Optional[str] = None
    capi_agent_id: Optional[str] = None
    demo_title: Optional[str] = None
    golden_queries: Optional[List[Dict]] = None
    schema: Optional[List[Dict]] = None
    metadata: Optional[Dict] = None

    # Errors
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class JobStateManager:
    """
    Manages state for all provisioning jobs.

    Thread-safe in-memory storage. Can be upgraded to database later.
    """

    def __init__(self):
        self._jobs: Dict[str, JobState] = {}
        self._lock = threading.RLock()
        self._subscribers: Dict[str, List[asyncio.Queue]] = {}

    def create_job(
        self,
        job_id: str,
        customer_url: str,
        mode: str = "default",
        crazy_frog_context: Optional[Dict] = None
    ) -> JobState:
        """Create a new provisioning job."""
        with self._lock:
            now = datetime.utcnow().isoformat()

            # Initialize 7 agents
            agent_names = [
                "Research Agent",
                "Demo Story Agent",
                "Data Modeling Agent",
                "Synthetic Data Generator",
                "Infrastructure Agent",
                "CAPI Instruction Generator",
                "Demo Validator"
            ]

            agents = [
                AgentProgress(
                    name=name,
                    status="pending",
                    progress_percentage=0,
                    elapsed_seconds=0
                )
                for name in agent_names
            ]

            job = JobState(
                job_id=job_id,
                customer_url=customer_url,
                status="pending",
                created_at=now,
                updated_at=now,
                mode=mode,
                crazy_frog_context=crazy_frog_context,
                agents=agents
            )

            self._jobs[job_id] = job
            self._subscribers[job_id] = []

            return job

    def get_job(self, job_id: str) -> Optional[JobState]:
        """Get job state by ID."""
        with self._lock:
            return self._jobs.get(job_id)

    def get_all_jobs(self, limit: int = 50) -> List[JobState]:
        """Get all jobs, sorted by most recent first."""
        with self._lock:
            jobs = sorted(
                self._jobs.values(),
                key=lambda j: j.created_at,
                reverse=True
            )
            return jobs[:limit]

    def update_job_status(self, job_id: str, status: JobStatus):
        """Update overall job status."""
        with self._lock:
            if job_id in self._jobs:
                self._jobs[job_id].status = status
                self._jobs[job_id].updated_at = datetime.utcnow().isoformat()
                self._notify_subscribers(job_id)

    def update_current_phase(self, job_id: str, phase: str):
        """Update current phase being executed."""
        with self._lock:
            if job_id in self._jobs:
                self._jobs[job_id].current_phase = phase
                self._jobs[job_id].updated_at = datetime.utcnow().isoformat()
                self._notify_subscribers(job_id)

    def update_agent_status(
        self,
        job_id: str,
        agent_index: int,
        status: JobStatus,
        progress: int = 0,
        error: Optional[str] = None
    ):
        """Update individual agent status."""
        with self._lock:
            if job_id not in self._jobs:
                return

            job = self._jobs[job_id]
            if 0 <= agent_index < len(job.agents):
                agent = job.agents[agent_index]
                agent.status = status
                agent.progress_percentage = progress

                if status == "running" and not agent.start_time:
                    agent.start_time = datetime.utcnow().isoformat()
                elif status in ["completed", "failed"]:
                    agent.end_time = datetime.utcnow().isoformat()
                    if agent.start_time:
                        start = datetime.fromisoformat(agent.start_time)
                        end = datetime.fromisoformat(agent.end_time)
                        agent.elapsed_seconds = int((end - start).total_seconds())

                if error:
                    agent.error_message = error

                # Calculate overall progress
                total_progress = sum(a.progress_percentage for a in job.agents)
                job.overall_progress = total_progress // len(job.agents)

                job.updated_at = datetime.utcnow().isoformat()
                self._notify_subscribers(job_id)

    def add_log(
        self,
        job_id: str,
        phase: str,
        message: str,
        level: str = "INFO"
    ):
        """Add a log entry to the job."""
        with self._lock:
            if job_id not in self._jobs:
                return

            log = LogEntry(
                timestamp=datetime.utcnow().isoformat(),
                phase=phase,
                level=level,
                message=message
            )

            self._jobs[job_id].logs.append(log)
            self._jobs[job_id].updated_at = datetime.utcnow().isoformat()
            self._notify_subscribers(job_id)

    def add_error(self, job_id: str, error: str):
        """Add an error to the job."""
        with self._lock:
            if job_id not in self._jobs:
                return

            self._jobs[job_id].errors.append(error)
            self._jobs[job_id].updated_at = datetime.utcnow().isoformat()
            self._notify_subscribers(job_id)

    def set_results(
        self,
        job_id: str,
        dataset_id: Optional[str] = None,
        dataset_full_name: Optional[str] = None,
        capi_agent_id: Optional[str] = None,
        demo_title: Optional[str] = None,
        golden_queries: Optional[List[Dict]] = None,
        schema: Optional[List[Dict]] = None,
        metadata: Optional[Dict] = None
    ):
        """Set final results for completed job."""
        with self._lock:
            if job_id not in self._jobs:
                return

            job = self._jobs[job_id]
            # FIX: Use 'is not None' instead of truthy check to allow empty strings/lists
            if dataset_id is not None:
                job.dataset_id = dataset_id
            if dataset_full_name is not None:
                job.dataset_full_name = dataset_full_name
            if capi_agent_id is not None:
                job.capi_agent_id = capi_agent_id
            if demo_title is not None:
                job.demo_title = demo_title
            if golden_queries is not None:
                job.golden_queries = golden_queries
            if schema is not None:
                job.schema = schema
            if metadata is not None:
                job.metadata = metadata

            job.updated_at = datetime.utcnow().isoformat()
            self._notify_subscribers(job_id)

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job."""
        with self._lock:
            if job_id not in self._jobs:
                return False

            job = self._jobs[job_id]
            if job.status == "running":
                job.status = "cancelled"
                job.updated_at = datetime.utcnow().isoformat()
                self.add_log(job_id, "system", "Job cancelled by user", "WARNING")
                self._notify_subscribers(job_id)
                return True

            return False

    # SSE Support

    async def subscribe(self, job_id: str) -> asyncio.Queue:
        """Subscribe to job updates (for SSE)."""
        queue = asyncio.Queue(maxsize=100)
        with self._lock:
            if job_id not in self._subscribers:
                self._subscribers[job_id] = []
            self._subscribers[job_id].append(queue)
        return queue

    def unsubscribe(self, job_id: str, queue: asyncio.Queue):
        """Unsubscribe from job updates."""
        with self._lock:
            if job_id in self._subscribers:
                try:
                    self._subscribers[job_id].remove(queue)
                except ValueError:
                    pass

    def _notify_subscribers(self, job_id: str):
        """Notify all subscribers of job update."""
        if job_id not in self._subscribers:
            return

        job = self._jobs.get(job_id)
        if not job:
            return

        # Put update in all queues (non-blocking)
        update = {
            "type": "update",
            "data": job.to_dict()
        }

        for queue in self._subscribers[job_id]:
            try:
                queue.put_nowait(update)
            except asyncio.QueueFull:
                # Skip if queue is full
                pass


# Global singleton instance
_job_manager = JobStateManager()


def get_job_manager() -> JobStateManager:
    """Get the global job state manager instance."""
    return _job_manager
