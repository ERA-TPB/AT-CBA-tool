import reportlab
import reportlab.rl_config
import reportlab.lib.styles
import pdfdocument.document
import copy
import pandas as pd
import matplotlib
import numpy as np
import PyPDF2
import streamlit as st
import plotly.express as px
from svglib.svglib import svg2rlg

import inputs
import outputs

def df2table(dataframe,style,format='{:,.2f}'):
    """Converts a Pandas DataFrame to a reportlab table. Also drops column levels named None"""
    df = dataframe
    if len(df.columns.names)>1 and None in df.columns.names:
        df = df.droplevel(None,axis=1)
    first_row = [df.index.name] + df.columns.tolist()
    if format is not None:
        try:
            for column in df:
                df[column] = df[column].map(format.format)
        except:
            pass
    array = np.array(df.reset_index())

    table_list = array.tolist()
    table_list.insert(0,first_row)
    table = reportlab.platypus.tables.Table(table_list, style=style)
    return table

table_count = 1
chart_count = 1

#Table style
ts = [('ALIGN', (0, 0), (0, 5), 'LEFT'),
    ('FONT', (0,0), (-1,0), 'Helvetica'),
    ('LINEABOVE',(0,0),(4,0),1,reportlab.lib.colors.black),
    ('LINEBELOW',(0,0),(4,0),0.5,reportlab.lib.colors.black),
    ('FONTSIZE', (1,0), (1, 5), 10),
    ('ALIGN', (1, 0), (4, 30), "RIGHT"),
    ('LINEBELOW',(0,-1),(4,-1),1,reportlab.lib.colors.black)]

PAGE_HEIGHT=reportlab.rl_config.defaultPageSize[1]
PAGE_WIDTH=reportlab.rl_config.defaultPageSize[0]
styles = reportlab.lib.styles.getSampleStyleSheet()
Title = ""
pageinfo = "Headline Results"
def myFirstPage(canvas, doc):
    canvas.saveState() 
    canvas.setFont('Helvetica',10)
    canvas.drawString(97.5 * reportlab.lib.units.mm, 19.05 * reportlab.lib.units.mm, "1")
    canvas.restoreState()
def myLaterPages(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica',10)
    canvas.drawString(97.5 * reportlab.lib.units.mm, 19.05 * reportlab.lib.units.mm, "%d" % (doc.page))
    canvas.restoreState()

class MyPdfDocument(pdfdocument.document.PDFDocument):
    def __init__(self, *args, **kwargs,):
        super(MyPdfDocument, self).__init__(*args, **kwargs)
        self.story = [reportlab.platypus.Spacer(1,0)]
        self.inputs = input

    def generate_style(self, font_name=None, font_size=None):
        super(MyPdfDocument, self).generate_style(font_name, font_size)
        _styles = reportlab.lib.styles.getSampleStyleSheet()
        self.style.normal = copy.deepcopy(_styles['Normal'])
        self.style.normal.alignment = reportlab.lib.enums.TA_CENTER
        self.style.normal.fontName = '%s' % 'Helvetica'
        self.style.normal.fontSize = 17
        self.style.normal.firstLineIndent = 0.4 * reportlab.lib.units.cm
        self.style.normal.spaceBefore = 12.1
        self.style.regular = copy.deepcopy(self.style.normal)
        self.style.regular.fontName = '%s' % 'Helvetica-Bold'
        self.style.regular.alignment = reportlab.lib.enums.TA_LEFT
        self.style.regular.fontSize = 14
        self.style.summary = copy.deepcopy(self.style.regular)
        self.style.summary.fontSize = 12
        self.style.table = copy.deepcopy(self.style.normal)
        self.style.table.fontSize = 10
        self.style.plot = copy.deepcopy(self.style.regular)
        self.style.plot.fontSize = 10

    def image(self, image_path, width=19 * reportlab.lib.units.cm, style=None):
        img = matplotlib.image.imread(image_path)
        x, y = img.shape[:2]
        image = reportlab.platypus.Image(image_path, width=width, height=width * x / y)
        self.story.append(image)

    def drawing(self,image_path,title):
        self.this_chart = [reportlab.platypus.Spacer(1,0)]
        global chart_count
        text = "Chart "+str(chart_count)+": "+title
        chart_count = chart_count +1

        self.this_chart.append(reportlab.platypus.Paragraph(text, self.style.table))
        self.this_chart.append(reportlab.platypus.Spacer(1,0.133333*reportlab.lib.units.inch))
        
        drawing = svg2rlg(image_path)
        self.this_chart.append(drawing)
        self.this_chart.append(reportlab.platypus.Spacer(1,0.133333*reportlab.lib.units.inch))
        self.this_chart = reportlab.platypus.KeepTogether(self.this_chart)
        
        
        self.story.append(self.this_chart)

    
    
    def together_table(self,heading,dataframe,style=ts,format='{:,.2f}',column_names=None,big_head=None):
        self.this_table = [reportlab.platypus.Spacer(1,0)]
        global table_count
        if big_head is not None:
            self.this_table.append(reportlab.platypus.Paragraph(big_head, self.style.summary))
        text = "Table "+str(table_count)+": "+heading
        self.inputs = input
        self.this_table.append(reportlab.platypus.Paragraph(text, self.style.table))
        self.this_table.append(reportlab.platypus.Spacer(1,0.133333*reportlab.lib.units.inch))
        if column_names is not None:
            if len(dataframe.columns) == len(column_names):
                dataframe.columns = column_names
        table = df2table(dataframe,style,format)
        self.this_table.append(table)
        table_count = table_count + 1
        self.this_table.append(reportlab.platypus.Spacer(1,0.3125*reportlab.lib.units.inch))
        self.this_table = reportlab.platypus.KeepTogether(self.this_table)
        self.story.append(self.this_table)
    

    def result(self):

        # Create document and title
        doc = reportlab.platypus.SimpleDocTemplate(filename=inputs.facility_name+' Cost-Benefit-Analysis.pdf', title=inputs.facility_name+' Cost-Benefit-Analysis')
        resulttext = inputs.facility_name+' Cost-Benefit-Analysis'
        self.story.append(reportlab.platypus.Paragraph(resulttext, self.style.normal))
        self.story.append(reportlab.platypus.Spacer(1,0.3125*reportlab.lib.units.inch))
        
        global table_count
        table_count = 1
        global chart_count
        chart_count = 1


        resulttext = "Outputs"         
        self.story.append(reportlab.platypus.Paragraph(resulttext, self.style.regular))
        self.story.append(reportlab.platypus.Spacer(1,121/720*reportlab.lib.units.inch))
        resulttext = "Summary"
        self.story.append(reportlab.platypus.Paragraph(resulttext, self.style.summary))
        self.story.append(reportlab.platypus.Spacer(1,0.2*reportlab.lib.units.inch))

        resulttext = "Table 1: Headline Results"
        self.story.append(reportlab.platypus.Paragraph(resulttext, self.style.table))
        self.story.append(reportlab.platypus.Spacer(1,1/9*reportlab.lib.units.inch))
        table_list = outputs.headline_results.copy()
        table_list.insert(0,['Metric',''])
        table = reportlab.platypus.tables.Table(table_list, style=ts)
        self.story.append(table)
        self.story.append(reportlab.platypus.Spacer(1,0.3125*reportlab.lib.units.inch))
        
        table_count = table_count +1
        # # Present value tables

        resulttext = "Present value of benefits"
        self.story.append(reportlab.platypus.Paragraph(resulttext, self.style.summary))
        self.story.append(reportlab.platypus.Spacer(1,0.2*reportlab.lib.units.inch))

        discounted_benefits = outputs.results_dict['Discounted Benefts'].copy()

        pv_tables = [
            ['Benefits by Benefit Type',discounted_benefits.groupby('benefit').sum()],
            ['Benefits by Mode', discounted_benefits.groupby('mode').sum()],
            ['Benefits by Mode and diversion source',discounted_benefits.groupby(['mode','from_mode']).sum().unstack()],
            ['Benefits by mode and benefit type',discounted_benefits.groupby(['benefit','mode']).sum().unstack()],
            ['Benefits by year',discounted_benefits.groupby('year').sum()]            
        ]   
        
        for table in pv_tables:
            self.together_table(table[0],table[1],format='${:,.0f}',column_names=['Present Value'])

        resulttext = "Sensitivity Tests"
        self.story.append(reportlab.platypus.Paragraph(resulttext, self.style.summary))
        self.story.append(reportlab.platypus.Spacer(1,0.2*reportlab.lib.units.inch))
        self.together_table('Sensitivity Tests',outputs.exported_sensitivities,format=None)

        self.story.append(reportlab.platypus.PageBreak())
        
        resulttext = 'Benefit charts'
        self.story.append(reportlab.platypus.Paragraph(resulttext, self.style.summary))
        self.story.append(reportlab.platypus.Spacer(1,0.2*reportlab.lib.units.inch))

        margin = {'l': 0,'r': 0, 'b': 0, 't': 0,'pad': 0}
        def fig_format():
            return fig.update_layout(
                margin = {'l': 0,'r': 0, 'b': 0, 't': 0,'pad': 0},
                font_family='Helvetica',
                font_size=8,
                font_color='black',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )


        df = discounted_benefits.groupby('mode').sum()
        fig = px.bar(df,y=df.index,x='value',orientation='h')
        fig_format()
        fig.update_layout(height=200,width=450)
        fig.write_image("images/fig.svg")
        self.drawing("images/fig.svg",'Benefits by mode')

        df = discounted_benefits.groupby('benefit').sum()
        fig = px.bar(df,y=df.index,x='value',orientation='h')
        fig_format()
        fig.update_layout(height=200,width=450)
        fig.write_image("images/fig.svg")
        self.drawing("images/fig.svg",'Benefits by benefit type')

        df = discounted_benefits.groupby('year').sum()
        fig = px.bar(df,y='value',x=df.index,orientation='v')
        fig_format()
        fig.update_layout(height=200,width=450,margin=margin)
        fig.write_image("images/fig.svg")
        self.drawing("images/fig.svg",'Benefits by year')
        
        df = discounted_benefits.groupby(['benefit','mode']).sum().reset_index()
        fig = px.bar(df,y='mode',x='value',color='benefit',orientation='h')
        fig_format()
        fig.update_layout(height=350,width=450,margin=margin)
        fig.update_layout(legend=dict(
            x=0.7,
            y=1,
            traceorder='normal'))
        fig.write_image("images/fig.svg")
        self.drawing("images/fig.svg",'Benefits by mode and benefit type')


        self.story.append(reportlab.platypus.PageBreak())

        # Add heading and discount rate
        resulttext = 'Inputs'
        self.story.append(reportlab.platypus.Paragraph(resulttext, self.style.regular))
        self.story.append(reportlab.platypus.Spacer(1,0.133333*reportlab.lib.units.inch))

        paras = outputs.exported_inputs.copy()

        for para in paras:
            if type(paras[para][1]) == pd.core.frame.DataFrame:
                self.together_table(paras[para][0],paras[para][1],format=paras[para][2],big_head=para)
            else:
                resulttext = para
                self.story.append(reportlab.platypus.Paragraph(resulttext, self.style.summary))
                text = paras[para][0]
                self.story.append(reportlab.platypus.Paragraph(text, self.style.table))
                try:
                    text = paras[para][2].format(paras[para][1])
                except:
                    text = str(paras[para][1])
                self.story.append(reportlab.platypus.Paragraph(text, self.style.table))

        doc.build(self.story, onFirstPage=myFirstPage, onLaterPages=myLaterPages)
    
def write_pdf():
    # Create PDF Document and add results
    result = MyPdfDocument(inputs.facility_name+' Cost-Benefit-Analysis.pdf')
    result.generate_style()
    result.result()
    # total = result.result(discounted_costs, discounted_benefits, input, basic_demand, discount_rate, capex_sensitivity, opex_sensitivity, demand_sensitivity, trip_distance_sensitivity, new_trips_sensitivity, transport_share_sensitivity, divert)
    file = open(inputs.facility_name+' Cost-Benefit-Analysis.pdf', 'rb+')
    reader = PyPDF2.PdfFileReader(file)
    writer = PyPDF2.PdfFileWriter()
    writer.appendPagesFromReader(reader)
    metadata = reader.getDocumentInfo()
    writer.addMetadata(metadata)
    writer.addMetadata({
        '/Author': 'Department of Transport and Main Roads',
        '/Title': inputs.facility_name+' Cost-Benefit-Analysis.pdf',
        '/Subject' : 'Economic Research and Analysis',
        '/Producer' : "CropPDF",
        '/Creator' : "CropPDF",
    })
    writer.write(file)
    file.close()