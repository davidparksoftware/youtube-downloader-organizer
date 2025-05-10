"""
    YouTube Downloader Organizer

    This script downloads and organizes YouTube videos and audio files into category and uploader folders

    Possible Future Functionality:
        - Playlist support
        - Download subtitles
        - Download thumbnail and metadata
        - Batch mode (list of urls)
    Possible UX Improvements:
        - Basic GUI
        - Progress Bar (CLI or GUI or Both)
"""


from pathlib import Path
import yt_dlp
import re

# Set the base directory for all downloads to be stored
download_dir = Path.home() / "Youtube_Downloads"
categories = {
    "1": "music", 
    "2": "podcast", 
    "3": "tutorial", 
    "4": "stories", 
    "5": "other"
}
format_choices = {
    "1": "mp3",
    "2": "mp4"
}

# Set the different download configurations
mp3_format_options = {
    # Get the best audio stream
    'format': 'bestaudio/best',
    # Get the output directory
    'outtmpl': None,    # This will be set dynamically
    # Convert to MP3 using FFmpeg
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    # Show the download progress
    'quiet': False
}
mp4_format_options = {
    # Get the best video and audio separate or if not then together
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
    # Get the output directory
    'outtmpl': None,    # This will be set dynamically
    # Show the download progress
    'quiet': False
}


def clean_filename(name):
    """
        This function cleans up the filename by removing any forbidden characters
    """
    return re.sub(r'[\\/*?:"<>|]', '-', name).strip()


def get_video_info(url):
    """
        This function attempts to get information on the video
    """
    try:
        url = url.split('&')[0] # strip all query parameters
        ydl_info_options = {
            # Dont show any progress
            "quiet": True, 
            # Dont download the file
            "skip_download": True
        }
        with yt_dlp.YoutubeDL(ydl_info_options) as ydl:
            return ydl.extract_info(url, download=False)
    except Exception:
        print("Failed to retrieve video info. Please check the URL.")
        return None


def download_youtube_video(url, format_choice, category):
    """
        This function downloads the actual youtube video if everything checks out
    """
    info = get_video_info(url)
    if not info:
        return # Exit this function if video info cant be retrieved
    
    # Get the info about the uploader and title
    uploader = clean_filename(info.get('uploader', 'UnknownUploader'))
    title    = clean_filename(info.get('title', 'UnknownTitle'))

    # Create/initialize the output directory
    target_dir = download_dir / category.capitalize() / uploader
    target_dir.mkdir(parents=True, exist_ok=True)
    output_template = str(target_dir / f"{title}.%(ext)s")

    # Check to see if file already exists or not in all categories
    filename_to_check = f"{title}.{format_choice}"
    for other_cat in categories.values():
        other_path = download_dir / other_cat.capitalize() / uploader / filename_to_check
        if other_path.exists():
            print(f"This file exists under {other_path}.")
            download_anyway = input(f"Do you still want to download it to {other_cat.capitalize()}? (Y/N): ").strip().lower()
            if download_anyway != "y":
                print("This file will not be downloaded")
                return
    
    # Copy the format options so that the global dict isn't changed
    if format_choice == "mp3":
        ydl_format_options = mp3_format_options.copy()
    elif format_choice == "mp4":
        ydl_format_options = mp4_format_options.copy()
    ydl_format_options['outtmpl'] = output_template
    
    # Double check to see if the user wants to download the given video
    print(f"Video Uploader: {uploader}")
    print(f"Video Title: {title}")
    download = input(f"Are you sure you want to download this file under: {target_dir} (Y/N): ").strip().lower()
    if download != "y":
        print("This file will not be downloaded")
        return
    else:
        with yt_dlp.YoutubeDL(ydl_format_options) as ydl:
            print(f"Downloading to {target_dir}...")
            ydl.download([url])
            print("Download complete")
        

def input_checking(type, input, choices):
    """
        This function checks that the user inputs are valid and normalizes the choice
    """
    if input in choices:
        final_choice = choices[input]
    elif input in choices.values():
        final_choice = input
    else:
        raise ValueError(f"Invalid {type}. Enter one of: {list(choices.values())} or {list(choices.keys())}")
    
    return final_choice


def main():
    """
        This function prompts the user for URL, format, and category and if they want to download another video
    """
    while True:
        url = input("\nEnter the URL for the YouTube video: ").strip()
        
        if "youtube.com" not in url and "youtu.be" not in url:
            print("Error: This script is only meant for youtube links.")
            continue
        
        # Print the format choices
        print("\nSelect a format:")
        for key, value in format_choices.items():
            print(f"    {key}: {value.upper()}")
        format_input = input("Enter the number or name of the format: ").strip().lower()

        # Normalize the input
        format_choice = input_checking(type="format", input=format_input, choices=format_choices)

        # Print the category choices
        print("\nSelect a category:")
        for key, value in categories.items():
            print(f"    {key}: {value.capitalize()}")
        category_input = input("Enter the number or name of the category: ").strip().lower()

        # Normalize the input
        category = input_checking(type="category", input=category_input, choices=categories)

        # Call the download youtube_video function
        try:
            download_youtube_video(url, format_choice, category)
        except Exception as e:
            print(f"Error: {e}")
        
        # Ask if user wants to download another video/audio file
        again = input("\nDownload another video? (Y/N): ").strip().lower()
        if again != "y":
            print("Goodbye")
            break


if __name__ == "__main__":
    main()
        