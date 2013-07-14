# Trimps - MIPS-driven robot emulator

## Introduction

Back in 2012, I had an electronic project at the university :
Make a small robot following a line on the ground.

The tricky part was the fact the robot didn't contain a CPU but only a FPGA (programmable transistors).
All the challenge was then to design an entire MIPS CPU, load it on the FPGA in order to make it execute an embedded line-tracer algorithm program.

## Why this project

During this great project, I realized I didn't have any simulating tool, and then have to deal with numerous possible piece of failures.
Indeed, when you execute a program you wrote (in assembly of course...) on a CPU you wrote, it's hard to know who is to blame.
In fact it was even worse than that given I wrote my own assembler [gopiler](https://github.com/touilleMan/gopiler) to build my code...

Thus the idea behind this project is to provide a simple environment to simulate a robot with an embedded MIPS CPU. Then it becomes quiet easier to develop and test at home some algorithm before loading them on the real robot with then only one possible point of failure : the designed CPU.

## State

The V1.1 contains the following functionalities :
 - a MIPS CPU emulator with two implementations : C++ and python
   - note : the C++ version is about 10times faster that the python version but is not avaible for windows so far
 - a robot with stepper motors
 - a memory area for sharing I/O between the robot and the CPU
 - a line sensor module plugged on the robot
 - a GUI in Qt where the user can trace lines and see the robot evolutes in
 - an editor inside the GUI to quickly write and test code on the robot
