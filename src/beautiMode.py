# -*- coding: utf-8 -*-
"""
Created on Wed Jan 16 16:48:13 2019

@author: revse
"""
import os
import pandas as pd
import numpy as np
from openpyxl import Workbook
from datetime import datetime
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.utils import coordinate_from_string, column_index_from_string


ddmmyy=datetime.now()
dow = ddmmyy.strftime('%a')
iseldt = ddmmyy.strftime('%d%b%Y')
foldname = ddmmyy.strftime('%d_%b_%Y')

def beautify(defaultpath, df,iselltype,rowlim,htlname,pth,glossary,ftr,pgdf,finaladop):
    os.chdir(pth)
    df = pd.DataFrame(df)
    #=============================df to wb conv =============================================   
    wb = Workbook()
    ws = wb.active
    
    for r in dataframe_to_rows(df, index=False, header=True):
        ws.append(r)

    #===================== column names and index and values===================================          
    col_index = [cell.column for cell in ws[1]]
    col_name = [cell.value for cell in ws[1]]
    
    ind_name = dict(zip(col_index,col_name))
    name_ind = dict(zip(col_name,col_index))    
    #=================== column value from name ================================================
    vals=[]
    for cs in col_name:
        xy = coordinate_from_string('{}1'.format(name_ind[cs])) # returns ('A',-)
        colvalue = column_index_from_string(xy[0])
        vals.append(colvalue)   
    
    name_vals = dict(zip(col_name,vals))  
    
    #=============================================================================
    if iselltype == 'internal':
        writer = pd.ExcelWriter('iSell_{}_{}-Copy.xlsx'.format(htlname,iseldt), engine='xlsxwriter')
    else:
        writer = pd.ExcelWriter('iSell_{}_{}.xlsx'.format(htlname,iseldt), engine='xlsxwriter')
    #df.to_excel(writer, sheet_name='Sheet1',index=False)
    #===============df positioning================================================
    df.to_excel(writer, sheet_name='iSell_{}'.format(iseldt),startrow=6, startcol=0, header=False, index=False)
    
    
    # Get the xlsxwriter objects from the dataframe writer object.
    workbook  = writer.book
    worksheet = writer.sheets['iSell_{}'.format(iseldt)]
    
    #============================header format===========================================
    header_format = workbook.add_format({
            'bold':True,
            'text_wrap':True,
            'align':'center',
            'valign':'vcenter',
            'bg_color':	'#333333',
            'font_color': '#FFFFFF',
            'border':1       
            })
    
    for col_num,value in enumerate(df.columns.values):
        worksheet.write(5, col_num, value, header_format)
    
    
    #========================================================================================
    format1 = workbook.add_format({'bg_color': '#FF0000',
                                   'align':'right',
                                   'border':1,
                                   'font_color': '#000000'}) #Red
    
    # Add a format. Green fill with dark green text.
    format2 = workbook.add_format({'bg_color': '#00FF00',
                                   'align':'right',
                                   'border':1,
                                   'font_color': '#000000'}) #Green
    
    format3 = workbook.add_format({'bg_color': '#FF8080',
                                   'border':1,
                                   'font_color': '#000000'}) #Pink
    
    
    format4 = workbook.add_format({'bg_color': '#FF99CC',
                                   'border':1,
                                   'align':'right',
                                   'font_color': '#000000'}) #darkPink
    
    format5 = workbook.add_format({'bg_color': '#FFCC99',
                                   'border':1,
                                   'align':'right',
                                   'font_color': '#000000'}) #thinOrange
        
    format6 = workbook.add_format({'bg_color': '#99CC00',
                                   'border':1,
                                   'align':'right',
                                   'font_color': '#000000'}) #thingreen
        
    format7 = workbook.add_format({'bg_color': '#99CCFF',
                                   'border':1,
                                   'align':'right',
                                   'font_color': '#000000'}) #thinblue
    border_form = workbook.add_format({
                                   'border':1,
                                   'align':'right',
                                   }) 
        
        
    
    #==================== loop through 1st row (column names =========================================
    
    for names in col_name:
        colnum = name_ind[names]
        colname = ind_name[colnum]
        
        #========================== Event ============================================================
        if colname == 'Event':
            worksheet.conditional_format('{}7:{}{}'.format(colnum,colnum,rowlim),
                                     {'type': 'cell',
                                      'criteria' : '>',
                                      'value' : 0,
                                     'format': format3})
#            print("Formatting {} column".format(colname))
            worksheet.set_column('{}2:{}{}'.format(colnum,colnum,rowlim),30)
            
            worksheet.conditional_format('{}7:{}{}'.format(colnum,colnum,rowlim),
                                         {'type': 'cell',
                                          'criteria' : '<=',
                                          'value' : 0,
                                         'format': border_form})
            
        #========================= Rms Avail to Sell =====================================================
        elif colname == 'Rooms Avail To Sell Online':
            worksheet.conditional_format('{}7:{}{}'.format(colnum,colnum,rowlim),
                                         {'type': 'cell',
                                          'criteria' : '<=',
                                          'value' : 0,
                                         'format': format1})  
        
            worksheet.conditional_format('{}7:{}{}'.format(colnum,colnum,rowlim),
                                         {'type': 'cell',
                                          'criteria' : '>',
                                          'value' : 0,
                                         'format': border_form})
              
#            print("Formatting {} column".format(colname))
            
         #========================= FTR name get from conditions =====================================================
        elif colname == ftr:
            worksheet.conditional_format('{}7:{}{}'.format(colnum,colnum,rowlim),
                                         {'type': 'cell',
                                          'criteria' : '<=',
                                          'value' : 0,
                                         'format': format1})  

            worksheet.conditional_format('{}7:{}{}'.format(colnum,colnum,rowlim),
                                         {'type': 'cell',
                                          'criteria' : '>',
                                          'value' : 0,
                                         'format': border_form})
    
            worksheet.conditional_format('{}7:{}{}'.format(colnum,colnum,rowlim),
                                         {'type': 'cell',
                                          'criteria' : '<',
                                          'value' : 0,
                                         'format': border_form})
            
        #========================== OTA Sold (G) =============================================================
        elif colname == 'OTA Sold':
            worksheet.conditional_format('{}7:{}{}'.format(colnum,colnum,rowlim),
                                         {'type': 'cell',
                                          'criteria' : '>=',
                                          'value' : 0,                              
                                         'format': format4}) 
#            print("Formatting {} column".format(colname))
        #=========================== PickupColumn(H) ===================================================================
        elif colname == 'Pickup':
            worksheet.conditional_format('{}7:{}{}'.format(colnum,colnum,rowlim),
                                         {'type': 'cell',
                                          'criteria' : '<',
                                          'value' : 0,
                                         'format': format1})
            
            worksheet.conditional_format('{}7:{}{}'.format(colnum,colnum,rowlim),
                                         {'type': 'cell',
                                          'criteria' : '>',
                                          'value' : 0,
                                         'format': format2})
        
            worksheet.conditional_format('{}7:{}{}'.format(colnum,colnum,rowlim),
                                         {'type': 'cell',
                                          'criteria' : '=',
                                          'value' : 0,
                                         'format': border_form})
        
        
#            print("Formatting {} column".format(colname))      
        
         #=========================== ADR, Revenue, Rate on CM, ReccRate ===================================================================
       
        elif colname in ['OTA Revenue','ADR OTB','Rate on CM','Recommended Rate','Lowest Rate']:
            worksheet.conditional_format('{}7:{}{}'.format(colnum,colnum,rowlim),
                                         {'type': 'cell',
                                          'criteria' : '>=',
                                          'value' : 0,
                                         'format': format5})
#            print("Formatting {} column".format(colname))
        
         
        
        #================================After market trend ============================================
        elif colname in col_name[name_vals['Market Trend']:]:
            worksheet.conditional_format('{}7:{}{}'.format(colnum,colnum,rowlim),
                                         {'type': 'cell',
                                          'criteria' : '>=',
                                          'value' : 0,
                                         'format': format6})
        
            worksheet.conditional_format('{}7:{}{}'.format(colnum,colnum,rowlim),
                                         {'type': 'cell',
                                          'criteria' : '<',
                                          'value' : 0,
                                         'format': border_form})
#            print("Formatting {} column".format(colname))
        
        #================================client and comp rateshop ============================================
        elif colname in col_name[name_vals['Lowest Rate']:name_vals['Market Trend']-1]:
            worksheet.conditional_format('{}7:{}{}'.format(colnum,colnum,rowlim),
                                         {'type': 'cell',
                                          'criteria' : '>=',
                                          'value' : 0,
                                         'format': format7})
            worksheet.set_column('{}2:{}{}'.format(colnum,colnum,rowlim),15)
#            print("Formatting {} column".format(colname))  
        #================================setting border for remaining columns ============================================
        
        else:        
            worksheet.conditional_format('{}7:{}{}'.format(colnum,colnum,rowlim),
                                         {'type': 'cell',
                                          'criteria' : '>=',
                                          'value' : 0,
                                         'format': border_form})
    
            worksheet.conditional_format('{}7:{}{}'.format(colnum,colnum,rowlim),
                                         {'type': 'cell',
                                          'criteria' : '<',
                                          'value' : 0,
                                         'format': border_form})
            
    
    #===================================== alignment =====================================================================
    alignment = workbook.add_format({ 'align': 'center'})  
    worksheet.set_column('D:{}'.format(col_index[-1]), None, alignment)

    #=========================== Market Trend Arrows ==========================================================================
    mtindx = name_ind['Market Trend']
    worksheet.conditional_format('{}7:{}{}'.format(mtindx,mtindx,rowlim),
                                 {'type':'icon_set',
                                  'icon_style': '3_arrows',
                                  'icons_only' : True,
                                  'icons': [{'criteria': '>=', 'type': 'number','value': 0},
#                                            {'criteria': '=',  'type': 'number', 'value': 0},
                                            {'criteria': '<=', 'type': 'number', 'value': 0}]})
    
    worksheet.conditional_format('{}7:{}{}'.format(mtindx,mtindx,rowlim),
                                         {'type': 'cell',
                                          'criteria' : '<',
                                          'value' : 0,
                                         'format': border_form})
#    print("Arrow Formatting {} column".format('Market Trend'))
    #===========================================================================================================================
    worksheet.set_column('{}2:{}{}'.format('A','A',rowlim),12)
     
    worksheet.hide_gridlines(2)
    worksheet.freeze_panes(6, 2)
    worksheet.insert_image('A2', defaultpath+r'\masters\logo\isell.jpg',{'x_offset': 15, 'y_offset': 0,'x_scale': 0.65, 'y_scale': 0.65})
    
    if htlname == 'Getfam Hotel Addis Ababa':
        worksheet.insert_image('G2', defaultpath+r'\masters\logo\Aleph.png',{'x_offset': 15, 'y_offset': 0,'x_scale': 0.85, 'y_scale': 0.85})
    else:
        worksheet.insert_image('G2', defaultpath+r'\masters\logo\logo.jpg',{'x_offset': 15, 'y_offset': 0,'x_scale': 0.85, 'y_scale': 0.85})
    
    #=============================================Glossary======================================
    glossary.to_excel(writer, sheet_name='Glossary',index=False)
    worksheet2 = writer.sheets['Glossary']
    worksheet2.set_column('{}1:{}{}'.format('A','A',rowlim),5)
    worksheet2.set_column('{}1:{}{}'.format('B','B',rowlim),32)
    worksheet2.set_column('{}1:{}{}'.format('C','C',rowlim),46)  
    
    gformat = workbook.add_format({ 'border':1})
    
    #assigning conditional formatting to glossary
    worksheet2.conditional_format('{}1:{}{}'.format('A','C',35),
                                         {'type': 'cell',
                                          'criteria' : '>',
                                          'value' : 0,                                
                                         'format': gformat})
    
    # Adding Formatting to Glossary
    # Add a bold format to use to highlight cells.
    boldcell = workbook.add_format({'bold': True,'bg_color': '#999999','align': 'center'})
    
    #Header Formatting
    worksheet2.write('A1', 'Sr No', boldcell)    
    worksheet2.write('B1', 'Column Name', boldcell)
    worksheet2.write('C1', 'Column Description', boldcell)       
    
    worksheet2.write('A17', 'Sr No', boldcell)    
    worksheet2.write('B17', 'Pricing Abbreviations', boldcell)
    worksheet2.write('C17', 'Rate Description', boldcell)  
      
    #===================================================================================================
    #-----------------------------Grid Addition and Adoption addition---------------------------------------------------
    #===================================================================================================
    if iselltype == 'internal':
        pgdf.to_excel(writer, sheet_name='Grids',index=False) 
        #======================================Add Adoption================================================
        finaladop.to_excel(writer,index=False,sheet_name='iSell_{}'.format(iseldt),startrow=1, startcol=15)  
    
    else:
        pass   
      
    
    writer.save()
    workbook.close()
    
def isellbeautify(defaultpath, df,htlname,pth2,name_win2,isellrange,glossary,ftr,pgdf,finaladop,acc_man):    
    try:
        os.chdir(pth2)
        os.mkdir(foldname)
    except:
        pass
    
    pth_1 = pth2 +'\\'+foldname #iSell/tdayfold
    
    try:
        os.chdir(pth_1)
        os.mkdir(acc_man)     #iSell/tdayfold/accman
    except FileExistsError:
        pass
    
    #-------------final pth-----------------------------
    pth = pth_1 +'\\'+acc_man

    df = pd.DataFrame(df)    
    df.fillna(value='N/A',inplace=True)
    df['Event'] = df['Event'].astype(str)
    df['Event'] = df['Event'].replace({'0':np.nan})
    df['Recommended Rate'] = df['Recommended Rate'].astype(str)
    df['Recommended Rate'] = df['Recommended Rate'].replace({'N/A':np.nan})
    df['Recommended Rate']  = df['Recommended Rate'].astype(float)
    df['Recommended Rate']  = df['Recommended Rate'].round(0)
    df.rename(columns={'OTA_Sold':'OTA Sold','LowestRate':'Lowest Rate'},inplace=True)
    
        
    beautify(defaultpath, df,'internal',isellrange+6,htlname,pth,glossary,ftr,pgdf,finaladop) 
    print("\tInternal iSell Dumped")
    
    if str(name_win2) != '0':
        df.drop('Recommended Rate',axis=1,inplace=True)
        try:
            df.drop('SeasonalRate_y',axis=1,inplace=True)
        except:
            pass
        beautify(defaultpath, df,'client',isellrange+6,htlname,pth,glossary,ftr,pgdf,finaladop)  
        print("\tClient iSell Dumped !!!")
        
    else:
            
        if dow in ['Mon','Fri']:
            df.drop('Recommended Rate',axis=1,inplace=True)
            try:
                df.drop('SeasonalRate_y',axis=1,inplace=True)
            except:
                pass
            beautify(defaultpath,df,'client',isellrange+6,htlname,pth,glossary,ftr,pgdf,finaladop)  
            print("\tClient iSell Dumped !!!")
        else:
            df = df.iloc[:30,:]
            df.drop('Recommended Rate',axis=1,inplace=True)
            try:
                df.drop('SeasonalRate_y',axis=1,inplace=True)
            except:
                pass
            beautify(defaultpath,df,'client',36,htlname,pth,glossary,ftr,pgdf,finaladop) 
            print("\tClient iSell Dumped !!!")
            
 