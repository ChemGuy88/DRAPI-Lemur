# Test shell expansion
shopt -s extglob
echo "/data/herman/mnt/ufhsd/SHANDS/SHARE/DSS/IDR Data Requests/ACTIVE RDRs/Bian/IRB202003281/Intermediate Results/BO Portion/data/output/script/2024-04-02 17-19-40/"* > asdf.txt
echo "/data/herman/mnt/ufhsd/SHANDS/SHARE/DSS/IDR Data Requests/ACTIVE RDRs/Bian/IRB202003281/Intermediate Results/Notes Portion/data/output/freeText/2024-04-03 12-38-35/free_text"/FlaDia_*/!(deid*) > asdf.txt
shopt -u extglob
