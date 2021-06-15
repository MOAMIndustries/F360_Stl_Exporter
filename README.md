# Fusion 360 Bulk STL exporter 
This is a work in progress and mostly serves as a scratch pad for my work.

Use it at your own peril!

It provides a mechanism to export all bodies within the open project to STL files.

# Features
Incomplete and untested (I think you get the gist now...)

## Folder creation
It will create a folder at the path specified and write all objects to this folder.

## Prefix
Appends a common prefix to all output file names. This is useful for multiple exports of parameteric models 
eg:
* 50x50_
* 30x30_
* Super_Final_last_version_

## Suffix
As above. Appends a common suffix to all output file names

## Rename Default bodies
Will rename bodies with a default name _Body1, Body2, etc_ based on the name of the parent component. 
If the component with the name _SomePart_ only has a single body, the output file name would be _SomePart.stl_ (assuming there are is no prefix or suffix). If there is multiple bodies, a number will be appended after the name _SomePart\_1.stl SomePart\_2.stl_

## Set Name at component level
Overwrites any body names with those of the parent component name. Workflow is then identical to **Rename Default bodies**

n.b. The incremental number applied to each component name is removed, _:1 :2 :3_ etc. This means, if you have multiple copies of the same name in your design, these will overwrite each other

## Overwrite existing outputs
When enabled, any pre-existing files in the output location with the same file name will be overwritten

## Ignore hidden bodies, Ignore hidden components
With these enabled, you can restrict the output by toggling component visibility. 
This means you can quickly select which parts you want to export by toggling the 'light bulb' at the component or body level. 

Particularly useful for sassemblies with multiple configurations, tool bodies or other projections that you may not wish to export.

It also facilitates exporting all bodies in a parametric design whilst keeping the view less congested by turning off some of the generated bodies.

# Installation
1. Download this repo and unzip it somewhere.
2. In Fusion, goto TOOLS > ADD-INS > Scripts and Add-Ins (or just hit Shift+S)
3. Next to "My Scripts", hit the green plus icon
4. Select the folder where you unzipped it
5. "_Exporter_" should now appear under "My Scripts"

# Usage
1. Goto Scripts and Add-Ins
2. Select _Body Exporter_ from "My Scripts"
3. Hit Run. It will take a second to display the options panel as it is fetching your list of projects.

After selecting your options and hitting okay, your fusion360 instance will be unusable. The script will be potentially opening and exporting a lot of bodies. It will do this as a background process though.

# Modifications and debugging
This is my first fusion360 so I hope these notes help anyone else getting started with generating or modifying a plugin
You will need VSCode installed to modify and debug Fusion360 plugins
1. Goto Scripts and Add-Ins
2. Select _Body Exporter_ from "My Scripts"
3. Hit Edit.
This will open the script in your editor and attach a remote debugger automatically.
You can then launch the script with breakpoints by pressing 'F5'. It can be a little flakey though 
Detailed documentation on the API, including sample code can be found here:
https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-A92A4B10-3781-4925-94C6-47DA85A4F65A

# Here be dragons
This program actively generates files based on several naming levers. There is a risk of overwriting files, or bodies being skipped if they share an identical name with another body

There is also a bug with components nested inside other components. 

It is not doing any modifications to component features, sketches or parameters. 

# Created By
Andrew Van Dam
https://MOAMindustries.com

Based on the work by aconz2
https://github.com/aconz2/Fusion360Exporter