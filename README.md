# Jangchi - MIPS-driven robot emulator

## Introduction

Back in 2012, I had an electronic project at the university :
Make a small robot following a line on the ground.

The tricky part was the fact the robot didn't contains a CPU but only a FPGA (programmable transistors).
All the challenge was then to design an entire MIPS CPU, load it on the FPGA in order to make it execute the line following algorithm.

## Why this project

During this great project, I realized I didn't have any simulating tool, and then have to deal with numerous possible piece of failures.
Indeed, when you execute a program you wrote (in assembly of course) on a CPU you wrote, it's hard to know what's the piece of failure.
In fact it was even worse than that given I wrote my own assembler [gopiler](https://github.com/touilleMan/gopiler) to build my code...)

Thus the idea behind this project is to provide a simple environment to simulate a robot with an embedded MIPS CPU. Then it becomes quiet easier to develop and test at home some algorithm before loading them on the real robot with then only one possible point of failure : the designed CPU.

## State

For the moment, the project is on it early days. Only a rough MIPS CPU emulator and a ugly gui.
But be sure things are moving fast !
