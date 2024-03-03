# synology-photos-dedupe
After importing photo libraries from iCloud and Google Photos, a lot of duplicate photos are present on my Synology nas. Because the Google Photos versions are not full resolution Synology does not detect them as duplicate. This tool helps you to find and move duplicate files based on filename and date. The largest version of the file will be kept.

# Get started
Clone this repo.
```sh
pip install -r requirements.txt
```
# Example usage
```sh
python dedupe.py --dirs "Photos/Google Photos" "Photos/MobileBackup" --dest dupes --filters @eaDir --exts jpg png gif mp4 -v 
```

For all arguments see:
```sh
python dedupe.py -h
```
