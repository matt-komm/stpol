desc="tmp"
i="$1"
size=${#i}
if [ $size>0 ];
then
    desc="_$1"
fi

mkdir -p output/added${desc}
cd output
for channel in "mu" "ele"
do
    mkdir -p added${desc}/$channel
    for dataset in "DYJets" "T_t" "Tbar_tW" "W4Jets_exclusive" "ZZ" "TTJets_FullLept" "T_tW" "Tbar_t_ToLeptons" "WJets_inclusive" "TTJets_MassiveBinDECAY" "T_t_ToLeptons" "W1Jets_exclusive" "WJets_sherpa" "TTJets_SemiLept" "Tbar_s" "W2Jets_exclusive" "WW" "T_s" "Tbar_t" "W3Jets_exclusive" "WZ"
    do
        hadd added${desc}/$channel/${channel}_${dataset}.root pdftest_${channel}_${dataset}_*.root
    done
done
