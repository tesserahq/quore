# Bug Report: 3 Critical Issues Found in Codebase

## Bug #1: Authorization Bypass in Direct Credential Access (SECURITY VULNERABILITY)

### Location
`app/routers/credential.py` - Lines 52-64 in `get_credential_direct` function

### Description
The `get_credential_direct` function retrieves a credential by ID but **does not verify that the current user has access to the workspace** containing that credential. This allows any authenticated user to access credentials from any workspace, including those they don't belong to.

### Security Impact
- **HIGH SEVERITY**: Users can access sensitive credentials from workspaces they don't have permission to access
- Potential data breach and unauthorized access to third-party services
- Violates principle of least privilege

### Current Vulnerable Code
```python
def get_credential_direct(
    credential_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> Credential:
    """Get a credential directly by ID, checking user permissions."""
    logger.info(f"Getting credential {credential_id} for user {current_user.id}")

    credential_service = CredentialService(db)
    credential = credential_service.get_credential(credential_id)
    if credential is None:
        logger.warning(f"Credential {credential_id} not found")
        raise HTTPException(status_code=404, detail="Credential not found")

    return credential  # ❌ NO PERMISSION CHECK!
```

### Fix Applied
Added proper authorization check to verify user has access to the workspace containing the credential.

---

## Bug #2: Array Index Out of Bounds Error in User Onboarding (RUNTIME ERROR)

### Location
`app/utils/auth.py` - Lines 122-125 in `handle_user_onboarding` function

### Description
The code assumes that a user's name will always contain at least 2 space-separated parts (first and last name), but this assumption can fail when:
- Name is a single word (e.g., "Madonna", "Cher")
- Name contains multiple spaces or unusual formatting
- Name is empty or None

### Impact
- **MEDIUM SEVERITY**: Application crashes during user onboarding
- Prevents legitimate users from accessing the system
- Poor user experience for users with non-standard names

### Current Vulnerable Code
```python
name = userinfo.get("name", "Unkown Unkown").split(" ")
first_name = name[0]
last_name = name[1]  # ❌ IndexError if name has only 1 part!
```

### Fix Applied
Added safe name parsing with proper fallbacks and bounds checking.

---

## Bug #3: Database Session Resource Leak in Middleware (PERFORMANCE ISSUE)

### Location
`app/middleware/db_session.py` - Lines 7-13

### Description
The database session middleware creates a new session for every request but doesn't handle exceptions properly. If an exception occurs during request processing, the session might not be properly closed, leading to:
- Database connection pool exhaustion
- Memory leaks
- Degraded application performance over time

### Impact
- **MEDIUM SEVERITY**: Performance degradation and potential service outages
- Database connection pool exhaustion under high load
- Memory leaks that accumulate over time

### Current Vulnerable Code
```python
async def dispatch(self, request, call_next):
    request.state.db_session = SessionLocal()
    try:
        response = await call_next(request)
    finally:
        request.state.db_session.close()  # ❌ Might not execute if exception in try block
    return response
```

### Fix Applied
Improved exception handling and added proper session cleanup with rollback on errors.

---

## Summary

These bugs represent critical security, runtime stability, and performance issues that could significantly impact the application's reliability and security posture. All fixes have been applied with proper error handling and security checks.