[![PyPI versio](https://img.shields.io/pypi/v/appletlib)](https://pypi.org/project/appletlib/)
[![PyPi format](https://img.shields.io/pypi/format/appletlib)](https://pypi.org/project/appletlib/)
[![PyPI license](https://img.shields.io/pypi/l/appletlib)](https://pypi.org/project/appletlib/)
[![PyPi weekly downloads](https://img.shields.io/pypi/dw/appletlib)](https://pypi.org/project/appletlib/)

appletlib
==============

Python library providing a QSystemTrayIcon wrapper

Classes
=============

- Application: provides several convenience function for logging,
  process detachment, application settings management

- Indicator:  base class for systemtray applets. A splash
  screen can be added as Indicator.splash.

- SystemTrayIcon: triggers regular updates every interval ms. Update
  by using SystemTrayIcon.setIcon( icon) and calling update().

- Splash: semi-transparent splash screen that is shown on all virtual desktops.

Requirements
============

- Python 3
- PyQt 5
