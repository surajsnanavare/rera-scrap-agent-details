from bs4 import BeautifulSoup
import requests
import pickle
import re
import pandas as pd
import os
import time
import subprocess

current_file_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_file_path)
sleep_time_seconds = 5
onLocal = False

subprocess.run(["git", "config", "--global", "user.email", "github-action@example.com"])
subprocess.run(["git", "config", "--global", "user.name", "GitHub Action"])

def commit_and_push(count):
    commit_message = f"Added new peroperty agents [Total:{count}]"
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", commit_message])
    subprocess.run(["git", "push", "origin", "main"])

def show_progress(percentage):
    print(f"\rProgress: {percentage:.2f}%", end="", flush=True)


def clean_string(input_string):
    # cleaned_string = re.sub(r"\s+", "", input_string)
    cleaned_string = input_string.strip()
    cleaned_string = cleaned_string.title()
    return cleaned_string


def load_data_from_file(filename):
    try:
        with open(filename, "rb") as file:
            data = pickle.load(file)
        return data
    except FileNotFoundError:
        return None


def save_data_to_file(data, filename):
    with open(filename, "wb") as file:
        pickle.dump(data, file)


def update_json_data(filename, new_data):
    existing_data = load_data_from_file(filename)
    if existing_data is None:
        existing_data = {}

    existing_data.update(new_data)
    save_data_to_file(existing_data, filename)


def convert_to_dataframe(data):
    df = pd.DataFrame(data.values(), index=data.keys())
    return df


def save_to_xlsx(dataframe, output_file):
    dataframe.to_excel(output_file)


base_url = "https://maharerait.mahaonline.gov.in"


def getAgentsListHtml(page_no):
    url = f"{base_url}/SearchList/Search"
    payload = f"__RequestVerificationToken=kwk2bw6laubnHTK_j6Q9W5-gwt_2XxS6G-em3EOpt-wrXshbPN4JyYT33sWCKHY9t5lzYbtbcJaW1nKT56yu0cE9Gj3AjNrzzXc0E5NB_Dc1&Type=Agent&ID=0&pageTraverse=1&Project=&hdnProject=&Promoter=&hdnPromoter=&AgentName=&hdnAgent=&CertiNo=&hdnCertiNo=&State=27&hdnDivision=&hdnDistrict=&hdnProject=&hdnDTaluka=&hdnVillage=&hdnState=&District=521&hdnState=&PinCode=&hdnPincode=&CompletionDate_From=&hdnfromdate=&CompletionDate_To=&hdntodate=&PType=&hdnPType=&btnSearch=Search&CurrentPage={page_no}&Command=Next"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-GB,en;q=0.9,mr;q=0.8,es;q=0.7",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": "__RequestVerificationToken=OlyLv50I35XgcxDPlJWMFVu9F9_1KAJpIqsRbhxo-EAQiGmreLiposk3nJ3NpBpMYhczP12aScShAoSo6uMgUwSpWPcCU1ZnCSamve6hc_c1; ASP.NET_SessionId=54dgaz12zge0lh0vi5t2aok4",
        "Origin": f"{base_url}",
        "Pragma": "no-cache",
        "Referer": f"{base_url}/SearchList/Search",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text


def getAgentPersonalDetailsHtml(profile_link):
    url = profile_link
    payload = {}
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-GB,en;q=0.9,mr;q=0.8,es;q=0.7",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Cookie": "ASP.NET_SessionId=ksajkbv403g3oyohksjfry2g",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "Referer": f"{profile_link}",
        "Origin": f"{base_url}",
        "If-None-Match": '"XKxBfuUXDsjc8U3Expq2BwOEZ38="',
        "If-Modified-Since": "Tue, 13 Jun 2023 11:15:45 GMT",
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.text


def getValueByLabel(soup, personal_label, company_label):
    elem = soup.find("label", {"for": personal_label})

    if elem is None:
        elem = soup.find("label", {"for": company_label})

    return elem.parent.find_next_sibling("div").get_text()


def getAgentPersonalDetails(profile_link):
    try:
        html_content = getAgentPersonalDetailsHtml(profile_link)
        soup = BeautifulSoup(html_content, "html.parser")

        locality = getValueByLabel(
            soup,
            "PersonalInfoModel_IndivisualLocality",
            "PersonalInfoModel_CompanyLocality",
        )

        district = getValueByLabel(
            soup,
            "PersonalInfoModel_IndivisualDistrictValue",
            "PersonalInfoModel_CompanyDistrictValue",
        )

        taluka = getValueByLabel(
            soup,
            "PersonalInfoModel_IndivisualTalukaValue",
            "PersonalInfoModel_CompanyTalukaValue",
        )

        village = getValueByLabel(
            soup,
            "PersonalInfoModel_IndivisualVillageValue",
            "PersonalInfoModel_CompanyVillageValue",
        )

        pin_code = getValueByLabel(
            soup,
            "PersonalInfoModel_IndivisualPinCode",
            "PersonalInfoModel_CompanyPinCode",
        )

        phone_no = getValueByLabel(
            soup,
            "PersonalInfoModel_IndivisualOfficeNo",
            "PersonalInfoModel_CompanyOfficeNo",
        )

        return {
            "Phone No": clean_string(phone_no),
            "Locality": clean_string(locality),
            "District": clean_string(district),
            "Taluka": clean_string(taluka),
            "Village": clean_string(village),
            "Pin Code": clean_string(pin_code),
        }
    except Exception as ex:
        print(ex)
        return {}


def getAgentDetailsFromHtmlRow(agent_row):
    try:
        agent_details = {}

        name = agent_row.find("td", {"data-name": "Name"}).text
        certiNoElement = agent_row.find("td", {"data-name": "CertiNo"})
        link = certiNoElement.find_next_siblings("td")[0].find("a", href=True)["href"]
        full_link = f"{base_url}{link}"
        agent_details["Name"] = name.title()
        agent_details["Certificate No"] = certiNoElement.text
        agent_details["Profile Link"] = full_link
        personal_details = getAgentPersonalDetails(full_link)
        agent_details.update(personal_details)
        return agent_details

    except Exception as ex:
        pass


def getAgentList(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    list_table = soup.find("table")
    agents = list_table.find_all("tr")
    return agents


if __name__ == "__main__":
    pickle_file = os.path.join(current_directory, "rera_agent_details_json.pkl")
    excel_output_file = os.path.join(current_directory, "rera_agent_details.xlsx")
    current_page_file = os.path.join(current_directory, "current_page.pkl")
    total_agents_expected = 9356

    agent_details = load_data_from_file(pickle_file)
    current_page = load_data_from_file(current_page_file)

    if agent_details is None:
        agent_details = {}

    if current_page is None:
        current_page = 0

    print(f"Starting from page_no: {current_page}")
    for page_no in range(current_page, 189):
        html_content = getAgentsListHtml(page_no)
        agents = getAgentList(html_content)

        for agentHtmlRow in agents:
            agent = getAgentDetailsFromHtmlRow(agentHtmlRow)
            if agent:
                agent_details[agent["Certificate No"]] = agent
                total_agents_fetched = len(agent_details.values())
                percentage = (total_agents_fetched / total_agents_expected) * 100
                show_progress(percentage)
        
        total_agents_fetched = len(agent_details.values())
        save_data_to_file(page_no + 1, current_page_file)
        save_data_to_file(agent_details, pickle_file)
        df = convert_to_dataframe(agent_details)
        save_to_xlsx(df, excel_output_file)
        if not onLocal: commit_and_push(total_agents_fetched)

        print(f"\n Sleeping for {sleep_time_seconds} seconds before next run!")
        time.sleep(sleep_time_seconds)
