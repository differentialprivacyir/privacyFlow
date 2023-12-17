#PBS -N job1
#PBS -m ae
#PBS -M golgolnia@sharif.edu
#PBS –l nodes=1:ppn=2
cd privacyFlow
python privacy_flow_test.py > results/hpcOutputnormalMu150Sigma50N10kR20.txt