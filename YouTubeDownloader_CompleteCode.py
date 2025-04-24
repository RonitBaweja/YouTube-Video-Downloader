# imports all the widgets offered by this module like Buttons,Labels,Tabs,ComboBox,OptionMenu etc.
from customtkinter import *
from tkinter import messagebox,DISABLED,NORMAL
import threading    # module that allows us to concurrently run multiple tasks without GUI freezing.
from pytubefix import YouTube   #Contains all the functions,attributes for video download and info.
from PIL import Image   #Python Library that supports integrating image into code.
import re  #Python module for regular expression matching.
from pytubefix.exceptions import RegexMatchError    #error encountered in URL expression matching.
from pytubefix.exceptions import AgeRestrictedError,VideoUnavailable   #other possible errors.
import pyperclip    #Module to copy and paste text from GUI.
from pytubefix import Playlist  #Contains all functions,attributes and methods for playlist download and info.
from pytubefix import Channel  #Contains all functions,attributes and methods for channel  download and info.

win = CTk()     #main window of application.
win.geometry("600x450")     #sets the dimensions of window.
win.title('YouTube Downloader')     #Main Heading of window.
win.resizable(width=False,height=False) #Prevents resizing of the window.

win.configure(bg='#F0F2F5',border_color='#ff0a54')

#set_appearance_mode('Dark')

#Logic to switch between tabs. Used in code below.
def tab_switch_logic():
    '''Handles the logic to reset current tab when another tab is explicitly clicked'''  #Docstring
    global current_tab  #Define current_tab as a global variable so that its value can be updated automatically with every click.
    selected_tab = tabview.get()    #Get the tab currently in use.

    if current_tab == "Video Download":
        create_video_download_frame()     #Reset this tab when some other tab is clicked.
    elif current_tab == "Playlist":
        create_playlist_download_frame()     #Reset this tab when some other tab is clicked.
    elif current_tab == "Video Info":
        create_video_info_frame()     #Reset this tab when some other tab is clicked.
    elif current_tab == "Playlist Info":
        create_playlist_info_frame()     #Reset this tab when some other tab is clicked.
    elif current_tab == "Channel Info":
        create_channel_info_frame()     #Reset this tab when some other tab is clicked.


    current_tab = selected_tab  #Now set the current_tab to the currently selected tab for next iteration.
    return



'''********************************************************************'''
# Common functions for both video and playlist download.
'''Code to actually download YouTube Video after selecting stream'''

def video_download(link,savepath,res,format,progressbar):
    '''Contains actual logic to download YouTube video with given resolution and format''' #Docstring

    #Create a try block to handle potential errors.
    try:    
        #Create a class object to access YouTube class methods
        yt = YouTube(url=link,on_progress_callback= lambda stream,chunk,bytes_remaining: update_video_progress(stream,chunk,bytes_remaining,progressbar))

        # Fetch all the streams availaible for the video, then filter based on given specifications.
        stream = yt.streams.filter(resolution=res,progressive=True,file_extension=format).first()  #In case of multiple possible streams we pick the first one.

        if stream:  #Checks if the required stream is availaible or not.
            stream.download(output_path=savepath) #Downloads the selected stream to the specified savepath.
            return True,f"Download Complete: {yt.title}"  #Returns True and a success message.
        else:  #If no matching stream was found.
            return False,f"No stream availaible with resolution :{res}"  #Returns False and a fail message.
    except RegexMatchError:
        return False,"Invalid URL provided"
    except AgeRestrictedError:
        return False,"This video is Age Restricted and cannot be downloaded"
    except VideoUnavailable:
        return False,"This video is unavailaible"
    except Exception as e:  # Catch any exceptions if raised during download process in variable e
        return False,f"{e}" #Returns False and an error message with exception details
        
    return

# We define a function to update the progressbar during video download.
def update_video_progress(stream, chunk, bytes_remaining, progress_bar):
    """Updates the progress bar during download."""
    total_size = stream.filesize    # finds out total filesize in bytes.
    bytes_downloaded = total_size - bytes_remaining     # bytes_remaining is retured by pytubefix during each internal function call.
    percentage = (bytes_downloaded / total_size) * 100  # calculate total percent download till now.
    progress_bar.set(percentage / 100)  # progress bar accepts values from 0.0 to 1.0


'''***********************************VIDEO DOWNLOAD TAB***************************************'''
# Adding Frame to Single Video Download Tab.

def create_video_download_frame():
    '''Function to create the Frame on Video Download Tab'''

    single_video_frame = CTkFrame(master=single_video_tab,corner_radius=25,border_width=3,border_color='#ADB5BD') #Creating a new frame that will be placed on top of Tab.
    single_video_frame.place(relx=0,rely=0,relwidth=1,relheight=1)    #Places frame on the main tab window.

    def video_download_button_click(video_url_entry,video_quality_menu,video_format_menu,video_status_label,video_download_button,video_download_progressbar):
        '''Handles the download button click event'''  #Docstring

        url = video_url_entry.get()     #Gets the YouTube video URL from entry.
        url_prefix = "https://www.youtube.com/watch?v="    #Standard format for YouTube URL.

        if not ("youtube.com" in url or "youtu.be" in url):  #Check if URL follows YouTube format or not.
            messagebox.showerror('Error','Invalid URL provided')    #Raise Error if URL format invalid.
            video_url_entry.delete(0,'end')     #clear the video_url entry.
            return

        vid_res = video_quality_menu.get()  #Gets the selected resolution from dropdown.
        vid_format = video_format_menu.get()  #Gets the selected format from dropdown.
        savepath = filedialog.askdirectory()  #Gets the savepath of the video to be downloaded.

        #Checks if any of the required fields are empty.
        if not url or not vid_res or not vid_format or not savepath:
            # Displays an error message, stating to provide all required fields.
            messagebox.showerror("Error","Please provide URL,savepath,video format and resolution")
            return
        
        # We now disable the download button while download process taking place.
        video_download_button.configure(state=DISABLED)  #Disables the download button during the download process.
        video_status_label.configure(text='Downloading....')  #Updates the status label indicating download has started.

        
        video_download_progressbar.set(0)   #Initialize the progressbar with 0


        # We create a separate thread to download video to prevent freezing of GUI.
        def download_thread():
            '''Runs download in a separate thread to avoid freezing of GUI'''
            success,message = video_download(link=url,savepath=savepath,res=vid_res,format=vid_format,progressbar=video_download_progressbar)  #unpack the tuple to fetch message and update success.
            update_video_status(success,message,video_status_label,video_download_button)    #Finally update the download status whether success or fail.

        threading.Thread(target=download_thread).start() #Creates a new thread to execute download_thread function.
        video_download_button.configure(state=NORMAL)     #Re-enables the download button after process is complete/failed.
        return


    #We create a function to update the download status
    def update_video_status(success,message,video_status_label,video_download_button):
        '''Updates the status label and re-enables the download button'''

        if success: #checks if download was successful
            #Truncate the message in case its too long.
            if len(message) > 40:
                message = message[:40] + '.....'
            
            video_status_label.configure(text=message,bg_color='#D1E7DD')  #Sets the status label to success message and sets the background colour to green.
        else: #If download was unsuccessful.
            video_status_label.configure(text=message,bg_color='#F8D7DA')  #Sets the status label to fail message and sets the backgroun colour to red.

        video_download_button.configure(state=NORMAL)  #Re-enables the download button.

    # Function to clear URL entry field.
    def url_reset_button_click():
        video_url_entry.delete(0,'end')

    # Placing widgets on Video Download Tab.

    # Video URL Label
    video_url_label = CTkLabel(master=single_video_frame,text='Video URL:',text_color='#212529',font=('Ariel',20,'bold'),corner_radius=10)    #Creates a label for video URL.
    video_url_label.place(relx=0.1,rely=0.1)    #Adds label to parent window.

    # Video URL Entry.
    video_url_entry = CTkEntry(master=single_video_frame,placeholder_text="Paste your video link here",font=('Ariel',20),width=300,corner_radius=10,placeholder_text_color='#6C757D')    #Creates an entry for video URL.
    video_url_entry.place(relx=0.35,rely=0.09)  #Adds entry to parent window.

    # Video Quality Label.
    video_quality_label = CTkLabel(master=single_video_frame,text="Select Quality",font=('Ariel',20,'bold'),text_color='#212529',corner_radius=10) #Creates a Label for video quality.
    video_quality_label.place(relx=0.1,rely=0.25)   #Adds Label to parent window.

    # Video Quality OptionMenu.
    resolutions = ["1080p", "720p", "480p", "360p","240p","144p"]  #Creates a list of availaible resolutions.
    video_quality_menu = CTkOptionMenu(master=single_video_frame,values=resolutions)  #Creates a dropdown OptionMenu for resolution selection.
    video_quality_menu.place(relx=0.45,rely=0.25)   #Adds dropdown to parent window.

    # Video Format Label.
    video_format_label = CTkLabel(master=single_video_frame,text="Select Format",font=('Ariel',20,'bold'),text_color='#212529',corner_radius=10) #Creates a label for video format.
    video_format_label.place(relx=0.1,rely=0.40)  #Adds Label to parent window.

    # Video Format OptionMenu.
    format_options = ['mp4', 'webm', 'mp3']    #Creates a list of available format options.
    video_format_menu = CTkOptionMenu(master=single_video_frame,values=format_options)  #Creates a dropdown OptionMenu for format selection.
    video_format_menu.place(relx=0.45,rely=0.40)    #Adds dropdown to parent window.


    # Main Download Button
    video_download_button = CTkButton(master=single_video_frame,corner_radius=20,text='Download',text_color='#212529',\
                                    command=lambda: video_download_button_click(video_url_entry, video_quality_menu, video_format_menu, video_status_label, video_download_button, video_download_progressbar),\
                                    fg_color='#32B8CB',font=('Ariel',20,'bold'),\
                                    border_width=3,border_color='black')  #Creates a download button that will give the main command.
    video_download_button.place(relx=0.32,rely=0.58)     #Adds button to parent window.

    # Status Label to indicate current status.
    message = "    Please paste link from address bar\n not from share icon."
    video_status_label = CTkLabel(master=single_video_frame,text=message,font=('Ariel',20,'bold'))  #Creates a label for video status like Downloading... or Downloaded.
    video_status_label.place(relx=0.1,rely=0.72)  #Adds status label to parent window.

    # Progressbar to indicate download progress.
    video_download_progressbar = CTkProgressBar(master=single_video_frame,orientation="horizontal",mode="determinate",width=350,progress_color='#0D6EFD') #Creates a progressbar that will indicate the download progress.
    video_download_progressbar.place(relx=0.1,rely=0.90)    #Adds progressbar to parent window.
    video_download_progressbar.set(0)   #Initialize the progressbar with 0

    # Importing reset button image into code to use it as a button icon.
    img = Image.open("YouTube Video Downloader/Reset_Button_Icon.png")
    ctk_image = CTkImage(light_image=img,dark_image=img)

    # Reset Button to clear the URL entry if needed.
    video_url_reset_button = CTkButton(master=single_video_frame,corner_radius=2,image=ctk_image,text="",width=img.width,height=img.height,command=lambda: url_reset_button_click())
    video_url_reset_button.place(relx=0.936,rely=0.095)


    return single_video_frame   #Returns the frame on which widgets are placed. Not used in our code but kept for future additions.





'''**********************************PLAYLIST DOWNLOAD TAB*************************************'''

# Adding Frame to Playlist Download Tab.

def create_playlist_download_frame():
    '''Function to create the Frame on Playlist Download Tab'''

    playlist_frame = CTkFrame(master=playlist_tab,corner_radius=25,border_color='#ADB5BD',border_width=3)
    playlist_frame.place(relx=0,rely=0,relwidth=1,relheight=1) 

    def playlist_download(link,res,format,path,playlist_status_label,playlist_download_progressbar):
        '''Handles the playlist download logic'''   #Docstring

        print(link) #Debug Point.
        #Create a try block to handle potential errors.
        try:
            #Create an object of Playlist class to access Playlist Class methods.
            pt = Playlist(link) 

            #Fetch list of URLs of all videos in playlist.   
            urls_list = pt.video_urls
            total_videos = len(urls_list)   #Total videos in playlist

            videos_downloaded = 0
            failed_videos = []
            #Now we run a for loop such that we fetch the URLs one by one and download videos. 
            for i in urls_list:
                #Unpack the tuple to check for download success and message.
                success,message = video_download(link=i,savepath=path,format=format,res=res,progressbar=playlist_download_progressbar)
                
                if success:     #If download was successful
                    videos_downloaded += 1
                else:
                    failed_videos.append(i)

                progress = videos_downloaded/total_videos     #calculate the current progress.
                playlist_download_progressbar.set(progress)     #update progress bar.

                #Update the playlist status label.
                update_playlist_status(success,message,playlist_status_label)

            #Check if all videos were successfully downloaded.
            if videos_downloaded == 0:  #If no videos downloaded.
                return False,"No videos downloaded"
            elif videos_downloaded == total_videos:     #If all videos downloaded.
                return True,"All videos downloaded successfully"
            elif video_download < total_videos:     #If few videos not downloaded.
                return True,f"{video_download} of {total_videos} downloaded successfully"
            
        except RegexMatchError:
            return False,"Invalid URL provided"
        except KeyError:
            return False,"YouTube structure may have changed"
        except Exception as e:  #Catch any exceptions if raised in creating playlist object.
            return False,f"{e}" #Return False and exception raised.
        
        return

    def playlist_download_button_click(playlist_url_entry,playlist_quality_menu,playlist_format_menu,playlist_status_label,playlist_download_button,playlist_download_progressbar):
        '''Handles the download button click'''     #Docstring

        url = playlist_url_entry.get()  #Fetches the playlist url.

        url_prefix = "https://www.youtube.com/watch?v="    #Standard format for YouTube URL.

        if not ("youtube.com" in url or "youtu.be" in url):  #Check if URL follows YouTube format or not.
            messagebox.showerror('Error','Invalid URL provided')    #Raise Error if URL format invalid.
            playlist_url_entry.delete(0,'end')     #clear the video_url entry.
            return

        video_res = playlist_quality_menu.get() #Fetch the playlist download resolution from dropdown.
        video_format = playlist_format_menu.get()  #Fetches the playlist download format from dropdown.
        savepath = filedialog.askdirectory()    #Fetches the path where downloaded playlist needs to be saved.

        #Checks if all the parameters are fetched or not.
        if not url or not video_res or not video_format or not savepath:
            messagebox.showerror('Error','Please enter URL,resolution,format and savepath') #Raises error if any value missing.
            return

        playlist_status_label.configure(text="Downloading....") #set the status label to indicate download has started.
        playlist_download_button.configure(DISABLED)    #Disable the download button once started.

        playlist_download_progressbar.set(0)    #Initially set the progressbar to 0.

        def download_thread():
            '''Executes playlist download and status update on a different thread to avoid GUI freezing'''  #Docstring
            playlist_download(link=url,res=video_res,format=video_format,path=savepath,playlist_status_label=playlist_status_label,playlist_download_progressbar=playlist_download_progressbar)
            pass

        threading.Thread(target=download_thread).start() #Create a separate thread to execute the download thread function.
        playlist_download_button.configure(NORMAL)      #Re-enable the download button once process is completed/failed.
        return

    def update_playlist_status(success,message,playlist_status_label):
        if success: #If video/playlist download was successful
            #Truncate if message to long.
            if len(message) > 40:
                message = message[:40]+'....'
            
            playlist_status_label.configure(text=message,bg_color='#D1E7DD')  #Set backgrund color to green.
        else:   #If download was unsuccessful
            playlist_status_label.configure(text=message,bg_color='#F8D7DA')   #Set background color to red.
        pass

    # Function to clear URL entry field.
    def url_reset_button_click():
        playlist_url_entry.delete(0,'end')

    #Placing widgets on Playlist Download Tab.

    # Create a playlist url label.
    playlist_url_label = CTkLabel(master=playlist_frame,text='Playlist URL:',font=('Ariel',20,'bold'),text_color='#212529',corner_radius=10)  #Create a playlist url label.
    playlist_url_label.place(relx=0.1,rely=0.1)

    # Create a playlist url entry.
    playlist_url_entry = CTkEntry(master=playlist_frame,corner_radius=10,placeholder_text='Paste your playlist link here',width=292,font=('Ariel',20))
    playlist_url_entry.place(relx=0.365,rely=0.095)

    # Importing reset button image into code to use it as a button icon.
    img = Image.open("YouTube Video Downloader/Reset_Button_Icon.png")
    ctk_image = CTkImage(light_image=img,dark_image=img)

    #Reset Button to clear URL entry if needed.
    playlist_url_reset_button = CTkButton(master=playlist_frame,image=ctk_image,width=img.width,height=img.height,text="",corner_radius=2,command=lambda:url_reset_button_click())
    playlist_url_reset_button.place(relx=0.936,rely=0.1)

    # Playlist Video Quality Label.
    playlist_quality_label = CTkLabel(master=playlist_frame,text="Select Quality",font=('Ariel',20,'bold'),text_color='Black',corner_radius=10) #Creates a Label for video quality.
    playlist_quality_label.place(relx=0.1,rely=0.25)   #Adds Label to parent window.

    # Playlist Video Quality OptionMenu.
    resolutions = ["1080p", "720p", "480p", "360p","240p","144p"]  #Creates a list of availaible resolutions.
    playlist_quality_menu = CTkOptionMenu(master=playlist_frame,values=resolutions) #Creates a dropdown OptionMenu for resolution selection.
    playlist_quality_menu.place(relx=0.45,rely=0.25)   #Adds dropdown to parent window.

    # Playlist Video Format Label.
    playlist_format_label = CTkLabel(master=playlist_frame,text="Select Format",font=('Ariel',20,'bold'),text_color='#212529',corner_radius=10) #Creates a label for playlist video format.
    playlist_format_label.place(relx=0.1,rely=0.40)  #Adds Label to parent window.

    # Playlist Video Format OptionMenu.
    format_options = ['mp4', 'webm', 'mp3']    #Creates a list of available format options.
    playlist_format_menu = CTkOptionMenu(master=playlist_frame,values=format_options)  #Creates a dropdown OptionMenu for format selection.
    playlist_format_menu.place(relx=0.45,rely=0.40)    #Adds dropdown to parent window.


    # Main Download Button
    playlist_download_button = CTkButton(master=playlist_frame,corner_radius=20,text='Download',text_color='Black',\
                                    command=lambda: playlist_download_button_click(playlist_url_entry,playlist_quality_menu,playlist_format_menu,playlist_status_label,playlist_download_button,playlist_download_progressbar),\
                                    fg_color='#32B8CB',font=('Ariel',20,'bold'),\
                                    border_width=3,border_color='black')  #Creates a download button that will give the main command.
    playlist_download_button.place(relx=0.32,rely=0.58)     #Adds button to parent window.

    # Status Label to indicate current status.
    playlist_status_label = CTkLabel(master=playlist_frame,text="",font=('Ariel',20,'bold'))  #Creates a label for video status like Downloading... or Downloaded.
    playlist_status_label.configure(text="Please copy URL from address bar and\n not by selecting the share icon")
    playlist_status_label.place(relx=0.1,rely=0.72)  #Adds status label to parent window.

    # Progressbar to indicate download progress.
    playlist_download_progressbar = CTkProgressBar(master=playlist_frame,orientation="horizontal",mode="determinate",width=350) #Creates a progressbar that will indicate the download progress.
    playlist_download_progressbar.place(relx=0.1,rely=0.90)    #Adds progressbar to parent window.
    playlist_download_progressbar.set(0)   #Initialize the progressbar with 0


    return playlist_frame   #Returns the frame on which widgets are placed. Not used in our code but kept for future additions.




'''**********************************VIDEO INFO TAB*******************************************'''

# Adding Frame to Video Info Tab.

def create_video_info_frame():
    '''Function to create the Frame on Video Info Tab'''


    video_info_frame = CTkFrame(master=video_info_tab,corner_radius=25,border_color='#ADB5BD',border_width=3)
    video_info_frame.place(relx=0,rely=0,relwidth=1,relheight=1) 

    # Creating a scrollable frame to display info.
    video_info_iframe = CTkScrollableFrame(master=video_info_tab,corner_radius=15,border_color='#ADB5BD',border_width=3,orientation="vertical")
    video_info_iframe.place_forget()    #Hide the scrollable frame initially

    '''Code to fetch the YouTube video details'''
    def get_video_info(videoinfo_url_entry,description_cb,channelurl_cb,thumbnailurl_cb,author_cb,channelid_cb,keywords_cb,videoinfo_status_label,video_info_frame,video_info_iframe):

        url = videoinfo_url_entry.get()     #Gets the YouTube video URL from entry.
        url_prefix = "https://www.youtube.com/watch?v="    #Standard format for YouTube URL.

        if not ("youtube.com" in url or "youtu.be" in url):  #Check if URL follows YouTube format or not.
            messagebox.showerror('Error','Invalid URL provided')    #Raise Error if URL format invalid.
            videoinfo_url_entry.delete(0,'end')     #clear the videoinfo_url entry.
            return

        #Create a try block to handle potential errors.
        try:
            #Create an object of YouTube class to utilize the methods and functions of class.
            yt = YouTube(url)

            #Video Info parameters.
            title = yt.title
            description = yt.description
            rating = yt.rating
            length = yt.length
            views = yt.views
            likes = yt.likes
            channel_url = yt.channel_url
            publish_date = yt.publish_date
            thumbnail_url = yt.thumbnail_url
            author = yt.author
            keywords = yt.keywords
            channel_id = yt.channel_id

            #Hide the original frame and show scrollable frame.
            video_info_frame.place_forget()
            video_info_iframe.place(relx=0,rely=0,relwidth=1,relheight=1)

            # Clear previous info if any
            for widget in video_info_iframe.winfo_children():
                widget.destroy()

            def copy_text(text):  # Function to copy text
                pyperclip.copy(text)

            # Load copy icon image
            img = Image.open("YouTube Video Downloader/copy_icon.png")
            copy_image = CTkImage(light_image=img, dark_image=img, size=(20, 20))
                

            # Initialize a row variable to 0 to place the widgets accordingly.
            cur_row = 0

            #Placing the video title label.
            video_title_label = CTkLabel(master=video_info_iframe,font=('Ariel',18,'bold'),text='Title:')
            video_title_label.grid(row=cur_row,column=0,sticky='w',padx=7.5,pady=5)
            copy_title_button = CTkButton(master=video_info_iframe, image=copy_image, text="", width=20, height=20, command=lambda: copy_text(title))
            copy_title_button.grid(row=cur_row, column=1, padx=5) # Place button next to label
            video_title_value_label = CTkLabel(master=video_info_iframe,text=f"{title}",font=('Ariel',15),wraplength=250)
            video_title_value_label.grid(row=cur_row,column=2,sticky='w',padx=7.5,pady=5) # Value in column 2
            cur_row += 1  #Increment the current row so that we can place the next widget below.

            #Placing the total views label.
            video_views_label = CTkLabel(master=video_info_iframe,text="Views:",font=('Ariel',18,'bold'))
            video_views_label.grid(row=cur_row,column=0,sticky='w',padx=7.5,pady=5)
            copy_views_button = CTkButton(master=video_info_iframe, image=copy_image, text="", width=20, height=20, command=lambda: copy_text(str(views))) # Pass views as string
            copy_views_button.grid(row=cur_row, column=1, padx=5) # Place button next to label
            video_views_value_label = CTkLabel(master=video_info_iframe,text=f"{views}",font=('Ariel',15),wraplength=250)
            video_views_value_label.grid(row=cur_row,column=2,sticky='w',padx=7.5,pady=5) # Value in column 2
            cur_row += 1  #Increment the current row so that we can place the next widget below.

            #Placing the total likes label.
            video_likes_label = CTkLabel(master=video_info_iframe,text="Likes:",font=('Ariel',18,'bold'))
            video_likes_label.grid(row=cur_row,column=0,sticky='w',padx=7.5,pady=5)
            copy_likes_button = CTkButton(master=video_info_iframe, image=copy_image, text="", width=20, height=20, command=lambda: copy_text(str(likes))) # Pass likes as string
            copy_likes_button.grid(row=cur_row, column=1, padx=5) # Place button next to label
            video_likes_value_label = CTkLabel(master=video_info_iframe,text=f"{likes}",font=('Ariel',15),wraplength=250)
            video_likes_value_label.grid(row=cur_row,column=2,sticky='w',padx=7.5,pady=5) # Value in column 2
            cur_row += 1  #Increment the current row so that we can place the next widget below.

            #Placing the total length label.
            video_length_label = CTkLabel(master=video_info_iframe,text="Length:",font=('Ariel',18,'bold'))
            video_length_label.grid(row=cur_row,column=0,sticky='w',padx=7.5,pady=5)
            copy_length_button = CTkButton(master=video_info_iframe, image=copy_image, text="", width=20, height=20, command=lambda: copy_text(f"{length} secs"))
            copy_length_button.grid(row=cur_row, column=1, padx=5) # Place button next to label
            video_length_value_label = CTkLabel(master=video_info_iframe,text=f"{length} secs",font=('Ariel',15),wraplength=250)
            video_length_value_label.grid(row=cur_row,column=2,sticky='w',padx=7.5,pady=5) # Value in column 2
            cur_row += 1  #Increment the current row so that we can place the next widget below.

            #Placing the total rating label.
            video_rating_label = CTkLabel(master=video_info_iframe,text="Rating:",font=('Ariel',18,'bold'))
            video_rating_label.grid(row=cur_row,column=0,sticky='w',padx=7.5,pady=5)
            copy_rating_button = CTkButton(master=video_info_iframe, image=copy_image, text="", width=20, height=20, command=lambda: copy_text(str(rating))) # Pass rating as string
            copy_rating_button.grid(row=cur_row, column=1, padx=5) # Place button next to label
            video_rating_value_label = CTkLabel(master=video_info_iframe,text=f"{rating}",font=('Ariel',15),wraplength=250)
            video_rating_value_label.grid(row=cur_row,column=2,sticky='w',padx=7.5,pady=5) # Value in column 2
            cur_row += 1  #Increment the current row so that we can place the next widget below.

            #Placing the publish date label.
            video_publishdate_label = CTkLabel(master=video_info_iframe,text="Publish Date:",font=('Ariel',18,'bold'))
            video_publishdate_label.grid(row=cur_row,column=0,sticky='w',padx=7.5,pady=5)
            copy_publishdate_button = CTkButton(master=video_info_iframe, image=copy_image, text="", width=20, height=20, command=lambda: copy_text(str(publish_date))) # Pass publish date as string
            copy_publishdate_button.grid(row=cur_row, column=1, padx=5) # Place button next to label
            video_publishdate_value_label = CTkLabel(master=video_info_iframe,text=f"{publish_date}",font=('Ariel',15),wraplength=250)
            video_publishdate_value_label.grid(row=cur_row,column=2,sticky='w',padx=7.5,pady=5) # Value in column 2
            cur_row += 1  #Increment the current row so that we can place the next widget below.

            if description_cb.get():  #Check if user has selected description or not.
                #Placing the description label.
                video_desc_label = CTkLabel(master=video_info_iframe,text="Description:",font=('Ariel',18,'bold'))
                video_desc_label.grid(row=cur_row,column=0,sticky='w',padx=7.5,pady=5)
                copy_desc_button = CTkButton(master=video_info_iframe, image=copy_image, text="", width=20, height=20, command=lambda: copy_text(description))
                copy_desc_button.grid(row=cur_row, column=1, padx=5) # Place button next to label
                video_desc_value_label = CTkLabel(master=video_info_iframe,text=f"{description}",font=('Ariel',15),wraplength=250,anchor='nw')
                video_desc_value_label.grid(row=cur_row,column=2,sticky='w',padx=7.5,pady=5) # Value in column 2
                cur_row += 1  #Increment the current row so that we can place the next widget below.

            if channelurl_cb.get():  #Check if user has selected channel url or not.
                #Placing the channel url label.
                channelurl_label = CTkLabel(master=video_info_iframe,text="Channel URL:",font=('Ariel',18,'bold'))
                channelurl_label.grid(row=cur_row,column=0,sticky='w',padx=7.5,pady=5)
                copy_channelurl_button = CTkButton(master=video_info_iframe, image=copy_image, text="", width=20, height=20, command=lambda: copy_text(channel_url))
                copy_channelurl_button.grid(row=cur_row, column=1, padx=5) # Place button next to label
                channelurl_value_label = CTkLabel(master=video_info_iframe,text=f"{channel_url}",font=('Ariel',15),wraplength=250)
                channelurl_value_label.grid(row=cur_row,column=2,sticky='w',padx=7.5,pady=5) # Value in column 2
                cur_row += 1  #Increment the current row so that we can place the next widget below.

            if thumbnailurl_cb.get():  #Check if user has selected thumbnail url or not.
                #Placing the thumbnail url label.
                thumbnailurl_label = CTkLabel(master=video_info_iframe,text="Thumbnail URL:",font=('Ariel',18,'bold'))
                thumbnailurl_label.grid(row=cur_row,column=0,sticky='w',padx=7.5,pady=5)
                copy_thumbnailurl_button = CTkButton(master=video_info_iframe, image=copy_image, text="", width=20, height=20, command=lambda: copy_text(thumbnail_url))
                copy_thumbnailurl_button.grid(row=cur_row, column=1, padx=5) # Place button next to label
                thumbnailurl_value_label = CTkLabel(master=video_info_iframe,text=f"{thumbnail_url}",font=('Ariel',15),wraplength=250)
                thumbnailurl_value_label.grid(row=cur_row,column=2,sticky='w',padx=7.5,pady=5) # Value in column 2
                cur_row += 1  #Increment the current row so that we can place the next widget below.

            if author_cb.get():  #Check if user has selected author or not.
                #Placing the author label.
                author_label = CTkLabel(master=video_info_iframe,text="Author:",font=('Ariel',18,'bold'))
                author_label.grid(row=cur_row,column=0,sticky='w',padx=7.5,pady=5)
                copy_author_button = CTkButton(master=video_info_iframe, image=copy_image, text="", width=20, height=20, command=lambda: copy_text(author))
                copy_author_button.grid(row=cur_row, column=1, padx=5) # Place button next to label
                author_value_label = CTkLabel(master=video_info_iframe,text=f"{author}",font=('Ariel',15),wraplength=250)
                author_value_label.grid(row=cur_row,column=2,sticky='w',padx=7.5,pady=5) # Value in column 2
                cur_row += 1  #Increment the current row so that we can place the next widget below.
            
            if channelid_cb.get():  #Check if user has selected channel id or not.
                #Placing the channelid label.
                channelid_label = CTkLabel(master=video_info_iframe,text="Channel Id:",font=('Ariel',18,'bold'))
                channelid_label.grid(row=cur_row,column=0,sticky='w',padx=7.5,pady=5)
                copy_channelid_button = CTkButton(master=video_info_iframe, image=copy_image, text="", width=20, height=20, command=lambda: copy_text(channel_id))
                copy_channelid_button.grid(row=cur_row, column=1, padx=5) # Place button next to label
                channelid_value_label = CTkLabel(master=video_info_iframe,text=f"{channel_id}",font=('Ariel',15),wraplength=250)
                channelid_value_label.grid(row=cur_row,column=2,sticky='w',padx=7.5,pady=5) # Value in column 2
                cur_row += 1  #Increment the current row so that we can place the next widget below.
            
            if keywords_cb.get():  #Check if user has selected keywords or not.
                #Placing the keywords label.
                keywords_label = CTkLabel(master=video_info_iframe,text="Keywords:",font=('Ariel',18,'bold'))
                keywords_label.grid(row=cur_row,column=0,sticky='w',padx=7.5,pady=5)
                copy_keywords_button = CTkButton(master=video_info_iframe, image=copy_image, text="", width=20, height=20, command=lambda: copy_text(str(keywords))) # Pass keywords as string
                copy_keywords_button.grid(row=cur_row, column=1, padx=5) # Place button next to label
                keywords_value_label = CTkLabel(master=video_info_iframe,text=f"{keywords}",font=('Ariel',15),wraplength=250)
                keywords_value_label.grid(row=cur_row,column=2,sticky='w',padx=7.5,pady=5) # Value in column 2
                cur_row += 1  #Increment the current row so that we can place the next widget below.
            
            # Load back button image
            back_img = Image.open("YouTube Video Downloader/back_button_icon.png")
            copy_back_image = CTkImage(light_image=back_img,dark_image=back_img,size=(250,30))

            #Creating a back button on the tab to allow user to exit the frame.
            back_button = CTkButton(master=video_info_iframe,border_color='black',border_width=3,text="",image=copy_back_image,width=copy_back_image.width,height=copy_back_image.height,command=back_button_click)
            back_button.grid(row=cur_row,column=0,sticky='w',padx=7.5,pady=5)

            def back_button_click():
                video_info_iframe.destroy()     #Destroy the frame containing video info.
                return


            videoinfo_status_label.configure(text="Video info fetched", bg_color='#D1E7DD')

        except RegexMatchError:
            videoinfo_status_label.configure(text="Invalid URL provided",bg_color='#F8D7DA')
            return
        except AgeRestrictedError:
            videoinfo_status_label.configure(text="Age Restricted Video",bg_color='#F8D7DA')
            return
        except VideoUnavailable:
            videoinfo_status_label.configure(text="Video Unavailaible",bg_color='#F8D7DA')
            return
        except Exception as e:
            videoinfo_status_label.configure(text=f"{e}",bg_color='#F8D7DA')
            return

    # Function to clear URL entry field.
    def url_reset_button_click():
        videoinfo_url_entry.delete(0,'end')

    # Placing widgets on Video Info Tab.

    # Video URL Label
    videoinfo_url_label = CTkLabel(master=video_info_frame,text='Video URL:',text_color='Black',font=('Ariel',20,'bold'),corner_radius=10)    #Creates a label for video URL.
    videoinfo_url_label.place(relx=0.08,rely=0.2)    #Adds label to parent window.

    # Video URL Entry.
    videoinfo_url_entry = CTkEntry(master=video_info_frame,placeholder_text="Paste your video link here",font=('Ariel',20),width=300,corner_radius=10)    #Creates an entry for video URL.
    videoinfo_url_entry.place(relx=0.32,rely=0.19)  #Adds entry to parent window.

    # Importing reset button image into code to use it as a button icon.
    img = Image.open("YouTube Video Downloader/Reset_Button_Icon.png")
    ctk_image = CTkImage(light_image=img,dark_image=img)

    # Reset Button to clear the URL entry if needed.
    videoinfo_url_reset_button = CTkButton(master=video_info_frame,corner_radius=2,image=ctk_image,\
                                           text="",width=img.width,height=img.height,\
                                           command=lambda: url_reset_button_click())
    videoinfo_url_reset_button.place(relx=0.92,rely=0.195)

    # Get Info Button.
    videoinfo_button = CTkButton(master=video_info_frame,text="Get Info",font=('Ariel',20,'bold'),\
                                corner_radius=25,border_width=2,border_color='black',\
                                command=lambda: get_video_info(videoinfo_url_entry,description_cb,channelurl_cb,thumbnailurl_cb,author_cb,channelid_cb,keywords_cb,videoinfo_status_label,video_info_frame,video_info_iframe))
    videoinfo_button.place(relx=0.40,rely=0.38)

    #Description checkbox.
    description_cb = CTkCheckBox(master=video_info_frame,text="Description",corner_radius=20,font=('Ariel',20,'bold'))
    description_cb.place(relx=0.05,rely=0.55)

    #Channel URL checkbox.
    channelurl_cb = CTkCheckBox(master=video_info_frame,text="Channel URL",corner_radius=20,font=('Ariel',20,'bold'))
    channelurl_cb.place(relx=0.335,rely=0.55)

    #Thumbnail URL checkbox.
    thumbnailurl_cb = CTkCheckBox(master=video_info_frame,text="Thumbnail URL",corner_radius=20,font=('Ariel',20,'bold'))
    thumbnailurl_cb.place(relx=0.65,rely=0.55)

    #Author checkbox.
    author_cb = CTkCheckBox(master=video_info_frame,text="Author",corner_radius=20,font=('Ariel',20,'bold'))
    author_cb.place(relx=0.05,rely=0.7)

    #Channel ID checkbox.
    channelid_cb = CTkCheckBox(master=video_info_frame,text="Channel ID",corner_radius=20,font=('Ariel',20,'bold'))
    channelid_cb.place(relx=0.335,rely=0.7)

    #Keywords checkbox.
    keywords_cb = CTkCheckBox(master=video_info_frame,text="Keywords",corner_radius=20,font=('Ariel',20,'bold'))
    keywords_cb.place(relx=0.65,rely=0.7)

    # Status Label.
    message = "Please paste link from address bar\nnot from share icon."
    videoinfo_status_label = CTkLabel(master=video_info_frame,text=message,font=('Ariel',20,'bold'))
    videoinfo_status_label.place(relx=0.20,rely=0.825)


    return video_info_frame     #Returns the frame on which widgets are placed. Not used in our code but kept for future additions.




'''*********************************Playlist Info**********************************************'''

# Add Frame to Playlist Info Tab.

def create_playlist_info_frame():
    '''Function to create the Frame on Playlist Info Tab'''

    playlist_info_frame = CTkFrame(master=playlist_info_tab,corner_radius=25,border_color='#ADB5BD',border_width=3)  #Adds a frame to display info and widgets. 
    playlist_info_frame.place(relx=0,rely=0,relwidth=1,relheight=1) 

    #Create a scrollable frame to display info.
    playlist_info_scrollableframe = CTkScrollableFrame(master=playlist_info_tab,border_color='#ADB5BD',border_width=3,corner_radius=25,orientation='vertical')
    playlist_info_scrollableframe.place_forget()    #Hide the scrollable frame initially.


    '''Code to fetch the YouTube Playlist details'''
    def playlist_details(playlistinfo_url_entry,last_update_cb,views_cb,thumbnailurl_cb,total_videos_cb,owner_cb,description_cb,ownerurl_cb,ownerid_cb,playlistid_cb,playlist_info_frame,playlist_info_scrollableframe):

        '''Fetches the YouTube Playlist details'''  #Docstring.

        url = playlistinfo_url_entry.get()  #Fetches the playlist url.

        url_prefix = "https://www.youtube.com/watch?v="    #Standard format for YouTube URL.

        if not ("youtube.com" in url or "youtu.be" in url):  #Check if URL follows YouTube format or not.
            messagebox.showerror('Error','Invalid URL provided')    #Raise Error if URL format invalid.
            playlistinfo_url_entry.delete(0,'end')     #clear the video_url entry.
            return
        
        try:

            #Create a Playlist Object.
            pt = Playlist(url)

            #Fetch the values of all the parameters.
            title = pt.title
            last_updated = pt.last_updated
            thumbnail_url = pt.thumbnail_url
            description = pt.description
            length = pt.length
            views = pt.views
            owner = pt.owner
            owner_id = pt.owner_id
            owner_url = pt.owner_url
            playlist_id = pt.playlist_id

            #Forget the previous frame and replace it with new one.
            playlist_info_frame.place_forget()
            playlist_info_scrollableframe.place(relx=0,rely=0,relwidth=1,relheight=1)

            # Clear previous info if any
            for widget in playlist_info_frame.winfo_children():
                widget.destroy()

            # Function to copy text
            def copy_text(text):  
                pyperclip.copy(text)

            # Load copy icon image
            img = Image.open("YouTube Video Downloader/copy_icon.png")
            copy_image = CTkImage(light_image=img, dark_image=img, size=(20, 20))

            # Initialize a row variable to 0 to place the widgets accordingly.
            cur_row = 0
            

            #Placing the playlist title label.
            title_label = CTkLabel(master=playlist_info_scrollableframe,text='Title:',font=('Ariel',18,'bold'))
            title_label.grid(row=cur_row,column=0,padx=7.5,pady=5,sticky='w')
            title_copy_button = CTkButton(master=playlist_info_scrollableframe,text="",image=copy_image,width=20,height=20,command=lambda: copy_text(title))
            title_copy_button.grid(row=cur_row,column=1,padx=5,pady=5)
            title_value_label = CTkLabel(master=playlist_info_scrollableframe,text=f"{title}",font=('Ariel',15),wraplength=250)
            title_value_label.grid(row=cur_row,column=2,padx=7.5,pady=5,sticky='nw')    #Value in column 2
            cur_row += 1    #Increment the current row so that we can place the next widget below.

            if views_cb.get():
                #Placing the views title label.
                views_label = CTkLabel(master=playlist_info_scrollableframe,text='Views:',font=('Ariel',18,'bold'))
                views_label.grid(row=cur_row,column=0,padx=7.5,pady=5,sticky='w')
                views_copy_button = CTkButton(master=playlist_info_scrollableframe,text="",image=copy_image,width=20,height=20,command=lambda: copy_text(views))
                views_copy_button.grid(row=cur_row,column=1,padx=5,pady=5)
                views_value_label = CTkLabel(master=playlist_info_scrollableframe,text=f"{views}",font=('Ariel',15),wraplength=250)
                views_value_label.grid(row=cur_row,column=2,padx=7.5,pady=5,sticky='nw')    #Value in column 2
                cur_row += 1    #Increment the current row so that we can place the next widget below.

            if total_videos_cb.get():
                #Placing the total videos title label.
                total_vids_label = CTkLabel(master=playlist_info_scrollableframe,text='Total Videos:',font=('Ariel',18,'bold'))
                total_vids_label.grid(row=cur_row,column=0,padx=7.5,pady=5,sticky='w')
                total_vids_copy_button = CTkButton(master=playlist_info_scrollableframe,text="",image=copy_image,width=20,height=20,command=lambda:copy_text(length))
                total_vids_copy_button.grid(row=cur_row,column=1,padx=5,pady=5)
                total_vids_value_label = CTkLabel(master=playlist_info_scrollableframe,text=f"{length}",font=('Ariel',15),wraplength=250)
                total_vids_value_label.grid(row=cur_row,column=2,padx=7.5,pady=5,sticky='nw')    #Value in column 2
                cur_row += 1    #Increment the current row so that we can place the next widget below.

            if description_cb.get():
                #Placing the description title label.
                description_label = CTkLabel(master=playlist_info_scrollableframe,text='Description:',font=('Ariel',18,'bold'))
                description_label.grid(row=cur_row,column=0,padx=7.5,pady=5,sticky='w')
                description_copy_button = CTkButton(master=playlist_info_scrollableframe,text="",image=copy_image,width=20,height=20,command=lambda:copy_text(description))
                description_copy_button.grid(row=cur_row,column=1,padx=5,pady=5)
                description_value_label = CTkLabel(master=playlist_info_scrollableframe,text=f"{description}",font=('Ariel',15),wraplength=250)
                description_value_label.grid(row=cur_row,column=2,padx=7.5,pady=5,sticky='nw')    #Value in column 2
                cur_row += 1    #Increment the current row so that we can place the next widget below.

            if last_update_cb.get():
                #Placing the last update title label.
                last_updated_label = CTkLabel(master=playlist_info_scrollableframe,text='Last Updated:',font=('Ariel',18,'bold'))
                last_updated_label.grid(row=cur_row,column=0,padx=7.5,pady=5,sticky='w')
                last_updated_copy_button = CTkButton(master=playlist_info_scrollableframe,text="",image=copy_image,width=20,height=20,command=lambda:copy_text(last_updated))
                last_updated_copy_button.grid(row=cur_row,column=1,padx=5,pady=5)
                last_updated_value_label = CTkLabel(master=playlist_info_scrollableframe,text=f"{last_updated}",font=('Ariel',15),wraplength=250)
                last_updated_value_label.grid(row=cur_row,column=2,padx=7.5,pady=5,sticky='nw')    #Value in column 2
                cur_row += 1    #Increment the current row so that we can place the next widget below.

            if thumbnailurl_cb.get():
                #Placing the thumbnail url title label.
                thumbnail_url_label = CTkLabel(master=playlist_info_scrollableframe,text='Thumbnail URL:',font=('Ariel',18,'bold'))
                thumbnail_url_label.grid(row=cur_row,column=0,padx=7.5,pady=5,sticky='w')
                thumbnail_copy_button = CTkButton(master=playlist_info_scrollableframe,text="",image=copy_image,width=20,height=20,command=lambda:copy_text(thumbnail_url))
                thumbnail_copy_button.grid(row=cur_row,column=1,padx=5,pady=5)
                thumbnail_url_value_label = CTkLabel(master=playlist_info_scrollableframe,text=f"{thumbnail_url}",font=('Ariel',15),wraplength=250)
                thumbnail_url_value_label.grid(row=cur_row,column=2,padx=7.5,pady=5,sticky='nw')    #Value in column 2
                cur_row += 1    #Increment the current row so that we can place the next widget below.

            if owner_cb.get():
                #Placing the owner title label.
                owner_label = CTkLabel(master=playlist_info_scrollableframe,text='Owner:',font=('Ariel',18,'bold'))
                owner_label.grid(row=cur_row,column=0,padx=7.5,pady=5,sticky='w')
                owner_copy_button = CTkButton(master=playlist_info_scrollableframe,text="",image=copy_image,width=20,height=20,command=lambda:copy_text(owner))
                owner_copy_button.grid(row=cur_row,column=1,padx=5,pady=5)
                owner_value_label = CTkLabel(master=playlist_info_scrollableframe,text=f"{owner}",font=('Ariel',15),wraplength=250)
                owner_value_label.grid(row=cur_row,column=2,padx=7.5,pady=5,sticky='nw')    #Value in column 2
                cur_row += 1    #Increment the current row so that we can place the next widget below.

            if ownerid_cb.get():
                #Placing the ownerid title label.
                owner_id_label = CTkLabel(master=playlist_info_scrollableframe,text='Owner Id:',font=('Ariel',18,'bold'))
                owner_id_label.grid(row=cur_row,column=0,padx=7.5,pady=5,sticky='w')
                owner_id_copy_button = CTkButton(master=playlist_info_scrollableframe,text="",image=copy_image,width=20,height=20,command=lambda:copy_text(owner_id))
                owner_id_copy_button.grid(row=cur_row,column=1,padx=5,pady=5)
                owner_id_value_label = CTkLabel(master=playlist_info_scrollableframe,text=f"{owner_id}",font=('Ariel',15),wraplength=250)
                owner_id_value_label.grid(row=cur_row,column=2,padx=7.5,pady=5,sticky='nw')    #Value in column 2
                cur_row += 1    #Increment the current row so that we can place the next widget below.

            if ownerurl_cb.get():
                #Placing the ownerurl title label.
                ownerurl_label = CTkLabel(master=playlist_info_scrollableframe,text='Owner URL:',font=('Ariel',18,'bold'))
                ownerurl_label.grid(row=cur_row,column=0,padx=7.5,pady=5,sticky='w')
                ownerurl_copy_button = CTkButton(master=playlist_info_scrollableframe,text="",image=copy_image,width=20,height=20,command=lambda:copy_text(owner_url))
                ownerurl_copy_button.grid(row=cur_row,column=1,padx=5,pady=5)
                ownerurl_value_label = CTkLabel(master=playlist_info_scrollableframe,text=f"{owner_url}",font=('Ariel',15),wraplength=250)
                ownerurl_value_label.grid(row=cur_row,column=2,padx=7.5,pady=5,sticky='nw')    #Value in column 2
                cur_row += 1    #Increment the current row so that we can place the next widget below.

            if playlistid_cb.get():
                #Placing the playlist title label.
                playlist_id_label = CTkLabel(master=playlist_info_scrollableframe,text='Playlist Id:',font=('Ariel',18,'bold'))
                playlist_id_label.grid(row=cur_row,column=0,padx=7.5,pady=5,sticky='w')
                playlist_id_copy_button = CTkButton(master=playlist_info_scrollableframe,text="",image=copy_image,width=20,height=20,command=lambda:copy_text(playlist_id))
                playlist_id_copy_button.grid(row=cur_row,column=1,padx=5,pady=5)
                playlist_id_value_label = CTkLabel(master=playlist_info_scrollableframe,text=f"{playlist_id}",font=('Ariel',15),wraplength=250)
                playlist_id_value_label.grid(row=cur_row,column=2,padx=7.5,pady=5,sticky='nw')    #Value in column 2
                cur_row += 1    #Increment the current row so that we can place the next widget below.
            return
        except RegexMatchError:
            messagebox.showerror('Error','Invalid URL provided')
        except KeyError:
            messagebox.showerror('Error','YouTube Structure may have changed')
        except Exception as e:      #Catch any exceptions if raised in creating Playlist object.
            messagebox.showerror('Error',f"{e}")

        return

    # Function to clear URL entry field.
    def url_reset_button_click():
        playlistinfo_url_entry.delete(0,'end')

    #Placing widgets on Playlist Info Frame.

    #Placing playlist URL label.
    playlistinfo_url_label = CTkLabel(master=playlist_info_frame,text="Playlist URL:",font=('Ariel',20,'bold'),text_color='#212529')
    playlistinfo_url_label.place(relx=0.1,rely=0.12)

    #Placing entry to fetch playlist URL.
    playlistinfo_url_entry = CTkEntry(master=playlist_info_frame,placeholder_text='Paste your playlist link here',width=280,font=('Ariel',20),corner_radius=10)
    playlistinfo_url_entry.place(relx=0.35,rely=0.12)

    #Importing reset button image.
    img = Image.open("YouTube Video Downloader/Reset_Button_Icon.png")
    ctk_image = CTkImage(light_image=img,dark_image=img)

    # Reset Button to clear the URL entry if needed.
    video_url_reset_button = CTkButton(master=playlist_info_frame,corner_radius=2,image=ctk_image,text="",width=img.width,height=img.height,command=lambda: url_reset_button_click())
    video_url_reset_button.place(relx=0.91,rely=0.12)

    # Placing get info button.
    get_info_button = CTkButton(master=playlist_info_frame,corner_radius=15,\
                                text="Get Info",border_width=3,font=('Ariel',20,'bold'),\
                                command=lambda: playlist_details(playlistinfo_url_entry, last_update_cb, views_cb, thumbnailurl_cb, total_videos_cb, owner_cb, description_cb, ownerurl_cb, ownerid_cb, playlistid_cb, playlist_info_frame, playlist_info_scrollableframe))
    get_info_button.place(relx=0.4,rely=0.275)

    #Placing checkboxes to take user choice.

    #Last Updated Checkbox
    last_update_cb = CTkCheckBox(master=playlist_info_frame,corner_radius=15,text="Last Updated",font=('Ariel',18,'bold'))
    last_update_cb.place(relx=0.1,rely=0.45)

    #Views Checkbox
    views_cb = CTkCheckBox(master=playlist_info_frame,text="Views",font=('Ariel',18,'bold'),corner_radius=15)
    views_cb.place(relx=0.42,rely=0.45)

    #Thumbnail URL Checkbox
    thumbnailurl_cb = CTkCheckBox(master=playlist_info_frame,text="Thumbnail URL",font=('Ariel',20,'bold'),corner_radius=15)
    thumbnailurl_cb.place(relx=0.63,rely=0.45)

    #No of videos checkbox
    total_videos_cb = CTkCheckBox(master=playlist_info_frame,text="Total Videos",font=('Ariel',20,'bold'),corner_radius=15)
    total_videos_cb.place(relx=0.1,rely=0.55)

    #Owner checkbox.
    owner_cb = CTkCheckBox(master=playlist_info_frame,text="Owner",font=('Ariel',20,'bold'),corner_radius=15)
    owner_cb.place(relx=0.42,rely=0.55)

    #Description checkbox
    description_cb = CTkCheckBox(master=playlist_info_frame,text="Description",font=('Ariel',20,'bold'),corner_radius=15)
    description_cb.place(relx=0.63,rely=0.55)

    #owner_url checkbox
    ownerurl_cb = CTkCheckBox(master=playlist_info_frame,text="Owner URL",font=('Ariel',20,'bold'),corner_radius=15)
    ownerurl_cb.place(relx=0.1,rely=0.65)

    # owner_id checkbox
    ownerid_cb = CTkCheckBox(master=playlist_info_frame,text="Owner Id",font=('Ariel',20,'bold'),corner_radius=15)
    ownerid_cb.place(relx=0.42,rely=0.65)

    #Playlist ID checkbox.
    playlistid_cb = CTkCheckBox(master=playlist_info_frame,text="Playlist ID",font=('Ariel',20,'bold'),corner_radius=15)
    playlistid_cb.place(relx=0.68,rely=0.65)

    # Label to display important playlist link info.
    message = "Please paste link from address bar\n not from share icon."
    msg_label = CTkLabel(master=playlist_info_frame,text=message,font=('Ariel',20,'bold'))
    msg_label.place(relx=0.20,rely=0.8)


    return playlist_info_frame  #Returns the frame on which widgets are placed. Not used in our code but kept for future additions.





'''*********************************Channel Info**********************************************'''

# Adds Frame to Channel Info Tab.
def create_channel_info_frame():
    '''Function to create the Frame on Channel Info Tab'''

    channel_info_frame = CTkFrame(master=channel_info_tab,corner_radius=25,border_color='#ADB5BD',border_width=3)  #Adds a frame to display info and widgets. 
    channel_info_frame.place(relx=0,rely=0,relwidth=1,relheight=1) 

    #Create a scrollable frame to display info.
    channel_info_scrollableframe = CTkScrollableFrame(master=channel_info_tab,border_color='#ADB5BD',border_width=3,corner_radius=25,orientation='vertical')
    channel_info_scrollableframe.place_forget()    #Hide the scrollable frame initially.


    '''Code to fetch the YouTube channel details'''
    def channel_details(channelinfo_url_entry,last_update_cb,views_cb,thumbnailurl_cb,total_videos_cb,owner_cb,description_cb,channel_info_frame,channel_info_scrollableframe):

        '''Fetches the YouTube channel details'''  #Docstring.

        url = channelinfo_url_entry.get()  #Fetches the channel url.

        try:

            #Create a channel Object.
            ct = Channel(url)

            #Fetch the values of all the parameters.
            name = ct.channel_name
            channel_id = ct.channel_id
            last_updated = ct.last_updated
            thumbnail_url = ct.thumbnail_url
            description = ct.description
            length = ct.length
            views = ct.views

            #Forget the previous frame and replace it with new one.
            channel_info_frame.place_forget()
            channel_info_scrollableframe.place(relx=0,rely=0,relwidth=1,relheight=1)

            # Clear previous info if any
            for widget in channel_info_frame.winfo_children():
                widget.destroy()

            # Function to copy text
            def copy_text(text):  
                pyperclip.copy(text)

            # Load copy icon image
            img = Image.open("YouTube Video Downloader/copy_icon.png")
            copy_image = CTkImage(light_image=img, dark_image=img, size=(20, 20))

            # Initialize a row variable to 0 to place the widgets accordingly.
            cur_row = 0
            

            #Placing the channel title label.
            name_label = CTkLabel(master=channel_info_scrollableframe,text='Title:',font=('Ariel',18,'bold'))
            name_label.grid(row=cur_row,column=0,padx=7.5,pady=5,sticky='w')
            name_copy_button = CTkButton(master=channel_info_scrollableframe,text="",image=copy_image,width=20,height=20,command=lambda: copy_text(name))
            name_copy_button.grid(row=cur_row,column=1,padx=5,pady=5)
            name_value_label = CTkLabel(master=channel_info_scrollableframe,text=f"{name}",font=('Ariel',15),wraplength=250)
            name_value_label.grid(row=cur_row,column=2,padx=7.5,pady=5,sticky='nw')    #Value in column 2
            cur_row += 1    #Increment the current row so that we can place the next widget below.

            if views_cb.get():
                #Placing the views title label.
                views_label = CTkLabel(master=channel_info_scrollableframe,text='Views:',font=('Ariel',18,'bold'))
                views_label.grid(row=cur_row,column=0,padx=7.5,pady=5,sticky='w')
                views_copy_button = CTkButton(master=channel_info_scrollableframe,text="",image=copy_image,width=20,height=20,command=lambda: copy_text(views))
                views_copy_button.grid(row=cur_row,column=1,padx=5,pady=5)
                views_value_label = CTkLabel(master=channel_info_scrollableframe,text=f"{views}",font=('Ariel',15),wraplength=250)
                views_value_label.grid(row=cur_row,column=2,padx=7.5,pady=5,sticky='nw')    #Value in column 2
                cur_row += 1    #Increment the current row so that we can place the next widget below.

            if total_videos_cb.get():
                #Placing the total videos title label.
                total_vids_label = CTkLabel(master=channel_info_scrollableframe,text='Total Videos:',font=('Ariel',18,'bold'))
                total_vids_label.grid(row=cur_row,column=0,padx=7.5,pady=5,sticky='w')
                total_vids_copy_button = CTkButton(master=channel_info_scrollableframe,text="",image=copy_image,width=20,height=20,command=lambda:copy_text(length))
                total_vids_copy_button.grid(row=cur_row,column=1,padx=5,pady=5)
                total_vids_value_label = CTkLabel(master=channel_info_scrollableframe,text=f"{length}",font=('Ariel',15),wraplength=250)
                total_vids_value_label.grid(row=cur_row,column=2,padx=7.5,pady=5,sticky='nw')    #Value in column 2
                cur_row += 1    #Increment the current row so that we can place the next widget below.

            if description_cb.get():
                #Placing the description title label.
                description_label = CTkLabel(master=channel_info_scrollableframe,text='Description:',font=('Ariel',18,'bold'))
                description_label.grid(row=cur_row,column=0,padx=7.5,pady=5,sticky='w')
                description_copy_button = CTkButton(master=channel_info_scrollableframe,text="",image=copy_image,width=20,height=20,command=lambda:copy_text(description))
                description_copy_button.grid(row=cur_row,column=1,padx=5,pady=5)
                description_value_label = CTkLabel(master=channel_info_scrollableframe,text=f"{description}",font=('Ariel',15),wraplength=250)
                description_value_label.grid(row=cur_row,column=2,padx=7.5,pady=5,sticky='nw')    #Value in column 2
                cur_row += 1    #Increment the current row so that we can place the next widget below.

            if last_update_cb.get():
                #Placing the last update title label.
                last_updated_label = CTkLabel(master=channel_info_scrollableframe,text='Last Updated:',font=('Ariel',18,'bold'))
                last_updated_label.grid(row=cur_row,column=0,padx=7.5,pady=5,sticky='w')
                last_updated_copy_button = CTkButton(master=channel_info_scrollableframe,text="",image=copy_image,width=20,height=20,command=lambda:copy_text(last_updated))
                last_updated_copy_button.grid(row=cur_row,column=1,padx=5,pady=5)
                last_updated_value_label = CTkLabel(master=channel_info_scrollableframe,text=f"{last_updated}",font=('Ariel',15),wraplength=250)
                last_updated_value_label.grid(row=cur_row,column=2,padx=7.5,pady=5,sticky='nw')    #Value in column 2
                cur_row += 1    #Increment the current row so that we can place the next widget below.

            if thumbnailurl_cb.get():
                #Placing the thumbnail url title label.
                thumbnail_url_label = CTkLabel(master=channel_info_scrollableframe,text='Thumbnail URL:',font=('Ariel',18,'bold'))
                thumbnail_url_label.grid(row=cur_row,column=0,padx=7.5,pady=5,sticky='w')
                thumbnail_url_copy_button = CTkButton(master=channel_info_scrollableframe,text="",image=copy_image,width=20,height=20,command=lambda:copy_text(thumbnail_url))
                thumbnail_url_copy_button.grid(row=cur_row,column=1,padx=5,pady=5)
                thumbnail_url_value_label = CTkLabel(master=channel_info_scrollableframe,text=f"{thumbnail_url}",font=('Ariel',15),wraplength=250)
                thumbnail_url_value_label.grid(row=cur_row,column=2,padx=7.5,pady=5,sticky='nw')    #Value in column 2
                cur_row += 1    #Increment the current row so that we can place the next widget below.

            if owner_cb.get():
                #Placing the owner title label.
                owner_label = CTkLabel(master=channel_info_scrollableframe,text='Owner:',font=('Ariel',18,'bold'))
                owner_label.grid(row=cur_row,column=0,padx=7.5,pady=5,sticky='w')
                owner_copy_button = CTkButton(master=channel_info_scrollableframe,text="",image=copy_image,width=20,height=20,command=lambda:copy_text(channel_id))
                owner_copy_button.grid(row=cur_row,column=1,padx=5,pady=5)
                owner_value_label = CTkLabel(master=channel_info_scrollableframe,text=f"{channel_id}",font=('Ariel',15),wraplength=250)
                owner_value_label.grid(row=cur_row,column=2,padx=7.5,pady=5,sticky='nw')    #Value in column 2
                cur_row += 1    #Increment the current row so that we can place the next widget below.

            return
        except RegexMatchError:
            messagebox.showerror('Error','Invalid URL provided')
        except KeyError:
            messagebox.showerror('Error','YouTube Structure may have changed')
        except Exception as e:      #Catch any exceptions if raised in creating channel object.
            messagebox.showerror('Error',f"{e}")

        return

    # Function to clear URL entry field.
    def url_reset_button_click():
        channelinfo_url_entry.delete(0,'end')

    #Placing widgets on channel Info Frame.

    #Placing channel URL label.
    channelinfo_url_label = CTkLabel(master=channel_info_frame,text="Channel URL:",font=('Ariel',20,'bold'),text_color='#212529')
    channelinfo_url_label.place(relx=0.08,rely=0.12)

    #Placing entry to fetch channel URL.
    channelinfo_url_entry = CTkEntry(master=channel_info_frame,placeholder_text='Paste your Channel link here',width=280,font=('Ariel',20),corner_radius=10)
    channelinfo_url_entry.place(relx=0.35,rely=0.12)

    #Importing reset button image.
    img = Image.open("YouTube Video Downloader/Reset_Button_Icon.png")
    ctk_image = CTkImage(light_image=img,dark_image=img)

    # Reset Button to clear the URL entry if needed.
    video_url_reset_button = CTkButton(master=channel_info_frame,corner_radius=2,image=ctk_image,text="",width=img.width,height=img.height,command=lambda: url_reset_button_click())
    video_url_reset_button.place(relx=0.91,rely=0.12)

    # Placing get info button.
    get_info_button = CTkButton(master=channel_info_frame,corner_radius=15,text="Get Info",border_width=3,font=('Ariel',20,'bold'),command=lambda :channel_details(channelinfo_url_entry,last_update_cb,views_cb,thumbnailurl_cb,total_videos_cb,owner_cb,description_cb,channel_info_frame,channel_info_scrollableframe))
    get_info_button.place(relx=0.4,rely=0.30)

    #Placing checkboxes to take user choice.

    #Last Updated Checkbox
    last_update_cb = CTkCheckBox(master=channel_info_frame,corner_radius=15,text="Last Updated",font=('Ariel',18,'bold'))
    last_update_cb.place(relx=0.1,rely=0.55)

    #Views Checkbox
    views_cb = CTkCheckBox(master=channel_info_frame,text="Views",font=('Ariel',18,'bold'),corner_radius=15)
    views_cb.place(relx=0.42,rely=0.55)

    #Thumbnail URL Checkbox
    thumbnailurl_cb = CTkCheckBox(master=channel_info_frame,text="Thumbnail URL",font=('Ariel',20,'bold'),corner_radius=15)
    thumbnailurl_cb.place(relx=0.63,rely=0.55)

    #No of videos checkbox
    total_videos_cb = CTkCheckBox(master=channel_info_frame,text="Total Videos",font=('Ariel',20,'bold'),corner_radius=15)
    total_videos_cb.place(relx=0.1,rely=0.65)

    #Owner checkbox.
    owner_cb = CTkCheckBox(master=channel_info_frame,text="Owner",font=('Ariel',20,'bold'),corner_radius=15)
    owner_cb.place(relx=0.42,rely=0.65)

    #Description checkbox
    description_cb = CTkCheckBox(master=channel_info_frame,text="Description",font=('Ariel',20,'bold'),corner_radius=15)
    description_cb.place(relx=0.63,rely=0.65)

    # Label to display important playlist link info.
    message = "Please paste link from address bar after double \nclicking not from share icon."
    msg_label = CTkLabel(master=channel_info_frame,text=message,font=('Ariel',20,'bold'))
    msg_label.place(relx=0.08,rely=0.8)


    return channel_info_frame #Returns the frame on which widgets are placed. Not used in our code but kept for future additions.




'''********************************TAB Creation***********************************************'''

# Now we will create a Tabview that ensures each functionality will take
# place on a different tab.
tabview = CTkTabview(master=win,corner_radius=25,border_width=3,border_color='#ADB5BD',fg_color='#FFFFFF',segmented_button_unselected_hover_color=None)
tabview.pack(padx=5,pady=5,expand=True,fill='both')

# Adding Tabs to the Tabview.
single_video_tab = tabview.add('Video Download')    #Creates tab for single YouTube video downloading.
playlist_tab = tabview.add('Playlist')      #Creates tab for YouTube Playlist downloading.
video_info_tab = tabview.add('Video Info')  #Creates tab for YouTube Video Info.
playlist_info_tab = tabview.add('Playlist Info')    #Creates tab for YouTube Playlist Info.
channel_info_tab = tabview.add('Channel Info')    #Creates tab for YouTube Channel Info.

# Create the tab frames and store them in the dictionary
tab_frames = {
    "Video Download": create_video_download_frame(),
    "Playlist": create_playlist_download_frame(),
    "Video Info": create_video_info_frame(),
    "Playlist Info": create_playlist_info_frame(),
    "Channel Info": create_channel_info_frame(),
}

current_tab = "Video Download"  #Initialize the current tab to the first one.
tabview.configure(command=tab_switch_logic)

win.mainloop()