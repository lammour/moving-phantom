# Moving Phantom for Medical Imaging
This projects provides the code for controlling a robotic system used for testing X-Ray imaging.

The purpose of the robot is to displace a carbon plate in a straight line, with a constant speed. The carbon plate holds a small copper disk, whose position is tracked using X-Ray imaging. The plate can move in 2 axes (X and Y) and is controlled by 3 stepper motors, these ones being controlled by an [Arduino script](controle_mouvement).

The robot also disposes of a [graphical user interface (GUI)](gui) thath allows users to define and manage the robot's route by specifying positions and speeds, and to send commands to the Arduino microcontroller which controls the robot's movement.

## Robot Overview

![Robot Overview](assets/robot_overview.png)
The robot is composed of 3 stepper motors: 2 for the Y-axis movement, attached to a wooden support, and 1 for the X-axis movement, attached to the carbon plate. The stepper motors are controlled by an Arduino MEGA which interprets the user commands received from the GUI.