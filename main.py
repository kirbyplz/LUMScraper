from excellib import excelEngine
from selenium import webdriver
from openpyxl import Workbook
import os


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
  engine = excelEngine()
  queue = engine.importColumn("queue.xlsx", "a")
  completed = engine.importColumn("completed.xlsx", "a")
  output = []
  
  #2 Scraping Loop
  loops = 0
  
  while (queue):
    if loops > 25:
      break
    url = queue.pop(0)

    if url in completed:    	#a
	
      print(url + 'in completed')
      continue

    gen = urlToList(url)   		#b this list is empty if follower count is <200 or > 1mill, so reloop
    if not gen:
      print('Page out of follower range')
      continue
	  
    crawlList = gen.pop(0)
	  #Deques for [0] operations to be more efficient 39:20 in Transforming Code
    while crawlList:   	        #c
      if (crawlList[0] not in completed) & (crawlList[0] not in queue):
        print(crawlList[0] + ' added to queue')
        queue.append(crawlList.pop(0))
      else:
        print(crawlList[0] + ' already scraped or in queue')
        crawlList.pop(0)
		
    output.append(gen)   		#d
    completed.append(gen[0])
	
    loops += 1

  #3 Exporting results
  exportFunc(engine, queue, "queue.xlsx")
  exportFunc(engine, output, "output.xlsx")
  exportFunc(engine, completed, "completed.xlsx")

  print("Sucessfully scraped", loops, "webpages, open output.xlsx")
  return

def exportFunc(engine, currList, fileName):
  '''
  Essentially wrapper for exportRow to conform to desired format
  '''
  if fileName in "output.xlsx":
    finalWB = Workbook()
    finalWS = finalWB.active
    engine.exportRow(finalWS, ["URL", "Artist Name", "Followers", "Location", "Facebook", "Twitter", "Instagram", "Email"], 1)
    i = 2
    while currList:
      engine.exportRow(finalWS, currList.pop(0), i)
      i += 1
    finalWB.save(fileName)
  else:
    os.remove(fileName)
    currList.insert(0,fileName.replace(".xlsx",""))
    wb = engine.exportColumn(currList, 1)
    wb.save(fileName)
  return
  
	
def urlToList(url):
  '''
  This function takes in a URL and does all of the driver function to scrape various elements
  '''
  PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
  DRIVER_BIN = os.path.join(PROJECT_ROOT, "chromedriver")
  driver = webdriver.Chrome(executable_path = DRIVER_BIN)
  driver.get(url)
  newList = []
  curr = driver.find_elements_by_class_name("infoStats__value")
  FC = currExists(curr)
  formattedFC = intToStr(FC)
  if (formattedFC < 200) or (formattedFC > 1000000):
    driver.close()
    return newList
  #Format: CrawlList,URL,Name,Followers,Location,Facebook,Twitter,Youtube,Emails
  #CrawlList
  crawlList = crawlGen(driver)
  newList.append(crawlList)
  #Current page's URL
  newList.append(url)
  #Artist Name
  curr = driver.find_elements_by_xpath('//*[@id="content"]/div/div[3]/div/div[1]/div/div[2]/h3')
  newList.append(currExists(curr))
  if curr: #Yearly Pro Plan status is attached to this tag, so this is a workaround
    if len(curr[0].text) > 15:
      if "Yearly Pro plan" == curr[0].text[len(curr[0].text)-15:len(curr[0].text)] : 
        newList = newList[:-1]
        newList.append(curr[0].text[0:len(curr[0].text) - 15])
  #FollowerCount gets added
  newList.append(FC)
  #Location
  curr = driver.find_elements_by_xpath('//*[@id="content"]/div/div[3]/div/div[1]/div/div[2]/h4')
  newList.append(currExists(curr))
	
  #Web Profiles
  curr = driver.find_elements_by_class_name("web-profile")
  webProfiles(curr, newList)
  
  #Emails
  emails = []
  curr = driver.find_elements_by_tag_name("a")
  for item in curr:
    link = item.get_attribute("href")
    if type(link) == str:
      if ("mailto:" in link):
        emails.append(link.replace("mailto:",""))
  driver.close()
  for item in emails:
    newList.append(item)
  return newList

def crawlGen(driver):
  '''
  Generate a list of the related profiles specifically
  '''
  crawlList = []             
  
  crawlList.extend(xpathAppend('//*[@id="content"]/div/div[5]/div[2]/div/article[3]/div/div/ul', 'soundTitle__username', driver)) #Likes
  crawlList.extend(xpathAppend('//*[@id="content"]/div/div[5]/div[2]/div/article[4]/div/div/ul', 'userBadge__usernameLink', driver)) #Following
  crawlList.extend(xpathAppend('//*[@id="content"]/div/div[3]/div/div[3]/div/div/div/ul', 'userBadge__usernameLink', driver)) #FP
  
  '''
  OLD CODE SEGMENT, nice and pretty
  if len(driver.find_elements_by_xpath('//*[@id="content"]/div/div[3]/div/div[3]/div/div/div/ul/li[1]/div/div/div[2]/div[1]/h3/a')) != 0:
    crawlList.append(driver.find_elements_by_xpath('//*[@id="content"]/div/div[3]/div/div[3]/div/div/div/ul/li[1]/div/div/div[2]/div[1]/h3/a')[0].get_attribute('href'))
  if len(driver.find_elements_by_xpath('//*[@id="content"]/div/div[3]/div/div[3]/div/div/div/ul/li[2]/div/div/div[2]/div[1]/h3/a')) != 0:
    crawlList.append(driver.find_elements_by_xpath('//*[@id="content"]/div/div[3]/div/div[3]/div/div/div/ul/li[2]/div/div/div[2]/div[1]/h3/a')[0].get_attribute('href'))
  if len(driver.find_elements_by_xpath('//*[@id="content"]/div/div[3]/div/div[3]/div/div/div/ul/li[3]/div/div/div[2]/div[1]/h3/a')) != 0:
    crawlList.append(driver.find_elements_by_xpath('//*[@id="content"]/div/div[3]/div/div[3]/div/div/div/ul/li[3]/div/div/div[2]/div[1]/h3/a')[0].get_attribute('href'))
   '''

  return crawlList

def xpathAppend(xpath, className, driver):
  '''
  Take an xpath list and return all elements. Note: we intentially use elements to generate a list for xpath,
  to cover the case where the page doesn't have a certain section as opposed to crashing
  '''
  genList = []
  xpathresult = driver.find_elements_by_xpath(xpath)
  if not xpathresult:
    return genList
  liList = xpathresult[0].find_elements_by_xpath("li")
  for item in liList:
    genList.append(item.find_element_by_class_name(className).get_attribute('href'))
  return genList

def currExists(curr):
  '''
  To handle if the element doesnt exist on specific page
  '''
  if curr:
    return curr[0].text
  else:
    return "None"

def webProfiles(curr, currList):
  '''
  Get links to Facebook,Twitter,Youtube if they have them
  '''
  fbAbsent = 1; twAbsent = 1; ytAbsent = 1
  fb = "None"; tw = "None"; yt = "None";
  i = 0
  while (curr and (fbAbsent or twAbsent or ytAbsent)):
    link = curr.pop().get_attribute('href')
    if "facebook.com" in link:
      fbAbsent = 0
      fb = formatExit(link)
    elif "twitter.com" in link:
      twAbsent = 0
      tw = formatExit(link)
    elif "youtube.com" in link:
      ytAbsent = 0
      yt = formatExit(link)
    i += 1
  currList.append(fb)
  currList.append(tw) 
  currList.append(yt)
  
  return

def intToStr(str):
  str1 = str.replace(".","")
  str1 = str1.replace(",","")
  if "K" in str:
    str2 = str1.replace("K","")
    return int(str2) * 100 #Remove 1 0 due to removed decimal place
  elif "M" in str:
    str2 = str1.replace("M","")
    return int(str2) * 100000
  else:
    return int(str1)

def formatExit(url):
  '''
  Pretty up soundclouds external URLs
  '''
  formatted = url.replace("%3A", ":")
  formatted = formatted.replace("%2F", "/")
  formatted = formatted.replace("https://exit.sc/?url=", "")
  return formatted

main()