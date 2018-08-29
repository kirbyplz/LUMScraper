class sc:
  def initDriver(driver):
    sc.driver = driver
    return

  def closeDriver():
    sc.driver.close()
    return

  def intFormat(str):
    '''
    This takes soundcouds followercount form and turns it into numerics
    '''
    if str in 'None':
      return 0
    str = str.replace('.','')
    str = str.replace(',','')
    if "K" in str:
      str = str.replace('K','')
      return int(str) * 100 #Remove 1 0 due to removed decimal place
    elif "M" in str:
      str = str.replace('M','')
      return int(str) * 100000
    else:
      return int(str)

  def formatExit(url):
    '''
    Pretty up soundclouds external URLs
    '''
    url = url.replace('%3A', ':')
    url = url.replace('%2F', '/')
    url = url.replace('https://exit.sc/?url=', '')
    return url

  def urlToList(url):
    '''
    This function takes in a URL and does all of the driver function to scrape various elements
    '''
    driver = sc.driver
    driver.get(url)
    newList = []
    FC = sc.currExists(driver.find_elements_by_class_name('infoStats__value'))
    formattedFC = sc.intFormat(FC)
    if (formattedFC < 200) or (formattedFC > 1000000):
      return newList
    #Format: CrawlList,URL,Name,Followers,Location,Facebook,Twitter,Youtube,Emails
    #CrawlList
    crawlList = sc.crawlGen()
    newList.append(crawlList)
    #Current page's URL
    newList.append(url)
    #Artist Name
    curr = driver.find_elements_by_xpath('//*[@id="content"]/div/div[3]/div/div[1]/div/div[2]/h3')
    newList.append(sc.currExists(curr))
    if curr: #Yearly Pro Plan status is attached to this tag, so this is a workaround
      if len(curr[0].text) > 15:
        if 'Yearly Pro plan' == curr[0].text[len(curr[0].text)-15:len(curr[0].text)] : 
          newList = newList[:-1]
          newList.append(curr[0].text[0:len(curr[0].text) - 15])
    #FollowerCount gets added
    newList.append(FC)
    #Location
    curr = driver.find_elements_by_xpath('//*[@id="content"]/div/div[3]/div/div[1]/div/div[2]/h4')
    newList.append(sc.currExists(curr))
    
    #Web Profiles
    curr = driver.find_elements_by_class_name('web-profile')
    sc.webProfiles(curr, newList)
    
    #Emails
    emails = []
    curr = driver.find_elements_by_tag_name('a')
    for item in curr:
      if item:
        link = item.get_attribute('href')
        if type(link) == str:
          if ('mailto:' in link):
            emails.append(link.replace('mailto:',''))
    for item in emails:
      newList.append(item)
    return newList

  def crawlGen():
    '''
    Generate a list of the related profiles specifically
    '''
    crawlList = []             
    
    crawlList.extend(sc.xpathAppend('//*[@id="content"]/div/div[5]/div[2]/div/article[3]/div/div/ul', 'soundTitle__username')) #Likes
    crawlList.extend(sc.xpathAppend('//*[@id="content"]/div/div[5]/div[2]/div/article[4]/div/div/ul', 'userBadge__usernameLink')) #Following
    crawlList.extend(sc.xpathAppend('//*[@id="content"]/div/div[3]/div/div[3]/div/div/div/ul', 'userBadge__usernameLink')) #FP

	#Defaultdict pop item removes last item in queue, so to scrape in same order we are going to make crawlist backwards
    return crawlList.reverse()

  def currExists(curr):
    '''
    To handle if the element doesnt exist on specific page
    '''
    if curr:
      return curr[0].text
    else:
      return 'None'

  def xpathAppend(xpath, className):
    '''
    Take an xpath list and return all elements. Note: we intentially use elements to generate a list for xpath,
    to cover the case where the page doesn't have a certain section as opposed to crashing
    '''
    genList = []
    xpathresult = sc.driver.find_elements_by_xpath(xpath)
    if not xpathresult:
      return genList
    liList = xpathresult[0].find_elements_by_xpath('li')
    for item in liList:
      temp = item.find_elements_by_class_name(className)
      if temp:
        genList.append(temp[0].get_attribute('href'))
    return genList

  def webProfiles(curr, currList):
    '''
    Get links to Facebook,Twitter,Youtube if they have them
    '''
    fbAbsent = 1; twAbsent = 1; ytAbsent = 1
    fb = 'None'; tw = 'None'; yt = 'None';
    i = 0
    while (curr and (fbAbsent or twAbsent or ytAbsent)):
      link = curr.pop().get_attribute('href')
      if 'facebook.com' in link:
        fbAbsent = 0
        fb = sc.formatExit(link)
      elif 'twitter.com' in link:
        twAbsent = 0
        tw = sc.formatExit(link)
      elif 'youtube.com' in link:
        ytAbsent = 0
        yt = sc.formatExit(link)
      i += 1
    currList.append(fb)
    currList.append(tw) 
    currList.append(yt)
    
    return