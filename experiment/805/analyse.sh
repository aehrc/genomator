p=$(pwd)
echo GAN
for i in $(find . -iname GAN_results.txt); do
  cd $p
  cd $(dirname $i)
  cat $(basename $i) | tail -n 1
done
cd $p

echo RBM
for i in $(find . -iname RBM_results.txt); do
  cd $p
  cd $(dirname $i)
  cat $(basename $i) | tail -n 1
done
cd $p

echo MARK
for i in $(find . -iname MARK_results.txt); do
  cd $p
  cd $(dirname $i)
  cat $(basename $i) | tail -n 1
done
cd $p

echo CRBM
for i in $(find . -iname CRBM_results.txt); do
  cd $p
  cd $(dirname $i)
  cat $(basename $i) | tail -n 1
done
cd $p

echo GENOMATOR
for i in $(find . -iname GENOMATOR_results.txt); do
  cd $p
  cd $(dirname $i)
  cat $(basename $i) | tail -n 1
done
cd $p
