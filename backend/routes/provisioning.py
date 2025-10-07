"""
Provisioning API Endpoints

Provides REST API for CE Dashboard to manage demo provisioning jobs.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List, Dict, Any, AsyncGenerator
import asyncio
import json
import uuid
import os
import logging
from datetime import datetime

from agentic_service.utils.job_state_manager import get_job_manager, JobState
from agentic_service.models.crazy_frog_request import CrazyFrogProvisioningRequest
from agentic_service.demo_orchestrator import run_demo_orchestrator

# Firebase auth middleware
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from middleware.auth import optional_google_user
from services.firestore_service import firestore_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/provision", tags=["provisioning"])

# Get job manager singleton
job_manager = get_job_manager()

# Track background tasks to prevent garbage collection
background_tasks = set()

# Job persistence directory
JOBS_DIR = "/tmp/jobs"
os.makedirs(JOBS_DIR, exist_ok=True)

def _persist_job_metadata(job_id: str, metadata: Dict[str, Any]) -> None:
    """Persist job metadata to file for recovery after server restart."""
    try:
        job_file = os.path.join(JOBS_DIR, f"{job_id}.json")
        with open(job_file, 'w') as f:
            json.dump({
                "job_id": job_id,
                "metadata": metadata,
                "persisted_at": datetime.utcnow().isoformat()
            }, f, indent=2)
        logger.info(f"✅ Persisted job metadata to {job_file}")
    except Exception as e:
        logger.error(f"Failed to persist job metadata: {e}")
        # Don't fail the whole job if persistence fails


# ============================================================================
# Request/Response Models
# ============================================================================

class StartProvisionRequest(BaseModel):
    """Request to start a new provisioning job (DEFAULT mode)."""
    customer_url: HttpUrl
    project_id: Optional[str] = None


class ProvisionResponse(BaseModel):
    """Response after starting a provisioning job."""
    job_id: str
    status: str
    message: str
    customer_url: str


class JobStatusResponse(BaseModel):
    """Current status of a provisioning job."""
    job_id: str
    customer_url: str
    company_name: Optional[str] = None
    status: str
    current_phase: str
    overall_progress: int
    mode: str
    created_at: str
    updated_at: str
    agents: List[Dict]
    recent_logs: List[Dict]
    errors: List[str]
    dataset_full_name: Optional[str] = None
    capi_agent_id: Optional[str] = None


class JobHistoryResponse(BaseModel):
    """List of provisioning jobs."""
    jobs: List[Dict]
    total: int


class DemoAssetsResponse(BaseModel):
    """Complete demo assets for a finished job."""
    job_id: str
    customer_url: str
    status: str
    demo_title: Optional[str]
    executive_summary: Optional[str]
    business_challenges: Optional[List[str]]
    talking_track: Optional[str]
    golden_queries: Optional[List[Dict]]
    schema: Optional[List[Dict]]
    metadata: Optional[Dict]
    provision_url: str
    total_time: Optional[str]


# ============================================================================
# Helper Functions
# ============================================================================

async def run_provisioning_workflow(
    job_id: str,
    customer_url: str,
    project_id: str,
    mode: str = "default",
    crazy_frog_context: Optional[Dict] = None,
    user_id: Optional[str] = None
):
    """
    Background task to run the provisioning workflow.

    This function runs the 7-agent orchestrator and updates job state.
    If user_id is provided, also saves to Firestore for persistence.
    """
    try:
        logger.info(f"Starting provisioning workflow for job {job_id}")

        # Update job status to running
        job_manager.update_job_status(job_id, "running")
        job_manager.add_log(
            job_id,
            "system",
            f"Starting {mode} mode provisioning for {customer_url}"
        )

        # Save initial job state to Firestore if user is authenticated
        if user_id:
            await firestore_service.save_job(user_id, job_id, {
                "customer_url": customer_url,
                "project_id": project_id,
                "mode": mode,
                "status": "running",
                "created_at": datetime.utcnow().isoformat()
            })

        # Run the orchestrator
        result = await run_demo_orchestrator(
            customer_url=customer_url,
            project_id=project_id,
            job_id=job_id,
            job_manager=job_manager,
            crazy_frog_context=crazy_frog_context
        )

        # DEBUG: Log what orchestrator returned
        logger.info(f"Orchestrator result status: {result.get('status')}")
        logger.info(f"Orchestrator result keys: {list(result.keys())}")
        logger.info(f"Has demo_title: {result.get('demo_title') is not None}")
        logger.info(f"Has golden_queries: {result.get('golden_queries') is not None}")
        logger.info(f"Has schema: {result.get('schema') is not None}")

        # Check if successful
        if result.get("status") == "completed":
            # Extract results from orchestrator
            metadata = result.get("metadata", {})
            logger.info(f"Calling set_results for job {job_id} with demo_title={result.get('demo_title')}")
            job_manager.set_results(
                job_id=job_id,
                dataset_id=result.get("dataset_id"),
                dataset_full_name=metadata.get("datasetFullName"),
                capi_agent_id=metadata.get("agentId"),
                demo_title=result.get("demo_title"),
                golden_queries=result.get("golden_queries"),
                schema=result.get("schema"),
                metadata=metadata
            )
            logger.info(f"✅ set_results completed for job {job_id}")

            # Persist job metadata to file for recovery after server restart
            _persist_job_metadata(job_id, metadata)

            job_manager.update_job_status(job_id, "completed")
            job_manager.add_log(
                job_id,
                "system",
                f"Provisioning completed successfully! Dataset: {result.get('dataset_id')}",
                "INFO"
            )

            # Save completed job to Firestore if user is authenticated
            if user_id:
                await firestore_service.update_job_status(user_id, job_id, "completed", metadata)

        else:
            # Failed
            error_msg = result.get("error", "Unknown error occurred")
            job_manager.add_error(job_id, error_msg)
            job_manager.update_job_status(job_id, "failed")
            job_manager.add_log(
                job_id,
                "system",
                f"Provisioning failed: {error_msg}",
                "ERROR"
            )

            # Save failed job to Firestore if user is authenticated
            if user_id:
                await firestore_service.update_job_status(user_id, job_id, "failed", {"error": error_msg})

    except Exception as e:
        logger.error(f"Provisioning workflow error for job {job_id}: {str(e)}", exc_info=True)
        job_manager.add_error(job_id, str(e))
        job_manager.update_job_status(job_id, "failed")
        job_manager.add_log(
            job_id,
            "system",
            f"Fatal error: {str(e)}",
            "ERROR"
        )

        # Save fatal error to Firestore if user is authenticated
        if user_id:
            await firestore_service.update_job_status(user_id, job_id, "failed", {"error": str(e)})


def calculate_total_time(job: JobState) -> Optional[str]:
    """Calculate total time from created_at to updated_at."""
    try:
        start = datetime.fromisoformat(job.created_at)
        end = datetime.fromisoformat(job.updated_at)
        delta = end - start

        minutes = int(delta.total_seconds() // 60)
        seconds = int(delta.total_seconds() % 60)

        return f"{minutes}m {seconds}s"
    except:
        return None


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/start", response_model=ProvisionResponse)
async def start_default_provision(
    request: StartProvisionRequest,
    user: Optional[dict] = Depends(optional_google_user)
):
    """
    Start a new provisioning job in DEFAULT mode.

    Only requires customer URL. Fully autonomous provisioning.

    Optional authentication: If user is signed in with @google.com,
    job will be saved to Firestore for persistence.
    """
    job_id = str(uuid.uuid4())
    customer_url = str(request.customer_url)
    project_id = request.project_id or os.getenv("DEVSHELL_PROJECT_ID") or "bq-demos-469816"

    # Extract user ID if authenticated
    user_id = user['uid'] if user else None
    if user:
        logger.info(f"Authenticated request from {user['email']} (uid: {user_id})")

    # Create job in state manager
    job_manager.create_job(
        job_id=job_id,
        customer_url=customer_url,
        mode="default"
    )

    # Create background task and keep strong reference to prevent garbage collection
    task = asyncio.create_task(run_provisioning_workflow(
        job_id=job_id,
        customer_url=customer_url,
        project_id=project_id,
        mode="default",
        crazy_frog_context=None,
        user_id=user_id
    ))

    # Done callback to log exceptions
    def task_done_callback(task):
        try:
            # This will raise if the task raised an exception
            task.result()
        except Exception as e:
            logger.error(f"Background task exception for job {job_id}: {e}", exc_info=True)
        finally:
            background_tasks.discard(task)

    # Add to tracking set to prevent garbage collection
    background_tasks.add(task)
    task.add_done_callback(task_done_callback)

    logger.info(f"Created provisioning job {job_id} for {customer_url}")

    return ProvisionResponse(
        job_id=job_id,
        status="pending",
        message="Provisioning workflow started",
        customer_url=customer_url
    )


@router.post("/crazy-frog", response_model=ProvisionResponse)
async def start_crazy_frog_provision(
    request: CrazyFrogProvisioningRequest,
    user: Optional[dict] = Depends(optional_google_user)
):
    """
    Start a new provisioning job in CRAZY FROG mode.

    Accepts detailed context for customized demo generation.

    Optional authentication: If user is signed in with @google.com,
    job will be saved to Firestore for persistence.
    """
    job_id = str(uuid.uuid4())
    customer_url = str(request.customer_url)
    project_id = request.project_id or os.getenv("DEVSHELL_PROJECT_ID") or "bq-demos-469816"

    # Extract user ID if authenticated
    user_id = user['uid'] if user else None
    if user:
        logger.info(f"Authenticated Crazy Frog request from {user['email']} (uid: {user_id})")

    # Extract crazy frog context
    crazy_frog_context = {
        "use_case_context": request.use_case_context,
        "industry_hint": request.industry_hint,
        "target_persona": request.target_persona,
        "demo_complexity": request.demo_complexity,
        "special_focus": request.special_focus,
        "integrations": request.integrations,
        "avoid_topics": request.avoid_topics
    }

    # Create job in state manager
    job_manager.create_job(
        job_id=job_id,
        customer_url=customer_url,
        mode="crazy_frog",
        crazy_frog_context=crazy_frog_context
    )

    # Create background task and keep strong reference to prevent garbage collection
    task = asyncio.create_task(run_provisioning_workflow(
        job_id=job_id,
        customer_url=customer_url,
        project_id=project_id,
        mode="crazy_frog",
        crazy_frog_context=crazy_frog_context,
        user_id=user_id
    ))

    # Done callback to log exceptions
    def task_done_callback(task):
        try:
            # This will raise if the task raised an exception
            task.result()
        except Exception as e:
            logger.error(f"Background task exception for job {job_id}: {e}", exc_info=True)
        finally:
            background_tasks.discard(task)

    # Add to tracking set to prevent garbage collection
    background_tasks.add(task)
    task.add_done_callback(task_done_callback)

    logger.info(f"Created Crazy Frog provisioning job {job_id} for {customer_url}")

    return ProvisionResponse(
        job_id=job_id,
        status="pending",
        message="Crazy Frog provisioning workflow started",
        customer_url=customer_url
    )


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_provision_status(
    job_id: str,
    user: Optional[dict] = Depends(optional_google_user)
):
    """
    Get current status of a provisioning job.

    If authenticated: Verifies user owns the job
    If not authenticated: Returns job from in-memory state (backwards compatibility)

    Returns job metadata, agent progress, recent logs, and errors.
    """
    # If user is authenticated, verify they own this job
    if user:
        user_id = user['uid']
        firestore_job = await firestore_service.get_job(user_id, job_id)

        if not firestore_job:
            raise HTTPException(
                status_code=404,
                detail=f"Job {job_id} not found for user {user['email']}"
            )

        # Job exists in Firestore for this user, now get current status from job_manager
        # (which has real-time progress updates)

    job = job_manager.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    # Get recent logs (last 20)
    recent_logs = [
        {
            "timestamp": log.timestamp,
            "phase": log.phase,
            "level": log.level,
            "message": log.message
        }
        for log in job.logs[-20:]
    ]

    # Format agents
    agents = [
        {
            "name": agent.name,
            "status": agent.status,
            "progress_percentage": agent.progress_percentage,
            "elapsed_seconds": agent.elapsed_seconds,
            "start_time": agent.start_time,
            "end_time": agent.end_time,
            "error_message": agent.error_message
        }
        for agent in job.agents
    ]

    return JobStatusResponse(
        job_id=job.job_id,
        customer_url=job.customer_url,
        company_name=job.company_name,
        status=job.status,
        current_phase=job.current_phase,
        overall_progress=job.overall_progress,
        mode=job.mode,
        created_at=job.created_at,
        updated_at=job.updated_at,
        agents=agents,
        recent_logs=recent_logs,
        errors=job.errors,
        dataset_full_name=getattr(job, 'dataset_full_name', None),
        capi_agent_id=getattr(job, 'capi_agent_id', None)
    )


@router.get("/metadata/{job_id}")
async def get_job_metadata(job_id: str):
    """
    Get persisted job metadata from file.

    This endpoint allows retrieving job metadata even after server restart,
    as long as the file still exists in /tmp/jobs/.
    """
    try:
        job_file = os.path.join(JOBS_DIR, f"{job_id}.json")

        if not os.path.exists(job_file):
            raise HTTPException(status_code=404, detail=f"Job metadata file not found for {job_id}")

        with open(job_file, 'r') as f:
            data = json.load(f)

        return {
            "job_id": data.get("job_id"),
            "metadata": data.get("metadata"),
            "persisted_at": data.get("persisted_at")
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading job metadata: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load job metadata: {str(e)}")


@router.get("/stream/{job_id}")
async def stream_provision_progress(job_id: str):
    """
    Stream real-time provisioning progress using Server-Sent Events (SSE).

    Frontend can connect to this endpoint to receive live updates.
    """
    job = job_manager.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events for job updates."""
        queue = await job_manager.subscribe(job_id)

        try:
            # Send initial state immediately
            current_job = job_manager.get_job(job_id)
            if current_job:
                yield f"data: {json.dumps(current_job.to_dict())}\n\n"

            # Stream updates
            while True:
                try:
                    # Wait for update with timeout
                    update = await asyncio.wait_for(queue.get(), timeout=30.0)

                    # Send update
                    yield f"data: {json.dumps(update['data'])}\n\n"

                    # Check if job is finished
                    if update['data']['status'] in ['completed', 'failed', 'cancelled']:
                        logger.info(f"Job {job_id} finished with status {update['data']['status']}")
                        break

                except asyncio.TimeoutError:
                    # Send heartbeat to keep connection alive
                    yield f": heartbeat\n\n"
                    continue

        except asyncio.CancelledError:
            logger.info(f"SSE stream cancelled for job {job_id}")
        finally:
            # Unsubscribe when client disconnects
            job_manager.unsubscribe(job_id, queue)
            logger.info(f"Client unsubscribed from job {job_id}")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


@router.get("/history", response_model=JobHistoryResponse)
async def get_provision_history(
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None,
    search: Optional[str] = None,
    user: Optional[dict] = Depends(optional_google_user)
):
    """
    Get list of provisioning jobs for the current user.

    If authenticated: Returns only user's jobs from Firestore with filtering
    If not authenticated: Returns all jobs from in-memory state (backwards compatibility)

    Query parameters:
    - limit: Max number of jobs to return (default: 50)
    - offset: Number of jobs to skip for pagination (default: 0)
    - status: Filter by status (all, completed, running, failed, pending)
    - search: Search in customer URL

    Returns most recent jobs first.
    """
    # If user is authenticated, return their jobs from Firestore
    if user:
        user_id = user['uid']
        logger.info(f"Fetching job history for user {user['email']} (limit={limit}, offset={offset}, status={status}, search={search})")

        firestore_jobs = await firestore_service.get_user_jobs(
            user_id,
            limit=limit,
            offset=offset,
            status=status,
            search=search
        )

        # Format Firestore jobs for response
        formatted_jobs = [
            {
                "job_id": job.get('id'),
                "customer_url": job.get('customer_url', ''),
                "status": job.get('status', 'unknown'),
                "mode": job.get('mode', 'default'),
                "current_phase": job.get('current_phase', ''),
                "overall_progress": job.get('overall_progress', 0),
                "created_at": job.get('created_at', ''),
                "updated_at": job.get('updated_at', ''),
                "dataset_id": job.get('metadata', {}).get('dataset_id'),
                "demo_title": job.get('metadata', {}).get('demo_title'),
                "total_time": None,  # Could calculate from timestamps
                "error_count": 0
            }
            for job in firestore_jobs
        ]

        return JobHistoryResponse(
            jobs=formatted_jobs,
            total=len(formatted_jobs)
        )

    # If not authenticated, fall back to in-memory jobs (for backwards compatibility)
    logger.info("Fetching job history from in-memory state (unauthenticated)")
    jobs = job_manager.get_all_jobs(limit=limit)

    # Format jobs for response
    formatted_jobs = [
        {
            "job_id": job.job_id,
            "customer_url": job.customer_url,
            "status": job.status,
            "mode": job.mode,
            "current_phase": job.current_phase,
            "overall_progress": job.overall_progress,
            "created_at": job.created_at,
            "updated_at": job.updated_at,
            "dataset_id": job.dataset_id,
            "demo_title": job.demo_title,
            "total_time": calculate_total_time(job),
            "error_count": len(job.errors)
        }
        for job in jobs
    ]

    return JobHistoryResponse(
        jobs=formatted_jobs,
        total=len(formatted_jobs)
    )


@router.get("/assets/{job_id}", response_model=DemoAssetsResponse)
async def get_demo_assets(
    job_id: str,
    user: Optional[dict] = Depends(optional_google_user)
):
    """
    Get complete demo assets for a finished provisioning job.

    If authenticated: Verifies user owns the job
    If not authenticated: Returns job from in-memory state (backwards compatibility)

    This endpoint provides all data needed for the Demo Assets Viewer.
    """
    try:
        logger.info(f"Getting demo assets for job {job_id}")

        # If user is authenticated, verify they own this job
        if user:
            user_id = user['uid']
            firestore_job = await firestore_service.get_job(user_id, job_id)

            if not firestore_job:
                raise HTTPException(
                    status_code=404,
                    detail=f"Job {job_id} not found for user {user['email']}"
                )

        job = job_manager.get_job(job_id)

        if not job:
            logger.error(f"Job {job_id} not found")
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

        logger.info(f"Job found: status={job.status}, has demo_title={job.demo_title is not None}, has golden_queries={job.golden_queries is not None}")

        if job.status not in ["completed"]:
            raise HTTPException(
                status_code=400,
                detail=f"Job {job_id} is not completed (status: {job.status})"
            )

        # Calculate total time
        total_time = calculate_total_time(job)

        # Extract executive summary and business challenges from demo story
        executive_summary = None
        business_challenges = None
        talking_track = None

        if job.golden_queries and len(job.golden_queries) > 0:
            # These would come from demo story agent results
            # For now, we'll extract from metadata if available
            if job.metadata:
                executive_summary = job.metadata.get("executive_summary")

                # FIX: Convert business_challenges from list of dicts to list of strings
                bc_raw = job.metadata.get("business_challenges")
                if bc_raw and isinstance(bc_raw, list):
                    business_challenges = [
                        item.get("challenge", str(item)) if isinstance(item, dict) else str(item)
                        for item in bc_raw
                    ]
                else:
                    business_challenges = bc_raw

                # FIX: Convert talking_track from dict to formatted string
                tt_raw = job.metadata.get("talking_track")
                if tt_raw and isinstance(tt_raw, dict):
                    # Format dict as readable text
                    parts = []
                    for key, value in tt_raw.items():
                        parts.append(f"{key.replace('_', ' ').title()}: {value}")
                    talking_track = "\n\n".join(parts)
                else:
                    talking_track = tt_raw

        # Enrich golden queries with CAPI validation status
        enriched_golden_queries = []
        if job.golden_queries:
            validation_results = job.metadata.get("validation_results", {}) if job.metadata else {}
            sql_results = validation_results.get("sql_results", [])  # Actually CAPI results now

            for query in job.golden_queries:
                enriched_query = query.copy()

                # Find matching validation result by sequence
                seq = query.get("sequence", 0)
                validation = next((r for r in sql_results if r.get("sequence") == seq), None)

                if validation:
                    # We're doing CAPI-only validation now
                    enriched_query["capi_tested"] = True
                    enriched_query["capi_passed"] = validation.get("capi_success", False)
                    enriched_query["capi_error"] = validation.get("capi_error")
                    enriched_query["capi_response_preview"] = validation.get("capi_response", "")[:200]
                    # No SQL validation anymore
                    enriched_query["sql_tested"] = False
                    enriched_query["sql_passed"] = False
                else:
                    enriched_query["capi_tested"] = False
                    enriched_query["sql_tested"] = False

                enriched_golden_queries.append(enriched_query)

        logger.info(f"Returning demo assets response")
        return DemoAssetsResponse(
            job_id=job.job_id,
            customer_url=job.customer_url,
            status=job.status,
            demo_title=job.demo_title,
            executive_summary=executive_summary,
            business_challenges=business_challenges,
            talking_track=talking_track,
            golden_queries=enriched_golden_queries if enriched_golden_queries else job.golden_queries,
            schema=job.schema,
            metadata=job.metadata,
            provision_url=job.customer_url,
            total_time=total_time
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting demo assets for job {job_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/cancel/{job_id}")
async def cancel_provision(job_id: str):
    """
    Cancel a running provisioning job.

    Returns success if cancelled, error if job is not running.
    """
    job = job_manager.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    success = job_manager.cancel_job(job_id)

    if not success:
        raise HTTPException(
            status_code=400,
            detail=f"Job {job_id} cannot be cancelled (status: {job.status})"
        )

    return {
        "job_id": job_id,
        "status": "cancelled",
        "message": "Job cancelled successfully"
    }


@router.get("/download-yaml/{job_id}")
async def download_capi_yaml(job_id: str):
    """
    Download CAPI instructions YAML for a completed job.

    Returns YAML file for manual CAPI agent creation.
    """
    job = job_manager.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    if job.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job {job_id} is not completed"
        )

    # Get YAML file path from metadata
    if not job.metadata or "yaml_file_path" not in job.metadata:
        raise HTTPException(
            status_code=404,
            detail="YAML file not found for this job"
        )

    yaml_path = job.metadata["yaml_file_path"]

    # Read YAML file
    try:
        with open(yaml_path, "r") as f:
            yaml_content = f.read()

        # Return as downloadable file
        from fastapi.responses import Response

        filename = f"capi_instructions_{job.dataset_id}.yaml"

        return Response(
            content=yaml_content,
            media_type="application/x-yaml",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="YAML file not found on server"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading YAML file: {str(e)}"
        )
