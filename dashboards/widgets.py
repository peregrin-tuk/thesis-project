import ipywidgets as widgets
from ipywidgets import Layout


### STYLES ###

description_style = {
    'description_width': 'initial',
    }



### INPUT ###

inputHeading = widgets.HTML(
    value="<h2>Select Input Melody<h2>",
    placeholder='Select Input Melody',
)

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
    min=1,
    max=1000,
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
        tooltip=description,
        description='',
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