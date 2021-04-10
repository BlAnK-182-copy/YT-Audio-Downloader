import os, sys, getpass, json, subprocess, datetime, time

#Close Chrome if it is running.
subprocess.call('TASKKILL /f /IM CHROME.exe')
subprocess.call('TASKKILL /f /IM CHROMEDRIVER.exe')

#Downloading Modules
os.system('pip install selenium')
os.system('pip install youtube-dl')
os.system('pip install chromedriver-autoinstaller')

#Importing the downloaded modules
import youtube_dl
import chromedriver_autoinstaller
import selenium 
from selenium import webdriver
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 

chromedriver_autoinstaller.install() #Installing chrome driver by checking version of the chrome.

#Constants
ILLEGAL_CHARS = ['<','>',':', '\"', '/', '\\', '|', '?', '*'] #List of all illegal chars as filename in windows.
OPTIONS = webdriver.ChromeOptions()
OPTIONS.add_argument(f"user-data-dir=C:\\Users\\{getpass.getuser()}\\Roaming\\Google\\Chrome\\User Data")
print('C:\\Users\\{getpass.getuser()}\\Roaming\\Google\\Chrome\\User Data')
OPTIONS.add_argument('log-level=3')

BROWSER = webdriver.Chrome(chrome_options = OPTIONS)
BROWSER.minimize_window()
BROWSER.get('https://www.youtube.com')


#Functions
def AppendIntoFileNameFile(string, file): #For apppending into filename-file without having to copy paste the same code 3 times.
    newFileName=''
    for char in string:
        if char not in ILLEGAL_CHARS:
            newFileName+=char
    
    file.write(newFileName + '\n')

#Asking User to enter song name or name of a file containing song names.
while True:

    fnFile = open('fnFile.txt', 'w') #Temporary file, created to read from and fetch urls.

    print('''How would you like to enter names of the audio you wish to download? 
1. input (singular) - Enter the name of one video you would like to download.
2. input (multiple) - Enter the names of multiple videos you would like to download.
3. file - Enter the location of a file containing a list of names of the video you would like to download
(Enter 'q' to terminate the execution of the program)''')

    askMode = input('Enter option number: ')

    #Input - singular
    if askMode == '1':
        songName = input('Enter name of a song in the format: <artist> - <song name>: ')
        AppendIntoFileNameFile(songName, fnFile)
        break

    #Input - multiple
    elif askMode == '2':
        enteredOne = 'no'
        while True:
            ask = input('Do you want to enter song names: ')
            if ask.lower() == 'yes':
                songName = input('Enter name of a song in the format: <artist> - <song name>: ')
                AppendIntoFileNameFile(songName, fnFile)
                enteredOne = 'yes'

            elif ask.lower() == 'no':
                if enteredOne == 'no':
                    print('Please enter at least one song name before quiting. ')
                else:
                    break
            else:
                print('Enter valid input.')
        break
            

    #File 
    elif askMode == '3':
        try:
            userFileName = input('Enter exact location of the file: ')
            userFile = open(userFileName, 'r')
            for line in userFile:
                line = line.strip('\n')
                AppendIntoFileNameFile(line, fnFile)
            break
                    
        except FileNotFoundError:
            print('Sorry. We couldn\'t locate the file. It either doesn\'t exist or is stored somewhere else.')

    #Quiting
    elif askMode.lower() == 'q':
        sys.exit()

    else:
        print('Enter valid input.')

urls = {} #dictionary of every songname and their respective urls.

#Asking or keywords
while True:
    ask = input('Do you want to add any kewywords to the search criteria (ex: lyrics, audio only etc.) (Yes/No): ')
    if ask.lower() == 'yes':
        keywords = input('Enter keywords: ')
        break 
    elif ask.lower() == 'no':
        keywords = ''
        break 
    else:
        print('Enter valid input.')

fnFile.close()
fnFile = open('fnFile.txt','r')


#Fetching urls using selenium

print('Fetching Urls. Do not panic if it looks stuck!')

for songName in fnFile:
    if songName!='\n':
        songName = songName.rstrip('\n')
        searchBar = WebDriverWait(BROWSER, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@id=\'search\']'))
        )
        searchBar.clear()
        searchBar.send_keys(songName+' '+keywords)
        searchBar.send_keys(Keys.RETURN)
        time.sleep(5)

        urlsRaw = BROWSER.find_elements_by_tag_name('a')
        urlsRaw = [i.get_attribute('href') for i in urlsRaw if i.get_attribute('href') != None]
        # print(json.dumps(urlsRaw, indent=2))

        for rawUrl in urlsRaw:
            splitUrl = rawUrl.split('/')
            if len(splitUrl)>3:
                # print(splitUrl)

                # print('Raw Url:', rawUrl)
                check_watch = splitUrl[3][0:5]
                # print(check_watch)
                if check_watch.lower() == 'watch':
                    urls[songName] = rawUrl
                    break 
        

BROWSER.quit() 

print(json.dumps(urls, indent = 3))

#Creating folder
folderName = ''
currentDT = str(datetime.datetime.now())
for i in currentDT:
    if i not in ILLEGAL_CHARS:
        folderName+=i 

folderName+='-'+str(len(urls))

os.mkdir(folderName)


#Downloading Songs 
ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessor': [{
        'key':'FFmpegExtractAudio',
        'preferredcodec':'mp3',
        'preferredquality':'192',
    }
    ],
}

for song in urls:
    ydl_opts['outtmpl'] = f'C:\\Users\\jagsa\\Documents\\Python Workspace - VSCODE\\Workspace α - Projects\\Tools\\Youtube Audio Downloader\\Beta v.1\\{folderName}\\{song}.mp3'
    # print(ydl_opts)
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        songUrl = [urls[song]]
        ydl.download(songUrl)
        print(f'Song Downloaded: {song}')

print(f'Downloaded songs in folder: {folderName}')
# sys.exit() 