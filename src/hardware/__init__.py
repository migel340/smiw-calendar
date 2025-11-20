from src.config import EPD_DRIVER
if EPD_DRIVER == 'mock':
    from src.hardware.epd_mock import EPD
else:
    from hardware.epd_waveshare_driver import EPD

def get_epd() -> EPD:
    return EPD()

__all__ = ['get_epd']