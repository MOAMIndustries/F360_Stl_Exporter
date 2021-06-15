import adsk.core, adsk.fusion, adsk.cam, traceback
from datetime import datetime
from pathlib import Path
from typing import NamedTuple, List, Set
import re
import hashlib
import os

handlers = []

class Ctx(NamedTuple):
    ''' Context manager. Passed between functions to provide paramaters
    '''
    folder: str
    app: adsk.core.Application
    prefix: str
    suffix: str
    rename_default_bodies: bool
    set_bodies_to_component_name: bool
    do_not_overwrite_outputs: bool

    def extend(self, other):
        return self._replace(folder=self.folder / other)

    @property
    def design(self):
        product = self.app.activeProduct
        return adsk.fusion.Design.cast(product)

    @property
    def root_component(self):
        product = self.app.activeProduct
        design = adsk.fusion.Design.cast(product)
        rootComp = design.rootComponent   
        return design.rootComponent
    
    def create_folder(self):
        try:
            os.makedirs(self.folder)
        except FileExistsError:
            pass



def export_job(ctx: Ctx):
    '''
    Processes the export job based on settings input in the dialog box
    '''
    ctx.create_folder()

    exportMgr = ctx.design.exportManager

    # Process any bodies At the root level
    process_bodies(
        ctx, 
        ctx.root_component.bRepBodies,
        ctx.root_component.name,
        exportMgr
        )
    
    # Process bodies within components
    process_components(
        ctx, 
        ctx.root_component.occurrences,
        exportMgr
        )
    
    print("hello")

def process_components(ctx, components, exportManager):
    '''
    Itterate through each component in the active design and process
    any bodies that need to be exported
    '''
    for component in components:
        if not component.isLightBulbOn and ctx.ignore_hidden_components:
            continue
        component_name = component.name

        process_bodies(ctx, component.bRepBodies, component_name, exportManager)

def process_bodies(ctx, bodies, parent_name, exportManager):
    '''
    Itterate through each body withing the corrent occurence (Fusions object name for component)
    Exporting files as STLs based on parameters stored in the context object ctx
    '''
    body_count = 0
    for body in bodies:
        body_count += 1
        

        if not body.isLightBulbOn and ctx.ignore_hidden_bodies:
            # Skip this body
            continue

        body_name = body.name
        
        # Check if name is default
        if re.match(r'Body\d+$',body_name):
            if ctx.rename_default_bodies:
                if len(bodies) == 1:
                    body_name = parent_name
                else:
                    body_name= f"{parent_name}_{body_count}"
        
        # There is a risk of overwrite here if there is duplicated component names
        if ctx.set_bodies_to_component_name:
            if len(bodies) == 1:
                body_name = parent_name[:-2]
            else:
                body_name= f"{parent_name[:-2]}_{body_count}"           
        
        body_name = sanitize_filename(body_name)
        body_name = f"{ctx.prefix}{body_name}{ctx.suffix}.stl"

        export_path = os.path.join(ctx.folder, body_name)
        if os.path.exists(export_path):
            if ctx.do_not_overwrite_outputs:
                continue
        
        export_job = exportManager.createSTLExportOptions(body, export_path)
        exportManager.execute(export_job)


class ExporterCommandExecuteHandler(adsk.core.CommandEventHandler):
    '''
    Command execution handler, instantiated by dialog when "ok" is selected
    '''
    def notify(self, args):
   #     try:
        inputs = args.command.commandInputs

        app = adsk.core.Application.get()
        ui = app.userInterface

        ctx = Ctx(
            app = app,
            folder = inputs.itemById('directory').value,
            prefix= inputs.itemById('prefix').value,
            suffix= inputs.itemById('suffix').value,
            rename_default_bodies = inputs.itemById('rename_bodies').value,
            do_not_overwrite_outputs = not inputs.itemById('overwrite_outputs').value,
            set_bodies_to_component_name = inputs.itemById('component_level_naming').value,
            ignore_hidden_bodies = inputs.itemById('ignore_hidden_bodies').value,
            ignore_hidden_compoents = inputs.itemById('ignore_hidden_compoents').value,
        )

        export_job(ctx)

        ui.messageBox("Lets just assume it worked")

       # except:
       #     tb = traceback.format_exc()


#region UI Elements
class ExporterCommandCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
    def notify(self, args):
        try:
            app = adsk.core.Application.get()
            product = app.activeProduct
            design = adsk.fusion.Design.cast(product)
            rootComp = design.rootComponent
            project_name = sanitize_project_name(rootComp.name)

            cmd = args.command
            cmd.setDialogInitialSize(600, 400)
            
            # http://help.autodesk.com/view/fusion360/ENU/?guid=GUID-C1BF7FBF-6D35-4490-984B-11EB26232EAD
            cmd.isExecutedWhenPreEmpted = False

            # Form handlers
            onExecute = ExporterCommandExecuteHandler()
            cmd.execute.add(onExecute)
            onDestroy = ExporterCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            handlers.append(onExecute)
            handlers.append(onDestroy)

            inputs = cmd.commandInputs
            inputs.addStringValueInput('directory', 'Output Directory', str(Path.home() / 'Documents/' / project_name ))
            inputs.addStringValueInput('prefix', 'File prefix', "")
            inputs.addStringValueInput('suffix', 'File suffix', "")
            inputs.addBoolValueInput('rename_bodies', 'Rename default bodies?', True, '', True)
            inputs.addBoolValueInput('component_level_naming', 'Set name at component level?', True, '', False)
            inputs.addBoolValueInput('overwrite_outputs', 'Overwrite existing outputs?', True, '', True)
            inputs.addBoolValueInput('ignore_hidden_bodies', 'Ignore hidden bodies?', True, '', True)
            inputs.addBoolValueInput('ignore_hidden_compoents', 'Ignore hidden components?', True, '', True)
        except:
            adsk.core.Application.get().userInterface.messageBox(traceback.format_exc())


class ExporterCommandDestroyHandler(adsk.core.CommandEventHandler):
    def notify(self, args):
        try:
            adsk.terminate()
        except:
            adsk.core.Application.get().userInterface.messageBox(traceback.format_exc())
#endregion UI Elements


def sanitize_project_name(name: str) -> str:
    return re.sub(r'[:\\*?<>| \/]', '_', name)


def sanitize_filename(name: str) -> str:
    """
    Remove "bad" characters from a filename. Right now just punctuation that Windows doesn't like
    If any chars are removed, we append _{hash} so that we don't accidentally clobber other files
    since eg `Model 1/2` and `Model 1 2` would otherwise have the same name
    """
    name = name.replace(" ","_")
    with_replacement = re.sub(r'[:\\*?<>|\/]', '_', name)
    if name == with_replacement:
        return name
    hash = hashlib.sha256(name.encode()).hexdigest()[:8]
    return f'{with_replacement}_{hash}'



def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        cmd_defs = ui.commandDefinitions
        
        CMD_DEF_ID = 'Bulk_Exporter'
        cmd_def = cmd_defs.itemById(CMD_DEF_ID)
        # This isn't how all the other demo scripts manage the lifecycle, but if we don't delete the old
        # command then we get double inputs when we run a second time
        if cmd_def:
            cmd_def.deleteMe()

        cmd_def = cmd_defs.addButtonDefinition(
            CMD_DEF_ID, 
            'Export all visible bodies', 
            'Tooltip',
        )
        
        cmd_created = ExporterCommandCreatedEventHandler()
        cmd_def.commandCreated.add(cmd_created)
        handlers.append(cmd_created)

        cmd_def.execute()

        adsk.autoTerminate(False)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

