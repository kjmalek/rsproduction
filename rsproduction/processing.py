import os
import platform
import subprocess


def fileConversions(sub_dir):
    """This function completes basic file format conversions to ensure media files will stream in Scalar."""
    # Check and adapt commands to work on Windows, Mac, and Linux operating systems.
    system = platform.system()
    if system == "Windows":
        magick = "magick"
    else:
        magick = ""
    print("Running conversions. This may take a while...")
    with os.scandir(sub_dir) as it:
        # Run an initial loop through the files to find any images in a RAW format and convert to TIFF using dcraw
        print("Checking for and converting RAW images.")
        for file in it:
            filename = os.path.splitext(file.name)[0]
            ext = os.path.splitext(file.name)[1]
            # dcraw supports nearly any RAW image format. The following list of extensions covers only the ones that I
            # am immediately aware of.
            if file.name.endswith(('.NEF', '.CR2', '.CRW', '.ARW', '.ORF', '.DNG')):
                # The following line passes a dcraw command to convert the identified file to TIFF. Because the TIFF
                # file is temporary and only used in the process of converting the file to JPEG, the suffix '_temp' is
                # added.
                subprocess.call(f"dcraw -o 1 -T -O {sub_dir}/{filename}_temp.tiff {sub_dir}/{file.name}")
                # Add the suffix '_M' to the original submission file
                os.rename(f"{sub_dir}/{file.name}", f"{sub_dir}/{filename}_M{ext}")
    with os.scandir(sub_dir) as it:
        # Run a second loop through the files to find and convert TIFF files to JPEG and any audio or video files to MP3
        # and MP4.
        for file in it:
            filename = os.path.splitext(file.name)[0]
            ext = os.path.splitext(file.name)[1]
            untemp = filename.split("_temp")[0]
            optmsg = f"Converting {untemp}..."
            if file.name.endswith('.tiff'):
                print(optmsg)
                # The following line passes an ImageMagick command to convert any TIFF files to JPEG files with a width
                # of 1040px and an approximate file size of 200kb.
                subprocess.call(f'{magick} convert {sub_dir}/{file.name} -resize "1040>" -quality 100 '
                                f'-define jpeg:extent=200KB -unsharp 0x0.75+0.75+0.008 '
                                f'-interlace Line {sub_dir}/{untemp}.jpg', shell=True)
                if file.name.endswith('_temp.tiff'):
                    os.remove(f'{sub_dir}/{file.name}')
                else:
                    os.rename(f'{sub_dir}/{file.name}', f'{sub_dir}/{filename}_M{ext}')
            # Pass a FFmpeg command to convert audio files to MP3 files with a sample rate of 44.1kHz and a bitrate of
            # 192kb/s.
            if file.name.endswith(('.wav', '.aiff', '.m4a', '.flac', '.wma', '.aac', '.bwf')):
                print(optmsg)
                subprocess.call(f"ffmpeg -loglevel quiet -i {sub_dir}/{file.name} -ar 44100 "
                                f"-b:a 192k {sub_dir}/{filename}.mp3", shell=True)
                os.rename(f"{sub_dir}/{file.name}", f"{sub_dir}/{filename}_M{ext}")
            # Pass a FFmpeg command to convert video files to MP4 files.
            if file.name.endswith(('.avi', '.mov')):
                print(optmsg)
                subprocess.call(f"ffmpeg -loglevel quiet -i {sub_dir}/{file.name} {sub_dir}/{filename}.mp4",
                                shell=True)
                os.rename(f"{sub_dir}/{file.name}", f"{sub_dir}/{filename}_M{ext}")
    print("File conversions complete!")


def fileOptimizations(sub_dir):
    """This function completes extensive optimizations to files."""
    # Check and adapt commands to work on Windows, Mac, and Linux operating systems.
    system = platform.system()
    if system == "Windows":
        magick = "magick"
    else:
        magick = ""
    print("Running optimizations. This may take a while...")
    with os.scandir(sub_dir) as it:
        # Run an initial loop through the files to find any images in a RAW format and convert to TIFF using dcraw
        print("Checking for and converting RAW images.")
        for file in it:
            filename = os.path.splitext(file.name)[0]
            ext = os.path.splitext(file.name)[1]
            # dcraw supports nearly any RAW image format. The following list of extensions covers only the ones that I
            # am immediately aware of.
            if file.name.endswith(('.NEF', '.CR2', '.CRW', '.ARW', '.ORF', '.DNG')):
                # The following line passes a dcraw command to convert the identified file to TIFF. Because the TIFF
                # file is temporary and only used in the process of converting the file to JPEG, the suffix '_temp' is
                # added.
                subprocess.call(f"dcraw -o 1 -T -O {sub_dir}/{filename}_temp.tiff {sub_dir}/{file.name}")
                # Add the suffix '_M' to the original submission file
                os.rename(f"{sub_dir}/{file.name}", f"{sub_dir}/{filename}_M{ext}")
    with os.scandir(sub_dir) as it:
        # Run a second loop through the files to find and convert TIFF files to JPEG and any audio or video files to MP3
        # and MP4.
        for file in it:
            filename = os.path.splitext(file.name)[0]
            ext = os.path.splitext(file.name)[1]
            untemp = filename.split("_temp")[0]
            optmsg = f"Optimizing {untemp}..."
            # Optimize JPEGs & TIFFs with sharpening
            if file.name.endswith(('.tiff', '.jpg')):
                print(optmsg)
                subprocess.call(
                    f'{magick} convert {sub_dir}/{file.name} -resize "1040>" -quality 100 -define jpeg:extent=200KB '
                    f'-unsharp 0x0.75+0.75+0.008 -interlace Line {sub_dir}/{untemp}_W.jpg',
                    shell=True)
                subprocess.call(
                    f'{magick} convert {sub_dir}/{file.name} -resize "206>" -quality 100 -define jpeg:extent=50KB '
                    f'-unsharp 0x0.75+0.75+0.008 {sub_dir}/{untemp}_TH.jpg',
                    shell=True)
                if file.name.endswith('_temp.tiff'):
                    os.remove(f'{sub_dir}/{file.name}')
            # Optimize PNGs without sharpening
            if file.name.endswith('.png'):
                print(optmsg)
                subprocess.call(
                    f"{magick} convert {sub_dir}/{file.name} +clone -resize 900x1012^> -quality 86 "
                    f"-set filename:w %t_W.jpg -write {sub_dir}/%[filename:w] +delete -thumbnail 206^> -quality 86 "
                    f"-set filename:t %t_TH.jpg {sub_dir}/%[filename:t]",
                    shell=True)
            # Convert and optimize and audio files that are not in MP3 format
            if file.name.endswith(('.wav', '.aiff', '.m4a', '.flac', '.wma', '.aac', '.bwf')):
                print(optmsg)
                subprocess.call(
                    f"ffmpeg -loglevel quiet -i {sub_dir}/{file.name} -ar 44100 -b:a 192k {sub_dir}/{filename}_W.mp3",
                    shell=True)
            # Convert, without optimizing, any video files that are not in MP4 format
            # TO DO create thumbnails for videos
            if file.name.endswith(('.avi', '.mov', '.mp4')):
                subprocess.call(f"ffmpeg -i {sub_dir}/{file.name} -ss 00:00:01.000 -frames:v 1 "
                                f"{sub_dir}/{filename}_TH.jpg", shell=True)
            if file.name.endswith(('.avi', '.mov')):
                print(f"Converting {filename} to MP4...")
                subprocess.call(f"ffmpeg -loglevel quiet -i {sub_dir}/{file.name} {sub_dir}/{filename}_W.mp4",
                                shell=True)
            # Append "_M" to master files
            if not file.name.endswith(('_temp.tiff', '.py')):
                os.rename(f"{sub_dir}/{file.name}", f"{sub_dir}/{filename}_M{ext}")
    print("Optimizations complete!")


if __name__ == "__main__":
    sub_dir = input("Folder to process: ")
    select = input("Convert or Optimize? ").lower()
    if select == "convert":
        fileConversions(sub_dir)
    elif select == "optimize":
        fileOptimizations(sub_dir)
