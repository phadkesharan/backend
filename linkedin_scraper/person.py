import asyncio
from linkedin_scraper import actions
from typing import TextIO
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .objects import Experience, Education, Scraper, Interest, Accomplishment, Contact
import os
import time 
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from db.store import queue
class Person(Scraper):

    __TOP_CARD = "pv-top-card"
    __WAIT_FOR_ELEMENT_TIMEOUT = 5

    def __init__(
        self,
        linkedin_url=None,
        name=None,
        about=None,
        experiences=None,
        educations=None,
        interests=None,
        email=None,
        accomplishments=None,
        company=None,
        job_title=None,
        contacts=None,
        driver=None,
        get=True,
        scrape=True,
        close_on_complete=True,
        cookie=None,
        link=None,
        messageText=None,
        queue=None,
        messagesLimit=None,
        searchLink=None,
        resultsToScrap=1,
        sendResponseFlag=True,
        hideAlready=False,
        prospectsUrl=[],
hideImage=False,hideCompany=False,hideKeywords=False,keywords=[],companies=[]
    ):
        self.hideImage=hideImage
        self.hideCompany=hideCompany
        self.hideKeywords=hideKeywords
        self.keywords=keywords
        self.companies=companies
        self.linkedin_url = linkedin_url
        self.hideAlready=hideAlready
        self.prospectsUrl=prospectsUrl
        self.name = name
        self.email=email
        self.about = about or []
        self.experiences = experiences or []
        self.educations = educations or []
        self.interests = interests or []
        self.accomplishments = accomplishments or []
        self.also_viewed_urls = []
        self.contacts = contacts or []
        self.cookie=cookie
        self.link=link
        self.messageText=messageText
        self.queue=queue
        self.messagesLimit=messagesLimit
        self.searchLink=searchLink
        self.resultsToScrap=resultsToScrap
        self.sendResponseFlag=sendResponseFlag
        self.dontSendConnect=False;
        if driver is None:
            try:
                if os.getenv("CHROMEDRIVER") == None:
                    driver_path = os.path.join(
                        os.path.dirname(__file__), "drivers/chromedriver"
                    )
                else:
                    driver_path = os.getenv("CHROMEDRIVER")

                driver = webdriver.Chrome(driver_path)
            except:
                driver = webdriver.Chrome()

        if get:
            driver.get(linkedin_url)

        self.driver = driver

        if scrape:
            self.scrape(close_on_complete)
        if cookie:
            #self.sendResponse(data="initiating login with cookie")
            actions.login(cookie=cookie,driver=driver)
            driver.get("https://www.linkedin.com/")

    def add_about(self, about):
        self.about.append(about)

    def add_experience(self, experience):
        self.experiences.append(experience)

    def add_education(self, education):
        self.educations.append(education)

    def add_interest(self, interest):
        self.interests.append(interest)

    def add_accomplishment(self, accomplishment):
        self.accomplishments.append(accomplishment)

    def add_location(self, location):
        self.location = location

    def add_contact(self, contact):
        self.contacts.append(contact)

    def scrape(self, close_on_complete=False,url='/'):
        if self.is_signed_in():
            return self.scrape_logged_in(close_on_complete=close_on_complete,url=url)
        self.driver.close()
        return False
    def _click_see_more_by_class_name(self, class_name):
        
        try:
            _ = WebDriverWait(self.driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_name))
            )
            div = self.driver.find_element_by_class_name(class_name)
            div.find_element_by_tag_name("button").click()
        except Exception as e:
            print("error")
            print(e)
            pass
    async def sendResponseAsync(self,data):
        yield data
  
    def sendResponse(self,data):
        # loop = asyncio.new_event_loop()
        # loop.run_until_complete(self.sendResponseAsync(data=data))
        if self.sendResponseFlag:
            asyncio.run(self.queue.put(data))
        
        #loop = asyncio.get_event_loop()
        #loop.create_task(self.queue.put(data))
        return
      
    def send_Message(self,close_on_complete=True,message=None,link=None):
        if message==None:
            message=self.messageText

        self.sendResponse(data="starting")
        
        driver = self.driver
        if link==None:
            driver.get(self.linkedin_url)
        else:
            driver.get(link)
        self.sendResponse(data="opened link")
        
        
        try:
            send_message =WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located(
                    (
                        By.CLASS_NAME,
                        "message-anywhere-button",
                    )
                )
            )
            send_message=send_message.find_elements(By.XPATH,"//a[contains(@class,'message-anywhere-button pvs-profile-actions__action artdeco-button')]")[-1]
            
            send_message.click()
            self.sendResponse(data="clicked message button")
            #yield 
            send_message =WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located(
                    (
                        By.CLASS_NAME,
                        "msg-form__contenteditable",
                    )
                )
            )
            send_message.send_keys(message)
            #yield 
            self.sendResponse(data="wrote message")
            send_message = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located(
                    (
                        By.CLASS_NAME,
                        "msg-form__send-button",
                    )
                )
            )
            time.sleep(1)
            #yield ""
            self.sendResponse(data="clicked send message")
            send_message.click()
            if close_on_complete:
                driver.close()
            data={}
            data["message"]="message sent Sucessfully"
            data["exitCode"]=200
            self.sendResponse(data=data)
            #return True
        except:
            if close_on_complete:
                driver.close()
            #return False
            data={}
            data["message"]="message not sent Sucessfully"
            data["exitCode"]=500
            self.sendResponse(data=data)
            pass
        
    def messageStatus(self,close_on_complete=True,link=None):
        driver = self.driver
        if link==None:
            driver.get(self.linkedin_url)
            link=self.linkedin_url
        else:
            driver.get(link)
        print("in message")
        try:
            send_message =WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located(
                    (
                        By.CLASS_NAME,
                        "message-anywhere-button",
                    )
                )
            )
            send_message=send_message.find_elements(By.XPATH,"//a[contains(@class,'message-anywhere-button pvs-profile-actions__action artdeco-button')]")[-1]
            
            send_message.click()
            print("clicked message")
            
            #yield 
            messageslist=WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until( EC.presence_of_element_located((By.XPATH,
                    "//ul[contains(@class,'msg-s-message-list-content')]")))
            lastSender=messageslist.find_elements(By.XPATH,"//a[contains(@class,'msg-s-event-listitem__link')]")[-1].get_attribute('href')
            print(lastSender)
            lastSender="https://www.linkedin.com/in/"+lastSender.split(".com/in/")[1].split("/")[0].split("?")[0]
            print(lastSender)
            if(lastSender==link):
                return 1 #replied case
            try:
                recipeint=messageslist.find_element(By.XPATH,"//div[contains(@class,'msg-s-event-listitem__seen-receipts')]")
                return 2 # scene but not replied
            except:
                pass
            #yield 
            
            if close_on_complete:
                driver.close()
            return 3 # nor scene nor replied
            #return True
        except Exception as e:
            print(e)
            if close_on_complete:
                driver.close()
            #return False
            data={}
            data["message"]="message not sent Sucessfully"
            data["exitCode"]=500
            self.sendResponse(data=data)
            pass
        return -1 # error in middle
    def get_Messages(self,close_on_complete=True):
        driver=self.driver
        driver.get("https://www.linkedin.com/messaging/")
        get_messages=WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until( EC.presence_of_element_located((By.XPATH,
                "//ul[contains(@class, 'list-style-none msg-conversations-container__conversations-list')]",)))
        #time.sleep(5)
        all_conversations={}
        
        #tes1=len(get_messages.find_elements(By.CSS_SELECTOR("li[class*='scaffold-layout__list-item msg-conversation-listitem msg-conversations-container__convo-item msg-conversations-container__pillar ember-view']")))
        convo_list=get_messages.find_elements(By.XPATH,".//li[contains(@class, 'scaffold-layout__list-item msg-conversation-listitem msg-conversations-container__convo-item msg-conversations-container__pillar ember-view')]")
        prev_len_con=len(convo_list)
        print(prev_len_con)
        #convo_list[prev_len_con-1].click()
        driver.execute_script("arguments[0].scrollIntoView();",convo_list[prev_len_con-1])
        time.sleep(1)
        while prev_len_con !=len(get_messages.find_elements(By.XPATH,".//li[contains(@class, 'scaffold-layout__list-item msg-conversation-listitem msg-conversations-container__convo-item msg-conversations-container__pillar ember-view')]")):
            convo_list=get_messages.find_elements(By.XPATH,".//li[contains(@class, 'scaffold-layout__list-item msg-conversation-listitem msg-conversations-container__convo-item msg-conversations-container__pillar ember-view')]")
            prev_len_con=len(convo_list)
            driver.execute_script("arguments[0].scrollIntoView();",convo_list[prev_len_con-1])
            
            print(prev_len_con)
            time.sleep(1)
            
            
            #convo_list[prev_len_con-1].click()
              #print(len(get_messages.find_elements(By.CSS_SELECTOR("li[class*='scaffold-layout__list-item msg-conversation-listitem msg-conversations-container__convo-item msg-conversations-container__pillar ember-view']"))))
        #print(len(get_messages.find_elements(By.CSS_SELECTOR("li[class*='scaffold-layout__list-item msg-conversation-listitem msg-conversations-container__convo-item msg-conversations-container__pillar ember-view']"))))
        #test2=len(get_messages.find_elements(By.CSS_SELECTOR("li[class*='scaffold-layout__list-item msg-conversation-listitem msg-conversations-container__convo-item msg-conversations-container__pillar ember-view']")))
        driver.execute_script(" window.scrollTo(0, 0)")
        for conversations in get_messages.find_elements(By.XPATH,".//li[contains(@class, 'scaffold-layout__list-item msg-conversation-listitem msg-conversations-container__convo-item msg-conversations-container__pillar ember-view')]"):
            
            try:
                #time.sleep(3)
                
                #action = ActionChains(driver)
                #action.moveToElement;

                clicking_span=conversations.find_element(By.TAG_NAME,"h3")
                driver.execute_script("arguments[0].scrollIntoView();",clicking_span)
                clicking_span.click()
                print(clicking_span.text.strip())
                #action.move_to_element(clicking_span).click()
                #conversations.click()
                #print(" iam not the issue")
                #driver.execute_script(" window.scrollTo(0, document.body.scrollHeight)")
                
                sender=conversations.find_element_by_tag_name("h3").text.strip()
                
                
                convo=WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until( EC.presence_of_element_located((By.XPATH,
                    ".//ul[contains(@class, 'msg-s-message-list-content')]",)))
                time.sleep(1)
                url=""
                try:
                    url=convo.find_element(By.XPATH,"//a[contains(@class,'msg-thread__link-to-profile ember-view')]").get_attribute('href')
                except Exception as e:
                    print(e)
                    print("error occurred at url")
                    pass
                print(url)
                img="/static/mock-images/avatars/avatar_default.jpg"
                try:
                    img=conversations.find_element(By.XPATH,".//img[contains(@class,'presence-entity__image   EntityPhoto-circle-4 lazy-image ember-view')]").get_attribute('src')
                except Exception as e:
                    print(e)
                    print("error occured at image")
                    pass
                print("here")
                msg_list=convo.find_elements(By.XPATH,".//li[contains(@class,'msg-s-message-list__event clearfix')]")
                precount=len(msg_list)
                try:
                    msg_list[0].find_element_by_tag_name('p').click()
                except Exception as e:
                    msg_list[precount-1].find_element_by_tag_name('p').click()
                    print(e)
                    pass
                #driver.execute_script(" window.scrollTo(0, document.body.scrollHeight);") shared-title-bar__title msg-title-bar__title-bar-title
                driver.execute_script("arguments[0].scrollIntoView();",convo.find_elements(By.XPATH,".//li[contains(@class,'msg-s-message-list__event clearfix')]")[0])
                time.sleep(1)
                i=1
                while precount!=len(convo.find_elements(By.XPATH,".//li[contains(@class,'msg-s-message-list__event clearfix')]")) and precount<self.messagesLimit:
                    print("doing againg")
                    i=i+1
                    first_msg=convo.find_elements(By.XPATH,".//li[contains(@class,'msg-s-message-list__event clearfix')]")
                    precount=len(first_msg)
                    driver.execute_script("arguments[0].scrollIntoView();",first_msg[0])
                    #first_msg[0].find_element_by_tag_name('p').click()
                    print("sleeping")
                    time.sleep(1)
                    print("awoke")
                # convo=WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until( EC.presence_of_element_located((By.XPATH,
                #     "//ul[contains(@class, 'msg-s-message-list-content')]",)))
                messages=[]
                previous="first"
                previousTime="first"
                previousId="first"
                for message in convo.find_elements(By.XPATH,".//li[contains(@class,'msg-s-message-list__event clearfix')]"):
                    
                    try:
                        try:
                            WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until( EC.presence_of_element_located((By.XPATH,
                    ".//a[contains(@class,'msg-s-event-listitem__link')]",)))

                        except:
                            print("not fpund")
                            pass
                        text={}
                        try:
                            
                            text["sentById"]=message.find_element(By.XPATH, ".//a[contains(@class,'msg-s-event-listitem__link')]").get_attribute('href')
                            previousId=text["sentById"]
                        except Exception as e:
                            print(e)
                            text["sentById"]=previousId
                            
                        try:
                            text["sentBy"]=message.find_element(By.XPATH,".//span[contains(@class,'msg-s-message-group__name t-14 t-black t-bold hoverable-link-text')]").text.strip()
                            previous=text["sentBy"]
                        except:
                            text["sentBy"]=previous
                        try:
                            text["timeHeader"]=message.find_element(By.XPATH, ".//time[contains(@class,'msg-s-message-list__time-heading')]").text.strip()
                        except:
                            pass
                        try:
                            text["time"]=message.find_element(By.XPATH, ".//time[contains(@class,'msg-s-message-group__timestamp')]").text.strip()
                            previousTime=text["time"]
                        except:
                            text["time"]=previousTime
                        
                        # for tag in message.find_elements_by_tag_name('time'):
                        #     try:
                        #          text["time"]=tag.find_element_by_class_name("msg-s-message-group__timestamp").text.strip()
                                 
                        #     except Exception as e:
                        #         print(e)
                        #         try:
                        #             text["timeHeader"]=tag.find_element_by_class_name("msg-s-message-list__time-heading").text.strip()
                        #         except Exception as e:
                        #             print(e)
                        #             pass 
                        #         pass
                        # #text["time"]=message.find_elements_by_tag_name('time').find_element_by_class_name("msg-s-message-group__timestamp").text.strip()
                        text["message"]=message.find_element_by_tag_name('p').text.strip()
                        messages.append(text)
               
                    except Exception as e:
                        print(e)
                        pass
                
                #all_conversations[sender]=messages
                print("messages length")
                print(len(messages))
                self.sendResponse(data={"name":sender,"messages":messages,"url":url,"img":img})

            except Exception as e:
                print(e)
                pass
        data={}
        data["exitCode"]=200
        self.sendResponse(data=data)
        if close_on_complete:
            driver.close()
        #return all_conversations    


   
    def search_Results(self,close_on_complete=True,url=None,resultsToScrap=None):
        driver=self.driver
        print(self.searchLink)
        if url is None:
            url=self.searchLink
        if resultsToScrap is None:
            resultsToScrap=self.resultsToScrap
        driver.get(url)
        
       
        sentResults=0
        while sentResults <resultsToScrap:
            try:
                withoutImage=[]
                containingKeywords=[]
                containingCompanies=[]
                scrapped_results=[]
                alreadyinSeq=[]
                print("here in search")
                search_results = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//ul[contains(@class,'reusable-search__entity-result-list list-style-none')]",
                )
            )
        )
                print("fine uptil here")
                search_list=search_results.find_elements_by_class_name("reusable-search__result-container")
                prev_len_search=len(search_list)
                print(prev_len_search)
                #search_list[prev_len_search-1].click()
                driver.execute_script("arguments[0].scrollIntoView();",search_list[prev_len_search-1])
                time.sleep(1)
                while prev_len_search !=len(search_results.find_elements_by_class_name("reusable-search__result-container")):
                    search_list=search_results.find_elements_by_class_name("reusable-search__result-container")
                    prev_len_search=len(search_list)
                    driver.execute_script("arguments[0].scrollIntoView();",search_list[prev_len_search-1])
                    
                    print(prev_len_search)
                    time.sleep(1)
            
                for results in search_results.find_elements_by_class_name("reusable-search__result-container"):
                    if sentResults>= resultsToScrap:
                        break
                    driver.execute_script("arguments[0].scrollIntoView();",results)
                    temp={}
                    temp["img"]="/static/mock-images/avatars/avatar_default.jpg"
                    try:
                        try:
                            temp["url"]=results.find_element_by_tag_name('a').get_attribute('href')
                            temp["url"]="https://www.linkedin.com/in/"+temp["url"].split(".com/in/")[1].split("/")[0].split("?")[0]
                            print(temp["url"])
                        except:
                            pass
                        try:
                            x=results.find_elements_by_tag_name('span')
                        except:
                            pass
                        print(f"x : {x[1].text}")
                        try:

                            nametemp=x[1].text.strip().split('\n')
                            temp["name"]=nametemp[0]
                            temp["degree"]=nametemp[3]
                        except:
                            pass
                        
                        try:
                            temp["img"]=results.find_element_by_tag_name('img').get_attribute('src')
                        except:
                            pass

                        try:

                            temp["role"]=results.find_element_by_class_name('entity-result__primary-subtitle').text.strip()
                        except:
                            pass
                        try:
                            temp["location"]=results.find_element_by_class_name("entity-result__secondary-subtitle").text.strip()
                        except:
                            pass
                        try:
                            temp["summary"]=results.find_element_by_class_name('entity-result__summary').text.strip()
                        except:
                            pass
                        try:
                            temp["mutalConnections"]=results.find_element_by_class_name('entity-result__simple-insight').text.strip()
                        except:
                            pass
                    except Exception as e:
                        
                        pass
                    added=False ## TO AVOID ADDTION OF SAME PROSPECT IN DIFFERENT LISTS 
                    #Prioirty first already in sequence then companies than keywork and last image
                    if self.hideAlready and temp["url"] in self.prospectsUrl:
                        
                        print(temp["url"])
                        print(self.prospectsUrl)
                        alreadyinSeq.append(temp)
                        added=True
                    if self.hideCompany and added==False and any(x.lower() in temp["role"].lower() for x in self.companies):
                        containingCompanies.append(temp)
                        added=True
                    if self.hideKeywords and added==False and any(x.lower() in temp["role"].lower() for x in self.keywords):
                        containingKeywords.append(temp)
                        added=True
                    if self.hideImage and added==False and temp["img"]=="/static/mock-images/avatars/avatar_default.jpg":
                        withoutImage.append(temp)
                        added=True
                    
                    if added==False:
                        print("in else")
                        scrapped_results.append(temp)
                        sentResults=sentResults+1
                    
                #driver.execute_script("window.scrollTo(0, Math.ceil(document.body.scrollHeight));")
                data={"data":scrapped_results,"withoutImage":withoutImage,"containingKeywords":containingKeywords,"containingCompanies":containingCompanies,"alreadyinSeq":alreadyinSeq}
                self.sendResponse(data=data)
                try:
                    next_page_disbaled = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until( EC.presence_of_element_located((By.XPATH,
                "//button[contains(@class, 'artdeco-pagination__button artdeco-pagination__button--next artdeco-button artdeco-button--muted artdeco-button--icon-right artdeco-button--1 artdeco-button--tertiary artdeco-button--disabled ember-view')]",)))
                    break
                except:
                    pass    
                next_page = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until( EC.presence_of_element_located((By.XPATH,
                "//button[contains(@class, 'artdeco-pagination__button artdeco-pagination__button--next')]",)))
                next_page.click()
            
            
            except Exception as e:
                print(e)
                pass
        data={}
        data["exitCode"]=200
        self.sendResponse(data=data)
        if close_on_complete:
            driver.close()
        return scrapped_results
       
    def send_Connect_Status(self,close_on_complete=True,link=None):
        driver = self.driver
        self.sendResponse(data="starting sending connect")
        if link==None:
            driver.get(self.linkedin_url)
        else:
            driver.get(link)
        try:
           
            send_connect=WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//button[@class='artdeco-button artdeco-button--2 artdeco-button--primary ember-view pvs-profile-actions__action']"
                    )
                )
            )
            self.sendResponse(data="not accepted")
            print("Not accepted")
            return False
        except:
            
            sendConnectButton=False
        try:
            send_connect=WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//button[@class='artdeco-button artdeco-button--muted artdeco-button--2 artdeco-button--full artdeco-button--secondary ember-view pvs-profile-actions__action']"
                    )
                )
            )
            self.sendResponse(data="already sent and not accepted")
            print("Not accepted already sent")
            self.dontSendConnect=True;
            return False
        except TimeoutException:
            #print(e)
            if close_on_complete:
                driver.close()
            self.sendResponse(data="accepted")
            print("accepted")
            return True

    def send_Connect(self,close_on_complete=True,link=None):
        driver = self.driver
        self.sendResponse(data="starting sending connect")
        if link==None:
            driver.get(self.linkedin_url)
        else:
            driver.get(link)
        try:
           
            send_connect=WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//button[@class='artdeco-button artdeco-button--2 artdeco-button--primary ember-view pvs-profile-actions__action']"
                   
                    )
                )
            )
            #send_connect = self.driver.find_element(By.XPATH,"//button[@class='artdeco-button artdeco-button--2 artdeco-button--primary ember-view pvs-profile-actions__action']")
            #send_connect.find_element_by_tag_name("button").click()
            send_connect.click()
            self.sendResponse(data="click connection")
            send_connect=WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//button[@class='ml1 artdeco-button artdeco-button--2 artdeco-button--primary ember-view']",
                    )
                )
            )
            time.sleep(3)

            send_connect.click()
            self.sendResponse(data="clicked send connection")
            if close_on_complete:
                driver.close()
            data={}
            data["message"]="connect sent Sucessfully"
            data["exitCode"]=200
            self.sendResponse(data=data)
            return True
        except Exception as e:
            print(e)
            
            data={}
            data["message"]="connect sent unsucessfully"
            data["exitCode"]=500
            self.sendResponse(data=data)
            if close_on_complete:
                driver.close()
            return False
    def withdraw_Connect(self,close_on_complete=True,link=None):
        driver = self.driver
        self.sendResponse(data="starting sending connect")
        if link==None:
            driver.get(self.linkedin_url)
        else:
            driver.get(link)
        try:
           
            send_connect=WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located(
                    (
                        By.CLASS_NAME,
                        "pvs-profile-actions ",
                    )
                )
            )
            
            withdraw_connect = self.driver.find_element_by_class_name("pvs-profile-actions")
            withdraw_connect.find_element_by_tag_name("button").click()
            self.sendResponse(data="click connection")
            withdraw_connect=WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//button[@class='artdeco-modal__confirm-dialog-btn artdeco-button artdeco-button--2 artdeco-button--primary ember-view']",
                    )
                )
            )
            time.sleep(3)

            withdraw_connect.click()
            self.sendResponse(data="clicked send connection")
            if close_on_complete:
                driver.close()
            data={}
            data["message"]="connect sent Sucessfully"
            data["exitCode"]=200
            self.sendResponse(data=data)
            return True
        except Exception as e:
            print(e)
            
            data={}
            data["message"]="connect sent unsucessfully"
            data["exitCode"]=500
            self.sendResponse(data=data)
            if close_on_complete:
                driver.close()
            return False
    def viewProfile(self, close_on_complete=True,link=None):
        driver = self.driver
        if link==None:
            driver.get(self.link)
            link=self.link
        else:
            driver.get(link)
        self.sendResponse(data="opened link")
        
        
       
        
        duration = None
        # driver.execute_script("window.onfocus()")
        # driver.execute_script("window.onblur = function() { window.onfocus() }")
        root = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
            EC.presence_of_element_located(
                (
                    By.CLASS_NAME,
                    self.__TOP_CARD,
                )
            )
        )

        self.name = root.find_element_by_class_name('text-heading-xlarge').text.strip()
        
        
        res={}
        # get 500 connections
        try:
            
            print("came here 1")
            

           

            connections = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//ul[contains(@class, 'pv-top-card--list pv-top-card--list-bullet display-flex pb1')]",
                    )
                )
            )
            res["connections"]=True
        except Exception as e:
            print("error")
            #print(e)
            res["connections"]=False
            pass

            
            
        
        #contact
        
        # driver.execute_script(
        #     "window.scrollTo(0, Math.ceil(document.body.scrollHeight/2));"
        # )

        # # get experience
        # driver.execute_script(
        #     "window.scrollTo(0, Math.ceil(document.body.scrollHeight*3/5));"
        # )

        
        try:
            driver.get(link+'/overlay/contact-info/')
            email = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located(
                    (
                        By.CLASS_NAME,
                        "ci-email",
                    )
                )
            )
            consct_section = self.driver.find_element_by_class_name("ci-email")
            self.email=consct_section.find_element_by_tag_name("a").text.strip()
            res["email"]=self.email
            print(res["email"])
        except:
            res["email"]=None
            pass
        try:
            driver.get(link+'/details/experience/')
            exp = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[contains(@class, 'pvs-list__container')]",
                    )
                )
            )
            exp.find_element(By.XPATH,".//li[contains(@class, 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated ')]")
            res["position"]=exp.find_element(By.XPATH,".//span[contains(@class,'t-bold mr1')]").text.strip().split("\n")[0]

            company=exp.find_element(By.XPATH,".//span[contains(@class,'t-14 t-normal')]").text.strip()
            print(company)
            company=company.split(" ·")[0]
            print(company)
            res["company"]=company
            print(res)
       
       
        except Exception as e:
            res["company"]=None
            res["role"]=None
        
        if close_on_complete:
            driver.quit()
        print(res)
        return res
    def highlight(self,element, effect_time, color, border):
   
        driver = element._parent
        def apply_style(s):
            driver.execute_script("arguments[0].setAttribute('style', arguments[1]);",
                                element, s)
        original_style = element.get_attribute('style')
        apply_style("border: {0}px solid {1};".format(border, color))
        time.sleep(effect_time)
        apply_style(original_style)

    def sendFollow(self, close_on_complete=True,link=None):
        driver = self.driver
        if link==None:
            driver.get(self.link)
            link=self.link
        else:
            driver.get(link)
        self.sendResponse(data="opened link")
        
        
       
        
        duration = None
        # driver.execute_script("window.onfocus()")
        # driver.execute_script("window.onblur = function() { window.onfocus() }")
        root = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
            EC.presence_of_element_located(
                (
                    By.CLASS_NAME,
                    self.__TOP_CARD,
                )
            )
        )
        time.sleep(2)
        more=root.find_elements(By.XPATH,"//button[contains(@class,'artdeco-dropdown__trigger artdeco-dropdown__trigger--placement-bottom ember-view pvs-profile-actions__action artdeco-button artdeco-button--secondary artdeco-button--muted')]")[-1]
        more.click()

        time.sleep(1)
        
        list=root.find_elements(By.XPATH,"//div[contains(@class,'pvs-overflow-actions-dropdown__content artdeco-dropdown__content artdeco-dropdown--is-dropdown-element artdeco-dropdown__content--justification-left artdeco-dropdown__content--placement-bottom ember-view')]")[-1]
        follow=list.find_elements(By.XPATH,"//*[contains(text(),'Follow')]")
        driver.execute_script(
            "window.scrollTo(0, Math.ceil(document.body.scrollHeight*.15));"
        )
        time.sleep(1)
        #self.highlight(element=follow[-1],effect_time= 3,color= "blue", border=5)
        #time.sleep(5)
        follow[2].click()
        if close_on_complete:
            driver.close()
   
    def likeLastPost(self, close_on_complete=True,link=None):
        driver = self.driver
        if link==None:
            driver.get(self.link+"/recent-activity/shares/")
            link=self.link
        else:
            driver.get(link)
        self.sendResponse(data="opened link")
        
        
       
        res=0
        duration = None
        # driver.execute_script("window.onfocus()")
        # driver.execute_script("window.onblur = function() { window.onfocus() }")
        try:
            root = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[contains(@class,'feed-shared-update-v2 feed-shared-update-v2--minimal-padding full-height relative artdeco-card ember-view')]",
                    )
                )
            )

            time.sleep(1)
            post_like_button=root.find_element(By.XPATH,"//button[contains(@class,'artdeco-button artdeco-button--muted artdeco-button--4 artdeco-button--tertiary ember-view social-actions-button react-button__trigger')]")
            post_like_button.click()
            res=1
        except:
            pass
        if close_on_complete:
            driver.close()
        return res
    @property
    def company(self):
        if self.experiences:
            return (
                self.experiences[0].institution_name
                if self.experiences[0].institution_name
                else None
            )
        else:
            return None

    @property
    def job_title(self):
        if self.experiences:
            return (
                self.experiences[0].position_title
                if self.experiences[0].position_title
                else None
            )
        else:
            return None

    def __repr__(self):
        return "{name}\n\nAbout\n{about}\n\nExperience\n{exp}\n\nEducation\n{edu}\n\nInterest\n{int}\n\nAccomplishments\n{acc}\n\nContacts\n{conn}\n\n{email}\n".format(
            name=self.name,
            about=self.about,
            exp=self.experiences,
            edu=self.educations,
            int=self.interests,
            acc=self.accomplishments,
            conn=self.contacts,
            email=self.email,
        )
