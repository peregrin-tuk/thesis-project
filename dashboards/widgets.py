from IPython.display import display
from src.io.plot import multi_evaluation_bars
import ipywidgets as widgets
from ipywidgets import Layout
from typing import List


### STYLES ###

description_style = {
    'description_width': 'initial',
    }



### INPUT ###

inputHeading = widgets.HTML(
    value="<h2>Select Input Melody<h2>",
    placeholder='Select Input Melody',
)

# inputSelect = widgets.ToggleButtons(
#     options=['Twinkle, Twinkle', 'Toto - Africa', 'Mozart - Eine kleine Nachtmusik', 'Mancini - Pink Panther'],
#     description='Select Input:',
#     tooltips=['2 Bars', '2 Bars from the Intro', '4 Bars Main Theme', '4 Bars Main Theme'],
#     style=style
# )

inputSelect = widgets.Dropdown(
    options=[('...', 1)],
    value=1,
    description='Select Input:',
    style=description_style
)

inputUpload = widgets.FileUpload(
    accept='.mid',
    multiple=False,
    description='Upload MIDI'
)


### GENERATION ###

generationHeading = widgets.HTML(
    value="<h2>Generation Settings<h2>",
    placeholder='Generation Settings',
)

checkpointSelect = widgets.Dropdown(
    options=[('...', 1)],
    value=1,
    # description='Model & Checkpoint:',
    style=description_style
)

tempSlider = widgets.FloatSlider(
    # description='Temperature',
    value=0.5,
    min=0,
    max=1.5,
    step=0.1,
    readout_format='.1f'
)

generationAmount = widgets.BoundedIntText(
    value=1,
    min=0,
    max=50,
    step=1,
    # description='Amount:',
    disabled=False,
    width=100
)

generationInfo = widgets.HTML(
    value="<p style='color:red;'>No generator initialized.<p>",
    placeholder='Generation Info',
)


### ADAPTATION ###

adaptationHeading = widgets.HTML(
    value="<h2>Select Adaptation Steps<h2>",
    placeholder='Select Adaptation Steps',
)

stepsSelect = widgets.SelectMultiple(
    options=['Operation 1', 'Operation 2', 'Operation 3'],
    #value=['Oranges'], # set to last selected ?
    #rows=10, # set to len(ops)
    #description='Steps',
)


### BUTTONS ###

button_layout = Layout(margin='20px 0', width='auto')

applyGenerationSettingsButton = widgets.Button(
    description='  APPLY GENERATION SETTINGS',
    disabled=False,
    button_style='info',
    icon='gear',
    layout=button_layout
)

applyAdaptationSettingsButton = widgets.Button(
    description='  APPLY ADAPTATION SETTINGS',
    disabled=False,
    button_style='info',
    icon='gear',
    layout=button_layout
)

startButton = widgets.Button(
    description='  RUN',
    disabled=False,
    button_style='success',
    icon='play',
    layout=button_layout
)

### PAGINATION ###

def paginationSlider(number: int, description: str):
    return widgets.IntSlider(
        description=description,
        value=0,
        min=0,
        max=number
    )

def iconButton(icon: str, description: str = '', style: str = 'info'):
    return widgets.Button(
        description=description,
        disabled=False,
        button_style=style,
        icon=icon,
        layout=Layout(width='36px', height='36px')
    )


### HEADINGS ###

def h2_heading(text: str):
    return widgets.HTML(
        value="<h2>" + text + "<h2>",
        placeholder=text,
    )