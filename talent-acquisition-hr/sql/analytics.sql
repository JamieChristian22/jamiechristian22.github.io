-- Run with: sqlite3 data/processed/talent_hr.sqlite < sql/analytics.sql
-- Query A: Stage funnel (reach, not mutually exclusive final disposition)
SELECT s.stage, COUNT(DISTINCT e.application_id) AS applicants_reaching_stage
FROM (SELECT 'Applied' stage, 1 ord UNION ALL SELECT 'Screened',2 UNION ALL
      SELECT 'Interview',3 UNION ALL SELECT 'Final',4 UNION ALL
      SELECT 'Offer',5 UNION ALL SELECT 'Hired',6) s
LEFT JOIN stage_events e ON e.stage = s.stage
GROUP BY s.stage, s.ord ORDER BY s.ord;

-- Query B: source-to-hire conversion, includes sources with zero hires
SELECT a.source, COUNT(*) AS applicants,
       SUM(CASE WHEN a.current_stage='Hired' THEN 1 ELSE 0 END) hires,
       ROUND(100.0*SUM(CASE WHEN a.current_stage='Hired' THEN 1 ELSE 0 END)/COUNT(*),2) hire_rate_pct
FROM applications a GROUP BY a.source ORDER BY hires DESC, applicants DESC;

-- Query C: time to fill on filled reqs ONLY (not on open/cancelled reqs)
SELECT department, COUNT(*) filled_req_count,
       ROUND(AVG(julianday(closed_at)-julianday(opened_at)),1) avg_days_to_fill
FROM requisitions WHERE status='Filled' GROUP BY department;

-- Query D: recruiting workload & open headcount by team
SELECT department, owner, COUNT(*) active_req_count,
       SUM(headcount_approved) headcount_open
FROM requisitions WHERE status='Open' GROUP BY department, owner ORDER BY active_req_count DESC;

-- Query E: HR ticket backlog and resolved within 5 calendar days
SELECT category,
       SUM(CASE WHEN status='Open' THEN 1 ELSE 0 END) open_cases,
       SUM(CASE WHEN status='Resolved' THEN 1 ELSE 0 END) resolved_cases,
       ROUND(100.0 * SUM(CASE WHEN status='Resolved' AND
           julianday(closed_at)-julianday(opened_at) <= 5 THEN 1 ELSE 0 END) /
           NULLIF(SUM(CASE WHEN status='Resolved' THEN 1 ELSE 0 END),0),1) closed_within_5d_pct
FROM hr_cases GROUP BY category ORDER BY open_cases DESC;

-- Query F: onboarding tasks by owner team
SELECT owner_team, COUNT(*) total_tasks,
       SUM(CASE WHEN status='Completed' THEN 1 ELSE 0 END) done,
       SUM(CASE WHEN status='Completed' AND completed_at <= due_at THEN 1 ELSE 0 END) done_on_time
FROM onboarding_tasks GROUP BY owner_team ORDER BY total_tasks DESC;
