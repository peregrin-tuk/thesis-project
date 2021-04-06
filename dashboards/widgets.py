import ipywidgets as widgets
from ipywidgets import HBox, VBox, Label, Layout, AppLayout


### STYLES ###

style = {
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
    style=style
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
    style=style
)

tempSlider = widgets.FloatSlider(
    # description='Temperature',
    value=0.5,
    min=0,
    max=1.5,
    step=0.1,
    readout_format='.1f')


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

button_layout = Layout(margin='20px 0')

applySettingsButton = widgets.Button(
    description='  APPLY SETTINGS',
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