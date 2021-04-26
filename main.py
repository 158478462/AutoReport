import sys, time, base64, json
from selenium import webdriver

class AutoReport(object):

    loginURL = "https://newsso.shu.edu.cn/login/"
    mainpageURL = "https://selfreport.shu.edu.cn"
    reportURL = "https://selfreport.shu.edu.cn/DayReport.aspx?day=%s"
    historyURL = "https://selfreport.shu.edu.cn/ReportHistory.aspx"

    def __init__(self, id="", password="", inShanghai="False", onCampus="False", isHomeAddress="True"):
        self.id = id
        self.password = password
        assert inShanghai in ["True", "False"], "inShanghai Input Error"
        self.inShanghai = True if inShanghai == "True" else False
        assert onCampus in ["True", "False"], "onCampus Input Error"
        self.onCampus = True if onCampus == "True" else False
        assert isHomeAddress in ["True", "False"], "isHomeAddress Input Error"
        self.isHomeAddress = True if isHomeAddress == "True" else False
        self.date = time.strftime("%Y-%m-%d", time.localtime())
        self.__browser = None
        # TODO logger need to be added

    def __generateLoginURL(self):
        param = {
            "timestamp": time.time_ns(),
            "responseType": "code",
            "clientId": "WUHWfrntnWYHZfzQ5QvXUCVy",
            "scope": "1",
            "redirectUri": "https://selfreport.shu.edu.cn/LoginSSO.aspx?ReturnUrl=%2f",
            "state": ""
        }
        loginURL = self.loginURL + str(base64.b64encode(json.dumps(param).encode()), encoding='utf8')
        return loginURL

    def __invokeBrowser(self):
        option = webdriver.ChromeOptions()
        # add --no-sandbox to enalbe chrome running under root account
        option.add_argument("--no-sandbox")
        option.add_argument("--headless")
        option.add_argument("--disable-gpu")
        option.add_argument("--disable-dev-shm-usage")
        # self.__browser = webdriver.Chrome("./chromedriver", options=option)
        self.__browser = webdriver.Chrome(options=option)
        return 1

    def __delBrowser(self):
        self.__browser.close()
        self.__browser.quit()
        
    # TODO handle the situation of wrong id or password
    def login(self):
        self.__browser.get(self.__generateLoginURL())
        self.__browser.implicitly_wait(1)
        idBlock = self.__browser.find_element_by_id("username")
        idBlock.send_keys(self.id)
        passwordBlock = self.__browser.find_element_by_id("password")
        passwordBlock.send_keys(self.password)
        button = self.__browser.find_element_by_id("submit")
        button.click()
        self.__browser.implicitly_wait(1)
        try:
            errorMsg = self.__browser.find_element_by_class_name("showMessage")
        except:
            return 1
        else:
            return 0


    def submitData(self, date):
        URL = self.reportURL % (date)
        self.__browser.get(URL)
        self.__browser.implicitly_wait(1)
        # Promise
        undertakeCheckBox = self.__browser.find_element_by_id("p1_ChengNuo-inputEl-icon")
        undertakeClassAttributes = undertakeCheckBox.get_attribute("class")
        if "f-checked" not in undertakeClassAttributes: undertakeCheckBox.click()
        # Body Status
        bodyStatus = self.__browser.find_element_by_id("fineui_0-inputEl-icon")
        bodyStatusClassAttributes = bodyStatus.get_attribute("class")
        if "f-checked" not in bodyStatusClassAttributes: bodyStatus.click()
        # location
        locationStatusElementId = "fineui_7-inputEl-icon" if self.inShanghai else "fineui_8-inputEl-icon"
        locationStatus = self.__browser.find_element_by_id(locationStatusElementId)
        locationStatusClassAttributes = locationStatus.get_attribute("class")
        if "f-checked" not in locationStatusClassAttributes: locationStatus.click()
        if self.inShanghai:
            campusStatusElementId = "fineui_9-inputEl-icon" if self.onCampus else "fineui_10-inputEl-icon"
            campusStatus = self.__browser.find_element_by_id(campusStatusElementId)
            campusStatusClassAttributes = campusStatus.get_attribute("class")
            if "f-checked" not in campusStatusClassAttributes: campusStatus.click()
        # Home Address
        homeAddressStatusElementId = "fineui_11-inputEl-icon" if self.isHomeAddress else "fineui_12-inputEl-icon"
        homeAddressStatus = self.__browser.find_element_by_id(homeAddressStatusElementId)
        homeAddressStatusCLassAttributes = homeAddressStatus.get_attribute("class")
        if "f-checked" not in homeAddressStatusCLassAttributes: homeAddressStatus.click()
        submitButton = self.__browser.find_element_by_id("p1_ctl01_btnSubmit")
        submitButton.click()
        self.__browser.implicitly_wait(1)
        try:
            errorMessage = self.__browser.find_element_by_class_name("f-messagebox-errorfield").text
        except:
            pass
        else:
            raise Exception(errorMessage)
        submitConfirmButton = self.__browser.find_element_by_xpath("//*[@class='f-btn-text' and text()='确定']")
        submitConfirmButton.click()
        self.__browser.implicitly_wait(1)
        returnMessage = self.__browser.find_element_by_class_name("f-messagebox-message").text
        assert "成功" in returnMessage, "Submit Failed"
        # TODO handle error


    def checkHistory(self):
        self.__browser.get(self.historyURL)
        records = self.__browser.find_element_by_class_name("f-datalist-list").text.split("\n")
        unfinishedRecord = [item[:10] for item in records if "未填报" in item]
        return unfinishedRecord if unfinishedRecord else None

    def reportUnfinished(self):
        unfinishedRecord = self.checkHistory()
        if unfinishedRecord == None:
            print("None")
            return None
        for item in unfinishedRecord:
            self.submitData(item)
            print(item)
        return str(unfinishedRecord)

    def report(self):
        self.__invokeBrowser()
        self.login()
        self.reportUnfinished()
        self.__delBrowser()

if __name__ == "__main__":
    flow = AutoReport(id=sys.argv[1], password=sys.argv[2], inShanghai=sys.argv[3], onCampus=sys.argv[4], isHomeAddress=sys.argv[5])
    flow.report()
    print()
