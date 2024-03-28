cd sources
python script.py
cd ..
p=$(pwd)
for i in $(find . -iname script.sh); do
  cd $p
  cd $(dirname $i)
  source $(basename $i)
done
