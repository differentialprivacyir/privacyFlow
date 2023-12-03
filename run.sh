#PBS –N job1
#PBS –m ae
#PBS –M xxx@ce.sharif.edu
#PBS –l nodes=1:ppn=2
cd privacyFlow
python privacy_flow_test.py > results/hpcOutputnormalMu=150Sigma=50N=10kR=20.txt