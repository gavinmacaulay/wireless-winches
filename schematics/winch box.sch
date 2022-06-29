EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title "Wireless winch cylinder wiring"
Date "2022-06-29"
Rev "1.0"
Comp "Aqualyd Limited"
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
Wire Wire Line
	6550 4750 6400 4750
$Comp
L Connector_Generic:Conn_01x06 JP4
U 1 1 6131914C
P 2850 4350
F 0 "JP4" H 2768 4767 50  0000 C CNN
F 1 "xbee_explorer_regulated" H 2768 4676 50  0000 C CNN
F 2 "" H 2850 4350 50  0001 C CNN
F 3 "~" H 2850 4350 50  0001 C CNN
	1    2850 4350
	-1   0    0    -1  
$EndComp
Wire Wire Line
	3050 4250 3850 4250
Wire Wire Line
	3850 4250 3850 4450
Wire Wire Line
	3850 4450 4500 4450
Wire Wire Line
	3050 4450 3650 4450
Wire Wire Line
	3650 4450 3650 4150
Wire Wire Line
	3650 4150 4500 4150
Wire Wire Line
	3050 4550 3550 4550
Wire Wire Line
	3550 4550 3550 4050
Wire Wire Line
	3550 4050 4500 4050
Text Label 3100 4250 0    50   ~ 0
GND
Text Label 3100 4350 0    50   ~ 0
5V
Text Label 3100 4450 0    50   ~ 0
DOUT
Text Label 3100 4550 0    50   ~ 0
DIN
Wire Notes Line style solid
	2250 5350 8450 5350
Wire Notes Line style solid
	8450 5350 8450 2200
Wire Notes Line style solid
	8450 2200 2250 2200
Wire Notes Line style solid
	2250 2200 2250 5350
Text Notes 2300 2400 0    118  ~ 0
Winch cylinder
Wire Wire Line
	6400 5100 6400 4850
Wire Wire Line
	6550 5000 6550 4750
$Comp
L Connector:Conn_01x03_Male J1
U 1 1 616E512B
P 8450 5000
F 0 "J1" H 8650 5300 50  0000 R CNN
F 1 "AD-02BFFB-QL8AP0" H 9250 5200 50  0000 R CNN
F 2 "" H 8450 5000 50  0001 C CNN
F 3 "~" H 8450 5000 50  0001 C CNN
	1    8450 5000
	-1   0    0    -1  
$EndComp
Wire Wire Line
	8050 5000 8050 5100
Wire Wire Line
	8050 5100 8250 5100
Wire Wire Line
	7850 5100 7850 4900
Wire Wire Line
	7850 4900 8250 4900
$Comp
L Connector:Conn_01x03_Female J2
U 1 1 616E5EDF
P 8450 5000
F 0 "J2" H 8300 5300 50  0000 C CNN
F 1 "AD-02PMMS-QC8001" H 8000 5200 50  0000 C CNN
F 2 "" H 8450 5000 50  0001 C CNN
F 3 "~" H 8450 5000 50  0001 C CNN
	1    8450 5000
	-1   0    0    -1  
$EndComp
Wire Wire Line
	6400 5100 7850 5100
Wire Wire Line
	6550 5000 8050 5000
Wire Wire Line
	3050 4350 4500 4350
$Comp
L Motor:Stepper_Motor_bipolar M1
U 1 1 62BF5A27
P 8100 3100
F 0 "M1" H 8050 2900 50  0000 L CNN
F 1 "23HS30-2804S-PG4" H 7650 2800 50  0000 L CNN
F 2 "" H 8110 3090 50  0001 C CNN
F 3 "http://www.infineon.com/dgdl/Application-Note-TLE8110EE_driving_UniPolarStepperMotor_V1.1.pdf?fileId=db3a30431be39b97011be5d0aa0a00b0" H 8110 3090 50  0001 C CNN
	1    8100 3100
	1    0    0    -1  
$EndComp
$Comp
L Connector:Conn_01x04_Female J3
U 1 1 62C02200
P 7350 3950
F 0 "J3" V 7288 3662 50  0000 R CNN
F 1 "Molex 43645-0400" V 7197 3662 50  0000 R CNN
F 2 "" H 7350 3950 50  0001 C CNN
F 3 "~" H 7350 3950 50  0001 C CNN
	1    7350 3950
	0    -1   -1   0   
$EndComp
$Comp
L Connector:Conn_01x04_Male J4
U 1 1 62C0321A
P 7350 3950
F 0 "J4" V 7504 3662 50  0000 R CNN
F 1 "Molex 43640-0401" V 7413 3662 50  0000 R CNN
F 2 "" H 7350 3950 50  0001 C CNN
F 3 "~" H 7350 3950 50  0001 C CNN
	1    7350 3950
	0    -1   -1   0   
$EndComp
$Comp
L winch-box-rescue:tic-t249-pololu-winch-box-rescue U1
U 1 1 606B474A
P 5450 4400
F 0 "U1" H 5450 3677 50  0000 C CNN
F 1 "tic-t249" H 5450 3586 50  0000 C CNN
F 2 "MODULE" H 5450 4400 50  0001 C CNN
F 3 "DOCUMENTATION" H 5450 4400 50  0001 C CNN
	1    5450 4400
	1    0    0    -1  
$EndComp
Wire Wire Line
	6400 4550 7250 4550
Wire Wire Line
	7250 4550 7250 4150
Wire Wire Line
	6400 4650 7350 4650
Wire Wire Line
	7350 4650 7350 4150
Wire Wire Line
	7450 4450 7450 4150
Wire Wire Line
	7550 4350 7550 4150
Text Label 6650 4350 0    50   ~ 0
red
Wire Wire Line
	6400 4350 7550 4350
Wire Wire Line
	6400 4450 7450 4450
Text Label 6650 4450 0    50   ~ 0
blue
Text Label 6650 4550 0    50   ~ 0
black
Text Label 6650 4650 0    50   ~ 0
yellow
Wire Wire Line
	7250 3750 7250 2450
Wire Wire Line
	7250 2450 8000 2450
Wire Wire Line
	8000 2450 8000 2800
Wire Wire Line
	7350 3750 7350 2550
Wire Wire Line
	7350 2550 8200 2550
Wire Wire Line
	8200 2550 8200 2800
Wire Wire Line
	7450 3750 7450 3200
Wire Wire Line
	7450 3200 7800 3200
Wire Wire Line
	7550 3750 7550 3000
Wire Wire Line
	7550 3000 7800 3000
Text Label 7700 3000 0    50   ~ 0
B+
Text Label 7700 3200 0    50   ~ 0
B-
Text Label 8200 2750 0    50   ~ 0
A-
Text Label 8000 2750 0    50   ~ 0
A+
$Comp
L Device:Battery BT1
U 1 1 62C21AD4
P 9650 4900
F 0 "BT1" H 9450 5300 50  0000 L CNN
F 1 "Hikoki MultiVolt 36V" H 9450 5200 50  0000 L CNN
F 2 "" V 9650 4960 50  0001 C CNN
F 3 "~" V 9650 4960 50  0001 C CNN
	1    9650 4900
	1    0    0    -1  
$EndComp
Wire Wire Line
	8650 5100 9650 5100
Wire Wire Line
	9350 4900 9350 4700
Wire Wire Line
	9350 4700 9650 4700
Wire Wire Line
	8650 4900 9350 4900
Text Label 3950 4150 0    50   ~ 0
yellow
Text Label 3950 4050 0    50   ~ 0
orange
Text Label 3950 4350 0    50   ~ 0
red
Text Label 3950 4450 0    50   ~ 0
black
Text Label 6850 5000 0    50   ~ 0
black
Text Label 6850 5100 0    50   ~ 0
red
Text Label 7450 3650 1    50   ~ 0
blue
Text Label 7550 3650 1    50   ~ 0
red
Text Label 7250 3650 1    50   ~ 0
black
Text Label 7350 3650 1    50   ~ 0
green(yellow)
$EndSCHEMATC
