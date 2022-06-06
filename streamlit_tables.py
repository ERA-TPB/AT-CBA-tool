import numpy as np
import pandas as pd
import streamlit as st

import inputs
import outputs
import CBA



inputs.saved_vars = pd.DataFrame(columns=['parameter','dimension_0','dimension_1','name_0','name_1','value'])
inputs.saved_vars.set_index(['parameter','dimension_0','dimension_1'],inplace=True)

def parameter_dimensions(parameter):
    if len(inputs.default_parameters.loc[parameter].groupby(level=['dimension_0']).first().index)==0:
        dimensions = 0
    elif len(inputs.default_parameters.loc[parameter].groupby(level=['dimension_1']).first().index)==0:
        dimensions = 1
    else:
        dimensions = 2
    return dimensions

def single_input(parameter, percent=False):
    #pull names and default values
    default = inputs.default_parameters.loc[(parameter,np.nan,np.nan),'value']
    text = inputs.default_parameters.loc[(parameter,np.nan,np.nan),'name_0']
    
    head = inputs.parameter_list.loc[parameter,'name']
    subhead = inputs.parameter_list.loc[parameter,'description']

    minvalue = inputs.parameter_list.loc[parameter,'min']
    maxvalue = inputs.parameter_list.loc[parameter,'max']
    stepvalue = inputs.parameter_list.loc[parameter,'step']

    if stepvalue < .01:
        paraformat = "%.3f"    
    elif stepvalue < .1:
        paraformat = "%.2f"
    elif stepvalue < 1:
        paraformat = "%.1f"
    else:
        paraformat = "%.0f"
    
    #streamlit code
    st.subheader(head)
    #expander_name.subheader(subhead)

    col = st.columns(3)

    widget = col[0].number_input(
        subhead,
        value=default,
        min_value=minvalue,
        max_value=maxvalue,
        step=stepvalue,
        format=paraformat,
        key=parameter
        )
    
    inputs.saved_vars.loc[parameter,'value'] = widget
    inputs.saved_vars.loc[parameter,'name_0'] = text


    return widget, head , subhead, paraformat

def column_input(parameter, percent=False):
    defaults = inputs.default_parameters.loc[parameter].reset_index(level=1, drop=True)
    default = defaults['value']
    text = defaults['name_0']

    head = inputs.parameter_list.loc[parameter,'name']
    subhead = inputs.parameter_list.loc[parameter,'description']

    minvalue = inputs.parameter_list.loc[parameter,'min']
    maxvalue = inputs.parameter_list.loc[parameter,'max']
    stepvalue = inputs.parameter_list.loc[parameter,'step']

    if stepvalue < .01:
        paraformat = "%.3f"
    elif stepvalue < .1:
        paraformat = "%.2f"
    elif stepvalue < 1:
        paraformat = "%.1f"
    else:
        paraformat = "%.0f"
    
    widget = pd.DataFrame(index = defaults.index)
    widget.index.rename(inputs.parameter_list.loc[parameter,'dimension_0'],inplace=True)

    #streamlit code
    st.subheader(head)
    st.markdown(subhead)

    if len(default) < 4:
        col = st.columns(len(default))
    if len(default) > 3:
        col = st.columns(4)
    
    n=0
    for row in widget.index:
        widget.loc[row,'value'] = col[n].number_input(
            text.loc[row],
            value=default.loc[row],
            min_value=minvalue,
            max_value=maxvalue,
            step=stepvalue,
            format=paraformat,
            key=str(parameter)+"-"+str(row)
            )

        inputs.saved_vars.loc[(parameter,row,""),'value'] = widget.loc[row,'value']
        inputs.saved_vars.loc[(parameter,row,""),'name_0'] = text.loc[row]


        n=n+1
        if n == 4:
            n = 0
    
    if percent==True and round(widget['value'].sum(axis=0),2)!=100:
        st.error("Total must equal 100%, \n Currently " + str(widget['value'].sum(axis=0))+'%')
    
    return widget, head, subhead, paraformat

def table_input(parameter, percent=False):
    defaults = inputs.default_parameters.loc[parameter]
    default = defaults['value']
    columnnames = inputs.default_parameters.loc[parameter].index.get_level_values('dimension_0').unique().tolist()
    rownames = inputs.default_parameters.loc[parameter].index.get_level_values('dimension_1').unique().tolist()
    
    head = inputs.parameter_list.loc[parameter,'name']
    subhead = inputs.parameter_list.loc[parameter,'description']

    minvalue = inputs.parameter_list.loc[parameter,'min']
    maxvalue = inputs.parameter_list.loc[parameter,'max']
    stepvalue = inputs.parameter_list.loc[parameter,'step']

    if stepvalue < .01:
        paraformat = "%.3f"
    elif stepvalue < .1:
        paraformat = "%.2f"
    elif stepvalue < 1:
        paraformat = "%.1f"
    else:
        paraformat = "%.0f"

    widget = pd.DataFrame(index = defaults.index)
    widget.index.rename(inputs.parameter_list.loc[parameter,['dimension_0','dimension_1']],inplace=True)

    #streamlit code
    st.subheader(head)
    st.markdown(subhead)

    col=st.columns(len(columnnames))
    n=0
    for column in columnnames:
        col[n].markdown(defaults.loc[(column),'name_0'].iloc[0])
        for row in rownames:
            widget.loc[(column,row),'value'] = col[0+n].number_input(
                defaults.loc[(column,row),'name_1'],
                value=default.loc[column,row],
                min_value=minvalue, max_value=maxvalue,
                step=stepvalue, format=paraformat,
                key=str(parameter)+"-"+str(column)+"-"+str(row)
                )
            
            inputs.saved_vars.loc[(parameter,column,row,),'value'] = widget.loc[(column,row),'value']
            inputs.saved_vars.loc[(parameter,column,row),'name_0'] = defaults.loc[(column),'name_0'].iloc[0]
            inputs.saved_vars.loc[(parameter,column,row),'name_1'] = defaults.loc[(column,row),'name_1']

        if percent==True and round(widget.loc[(column)].value.sum(axis=0),2)!=100:
            col[n].error("Total must equal 100%, \n Currently " + str((widget.loc[(column)].value.sum(axis=0)))+'%')
        n=n+1
    return widget, head, subhead, paraformat
       

def number_table(parameter, percent=False):
    """Return a Pandas DataFrame shaped to match the defaults .csv which is set equal to a streamlit
    number input element. Also append the DataFrame to exported_inputs"""

    parafarmat_dict={
        "%.0f":'{:.0f}',
        "%.3f":'{:.3f}',
        "%.2f":'{:.2f}',
        "%.1f":'{:.1f}',
    }

    if parameter_dimensions(parameter)==0:
        df, name, description, paraformat = single_input(parameter, percent)
        outputs.exported_inputs[name] = description, df, parafarmat_dict[paraformat]

    if parameter_dimensions(parameter)==1:
        df, name, description, paraformat = column_input(parameter, percent)
        outputs.exported_inputs[name] = description, df, parafarmat_dict[paraformat]

    if parameter_dimensions(parameter)==2:
        df, name, description, paraformat = table_input(parameter, percent)
        outputs.exported_inputs[name] = description, df.unstack(), parafarmat_dict[paraformat]
    return df

def help_button(parameter):
    """Create a stremlit help button that opens help_text/[parameter].txt in the sidebar"""

    if st.button('Help',key=parameter+' help button'):
        st.sidebar.markdown(open('help_text/'+parameter+'.txt').read())#, unsafe_allow_html=True)

def sensitivity_test(sensitivity,bounding_parameter=None,convert_to_decimal=True):
    """Adds two rows with a streamlit number inputs, takes these inputs to call
    do_sensitivity_CBA and displays the high level CBA results in the row. Default
    values and text are defined in names/sensitivity_test.csv"""

    defaults = inputs.sensitivities.loc[sensitivity].copy()
    cols = st.columns(4)

    if bounding_parameter == None:
        up_min = defaults['up_min']
        down_max = defaults['down_max']
    else:
        up_min = bounding_parameter
        down_max = bounding_parameter
        if up_min > defaults['up_default']:
            defaults['up_default'] = up_min + 1
        if down_max < defaults['down_default']:
            defaults['down_default'] = down_max - 1



    cols[0].markdown("")
    sens_up_input= cols[0].number_input(
        min_value=up_min,
        max_value=defaults['up_max'],
        value=defaults['up_default'],
        step=defaults['step'],
        label=defaults['up_name'],
        key=sensitivity+' up',
        format = "%.0f"
        )
    if convert_to_decimal == True:
        sens_up = sens_up_input/100 + 1
    else:
        sens_up = sens_up_input
    sens_up_results = CBA.do_sensitivity_CBA(**{sensitivity: sens_up})
    df = pd.DataFrame([sens_up_results])
    df.insert(0,'Sensitivity',defaults['up_name'][:-1]+'('+str(sens_up_input)+'%)')

    outputs.exported_sensitivities_table = pd.concat([outputs.exported_sensitivities_table,df])

    df['NPV'] = df['NPV'].map('${:,.0f}'.format)
    df['BCR1'] = df['BCR1'].map("{:,.2f}".format)
    df['BCR2'] = df['BCR2'].map("{:,.2f}".format)

    outputs.exported_sensitivities = pd.concat([outputs.exported_sensitivities,df])

    for i in range(1,4):
        cols[i].markdown("")

    cols[1].metric(
        'Net Present Value',
        value='$'+"{:,.0f}".format(sens_up_results['NPV']),
        delta= "{:,.0f}".format(sens_up_results['NPV']-outputs.results['NPV'])
        )
    cols[2].metric(
        'Benefit Cost Ratio (BCR1)',
        value='{:,.2f}'.format(sens_up_results['BCR1']),
        delta='{:,.2f}'.format(sens_up_results['BCR1']-outputs.results['BCR1'])
        )
    cols[3].metric(
        'Benefit Cost Ratio (BCR2)',
        value='{:,.2f}'.format(sens_up_results['BCR2']),
        delta='{:,.2f}'.format(sens_up_results['BCR2']-outputs.results['BCR1'])
        )
    

    cols[0].markdown("")
    sens_down_input= cols[0].number_input(
        min_value=defaults['down_min'],
        max_value=down_max,
        value=defaults['down_default'],
        step=defaults['step'],
        label=defaults['down_name'],
        key=sensitivity+' down',
        format = "%.0f"
        )
    if convert_to_decimal == True:
        sens_down = sens_down_input/100 + 1
    else:
        sens_down = sens_down_input
    sens_down_results = CBA.do_sensitivity_CBA(**{sensitivity: sens_down})
    
    df = pd.DataFrame([sens_down_results])
    df.insert(0,'Sensitivity',defaults['down_name'][:-1]+'('+str(sens_down_input)+'%)')

    outputs.exported_sensitivities_table = pd.concat([outputs.exported_sensitivities_table,df])

    df['NPV'] = df['NPV'].map('${:,.0f}'.format)
    df['BCR1'] = df['BCR1'].map("{:,.2f}".format)
    df['BCR2'] = df['BCR2'].map("{:,.2f}".format)

    outputs.exported_sensitivities = pd.concat([outputs.exported_sensitivities,df])


    cols[1].metric(
        'Net Present Value',
        value='$'+"{:,.0f}".format(sens_down_results['NPV']),
        delta= "{:,.0f}".format(sens_down_results['NPV']-outputs.results['NPV'])
        )
    cols[2].metric(
        'Benefit Cost Ratio (BCR1)',
        value='{:,.2f}'.format(sens_down_results['BCR1']),
        delta='{:,.2f}'.format(sens_down_results['BCR1']-outputs.results['BCR1'])
        )
    cols[3].metric(
        'Benefit Cost Ratio (BCR2)',
        value='{:,.2f}'.format(sens_down_results['BCR2']),
        delta='{:,.2f}'.format(sens_down_results['BCR2']-outputs.results['BCR1'])
        )

    st.markdown('''---''')

