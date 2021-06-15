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
Overwrites any body names with those of the parent component name. Workflow is then identical to **Renaame Default bodies**

## Overwrite existing outputs
When enabled, any pre-existing files in the output location with the same file name will be overwritten

## Ignore hidden bodies, Ignore hidden components
With these enabled, you can restrict the output by toggling component visibility. 
This means you can quickly select which parts you want to export by toggling the 'light bulb' at the component or body level. 

Particularly useful for sassemblies with multiple configurations, tool bodies or other projections that you may not wish to export.

It also facilitates exporting all bodies in a parametric design whilst keeping the view less congested by turning off some of the generated bodies.

# Here be dragons
This program actively generates files based on several naming levers. There is a risk of overwriting files, or bodies being skipped if they share an identical name with another body

There is also a bug with components nested inside other components. 