from excellib import excel
from datetime import datetime
from collections import defaultdict
from time import sleep
from sclib import sc
from selenium import webdriver
import os

import sys

def main():
  '''
  This is the general workflow logic of this project
  1)Import previous work done as completed and queue
  2)Loop through queue
    a)Verify this page hasn't been processed prior, if so remove from queue and reloop
    b)Take url, process and generate list of elements
    c)Add recommened profiles to queue provided they aren't in completed
    d)Add list of elements from page to list of output
  3)Update the completed and queue files, make new output file
  '''
  
  #1
  output = []
  queue = defaultdict(lambda: 0, {item:1 for item in excel.importColumn('queue.xlsx', 'a')})
  completed = defaultdict(lambda: 0, {item:1 for item in excel.importColumn('completed.xlsx', 'a')})
  
  #2 Scraping Loop
  loops = 0
  
  startTime = datetime.now()
  while (queue):
    if loops == pagesToLoop:
      break
    if pauseTime != 0:
      sleep(pauseTime)
    url = queue.popitem()[0]
	
    if completed[url] == 1:    	  #a
      continue

    gen = sc.urlToList(url)   	 	#b 
    if not gen: #list is empty if outside range, so reloop
      continue
	  
    crawlList = gen.pop(0)

    while crawlList:              #c
      if (completed[crawlList[0]] == 0) & (queue[crawlList[0]] == 0):
        queue[crawlList.pop(0)] = 1
      else:
        crawlList.pop(0)          #No point in making a deque it's size 9
    completed[gen[0]] = 1
    output.append(gen)            #d
	
    loops += 1

  endTime = datetime.now()
  sc.closeDriver()
  #3 Exporting results
  for key in list(completed.keys()):
    if completed[key] == 0:
      del completed[key]
	
  excel.exportFunc(list(queue.keys()), 'queue.xlsx')
  excel.exportFunc(output, 'output.xlsx')
  excel.exportFunc(list(completed.keys()), 'completed.xlsx')

  print('Start time: {}, End Time: {}, Pages: {}, Pause Time: {} '.format(startTime, endTime, pagesToLoop, pauseTime))
  print('O(N) size = {}'.format(str(len(queue) + len(completed))))
  print('Sucessfully scraped {} webpages, open output.xlsx'.format(pagesToLoop))
  return


if __name__ == '__main__':
  if len(sys.argv) != 4:
    print('Usage: python main.py <pages to loop> <time to pause between> <geckodriver or chromedriver>')
    exit()

  pagesToLoop = int(sys.argv[1])
  pauseTime = int(sys.argv[2])
  PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
  DRIVER_BIN = os.path.join(PROJECT_ROOT, sys.argv[3])
  sc.initDriver(webdriver.Chrome(executable_path = DRIVER_BIN))
  main()