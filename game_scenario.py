from typing import Optional

PHRASES = {
    1957: 'First Sputnik',
    1961: 'Gagarin flew!',
    1969: 'Armstrong got on the moon!',
    1971: 'First orbital space station Salute-1',
    1981: 'Flight of the Shuttle Columbia',
    1998: 'ISS start building',
    2011: 'Messenger launch to Mercury',
    2020: 'Take the plasma gun! Shoot the garbage!',
}


def get_garbage_delay_tics(year: int) -> Optional[int]:
    """Get garbage delay by year."""
    if year < 1961:
        return None
    if year < 1969:
        return 20
    if year < 1981:
        return 14
    if year < 1995:
        return 10
    if year < 2010:
        return 8
    if year < 2020:
        return 6
    return 2
