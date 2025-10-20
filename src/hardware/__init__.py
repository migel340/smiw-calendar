from src.config import EDP_DRIVER
if EDP_DRIVER == 'mock':
    from src.hardware.epd_mock import EPD
else:
    from src.hardware.epd_waveshare import EPD

def get_epd() -> EPD:
    return EPD()

__all__ = ['get_epd']