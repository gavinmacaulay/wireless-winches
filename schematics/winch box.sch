EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title "Wireless winch cylinder wiring"
Date "2021-10-18"
Rev "0.2"
Comp "Aqualyd Limited"
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L Converter_ACDC:VTX-214-015-124 PS1
U 1 1 606B1811
P 9350 4650
F 0 "PS1" H 9350 5017 50  0000 C CNN
F 1 "VTX-214-015-124" H 9350 4926 50  0000 C CNN
F 2 "Converter_ACDC:Converter_ACDC_Vigortronix_VTX-214-015-1xx_THT" H 9350 5100 50  0001 C CNN
F 3 "http://www.vigortronix.com/15WattSMPSPCBModuleAC-DC" H 10450 3850 50  0001 C CNN
	1    9350 4650
	-1   0    0    -1  
$EndComp
Wire Wire Line
	6200 4400 6050 4400
$Comp
L Connector_Generic:Conn_01x06 JP4
U 1 1 6131914C
P 2500 4000
F 0 "JP4" H 2418 4417 50  0000 C CNN
F 1 "xbee_explorer_regulated" H 2418 4326 50  0000 C CNN
F 2 "" H 2500 4000 50  0001 C CNN
F 3 "~" H 2500 4000 50  0001 C CNN
	1    2500 4000
	-1   0    0    -1  
$EndComp
Wire Wire Line
	2700 3900 3500 3900
Wire Wire Line
	3500 3900 3500 4100
Wire Wire Line
	3500 4100 4150 4100
Wire Wire Line
	2700 4000 3900 4000
Wire Wire Line
	2700 4100 3300 4100
Wire Wire Line
	3300 4100 3300 3800
Wire Wire Line
	3300 3800 4150 3800
Wire Wire Line
	2700 4200 3200 4200
Wire Wire Line
	3200 4200 3200 3700
Wire Wire Line
	3200 3700 4150 3700
Text Label 2750 3900 0    50   ~ 0
GND
Text Label 2750 4000 0    50   ~ 0
5V
Text Label 2750 4100 0    50   ~ 0
DOUT
Text Label 2750 4200 0    50   ~ 0
DIN
Wire Notes Line style solid
	1900 5000 8100 5000
Wire Notes Line style solid
	8100 5000 8100 1850
Wire Notes Line style solid
	8100 1850 1900 1850
Wire Notes Line style solid
	1900 1850 1900 5000
Text Notes 1950 2050 0    118  ~ 0
Winch cylinder
$Comp
L winch-box-rescue:tic-t249-pololu-winch-box-rescue U1
U 1 1 606B474A
P 5100 4050
F 0 "U1" H 5100 3327 50  0000 C CNN
F 1 "tic-t249" H 5100 3236 50  0000 C CNN
F 2 "MODULE" H 5100 4050 50  0001 C CNN
F 3 "DOCUMENTATION" H 5100 4050 50  0001 C CNN
	1    5100 4050
	1    0    0    -1  
$EndComp
$Comp
L Connector_Generic:Conn_01x06 J1
U 1 1 6131BDEC
P 6600 2600
F 0 "J1" H 6680 2592 50  0000 L CNN
F 1 "ISD04 motor controller" H 6680 2501 50  0000 L CNN
F 2 "" H 6600 2600 50  0001 C CNN
F 3 "~" H 6600 2600 50  0001 C CNN
	1    6600 2600
	1    0    0    -1  
$EndComp
Wire Wire Line
	5250 3100 5250 2800
Wire Wire Line
	5250 2800 6400 2800
Text Label 6200 2800 0    50   ~ 0
STEP
Wire Wire Line
	5150 3100 5150 2700
Wire Wire Line
	5150 2700 6400 2700
Text Label 6200 2700 0    50   ~ 0
DIR
Wire Wire Line
	6400 2900 6150 2900
Text Label 6200 2900 0    50   ~ 0
ENA
Wire Wire Line
	6400 2600 3900 2600
Wire Wire Line
	3900 2600 3900 4000
Connection ~ 3900 4000
Wire Wire Line
	3900 4000 4150 4000
Text Label 6200 2600 0    50   ~ 0
VCC
Wire Wire Line
	6400 2400 6150 2400
Wire Wire Line
	6150 2400 6150 2150
Wire Wire Line
	6150 2150 7050 2150
Wire Wire Line
	7050 2150 7050 4750
Wire Wire Line
	7050 4750 6050 4750
Wire Wire Line
	6050 4750 6050 4500
Wire Wire Line
	6400 2500 6050 2500
Wire Wire Line
	6050 2500 6050 2050
Wire Wire Line
	6050 2050 7150 2050
Wire Wire Line
	7150 2050 7150 4650
Wire Wire Line
	7150 4650 6200 4650
Wire Wire Line
	6200 4650 6200 4400
Text Label 6200 2400 0    50   ~ 0
V+
Text Label 6200 2500 0    50   ~ 0
GND
$Comp
L Connector:Conn_01x03_Male J2
U 1 1 616E512B
P 8100 4650
F 0 "J2" H 8300 4950 50  0000 R CNN
F 1 "AD-02BFFB-QL8AP0" H 8900 4850 50  0000 R CNN
F 2 "" H 8100 4650 50  0001 C CNN
F 3 "~" H 8100 4650 50  0001 C CNN
	1    8100 4650
	-1   0    0    -1  
$EndComp
Wire Wire Line
	7150 4650 7700 4650
Wire Wire Line
	7700 4650 7700 4750
Wire Wire Line
	7700 4750 7900 4750
Connection ~ 7150 4650
Wire Wire Line
	7050 4750 7500 4750
Wire Wire Line
	7500 4750 7500 4550
Wire Wire Line
	7500 4550 7900 4550
Connection ~ 7050 4750
Wire Wire Line
	8300 4750 8950 4750
Wire Wire Line
	8300 4550 8950 4550
$Comp
L Connector:Conn_01x03_Female J3
U 1 1 616E5EDF
P 8100 4650
F 0 "J3" H 7950 4950 50  0000 C CNN
F 1 "AD-02PMMS-QC8001" H 7650 4850 50  0000 C CNN
F 2 "" H 8100 4650 50  0001 C CNN
F 3 "~" H 8100 4650 50  0001 C CNN
	1    8100 4650
	-1   0    0    -1  
$EndComp
$EndSCHEMATC