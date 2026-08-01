# Denticles

This repository aims at simulating the fluid flow on a NACA0012 airfoil that is covered with shark denticles that is generated using the simulation in `addin`. Simulating different shark species' denticles will help us understand better how denticles help with reducing friction.

## Akash's curiosity
- About turbulent flow
    - Steady or Transient: **Probably doing steady so it is less computationally expensive**
    - RAS or LES **Gökçe- We need to use RAS if we go with steady-state because LES is time-dependent**
    - Find $k$, $\omega$, and $\epsilon$
    $$k = 1.5(UI)^2$$
    $$\epsilon = 0.09^{3/4}\frac{k^{3/2}}{L}$$
    $$\omega = \frac{\sqrt{k}}{\sqrt[4]{C_{\mu}}L}$$
- **DONE (JUST IN CASE I WILL CHECK OUT A TUTORIAL FOR AIRFOIL TO MAKE SURE IT LOOKS RIGHT)**: Understand how SnappyHexMesh works
- Figure out if we can use adaptive mesh refinement
- How do we use adaptive time step? (Useful for our turbulent flow)
- Learn more about aerodynamics theory
- **DONE**: How do we run multicore parallel simulation?
- Find out if it would be feasible to run an FSI simulation
- **GOT IT FROM NIK**: What template should we use for the paper?
- **DECREASED SIZE BY 4**: Improve STL
- **DONE**: Make bash script stop on error
- Try Local Scratch Storage

## Akash Notes
I found a problem today. If the cpu cores are found in different nodes, it will not run the simulation. I need to read the documentations to fix. I could have been writing the paper right now... But I ran into this problem. Which is good because it means we can scale our simulation even more now.

I understood what it was. I was trying to be smart and brought the files into the tmp folder because they are the fastest. But once the processor were on different nodes, they could not read each other's files.

I want to figure out how to make snappyHexMesh even faster. I need to make it work stop shell refinement earlier because it gets stuck with the same cells.

I will also try to improve the stl files

I changed the STL files. We expect a drag reduction of almost 25%...

## Gökçe Notes
Well, I generally take notes but they are never organized...

Turbulence properties 
Parallel computing
Simulation parameters

- run only airfoil 
- Look for github stuff

**NEW**: I added possible shark designs folder 

--We need to use RANS because LES 