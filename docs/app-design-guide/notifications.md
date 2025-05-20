# Notifications

## Introduction

Notifications are one of the primary ways your application communicates with users. They let users know when something important has happened, guide them to take action, or confirm that their actions were successful.

In web apps, notifications can come in many forms: toast messages, banners, modals, email alerts, and badges. Well-designed notifications improve user experience by keeping people informed without overwhelming or distracting them.

This guide will help you design clear, timely, and non-intrusive notifications that support your app's goals and your users’ needs.

## Why It Matters

Notifications are essential for:
- Confirming user actions (e.g., “Profile updated”)
- Prompting time-sensitive decisions (e.g., “Your session is about to expire”)
- Alerting users to issues (e.g., “Connection lost”)
- Keeping users informed of updates (e.g., “You have new messages”)

Done well, they create confidence, reduce confusion, and drive engagement. Done poorly, they interrupt, annoy, or get ignored.

## Key Principles

### Relevance
Only show notifications that matter to the user in the context they’re in. Irrelevant alerts are noise.

### Clarity
Notifications should be easy to read and understand. Use plain, direct language with a clear purpose and call to action if needed.

### Timeliness
Show notifications at the right moment. Don’t delay confirmations or surface alerts too late for the user to act on them.

### Non-blocking by Default
Unless absolutely necessary, notifications should not interrupt user flow. Use non-blocking formats like toast messages or badges.

### Visual Hierarchy
Use visual design (color, size, icon) to signal the importance and type of the message:
- Green for success
- Yellow/orange for warnings
- Red for errors
- Neutral or blue for info

### User Control
Allow users to dismiss, snooze, or configure notification settings where appropriate. Don’t trap them in modals or overload them with repeat alerts.

### Accessibility
Ensure notifications are accessible:
- Announce them via ARIA live regions
- Provide sufficient contrast
- Avoid using color as the only signal

## Best Practices

### Toast Notifications

Use for short, ephemeral messages like:
- “Changes saved”
- “Item added to cart”

**Guidelines:**
- Auto-dismiss after 3–5 seconds
- Allow manual dismissal
- Keep them short and actionable
- Avoid stacking more than 2–3 at once

### Banners

Use for persistent, page-wide alerts:
- System errors
- Warnings that require user attention
- Announcements or outages

**Guidelines:**
- Place at the top of the content area
- Use clear icons and strong contrast
- Allow dismissing or resolving when possible

### Inline Messages

Use for contextual feedback:
- Form validation errors
- Field-specific instructions
- Status within a component (e.g., “Syncing...”)

**Guidelines:**
- Place near the related UI element
- Use concise language
- Align with field layout and spacing

### Badges

Use for status indicators:
- New message counts
- Pending tasks

**Guidelines:**
- Keep counts accurate and up to date
- Avoid large or flashing elements
- Provide meaningful hover tooltips

### Modals

Use only when user action is required before proceeding:
- Confirming destructive actions
- Accepting terms or permissions

**Guidelines:**
- Avoid using modals for passive alerts
- Always provide a clear exit or “Cancel” option

### Emails and Push Notifications

Use for updates when users are not active in the app:
- Weekly digests
- Security alerts
- Workflow approvals

**Guidelines:**
- Let users manage preferences
- Group updates where possible
- Avoid sending too frequently

## Examples

### Good

**"Item deleted" toast**  
Appears instantly after action, confirms result, and auto-dismisses.

**Form field error**  
Inline message under the field: “Password must be at least 8 characters.”

**Top banner for downtime**  
“Some features may be temporarily unavailable due to maintenance” with a link to status page.

### Bad

**Multiple stacked toasts**  
Covering important UI and not dismissing properly.

**Ambiguous alert**  
“Something went wrong” – doesn’t say what, where, or what to do next.

**Unclear badge**  
Badge with a number but no label or tooltip – user has no idea what it’s for.

## Collaboration Tips

- Designers and engineers should define consistent notification styles and components as part of the design system.
- Product managers should clarify which events should trigger notifications and when.
- Content designers should review wording for tone, clarity, and usefulness.
- QA should test notifications for timing, behavior, and accessibility (especially ARIA live announcements and screen reader compatibility).

## Conclusion

Notifications are a powerful way to keep users informed and engaged — but they should be used thoughtfully. Focus on clarity, timing, and relevance. Make them helpful, not annoying.

Design them as part of the user journey, not an afterthought.