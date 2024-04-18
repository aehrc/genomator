import os
def running(a):
    print("RUNNING: {}".format(a))
    os.system(a)

#the data_source and chromisome vcf files
prepend = "http://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/1000G_2504_high_coverage/working/20220422_3202_phased_SNV_INDEL_SV/"
chromisome_files = ["1kGP_high_coverage_Illumina.chr{}.filtered.SNV_INDEL_SV_phased_panel.vcf.gz".format(i) for i in range(1,23)]

#NOTE: these are just the first 400 samples in the files
selected_samples = ["HG{:05d}".format(s) for s in [96, 97, 99, 100, 101, 102, 103, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117,
 118, 119, 120, 121, 122, 123, 125, 126, 127, 128, 129, 130, 131, 132, 133, 136, 137, 138, 139, 140,
 141, 142, 143, 145, 146, 148, 149, 150, 151, 154, 155, 157, 158, 159, 160, 171, 173, 174, 176, 177,
 178, 179, 180, 181, 182, 183, 185, 186, 187, 188, 189, 190, 231, 232, 233, 234, 235, 236, 237, 238,
 239, 240, 242, 243, 244, 245, 246, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262,
 263, 264, 265, 266, 267, 268, 269, 271, 272, 273, 274, 275, 276, 277, 278, 280, 281, 282, 284, 285,
 288, 290, 304, 306, 308, 309, 310, 311, 313, 315, 318, 319, 320, 321, 323, 324, 325, 326, 327, 328,
 329, 330, 331, 332, 334, 335, 336, 337, 338, 339, 341, 342, 343, 344, 345, 346, 349, 350, 351, 353,
 355, 356, 357, 358, 360, 361, 362, 364, 365, 366, 367, 368, 369, 371, 372, 373, 375, 376, 378, 379,
 380, 381, 382, 383, 384, 403, 404, 405, 406, 407, 408, 409, 410, 418, 419, 420, 421, 422, 423, 427,
 428, 429, 436, 437, 438, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 457, 458, 459,
 463, 464, 465, 472, 473, 474, 475, 476, 477, 478, 479, 480, 500, 501, 502, 512, 513, 514, 524, 525,
 526, 530, 531, 532, 533, 534, 535, 536, 537, 538, 542, 543, 544, 551, 552, 553, 554, 555, 556, 557,
 558, 559, 560, 561, 565, 566, 567, 577, 578, 579, 580, 581, 582, 583, 584, 585, 589, 590, 591, 592,
 593, 594, 595, 596, 597, 598, 599, 607, 608, 609, 610, 611, 612, 613, 614, 615, 619, 620, 621, 622,
 623, 625, 626, 627, 628, 629, 630, 631, 632, 634, 635, 636, 637, 638, 639, 640, 641, 642, 650, 651,
 652, 653, 654, 655, 656, 657, 658, 662, 663, 664, 671, 672, 673, 674, 675, 683, 684, 685, 689, 690,
 691, 692, 693, 694, 698, 699, 700, 701, 702, 703, 704, 705, 706, 707, 708, 709, 717, 728, 729, 731,
 732, 733, 734, 735, 736, 737, 738, 739, 740, 741, 742, 743, 759, 766, 844, 851, 864, 867, 879, 881,
 956, 978, 982, 1028, 1029, 1031, 1046, 1047, 1048, 1049, 1050, 1051, 1052, 1053, 1054, 1055, 1056, 1058, 1060, 1061]]

print("Downloading 1000 genomes data")
for c in chromisome_files:
  running(f"wget {prepend+c}")
  running(f"wget {prepend+c}.tbi")

genes = {
  "AGBL4":(1,48532854,50023954),
  "FHIT":(3,59747277,61251452),
  "CCSER1":(4,90127394,91605295),
  "RBFOX1":(16,6019024,7713340)
}
print("Splitting out genes")
for gene,data in genes.items():
  running(f"bcftools view -r chr{data[0]}:{data[1]}-{data[2]} {chromisome_files[data[0]-1]} > {gene}.vcf")
  running(f"plink2 --vcf {gene}.vcf --maf 0.01 --hwe 1e-6 --rm-dup 'exclude-all' --recode vcf --out {gene}.cleaned")
  running(f"gzip {gene}.cleaned.vcf")
  running(f"mv {gene}.cleaned.vcf.gz {gene}.vcf.gz")
running(f"plink2 --vcf AGBL4.vcf.gz --maf 0.05 --rm-dup 'exclude-all' --recode vcf --out AGBL4.SMALLER")
running(f"gzip AGBL4.SMALLER.vcf")


print("Compiling big data")
for i,file in enumerate(chromisome_files):
  print(f"Cleaning chromisome {i+1}")
  running(f"bcftools view -s {','.join(selected_samples)} {file} > temp_CHROM{i+1}.vcf" )
  running(f"plink2 --vcf temp_CHROM{i+1}.vcf --maf 0.01 --hwe 1e-6 --rm-dup 'exclude-all' --recode vcf --out CHROM{i+1}")
  running(f"bgzip CHROM{i+1}.vcf")
  running(f"tabix CHROM{i+1}.vcf.gz")
print("Merging human genome data")
running(f"bcftools concat {' '.join(['CHROM'+str(i+1)+'.vcf.gz' for i in range(len(chromisome_files))])} -o chr_filtered_.vcf")

running(f"gzip chr_filtered_.vcf")
print("Splitting big data into incremental parts")
for i in [100*4**j for j in range(9)]:
    print(i)
    running("zcat chr_filtered_.vcf.gz | head -n {} | gzip > chr_filtered_{}.vcf.gz".format(i+113,i))
print("pickling")
for i in [100*4**j for j in range(9)]+[""]:
    running(f"vcf_to_pickle.py chr_filtered_{i}.vcf.gz chr_filtered_{i}.vcf.gz.pickle")

print("Merging chrom 10 and 16")
running(f"bcftools concat {chromisome_files[9]} {chromisome_files[15]} -o ALL.chr10_and_16.vcf")
running(f"plink2 --vcf ALL.chr10_and_16.vcf --maf 0.01 --rm-dup 'exclude-all' --recode vcf --out ALL.chr10_and_16.cleaned")
running("vcf_to_pickle.py ALL.chr10_and_16.cleaned.vcf ALL.chr10_and_16.cleaned.vcf.pickle")
