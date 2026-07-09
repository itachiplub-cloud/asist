from database import Database
from utils.logger import logger

db = Database()


async def create_ticket(user_id: int, issue: str, priority: str = "normal") -> dict:
    ticket = await db.create_ticket(user_id, issue, priority)
    logger.info(f"Ticket created by {user_id}: {issue[:50]}")
    return ticket


async def close_ticket(ticket_id) -> bool:
    success = await db.close_ticket(ticket_id)
    if success:
        logger.info(f"Ticket {ticket_id} closed")
    return success


async def assign_ticket(ticket_id, sudo_id: int) -> None:
    await db.assign_ticket(ticket_id, sudo_id)
    logger.info(f"Ticket {ticket_id} assigned to {sudo_id}")


async def get_tickets_summary(status: str = None) -> str:
    tickets = await db.get_tickets(status)
    if not tickets:
        return "No tickets found."

    lines = "🎟️ **Tickets**\n\n"
    for t in tickets:
        ts = str(t.get("_id"))[-8:]
        uid = t.get("user_id", "?")
        priority = t.get("priority", "normal")
        status_icon = "🟢" if t.get("status") == "open" else "🔴"
        assigned = f"→ {t.get('assigned_to')}" if t.get("assigned_to") else ""
        lines += f"{status_icon} `{ts}` | {uid} [{priority}] {assigned}\n"
    return lines
