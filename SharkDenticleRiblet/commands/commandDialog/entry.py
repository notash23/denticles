import adsk.core, adsk.fusion
import os
from ...lib import fusionAddInUtils as futil
from ... import config

app = adsk.core.Application.get()
ui = app.userInterface


# TODO *** Specify the command identity information. ***
CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_cmdDialog'
CMD_NAME = 'Riblet Generator'
CMD_Description = 'A Fusion Add-in Command that generates sketches for riblets'

# Specify that the command will be promoted to the panel.
IS_PROMOTED = True

# TODO *** Define the location where the command button will be created. ***
# This is done by specifying the workspace, the tab, and the panel, and the 
# command it will be inserted beside. Not providing the command to position it
# will insert it at the end.
WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'SurfaceCreatePanel'

# Resource location for command icons, here we assume a sub folder in this directory named "resources".
ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '')

# Local list of event handlers used to maintain a reference so
# they are not released and garbage collected.
local_handlers = []


# Executed when add-in is run.
def start():
    # Create a command Definition.
    cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER)

    # Define an event handler for the command created event. It will be called when the button is clicked.
    futil.add_handler(cmd_def.commandCreated, command_created)

    # ******** Add a button into the UI so the user can run the command. ********
    # Get the target workspace the button will be created in.
    workspace = ui.workspaces.itemById(WORKSPACE_ID)

    # Get the panel the button will be created in.
    panel = workspace.toolbarPanels.itemById(PANEL_ID)

    # Create the button command control in the UI after the specified existing command.
    control = panel.controls.addCommand(cmd_def)

    # Specify if the command is promoted to the main toolbar. 
    control.isPromoted = IS_PROMOTED


# Executed when add-in is stopped.
def stop():
    # Get the various UI elements for this command
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    command_control = panel.controls.itemById(CMD_ID)
    command_definition = ui.commandDefinitions.itemById(CMD_ID)

    # Delete the button command control
    if command_control:
        command_control.deleteMe()

    # Delete the command definition
    if command_definition:
        command_definition.deleteMe()


# Function that is called when a user clicks the corresponding button in the UI.
# This defines the contents of the command dialog and connects to the command related events.
def command_created(args: adsk.core.CommandCreatedEventArgs):
    # https://help.autodesk.com/view/fusion360/ENU/?contextId=CommandInputs
    inputs = args.command.commandInputs
    inputs.addIntegerSpinnerCommandInput('num_riblets', 'Number of Riblets', 1, 30, 1, 3)

    # TODO Connect to the events that are needed by this command.
    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)


# This event handler is called when the user clicks the OK button in the command dialog or 
# is immediately called after the created event not command inputs were created for the dialog.
def command_execute(args: adsk.core.CommandEventArgs):
    design = adsk.fusion.Design.cast(app.activeProduct)
    rootComp = design.rootComponent
    userParams = design.userParameters
    sketches = rootComp.sketches

    # Get a reference to your command's inputs.
    inputs = args.command.commandInputs
    num_riblets_spinner: adsk.core.IntegerSpinnerCommandInput = inputs.itemById('num_riblets')
    num_riblets = num_riblets_spinner.value
    length = userParams.itemByName('CW').value * 0.75
    height = userParams.itemByName('Height').value
    crown_height = userParams.itemByName('CH').value
    depth = userParams.itemByName('CL').value
    riblet_depth = userParams.itemByName('RD').value

    # ******************************** Profile Code ********************************
    planes = rootComp.constructionPlanes
    profileSketch = sketches.add(planes.itemByName('ProfilePlane'))
    splines = profileSketch.sketchCurves.sketchFittedSplines
    constraints = profileSketch.geometricConstraints
    sketchDimensions = profileSketch.sketchDimensions
    sketchLines = profileSketch.sketchCurves.sketchLines
    

    for i in range(num_riblets):
        points = adsk.core.ObjectCollection.create()

        # Define the points the spline with fit through.
        points.add(adsk.core.Point3D.create(0, -height, 0))
        points.add(adsk.core.Point3D.create(-length/(2*num_riblets), -height-0.1, 0))
        points.add(adsk.core.Point3D.create(-length/num_riblets, -height-0.2, 0))
        
        spline = splines.add(points)
        fitPoints = spline.fitPoints

        fitPoint1 = fitPoints.item(1)
        line = spline.activateTangentHandle(fitPoint1)            
        constraints.addHorizontal(line)
        sketchDimension = sketchDimensions.addDistanceDimension(line.startSketchPoint, line.endSketchPoint, adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation, line.endSketchPoint.geometry)
        # TODO: might use curvature handle here
        sketchDimension.parameter.expression = '1.5 mm'

        fitPoint0 = fitPoints.item(0)
        line = spline.activateTangentHandle(fitPoint0)            
        constraints.addHorizontal(line)
        sketchDimension = sketchDimensions.addDistanceDimension(line.startSketchPoint, line.endSketchPoint, adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation, line.endSketchPoint.geometry)
        sketchDimension.parameter.expression = '1 mm'

        fitPoint2 = fitPoints.item(2)
        line = spline.activateTangentHandle(fitPoint2)
        constraints.addHorizontal(line)
        sketchDimension = sketchDimensions.addDistanceDimension(line.startSketchPoint, line.endSketchPoint, adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation, line.endSketchPoint.geometry)
        sketchDimension.parameter.expression = '1 mm'

        sketchDimension = sketchDimensions.addDistanceDimension(fitPoint0, fitPoint2, adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation, fitPoint0.geometry)
        sketchDimension.parameter.expression = f'CW*0.75/{num_riblets}'

        sketchDimension = sketchDimensions.addDistanceDimension(fitPoint0, fitPoint1, adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation, fitPoint1.geometry)
        sketchDimension.parameter.expression = f'{(i+1)/(num_riblets+1)}*CW*0.75/{num_riblets}'
        
        if i == 0:
            first_spline = spline
        else:
            constraints.addCoincident(spline.startSketchPoint, prev_spline.endSketchPoint)
        
        displacementFull = -crown_height*40*((i+1)/num_riblets)*((i+1)/num_riblets-1)
        displacementHalf = -crown_height*40*((i+0.5)/num_riblets)*((i+0.5)/num_riblets-1)

        sketchDimension = sketchDimensions.addDistanceDimension(first_spline.fitPoints.item(0), fitPoint2, adsk.fusion.DimensionOrientations.VerticalDimensionOrientation, fitPoint2.geometry)
        sketchDimension.parameter.expression = f'{displacementFull} mm'

        sketchDimension = sketchDimensions.addDistanceDimension(first_spline.fitPoints.item(0), fitPoint1, adsk.fusion.DimensionOrientations.VerticalDimensionOrientation, fitPoint1.geometry)
        sketchDimension.parameter.expression = f'{displacementHalf} mm - RD'
        prev_spline = spline
    
    horizontalConstructionLine = sketchLines.addByTwoPoints(adsk.core.Point3D.create(0, 0, 0), adsk.core.Point3D.create(0, 0, 0))
    constraints.addCoincident(horizontalConstructionLine.startSketchPoint, first_spline.startSketchPoint)
    constraints.addCoincident(horizontalConstructionLine.endSketchPoint, spline.endSketchPoint)
    horizontalConstructionLine.isConstruction = True

    verticalConstructionLine = sketchLines.addByTwoPoints(adsk.core.Point3D.create(0, 0, 0), adsk.core.Point3D.create(0, 0, 0))
    constraints.addMidPoint(verticalConstructionLine.startSketchPoint, horizontalConstructionLine)
    constraints.addCoincident(verticalConstructionLine.endSketchPoint, profileSketch.originPoint)
    constraints.addVertical(verticalConstructionLine)
    verticalConstructionLine.isConstruction = True

    sketchDimension = sketchDimensions.addDistanceDimension(verticalConstructionLine.startSketchPoint, verticalConstructionLine.endSketchPoint, adsk.fusion.DimensionOrientations.VerticalDimensionOrientation, verticalConstructionLine.endSketchPoint.geometry)
    sketchDimension.parameter.expression = 'Height'
    profileSketch.isVisible = False

    # ******************************** Cutout Code ********************************
    planes = rootComp.constructionPlanes
    cutoutSketch = sketches.add(planes.itemByName('CrownPlane'))
    sketchLines = cutoutSketch.sketchCurves.sketchLines
    conicCurves = cutoutSketch.sketchCurves.sketchConicCurves
    constraints = cutoutSketch.geometricConstraints
    sketchDimensions = cutoutSketch.sketchDimensions
    splines = cutoutSketch.sketchCurves.sketchFittedSplines

    points = adsk.core.ObjectCollection.create()

    # Define the points the spline with fit through.
    points.add(adsk.core.Point3D.create(-3, 2.5, 0))
    points.add(adsk.core.Point3D.create(-4, -1, 0))
    points.add(adsk.core.Point3D.create(0, -4.5, 0))
    points.add(adsk.core.Point3D.create(4, -1, 0))
    points.add(adsk.core.Point3D.create(3, 2.5, 0))

    
    spline1 = splines.add(points)
    fitPoints1 = spline1.fitPoints

    # Get the second fit point
    fitPoint1 = fitPoints1.item(0)
    line1 = spline1.activateTangentHandle(fitPoint1)            
    constraints.addHorizontal(line1)
    sketchDimension = sketchDimensions.addDistanceDimension(line1.startSketchPoint, line1.endSketchPoint, adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation, line1.endSketchPoint.geometry)
    sketchDimension.parameter.expression = '5 mm'
    fitPoint2 = fitPoints1.item(4)
    line2 = spline1.activateTangentHandle(fitPoint2)
    constraints.addHorizontal(line2)
    constraints.addEqual(line1, line2)

    topConstructionLine = sketchLines.addByTwoPoints(adsk.core.Point3D.create(0, 0, 0), adsk.core.Point3D.create(0, 0, 0))
    constraints.addCoincident(topConstructionLine.startSketchPoint, fitPoint1)
    constraints.addCoincident(topConstructionLine.endSketchPoint, fitPoint2)
    topConstructionLine.isConstruction = True
    sketchDimension = sketchDimensions.addDistanceDimension(topConstructionLine.startSketchPoint, topConstructionLine.endSketchPoint, adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation, topConstructionLine.endSketchPoint.geometry)
    sketchDimension.parameter.expression = 'CW * 0.75'

    fitPoint1 = fitPoints1.item(1)
    line1 = spline1.activateTangentHandle(fitPoint1)
    constraints.addVertical(line1)
    sketchDimension = sketchDimensions.addDistanceDimension(line1.startSketchPoint, line1.endSketchPoint, adsk.fusion.DimensionOrientations.VerticalDimensionOrientation, line1.endSketchPoint.geometry)
    sketchDimension.parameter.expression = '15 mm'
    fitPoint2 = fitPoints1.item(3)
    line2 = spline1.activateTangentHandle(fitPoint2)
    constraints.addVertical(line2)
    constraints.addEqual(line1, line2)

    constructionLine = sketchLines.addByTwoPoints(adsk.core.Point3D.create(0, 0, 0), adsk.core.Point3D.create(0, 0, 0))
    constraints.addCoincident(constructionLine.startSketchPoint, fitPoint1)
    constraints.addCoincident(constructionLine.endSketchPoint, fitPoint2)
    constraints.addMidPoint(cutoutSketch.originPoint, constructionLine)
    constructionLine.isConstruction = True
    sketchDimension = sketchDimensions.addDistanceDimension(constructionLine.startSketchPoint, constructionLine.endSketchPoint, adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation, constructionLine.endSketchPoint.geometry)
    sketchDimension.parameter.expression = 'CW'
    
    fitPoint = fitPoints1.item(2)
    line = spline1.activateTangentHandle(fitPoint)
    constraints.addHorizontal(line)
    sketchDimension = sketchDimensions.addDistanceDimension(line.startSketchPoint, line.endSketchPoint, adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation, line.endSketchPoint.geometry)
    sketchDimension.parameter.expression = '20 mm'

    verticalConstructionLine = sketchLines.addByTwoPoints(adsk.core.Point3D.create(0, 0, 0), adsk.core.Point3D.create(0, 0, 0))
    constraints.addVertical(verticalConstructionLine)
    constraints.addMidPoint(verticalConstructionLine.startSketchPoint, constructionLine)
    constraints.addCoincident(verticalConstructionLine.endSketchPoint, fitPoint)
    verticalConstructionLine.isConstruction = True
    sketchDimension = sketchDimensions.addDistanceDimension(verticalConstructionLine.startSketchPoint, verticalConstructionLine.endSketchPoint, adsk.fusion.DimensionOrientations.VerticalDimensionOrientation, verticalConstructionLine.endSketchPoint.geometry)
    sketchDimension.parameter.expression = 'CL/2'
    constraints.addSymmetry(fitPoints1.item(0), fitPoints1.item(4), verticalConstructionLine)
    constraints.addSymmetry(fitPoints1.item(1), fitPoints1.item(3), verticalConstructionLine)

    sketchDimension = sketchDimensions.addOffsetDimension(constructionLine, topConstructionLine, constructionLine.startSketchPoint.geometry)
    sketchDimension.parameter.expression = 'CL/2'

    points = adsk.core.ObjectCollection.create()

    # Define the points the spline with fit through.
    points.add(adsk.core.Point3D.create(-1, 2.5, 0))
    points.add(adsk.core.Point3D.create(0, 10, 0))
    points.add(adsk.core.Point3D.create(1, 2.5, 0))

    spline2 = splines.add(points)
    spline2.isConstruction = True
    fitPoints2 = spline2.fitPoints

    fitPoint1 = fitPoints2.item(0)
    line1 = spline2.activateTangentHandle(fitPoint1)
    constraints.addCoincident(fitPoint1, fitPoints1.item(0))       
    constraints.addVertical(line1)
    fitPoint2 = fitPoints2.item(2)
    line2 = spline2.activateTangentHandle(fitPoint2)
    constraints.addCoincident(fitPoint2, fitPoints1.item(4)) 
    constraints.addVertical(line2)
    constraints.addEqual(line1, line2)
    sketchDimension = sketchDimensions.addDistanceDimension(line1.startSketchPoint, line1.endSketchPoint, adsk.fusion.DimensionOrientations.VerticalDimensionOrientation, line1.endSketchPoint.geometry)
    sketchDimension.parameter.expression = '10 mm'

    fitPoint = fitPoints2.item(1)
    line = spline2.activateTangentHandle(fitPoint)            
    constraints.addHorizontal(line)
    sketchDimension = sketchDimensions.addDistanceDimension(line.startSketchPoint, line.endSketchPoint, adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation, line.endSketchPoint.geometry)
    sketchDimension.parameter.expression = '15 mm'

    verticalConstructionLine = sketchLines.addByTwoPoints(adsk.core.Point3D.create(0, 0, 0), adsk.core.Point3D.create(0, 0, 0))
    constraints.addVertical(verticalConstructionLine)
    constraints.addCoincident(verticalConstructionLine.startSketchPoint, fitPoint)
    constraints.addMidPoint(verticalConstructionLine.endSketchPoint, topConstructionLine)
    verticalConstructionLine.isConstruction = True
    sketchDimension = sketchDimensions.addDistanceDimension(verticalConstructionLine.startSketchPoint, verticalConstructionLine.endSketchPoint, adsk.fusion.DimensionOrientations.VerticalDimensionOrientation, verticalConstructionLine.endSketchPoint.geometry)
    sketchDimension.parameter.expression = 'CT'
    
    riblet_peaks = [0]
    for i in range(num_riblets):
        conicCurve = conicCurves.add(
            adsk.core.Point3D.create(0, 6.7, 0),
            adsk.core.Point3D.create(length, 6.7, 0), 
            adsk.core.Point3D.create(0, 0, 0),
            0.75
        )

        if i == 0:
            constraints.addCoincident(conicCurve.startSketchPoint, spline2.startSketchPoint)
        else:
            pass
            constraints.addCoincident(conicCurve.startSketchPoint, prev_conicCurve.endSketchPoint)

        constraints.addCoincident(conicCurve.endSketchPoint, spline2)
        pointLine = sketchLines.addByTwoPoints(conicCurve.startSketchPoint, conicCurve.endSketchPoint)
        pointLine.isConstruction = True

        verticalLine = sketchLines.addByTwoPoints(adsk.core.Point3D.create(0, 0, 0), adsk.core.Point3D.create(0, 0, 0))
        constraints.addMidPoint(verticalLine.startSketchPoint, pointLine)
        constraints.addVertical(verticalLine)
        constraints.addCoincident(verticalLine.endSketchPoint, conicCurve.apexSketchPoint)
        verticalLine.isConstruction = True

        sketchDimension = sketchDimensions.addDistanceDimension(verticalLine.startSketchPoint, verticalLine.endSketchPoint, adsk.fusion.DimensionOrientations.VerticalDimensionOrientation, verticalLine.endSketchPoint.geometry)
        sketchDimension.parameter.expression = 'RT'
        sketchDimension = sketchDimensions.addDistanceDimension(pointLine.startSketchPoint, pointLine.endSketchPoint, adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation, pointLine.startSketchPoint.geometry)
        sketchDimension.parameter.expression = f'CW*0.75/{num_riblets}'

        sketchDimension = sketchDimensions.addDistanceDimension(pointLine.startSketchPoint, pointLine.endSketchPoint, adsk.fusion.DimensionOrientations.VerticalDimensionOrientation, pointLine.startSketchPoint.geometry, False)
        riblet_peaks.append(sketchDimension.parameter.value)
        sketchDimension.deleteMe()

        prev_conicCurve = conicCurve

    for i in range(len(riblet_peaks)//2):
        riblet_peaks[i+1] += riblet_peaks[i]
        riblet_peaks[len(riblet_peaks) - i - 1] = riblet_peaks[i]

    cutoutSketch.isVisible = False
    
    # ******************************** Path Code ********************************
    pathSketch = sketches.add(rootComp.yZConstructionPlane)
    splines = pathSketch.sketchCurves.sketchFittedSplines
    constraints = pathSketch.geometricConstraints
    sketchDimensions = pathSketch.sketchDimensions
    sketchLines = pathSketch.sketchCurves.sketchLines

    for i in range(num_riblets + 1):
        points = adsk.core.ObjectCollection.create()
        displacement = -crown_height*4*(i/num_riblets)*(i/num_riblets-1)
        k = num_riblets/2 - i

        # Define the points the spline with fit through.
        points.add(adsk.core.Point3D.create(-height-displacement, - depth/2, -length*i/num_riblets + length/2))
        points.add(adsk.core.Point3D.create(-height-riblet_depth/2-displacement, depth/10 - depth/2, -length*i/num_riblets + length/2)) # + length*k/25))
        points.add(adsk.core.Point3D.create(-height-riblet_depth-displacement, riblet_peaks[i] + depth/2, -length*i/num_riblets + length/2))

        spline = splines.add(points)
    
    pathSketch.isVisible = False
    
    # ******************************** Surface Code ********************************
    wingLine1 = sketchLines.addByTwoPoints(adsk.core.Point3D.create(-height, depth/2, -length/1.5), adsk.core.Point3D.create(-height, - depth/2, -length/1.5))
    wing1 = sketchLines.addByTwoPoints(adsk.core.Point3D.create(-height, depth/2, -length/1.5), adsk.core.Point3D.create(-height-riblet_depth, depth/2, -length/2))

    wingLine2 = sketchLines.addByTwoPoints(adsk.core.Point3D.create(-height, depth/2, length/1.5), adsk.core.Point3D.create(-height, - depth/2, length/1.5))
    wing2 = sketchLines.addByTwoPoints(adsk.core.Point3D.create(-height, depth/2, length/1.5), adsk.core.Point3D.create(-height-riblet_depth, depth/2, length/2))

    surfaces = adsk.core.ObjectCollection.create()
    splines = profileSketch.sketchCurves.sketchFittedSplines
    for i in range(num_riblets):
        prof = rootComp.createOpenProfile(splines.item(i), False)
        
        paths = pathSketch.sketchCurves.sketchFittedSplines
        path = rootComp.features.createPath(paths.item(i + round(1 - i/num_riblets)))
        # guide = rootComp.features.createPath(paths.item(i + 1))

        sweeps = rootComp.features.sweepFeatures
        sweepInput = sweeps.createInput(prof, path, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        sweepInput.extent = adsk.fusion.SweepExtentTypes.FullExtentsExtentType
        sweepInput.orientation = adsk.fusion.SweepOrientationTypes.ParallelOrientationType
        # sweepInput.guideRail = guide
        sweepInput.isSolid = False
        sweep = sweeps.add(sweepInput)

        surface = sweep.bodies.item(0)
        surfaces.add(surface)
    
    prof = rootComp.createOpenProfile(wing1)

    paths = pathSketch.sketchCurves.sketchFittedSplines
    path = rootComp.features.createPath(wingLine1)
    guide = rootComp.features.createPath(paths.item(num_riblets))

    sweeps = rootComp.features.sweepFeatures
    sweepInput = sweeps.createInput(prof, path, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    sweepInput.guideRail = guide
    sweepInput.extent = adsk.fusion.SweepExtentTypes.FullExtentsExtentType
    sweepInput.isSolid = False
    sweep = sweeps.add(sweepInput)
    surface = sweep.bodies.item(0)
    surfaces.add(surface)

    prof = rootComp.createOpenProfile(wing2, False)
        
    paths = pathSketch.sketchCurves.sketchFittedSplines
    path = rootComp.features.createPath(wingLine2)
    guide = rootComp.features.createPath(paths.item(0))

    sweeps = rootComp.features.sweepFeatures
    sweepInput = sweeps.createInput(prof, path, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    sweepInput.guideRail = guide
    sweepInput.extent = adsk.fusion.SweepExtentTypes.FullExtentsExtentType
    sweepInput.isSolid = False
    sweep = sweeps.add(sweepInput)
    surface = sweep.bodies.item(0)
    surfaces.add(surface)
    
    # Define tolerance with 1 cm.
    tolerance = adsk.core.ValueInput.createByReal(0.1)
    
    stitches = rootComp.features.stitchFeatures
    stitchInput = stitches.createInput(surfaces, tolerance, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    stitchInput.isSolid = False
    stitchFeature = stitches.add(stitchInput)

    curve_list = adsk.core.ObjectCollection.create()
    curve_list.add(cutoutSketch.sketchCurves.sketchFittedSplines.item(0))
    for i in range(cutoutSketch.sketchCurves.sketchConicCurves.count):
        curve_list.add(cutoutSketch.sketchCurves.sketchConicCurves.item(i))
    openProfile = rootComp.createOpenProfile(curve_list)

    extrudes = rootComp.features.extrudeFeatures
    extrudeInput = extrudes.createInput(openProfile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    extrudeInput.isSolid = False
    
    # Define the extent with a distance extent of 3 cm.
    distance = adsk.core.ValueInput.createByReal(3.0)
    extrudeInput.setDistanceExtent(False, distance)
    
    # Create the extrusion.
    extrude = extrudes.add(extrudeInput)
    
    # Get the body created by extrusion
    body = extrude.bodies[0]

    splitBodyFeats = rootComp.features.splitBodyFeatures
    splitBodyInput = splitBodyFeats.createInput(stitchFeature.bodies.item(0), body, True)
    
    # Create split body feature
    splitBody = splitBodyFeats.add(splitBodyInput)

    body.isVisible = False
    splitBody.bodies.item(1).isVisible = False
    

# This event handler is called when the command terminates.
def command_destroy(args: adsk.core.CommandEventArgs):
    global local_handlers
    local_handlers = []
    