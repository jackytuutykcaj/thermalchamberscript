Make sure you have the library pymodbus installed


How to use readwrite.py
For reading:
Type py readwrite.py read [currenttemp|setpoint|rangehigh|rangelow]
For writing:
Type py readwrite.py write [setpoint|rangehigh|rangelow] [value]


How to use ramping.py
Type py ramping.py [starting Temperature value] [ending temperature value] [temperature difference] [amount of cycles] [interval between each ramp]