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

- Python 2.7
- PyQt 4.x
