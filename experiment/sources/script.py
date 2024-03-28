import os

prepend = "https://ftp-trace.ncbi.nih.gov/1000genomes/ftp/release/20130502/"
chromisome_files = [
  "ALL.chr1.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz",
  "ALL.chr2.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz",
  "ALL.chr3.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz",
  "ALL.chr4.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz",
  "ALL.chr5.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz",
  "ALL.chr6.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz",
  "ALL.chr7.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz",
  "ALL.chr8.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz",
  "ALL.chr9.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz",
  "ALL.chr10.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz",
  "ALL.chr11.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz",
  "ALL.chr12.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz",
  "ALL.chr13.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz",
  "ALL.chr14.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz",
  "ALL.chr15.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz",
  "ALL.chr16.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz",
  "ALL.chr17.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz",
  "ALL.chr18.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz",
  "ALL.chr19.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz",
  "ALL.chr20.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz",
  "ALL.chr21.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz",
  "ALL.chr22.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz"
]

selected_samples=["HG00096", "HG00097", "HG00099", "HG00100", "HG00101", "HG00102", "HG00103", "HG00105", "HG00106", "HG00107", "HG00108",
"HG00109", "HG00110", "HG00111", "HG00112", "HG00113", "HG00114", "HG00115", "HG00116", "HG00117", "HG00118", "HG00119",
"HG00120", "HG00121", "HG00122", "HG00123", "HG00125", "HG00126", "HG00127", "HG00128", "HG00129", "HG00130", "HG00131",
"HG00132", "HG00133", "HG00136", "HG00137", "HG00138", "HG00139", "HG00140", "HG00141", "HG00142", "HG00143", "HG00145",
"HG00146", "HG00148", "HG00149", "HG00150", "HG00151", "HG00154", "HG00155", "HG00157", "HG00158", "HG00159", "HG00160",
"HG00171", "HG00173", "HG00174", "HG00176", "HG00177", "HG00178", "HG00179", "HG00180", "HG00181", "HG00182", "HG00183",
"HG00185", "HG00186", "HG00187", "HG00188", "HG00189", "HG00190", "HG00231", "HG00232", "HG00233", "HG00234", "HG00235",
"HG00236", "HG00237", "HG00238", "HG00239", "HG00240", "HG00242", "HG00243", "HG00244", "HG00245", "HG00246", "HG00250",
"HG00251", "HG00252", "HG00253", "HG00254", "HG00255", "HG00256", "HG00257", "HG00258", "HG00259", "HG00260", "HG00261",
"HG00262", "HG00263", "HG00264", "HG00265", "HG00266", "HG00267", "HG00268", "HG00269", "HG00271", "HG00272", "HG00273",
"HG00274", "HG00275", "HG00276", "HG00277", "HG00278", "HG00280", "HG00281", "HG00282", "HG00284", "HG00285", "HG00288",
"HG00290", "HG00304", "HG00306", "HG00308", "HG00309", "HG00310", "HG00311", "HG00313", "HG00315", "HG00318", "HG00319",
"HG00320", "HG00321", "HG00323", "HG00324", "HG00325", "HG00326", "HG00327", "HG00328", "HG00329", "HG00330", "HG00331",
"HG00332", "HG00334", "HG00335", "HG00336", "HG00337", "HG00338", "HG00339", "HG00341", "HG00342", "HG00343", "HG00344",
"HG00345", "HG00346", "HG00349", "HG00350", "HG00351", "HG00353", "HG00355", "HG00356", "HG00357", "HG00358", "HG00360",
"HG00361", "HG00362", "HG00364", "HG00365", "HG00366", "HG00367", "HG00368", "HG00369", "HG00371", "HG00372", "HG00373",
"HG00375", "HG00376", "HG00378", "HG00379", "HG00380", "HG00381", "HG00382", "HG00383", "HG00384", "HG00403", "HG00404",
"HG00406", "HG00407", "HG00409", "HG00410", "HG00419", "HG00421", "HG00422", "HG00428", "HG00436", "HG00437", "HG00442",
"HG00443", "HG00445", "HG00446", "HG00448", "HG00449", "HG00451", "HG00452", "HG00457", "HG00458", "HG00463", "HG00464",
"HG00472", "HG00473", "HG00475", "HG00476", "HG00478", "HG00479", "HG00500", "HG00513", "HG00524", "HG00525", "HG00530",
"HG00531", "HG00533", "HG00534", "HG00536", "HG00537", "HG00542", "HG00543", "HG00551", "HG00553", "HG00554", "HG00556",
"HG00557", "HG00559", "HG00560", "HG00565", "HG00566", "HG00580", "HG00581", "HG00583", "HG00584", "HG00589", "HG00590",
"HG00592", "HG00593", "HG00595", "HG00596", "HG00598", "HG00599", "HG00607", "HG00608", "HG00610", "HG00611", "HG00613",
"HG00614", "HG00619", "HG00620", "HG00622", "HG00623", "HG00625", "HG00626", "HG00628", "HG00629", "HG00631", "HG00632",
"HG00634", "HG00637", "HG00638", "HG00640", "HG00641", "HG00650", "HG00651", "HG00653", "HG00654", "HG00656", "HG00657",
"HG00662", "HG00663", "HG00671", "HG00672", "HG00674", "HG00675", "HG00683", "HG00684", "HG00689", "HG00690", "HG00692",
"HG00693", "HG00698", "HG00699", "HG00701", "HG00704", "HG00705", "HG00707", "HG00708", "HG00717", "HG00728", "HG00729",
"HG00731", "HG00732", "HG00734", "HG00736", "HG00737", "HG00739", "HG00740", "HG00742", "HG00743", "HG00759", "HG00766",
"HG00844", "HG00851", "HG00864", "HG00867", "HG00879", "HG00881", "HG00956", "HG00978", "HG00982", "HG01028", "HG01029",
"HG01031", "HG01046", "HG01047", "HG01048", "HG01049", "HG01051", "HG01052", "HG01054", "HG01055", "HG01058", "HG01060",
"HG01061", "HG01063", "HG01064", "HG01066", "HG01067", "HG01069", "HG01070", "HG01072", "HG01073", "HG01075", "HG01077",
"HG01079", "HG01080", "HG01082", "HG01083", "HG01085", "HG01086", "HG01088", "HG01089", "HG01092", "HG01094", "HG01095",
"HG01097", "HG01098", "HG01101", "HG01102", "HG01104", "HG01105", "HG01107", "HG01108", "HG01110", "HG01111", "HG01112",
"HG01113", "HG01119", "HG01121", "HG01122", "HG01124", "HG01125", "HG01130", "HG01131", "HG01133", "HG01134", "HG01136",
"HG01137", "HG01139", "HG01140", "HG01142", "HG01148", "HG01149", "HG01161", "HG01162", "HG01164", "HG01167", "HG01168",
"HG01170", "HG01171", "HG01173", "HG01174", "HG01176", "HG01177", "HG01182", "HG01183", "HG01187", "HG01188", "HG01190",
"HG01191", "HG01197", "HG01198", "HG01200"]



print("Downloading 1000 genomes data")
for c in chromisome_files:
  print(c)
  os.system(f"wget {prepend+c}")
  os.system(f"wget {prepend+c}.tbi")

genes = {
  "AGBL4":(1,48532854,50023954),
  "FHIT":(3,59747277,61251452),
  "CCSER1":(4,90127394,91605295),
  "RBFOX1":(16,6019024,7713340)
}

print("Splitting out genes")
for gene,data in genes.items():
  os.system(f"bcftools view -r {data[0]}:{data[1]}-{data[2]} {chromisome_files[data[0]-1]} > {gene}.vcf")
  os.system(f"plink2 --vcf {gene}.vcf --maf 0.01 --hwe 1e-6 --rm-dup 'exclude-all' --recode vcf --out {gene}.cleaned")
  os.system(f"gzip {gene}.cleaned.vcf")
  os.system(f"mv {gene}.cleaned.vcf.gz {gene}.vcf.gz")
os.system(f"plink2 --vcf AGBL4.vcf.gz --maf 0.05 --rm-dup 'exclude-all' --recode vcf --out AGBL4.SMALLER")
os.system(f"gzip AGBL4.SMALLER.vcf")
os.system(f"bcftools view -s {','.join(selected_samples)} AGBL4.vcf.gz > AGBL4.TRIMMED.vcf")
os.system(f"gzip AGBL4.TRIMMED.vcf")

print("Cleaning big data")
for i,file in enumerate(chromisome_files):
  print(f"Cleaning chromisome {i+1}")
  os.system(f"bcftools view -s {','.join(selected_samples)} {file} > temp_CHROM{i+1}.vcf" )
  os.system(f"plink2 --vcf temp_CHROM{i+1}.vcf --maf 0.01 --hwe 1e-6 --rm-dup 'exclude-all' --recode vcf --out CHROM{i+1}")
  os.system(f"bgzip CHROM{i+1}.vcf")
  os.system(f"tabix CHROM{i+1}.vcf.gz")
print("Merging human genome data")
os.system(f"bcftools concat {' '.join(['CHROM'+str(i+1)+'.vcf.gz' for i in range(len(chromisome_files))])} -o chr_filtered_.vcf")

os.system(f"gzip chr_filtered_.vcf")
print("Splitting")
for i in [100*4**j for j in range(9)]:
    print(i)
    os.system("zcat chr_filtered_.vcf.gz | head -n {} | gzip > chr_filtered_{}.vcf.gz".format(i+193,i))
print("pickling")
for i in [100*4**j for j in range(9)]+[""]:
    os.system("vcf_to_pickle.py chr_filtered_{i}.vcf.gz chr_filtered_{i}.vcf.gz.pickle")

print("Merging chrom 10 and 16")
os.system(f"bcftools concat {chromisome_files[9]} {chromisome_files[15]} -o ALL.chr10_and_16.vcf")
os.system(f"plink2 --vcf ALL.chr10_and_16.vcf --maf 0.01 --rm-dup 'exclude-all' --recode vcf --out ALL.chr10_and_16.cleaned")
os.system("vcf_to_pickle.py ALL.chr10_and_16.cleaned.vcf ALL.chr10_and_16.cleaned.vcf.pickle")
