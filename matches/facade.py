from datetime import datetime
from matches.models import Match, Seat


def get_match_by_id(id: int) -> Match | None:
    return Match.objects.filter(id=id).first()


def get_unreserved_seat_by_id(id: int) -> Seat | None:
    return Seat.objects.filter(id=id, is_reserved=False).first()


def safe_reserve_seat_by_id(id: int, updated_at: datetime) -> None:
    Seat.objects.filter(id=id, updated_at=updated_at).update(is_reserved=True)
