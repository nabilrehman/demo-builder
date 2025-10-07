# 📊 User Management Features - Implementation Plan

## Overview
Add comprehensive user management features for CE (Customer Engineer) workflow optimization.

---

## 🎯 Feature List

### Phase 1: User Dashboard & Stats (30 min)
**Features:**
- [ ] User stats widget (total jobs, success rate, avg time)
- [ ] Recent activity timeline
- [ ] Quick actions (create job, view all, settings)
- [ ] Welcome message with user name

**Backend:**
- [ ] GET `/api/user/stats` - Returns user statistics
- [ ] Aggregate data from Firestore jobs

**Frontend:**
- [ ] `UserStatsCard` component
- [ ] `RecentActivity` component
- [ ] Update CEDashboard layout

---

### Phase 2: Job Management (45 min)
**Features:**
- [ ] Filter jobs by status (all, running, completed, failed)
- [ ] Search jobs by customer URL or title
- [ ] Sort by date, status, or duration
- [ ] Delete individual jobs
- [ ] Bulk actions (delete multiple)
- [ ] Pin important jobs

**Backend:**
- [ ] GET `/api/user/jobs?status=completed&search=nike&limit=20&offset=0`
- [ ] DELETE `/api/user/jobs/{job_id}`
- [ ] PATCH `/api/user/jobs/{job_id}` - Update job (pin/unpin)

**Frontend:**
- [ ] Job filter controls
- [ ] Search bar
- [ ] Sort dropdown
- [ ] Delete confirmation modal
- [ ] Pin/unpin button

---

### Phase 3: Pagination & Performance (20 min)
**Features:**
- [ ] Paginated job list (20 jobs per page)
- [ ] Load more button
- [ ] Infinite scroll (optional)
- [ ] Loading states

**Backend:**
- [ ] Add pagination to Firestore queries
- [ ] Cursor-based pagination for performance

**Frontend:**
- [ ] Pagination component
- [ ] Page navigation
- [ ] Loading skeletons

---

### Phase 4: User Profile & Settings (30 min)
**Features:**
- [ ] User profile page
- [ ] Display name & email
- [ ] Account creation date
- [ ] Preferences:
  - Default provision mode
  - Email notifications
  - Job retention period
- [ ] Change preferences

**Backend:**
- [ ] GET `/api/user/profile`
- [ ] PATCH `/api/user/profile` - Update preferences
- [ ] Store preferences in Firestore: `users/{uid}/profile`

**Frontend:**
- [ ] Profile page route
- [ ] Profile form
- [ ] Settings sections

---

### Phase 5: Advanced Features (Optional)
**Features:**
- [ ] Export job history (CSV/JSON)
- [ ] Share jobs with team members
- [ ] Job templates (save common configs)
- [ ] Analytics dashboard (charts, trends)
- [ ] Keyboard shortcuts

---

## 🏗️ Implementation Order

**Now (Phase 1 - Stats):**
1. Create backend endpoint for user stats
2. Create UserStatsCard component
3. Update dashboard to show stats
4. Test with real user

**Next (Phase 2 - Job Management):**
1. Add filtering backend logic
2. Create filter UI components
3. Implement delete functionality
4. Test all filters

**Then (Phase 3 - Pagination):**
1. Add pagination to backend
2. Create pagination UI
3. Test with 50+ jobs

**Finally (Phase 4 - Profile):**
1. Create profile endpoint
2. Build profile page
3. Add settings

---

## 📐 Architecture

### Backend Structure
```
backend/routes/
  user_management.py       # New file
    - GET  /api/user/stats
    - GET  /api/user/jobs (with filters)
    - DELETE /api/user/jobs/{job_id}
    - PATCH /api/user/jobs/{job_id}
    - GET  /api/user/profile
    - PATCH /api/user/profile

backend/services/
  user_service.py          # New file
    - calculate_user_stats()
    - get_filtered_jobs()
    - delete_user_job()
    - update_job_metadata()
```

### Frontend Structure
```
src/components/
  UserStatsCard.tsx        # Stats widget
  JobFilters.tsx           # Filter controls
  JobSearchBar.tsx         # Search input
  DeleteJobModal.tsx       # Confirmation modal
  Pagination.tsx           # Page navigation

src/pages/
  UserProfile.tsx          # Profile page
  JobHistory.tsx           # Full job list (optional)
```

### Firestore Structure
```
users/{userId}/
  jobs/{jobId}/
    (existing fields...)
    is_pinned: boolean
    tags: array

  profile/
    display_name: string
    preferences:
      default_mode: "default" | "crazy_frog"
      email_notifications: boolean
      retention_days: number
    created_at: timestamp
    updated_at: timestamp
```

---

## 🎨 UI Mockup (Text)

```
┌──────────────────────────────────────────────────────────┐
│  CE Dashboard                            👤 alice@google │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │ Total Jobs  │ │ Success Rate│ │ Avg Time    │       │
│  │     24      │ │    87.5%    │ │   4m 32s    │       │
│  └─────────────┘ └─────────────┘ └─────────────┘       │
│                                                           │
│  Recent Activity:                                        │
│  🟢 Completed: Nike demo (2 min ago)                    │
│  🔵 Running: Adidas demo (5 min ago)                    │
│  🔴 Failed: Puma demo (1 hour ago)                      │
│                                                           │
├──────────────────────────────────────────────────────────┤
│  Your Recent Provisions                                  │
│  ┌────────────────────────────────────────────────────┐ │
│  │ 🔍 Search: [nike          ] 📊 Filter: [All ▼]   │ │
│  └────────────────────────────────────────────────────┘ │
│                                                           │
│  ┌────────────────────────────────────────────────────┐ │
│  │ ⭐ Nike.com        ✅ Complete  4m 23s  [Delete] │ │
│  │ Adidas.com        🔄 Running   2m 10s  [Delete]   │ │
│  │ Puma.com          ❌ Failed    1m 05s  [Delete]   │ │
│  └────────────────────────────────────────────────────┘ │
│                                                           │
│  [← Prev]  Page 1 of 3  [Next →]                        │
└──────────────────────────────────────────────────────────┘
```

---

## 🧪 Testing Plan

### Test 1: User Stats Calculation
```python
# Create test jobs
create_job(status="completed")
create_job(status="completed")
create_job(status="failed")
create_job(status="running")

# Call stats endpoint
stats = get_user_stats(user_id)

assert stats["total_jobs"] == 4
assert stats["completed_jobs"] == 2
assert stats["success_rate"] == 50.0
```

### Test 2: Job Filtering
```python
# Filter by status
jobs = get_filtered_jobs(user_id, status="completed")
assert all(j["status"] == "completed" for j in jobs)

# Search by URL
jobs = get_filtered_jobs(user_id, search="nike")
assert all("nike" in j["customer_url"].lower() for j in jobs)
```

### Test 3: Job Deletion
```python
# Delete job
delete_user_job(user_id, job_id)

# Verify deleted
job = get_job(user_id, job_id)
assert job is None
```

### Test 4: Pagination
```python
# Create 50 jobs
for i in range(50):
    create_job(f"https://customer{i}.com")

# Get page 1
jobs_p1 = get_filtered_jobs(user_id, limit=20, offset=0)
assert len(jobs_p1) == 20

# Get page 2
jobs_p2 = get_filtered_jobs(user_id, limit=20, offset=20)
assert len(jobs_p2) == 20
assert jobs_p1[0]["job_id"] != jobs_p2[0]["job_id"]
```

---

## 🚀 Let's Start: Phase 1 - User Stats

**I'll implement:**
1. Backend endpoint for user stats
2. Frontend stats component
3. Update dashboard
4. Test with your deployed app

**Time:** 30 minutes
**Files to create/modify:**
- `backend/routes/user_management.py` (new)
- `backend/services/user_service.py` (new)
- `newfrontend/.../components/UserStatsCard.tsx` (new)
- `newfrontend/.../pages/CEDashboard.tsx` (update)

Ready to start? 🚀
