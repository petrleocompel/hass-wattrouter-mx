# Wattrouter MX for Home Assistant

Integration for [Wattrouter MX](https://solarcontrols.cz/en/wattrouter_mx.html)

- [Manual EN](https://solarcontrols.cz/archives/eshop/WATTrouterMx_EN.pdf)
- [Manual CZ](https://solarcontrols.cz/archives/eshop/WATTrouterMx_CZ.pdf)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)


## Implemented

- Relay control for from T11 to T61
- Grouped control T11, T21, T31 and T41, T51, T61
- Reading state of relays


## Not implemetned

- any readings


## Installation

### HACS

1. Install HACS if you don't have it already
2. Open HACS in Home Assistant
3. Go to "Integrations" section
4. Click ... button on top right and in menu select "Custom repositories"
5. Add repository https://github.com/petrleocompel/hass-wattrouter-mx and select category "Integration"
6. Search for "hass-wattrouter-mx" and install it
7. Restart Home Assistant

### Manual

Download the [zip](https://github.com/petrleocompel/hass-wattrouter-mx/archive/refs/heads/master.zip) and extract it. Copy the folder `hass-wattrouter-mx` to your `custom_components` folder.
