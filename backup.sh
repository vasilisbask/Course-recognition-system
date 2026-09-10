# Dump data base

current_date=$(date +"%Y-%m-%d")
echo $current_date
filename="pg2.data.$current_date"
cd /docker/myfaculty2.0/myfaculty2.0
/usr/bin/docker compose exec -T -u postgres db pg_dump postgres > $filename
/usr/bin/rclone copy $filename gdrive:
rm $filename

tarfile="media2.$current_date.tar.gz"
/usr/bin/tar czf $tarfile code/myfaculty/media
/usr/bin/rclone copy $tarfile gdrive:
rm $tarfile

 
