EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L Switch:SW_SPDT_MSM SW1
U 1 1 6111E1B0
P 2750 2550
F 0 "SW1" H 2750 2750 50  0000 C CNN
F 1 "SW_SPDT_MSM" H 2750 2744 50  0001 C CNN
F 2 "" H 2750 2550 50  0001 C CNN
F 3 "~" H 2750 2550 50  0001 C CNN
	1    2750 2550
	1    0    0    -1  
$EndComp
$Comp
L Switch:SW_SPDT_MSM SW3
U 1 1 6111FC07
P 2750 4600
F 0 "SW3" H 2750 4793 50  0000 C CNN
F 1 "SW_SPDT_MSM" H 2750 4794 50  0001 C CNN
F 2 "" H 2750 4600 50  0001 C CNN
F 3 "~" H 2750 4600 50  0001 C CNN
	1    2750 4600
	1    0    0    -1  
$EndComp
$Comp
L Switch:SW_SPST SW4
U 1 1 6112106D
P 2750 2000
F 0 "SW4" H 2750 2143 50  0000 C CNN
F 1 "SW_SPST" H 2750 2144 50  0001 C CNN
F 2 "" H 2750 2000 50  0001 C CNN
F 3 "~" H 2750 2000 50  0001 C CNN
	1    2750 2000
	1    0    0    -1  
$EndComp
$Comp
L Device:R_POT_US RV1
U 1 1 61122972
P 2900 3800
F 0 "RV1" H 2832 3846 50  0000 R CNN
F 1 "10k" H 2832 3755 50  0000 R CNN
F 2 "" H 2900 3800 50  0001 C CNN
F 3 "~" H 2900 3800 50  0001 C CNN
	1    2900 3800
	1    0    0    -1  
$EndComp
Wire Wire Line
	2300 2550 2550 2550
Wire Wire Line
	2300 4600 2550 4600
$Comp
L Device:Battery_Cell BT1
U 1 1 611301AD
P 1600 2200
F 0 "BT1" H 1718 2296 50  0000 L CNN
F 1 "LiPo single cell" H 1718 2205 50  0000 L CNN
F 2 "" V 1600 2260 50  0001 C CNN
F 3 "~" V 1600 2260 50  0001 C CNN
	1    1600 2200
	1    0    0    -1  
$EndComp
$Comp
L Connector_Generic:Conn_01x12 J1
U 1 1 61134A8C
P 4300 2800
F 0 "J1" H 4380 2746 50  0000 L CNN
F 1 "Conn_01x12" H 4380 2701 50  0001 L CNN
F 2 "" H 4300 2800 50  0001 C CNN
F 3 "~" H 4300 2800 50  0001 C CNN
	1    4300 2800
	1    0    0    -1  
$EndComp
Wire Wire Line
	4100 2600 3750 2600
Wire Wire Line
	4100 2700 3750 2700
Text Label 3750 2700 0    50   ~ 0
D07
Wire Wire Line
	4100 2800 3750 2800
Text Label 3750 2800 0    50   ~ 0
D08
Wire Wire Line
	4100 2900 3750 2900
Text Label 3750 2900 0    50   ~ 0
D09
Text Label 3750 3000 0    50   ~ 0
D10
Text Label 3750 3100 0    50   ~ 0
D12
Wire Wire Line
	4100 3200 3750 3200
Text Label 3750 3200 0    50   ~ 0
D19
Text Label 3750 3300 0    50   ~ 0
D01
Text Label 3750 3400 0    50   ~ 0
D11
Wire Wire Line
	3750 2400 4100 2400
Text Label 3750 2400 0    50   ~ 0
EN
Wire Wire Line
	3750 2500 4100 2500
Text Label 3750 2500 0    50   ~ 0
V_USB
Text Label 3750 2300 0    50   ~ 0
V_BATT
Text Label 3750 2600 0    50   ~ 0
D17
Wire Wire Line
	3400 2450 2950 2450
Wire Wire Line
	3400 3000 4100 3000
Wire Wire Line
	3300 3100 3300 2650
Wire Wire Line
	3300 2650 2950 2650
Wire Wire Line
	3300 3100 4100 3100
$Comp
L Connector_Generic:Conn_01x16 J2
U 1 1 6114364B
P 4300 4400
F 0 "J2" H 4380 4346 50  0000 L CNN
F 1 "Conn_01x16" H 4380 4301 50  0001 L CNN
F 2 "" H 4300 4400 50  0001 C CNN
F 3 "~" H 4300 4400 50  0001 C CNN
	1    4300 4400
	1    0    0    -1  
$EndComp
Wire Wire Line
	4100 3700 3750 3700
Wire Wire Line
	4100 3900 3750 3900
Wire Wire Line
	4100 4400 3750 4400
Wire Wire Line
	4100 4600 3750 4600
Wire Wire Line
	4100 4900 3750 4900
Wire Wire Line
	4100 5000 3750 5000
Wire Wire Line
	4100 5100 3750 5100
Text Label 3750 3700 0    50   ~ 0
RST
Text Label 3750 3800 0    50   ~ 0
3.3V
Text Label 3750 4100 0    50   ~ 0
A0
Text Label 3750 4200 0    50   ~ 0
A2
Text Label 3750 4300 0    50   ~ 0
A3
Text Label 3750 4400 0    50   ~ 0
D4
Text Label 3750 4500 0    50   ~ 0
D5
Text Label 3750 4600 0    50   ~ 0
D6
Text Label 3750 5000 0    50   ~ 0
D14
Text Label 3750 5100 0    50   ~ 0
D13
Text Label 3750 4700 0    50   ~ 0
D18
Text Label 3750 4800 0    50   ~ 0
D16
Text Label 3750 4900 0    50   ~ 0
D15
Text Label 3750 3900 0    50   ~ 0
NC
Text Label 3750 4000 0    50   ~ 0
GND
Text Label 3750 5200 0    50   ~ 0
GND
Wire Wire Line
	2950 2000 3600 2000
Wire Wire Line
	3600 2000 3600 2300
Wire Wire Line
	3600 2300 4100 2300
Wire Wire Line
	2900 3650 3550 3650
Wire Wire Line
	3550 3800 4100 3800
Wire Wire Line
	3050 3800 3400 3800
Wire Wire Line
	3400 4100 4100 4100
Wire Wire Line
	1600 2000 2550 2000
Wire Notes Line
	3700 1850 3700 5350
Wire Notes Line
	3700 5350 4950 5350
Wire Notes Line
	4950 5350 4950 1850
Wire Notes Line
	4950 1850 3700 1850
Text Notes 3800 1950 0    50   ~ 0
Sparkfun Thing Plus Xbee3
Wire Wire Line
	1600 5550 1600 2300
Wire Wire Line
	1600 5550 2300 5550
Wire Wire Line
	2900 3950 2900 4000
Text Notes 2400 1300 0    118  ~ 0
Hand controller
Wire Notes Line style solid rgb(0, 0, 0)
	5500 900  1050 900 
Wire Notes Line style solid rgb(0, 0, 0)
	1050 900  1050 5800
Wire Notes Line style solid rgb(0, 0, 0)
	1050 5800 5500 5800
Wire Notes Line style solid rgb(0, 0, 0)
	5500 900  5500 5800
Text Label 3050 2450 0    79   ~ 0
raise
Text Label 3050 2650 0    79   ~ 0
lower
Text Label 3050 4500 0    79   ~ 0
raise
Text Label 3050 4700 0    79   ~ 0
lower
Wire Wire Line
	3400 3000 3400 2450
Text Label 3050 3500 0    79   ~ 0
lower
Text Label 3050 3300 0    79   ~ 0
raise
Wire Wire Line
	2950 3500 3500 3500
Wire Wire Line
	2300 3400 2550 3400
$Comp
L Switch:SW_SPDT_MSM SW2
U 1 1 611205D5
P 2750 3400
F 0 "SW2" H 2750 3593 50  0000 C CNN
F 1 "SW_SPDT_MSM" H 2750 3594 50  0001 C CNN
F 2 "" H 2750 3400 50  0001 C CNN
F 3 "~" H 2750 3400 50  0001 C CNN
	1    2750 3400
	1    0    0    -1  
$EndComp
Connection ~ 2300 4600
Wire Wire Line
	3450 4500 3450 4200
Wire Wire Line
	3450 4200 4100 4200
Wire Wire Line
	2950 4500 3450 4500
Wire Wire Line
	3550 4700 3550 4300
Wire Wire Line
	3550 4300 4100 4300
Wire Wire Line
	2950 4700 3550 4700
Wire Wire Line
	2900 4000 4100 4000
Wire Wire Line
	3400 3800 3400 4100
Wire Wire Line
	3550 3650 3550 3800
Wire Wire Line
	2300 4600 2300 5200
Connection ~ 2300 3400
Wire Wire Line
	2300 3400 2300 4600
Wire Wire Line
	2300 2550 2300 3400
Wire Wire Line
	2950 3300 4100 3300
Wire Wire Line
	3500 3500 3500 3400
Wire Wire Line
	3500 3400 4100 3400
Text Notes 1200 7300 0    79   ~ 0
Wiring colour standard:\n- SW1, SW2, SW3 terminal 1: yellow\n- SW1, SW2, SW3 terminal 2: black\n- SW1, SW2, SW3 terminal 3: orange\n- RV1 terminal 1: red\n- RV1 terminal 2: green\n- RV1 terminal 3: black\n- BT1 +ve: red\n- BT1 gnd: black
Text Notes 4250 6800 0    59   ~ 0
Versioning:\nv1.0 - original\nv1.1 - moved SW2 to different XBee3 pins\nv2.0 - range extender is now part of the controller
$Comp
L Switch:SW_SPDT SW5
U 1 1 62BC4939
P 2750 5200
F 0 "SW5" H 2750 5400 50  0000 C CNN
F 1 " " H 2750 5394 50  0000 C CNN
F 2 "" H 2750 5200 50  0001 C CNN
F 3 "~" H 2750 5200 50  0001 C CNN
	1    2750 5200
	1    0    0    -1  
$EndComp
Wire Wire Line
	2300 5550 3650 5550
Wire Wire Line
	3650 5550 3650 5200
Wire Wire Line
	3650 5200 4100 5200
Connection ~ 2300 5550
Wire Wire Line
	2550 5200 2300 5200
Connection ~ 2300 5200
Wire Wire Line
	2300 5200 2300 5550
Wire Wire Line
	3650 4500 3650 5100
Wire Wire Line
	3650 5100 2950 5100
Wire Wire Line
	3650 4500 4100 4500
Text Label 3050 5100 0    79   ~ 0
mode
$EndSCHEMATC
