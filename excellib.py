from openpyxl import load_workbook
from openpyxl import Workbook

# Module Doc: https://openpyxl.readthedocs.io/en/stable/

class excelEngine:

  def columnHeight(self, fileName, column):
    '''
    This module will handle importing the excel documents and populating the lists appropriately.
    '''
    wb = load_workbook(fileName)
    ws = wb.active
    rowNum = 1
    cell = str(column) + str(rowNum)
    while(ws[cell].value != None):
      rowNum+= 1
      cell = str(column) + str(rowNum)
    return rowNum


  def importColumn(self, fileName, column):
    '''
    This module will handle importing the excel documents and populating the lists appropriately.
    '''
    # Load workbook from file
    wb = load_workbook(fileName)
    ws = wb.active
    # create list of pages
    generatedList = []
    rowNum = 2
    cell = str(column) + str(rowNum)
    while(ws[cell].value != None):
      generatedList.append(ws[cell].value)
      rowNum+= 1
      cell = str(column) + str(rowNum)
    return generatedList

  def exportRow(self, ws, generatedList, row):
    '''
    This module will handle exporting the resulting list to excel
    '''
    i = 1
    for item in generatedList:
      ws.cell(row = row, column = i).value = item
      i += 1
    return

  def exportColumn(self, generatedList, col):
    '''
    This module will handle exporting the resulting list to excel
    '''
    i = 1
    wb = Workbook()
    ws = wb.active
    for item in generatedList:
      ws.cell(row = i, column = col).value = item
      i += 1
    return wb
