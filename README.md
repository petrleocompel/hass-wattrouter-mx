# Wattrouter MX for Home Assistant


## ⚠️ Deprecated ⚠️ Use modbus

> From version 2.2 there is modbus inside of Wattrouter fw. We should use it insted. Their custom HTTP XML is not great. All registries can be found in documentation [CZ](https://solarcontrols.cz/archives/eshop/WATTrouterMx_CZ.pdf) [EN](https://solarcontrols.cz/archives/eshop/WATTrouterMx_EN.pdf)
 
### Modbus Example configuration 
- [x] modbus connection
- [x] basic readouts
- [ ] all readouts 
- [ ] example for using relays

```yaml
modbus:
  - name: wattrouter
    type: tcp
    host: 192.168.0.50 # IP zařízení
    port: 502
    sensors:
      - name: Wattrouter Voltage Phase 1
        unique_id: wattrouter_voltage_phase_1
        slave: 1
        address: 8
        data_type: int32
        device_class: voltage
        input_type: input
        state_class: measurement
        unit_of_measurement: "V"
      - name: power_phase_1
        unique_id: wattrouter_power_phase_1
        slave: 1
        address: 0
        data_type: int32
        count: 2
        device_class: power
        scale: 10
        input_type: input
        state_class: measurement
        unit_of_measurement: "W"
      - name: power_phase_2
        unique_id: wattrouter_power_phase_2
        slave: 1
        address: 2
        data_type: int32
        device_class: power
        scale: 10
        input_type: input
        state_class: measurement
        unit_of_measurement: "W"
      - name: power_phase_3
        unique_id: wattrouter_power_phase_3
        slave: 1
        address: 4
        data_type: int32
        device_class: power
        scale: 10
        input_type: input
        state_class: measurement
        unit_of_measurement: "W"
      - name: consumption_vt_daily
        unique_id: wattrouter_consumption_vt_daily
        slave: 1
        address: 92
        data_type: int32
        device_class: energy
        scale: 10
        input_type: input
        state_class: total_increasing
        unit_of_measurement: "Wh"
      - name: consumption_nt_daily
        unique_id: wattrouter_consumption_nt_daily
        slave: 1
        address: 94
        data_type: int32
        device_class: energy
        scale: 10
        input_type: input
        state_class: total_increasing
        unit_of_measurement: "Wh"
      - name: leftower_daily
        unique_id: wattrouter_leftower_daily
        slave: 1
        address: 96
        data_type: int32
        device_class: energy
        scale: 10
        input_type: input
        state_class: total_increasing
        unit_of_measurement: "Wh"
      - name: production_daily
        unique_id: wattrouter_production_daily
        slave: 1
        address: 98
        data_type: int32
        device_class: energy
        scale: 10
        input_type: input
        state_class: total_increasing
        unit_of_measurement: "Wh"
```
--------------

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
