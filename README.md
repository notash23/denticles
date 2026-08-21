# Denticles

This repository aims at simulating the fluid flow on a NACA0012 airfoil that is covered with shark denticles that is generated using the simulation in `addin`. Simulating different shark species' denticles will help us understand better how denticles help with reducing friction.

## Akash's curiosity
- About turbulent flow
    - Steady or Transient: **Probably doing steady so it is less computationally expensive**
    - RAS or LES **Gökçe- We need to use RAS if we go with steady-state because LES is time-dependent**
    - Find $k$, $\omega$, and $\epsilon$
    $$k = 1.5(UI)^2$$
    $$\epsilon = (C_{\mu})^{3/4}\frac{k^{3/2}}{L}$$
    $$\omega = \frac{\sqrt{k}}{\sqrt[4]{C_{\mu}}L}$$
- **DONE**: Understand how SnappyHexMesh works
- Figure out if we can use adaptive mesh refinement
- How do we use adaptive time step? (Useful for our turbulent flow)
- Learn more about aerodynamics theory
    - What is wall shear stress?
    - What is skin friction?
    - How does turbulence increase drag?
- **DONE**: How do we run multicore parallel simulation?
- Find out if it would be feasible to run an FSI simulation
- **GOT IT FROM NIK**: What template should we use for the paper?
- **DECREASED SIZE BY 4**: Improve STL (obtained airfoil from https://www.bigfoil.com/D/ed677818-5a94-4df6-8006-2eebed47df40_infoDAT.php)
- **DONE**: Make bash script stop on error
- Try Local Scratch Storage
- Explain what our approach is in our intro (forget theory. Assume that shark perfected it and see what result it gives us)
- **DONE**: How to add wallshearstress and other variables in simulations?

## Final countdown
- use words instead of numbers
- Dont forget to reference the first paper for $SST-k\omega$ and $LES$ from Smagorinsky
- Mesh refinement study: Do 3 cases of the base case at different angles
- orthogonal vs smoothing layer in snappy
- Why is angle 8 and 16 not working?? Try to use better boundary conditions
- Check $y^+$
- we should use EPS format
- From Rishi
    - Sequential numbering: Your in-text citations are currently alphabetical (your first citation in the text is [6]). Please reorder them sequentially ([1], [2], etc.) based on exactly where they first appear in the text.

    - Reference list: Update all entries in your bibliography to the standard IEEE format (e.g., [1] F. Lastname, "Title," Journal, Year.).

    - Incomplete Sections/Placeholders: Your draft contains numerous "[will be added later]" placeholders throughout the Abstract, Section 3.1, Section 4 (Results), and Section 5 (Conclusion). Please finalize all of these sections and remove the template instructions.

    - Editor Comments: Please ensure you address the four margin comments Kartik left on your draft document regarding:
        - Explaining the simulation vs. experiment discrepancy in Table 1.
        - Explaining the translation of Table 2 micro-measurements to CAD.
        - Adding a grid convergence/mesh independence statement for your CFD methodology.
        - Specifying the units for the NACA 0012 airfoil dimensions.
- For LES
    - set up the simulation according the the TKE from RANS
    - Implement adaptive mesh and timestep
    - Calculate $k_{res}$ using `UPrime2MeanXX` and $k_{sgs}$ which is given by `k`
    - Calculate ratio of $k$ and make sure that they are always more than $80\%$

## Akash Notes
I found a problem today. If the cpu cores are found in different nodes, it will not run the simulation. I need to read the documentations to fix. I could have been writing the paper right now... But I ran into this problem. Which is good because it means we can scale our simulation even more now.

I understood what it was. I was trying to be smart and brought the files into the tmp folder because they are the fastest. But once the processor were on different nodes, they could not read each other's files.

I want to figure out how to make snappyHexMesh even faster. I need to make it work stop shell refinement earlier because it gets stuck with the same cells.

I will also try to improve the stl files

I changed the STL files. We expect a drag reduction of almost 25%...

## Gökçe Notes
Well, I generally take notes but they are never organized...

**NEW**: I added possible shark designs folder 

- The first results here: 
    Drag force of airfoil w/ denticle = 0.000619378 N 
    Drag force of airfoil smooth = 0.00124926 N  **Well wait! I scaled down to mm maybe it effects the units here?

    Drag - airfoil w/denticle = 5e-4
    Drag - airfoil smooth = 1e-3 

    Drag reduction rate: 50%  *Too much!*