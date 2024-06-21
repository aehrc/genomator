#!/usr/bin/env Rscript 
## Move to R for visualisation - required files:
#   - ALL.chr10_and_16.cleaned.vcf.pruned.pca.eigenvec (from step 3)
#   - 20130606_g1k.ped (downloaded from 1000 Genomes Project - metadata on ancestry)
#   - GENOMATOR.1KGProjected.sscore (from step 4)
#   - ALL.chr10_and_16.cleaned.vcf.pruned.pca.eigenval (from step 3)
#   - GENOMATOR.pharmacogenetics.raw (from step 5)

library(data.table)
library(tidyverse)
library(janitor)
library(ggpubr)
library(knitr)

ped <- fread('/data/20130606_g1k.ped')
df2 <- fread('ALL.chr10_and_16.cleaned.vcf.pruned.pca.eigenvec') %>%
  left_join(ped %>% select(`Individual ID`, Population), by = c('IID' = 'Individual ID')) %>%
  # mutate(Population = ifelse(is.na(Population), 'Genomator', Population)) %>%
  mutate(SuperPopulation = ifelse(Population %in% c("ACB","ASW","ESN","GWD","LWK","MSL","YRI"), 'African',
                                  ifelse(Population %in% c("CLM","MXL","PEL","PUR"), 'American', 
                                         ifelse(Population %in% c("CDX","CHB","CHS","JPT","KHV"), 'East Asian', 
                                                ifelse(Population %in% c("CEU","FIN","GBR","IBS","TSI"), "European",
                                                       ifelse(Population %in% c("BEB","GIH","ITU","PJL","STU"), "South Asian", NA)))))) %>%
  column_to_rownames('IID') %>% select(-1)
  
df3 <- fread('GENOMATOR.1KGProjected.sscore') %>% rename(IID = `#IID`)
df4 <- fread('ALL.chr10_and_16.cleaned.vcf.pruned.pca.eigenval') %>% pull(V1)

df5 <- df3 %>% rowwise() %>% mutate(PC1 = PC1_AVG/(-sqrt(df4[1])/2), PC2 = PC2_AVG/(-sqrt(df4[2])/2), PC3 = PC3_AVG/(-sqrt(df4[3])/2)) %>% mutate(SuperPopulation = 'Genomator') %>%
  column_to_rownames('IID')

df6 <- df2 %>% select(SuperPopulation, PC1, PC2, PC3) %>% bind_rows(df5 %>% select(SuperPopulation, PC1, PC2, PC3))


g3 <- ggplot(df6, aes(x = PC1, y = PC2, col = as.factor(SuperPopulation), shape = as.factor(SuperPopulation))) + 
  geom_point() +
  theme_bw() +
  scale_colour_manual(values = c('#E55812', '#EDA507', '#643173', '#08415C', '#697A21', '#94999E'), name = 'Super Population', 
                      breaks = c('African', 'American', 'East Asian', 'European', 'South Asian', 'Genomator'),
                      labels = c('African (AFR)', 'American (AMR)', 'East Asian (EAS)', 'European (EUR)', 'South Asian (SAS)', 'Genomator')) +
  scale_shape_manual(values = c(16, 16, 16, 16, 16, 4), name = 'Super Population', breaks = c('African', 'American', 'East Asian', 'European', 'South Asian', 'Genomator'),
                      labels = c('African (AFR)', 'American (AMR)', 'East Asian (EAS)', 'European (EUR)', 'South Asian (SAS)', 'Genomator')) + 
  geom_vline(aes(xintercept = 0.02), col = '#941B0C', linetype = 'dotted') +
  geom_hline(aes(yintercept = -0.022), col = '#941B0C', linetype = 'dotted') +
  geom_hline(aes(yintercept = 0.025), col = '#941B0C', linetype = 'dotted') 
g4 <- ggplot(df6, aes(x = PC1, y = PC3, col = as.factor(SuperPopulation), shape = as.factor(SuperPopulation))) + 
  geom_point() +
  theme_bw() + 
  scale_colour_manual(values = c('#E55812', '#EDA507', '#643173', '#08415C', '#697A21', '#94999E'), name = 'Super Population', 
                      breaks = c('African', 'American', 'East Asian', 'European', 'South Asian', 'Genomator'),
                      labels = c('African (AFR)', 'American (AMR)', 'East Asian (EAS)', 'European (EUR)', 'South Asian (SAS)', 'Genomator')) +
  scale_shape_manual(values = c(16, 16, 16, 16, 16, 4), name = 'Super Population', 
                     breaks = c('African', 'American', 'East Asian', 'European', 'South Asian', 'Genomator'),
                      labels = c('African (AFR)', 'American (AMR)', 'East Asian (EAS)', 'European (EUR)', 'South Asian (SAS)', 'Genomator'))  

p1 <- ggarrange(g3, g4, align = 'h', common.legend = T, legend = 'right', labels = c('A', 'B')) #Supplementary Figure 10
ggsave('PCA.tiff', p1, units = 'px', height = 1700, width = 3000)

##Thresholds to Determine Ethnicities:

##- Africans: PC1 > 0.02
##- East Asians: PC1 < 0.02 & PC2 > 0.025
##- Europeans: PC1 < 0.02 & PC2 < -0.022

gen.ethnicity <- df6 %>% rownames_to_column('ID') %>%
  filter(grepl('GENERATED', ID)) %>%
  mutate(PC.Population = ifelse(PC1 > 0.02, 'African', 
                                ifelse(PC1 < 0.02 & PC2 > 0.025, 'East Asian', 
                                       ifelse(PC1 < 0.02 & PC2 < -0.022, 'European', 'Other'))))

#Supplementary Table 6
count(df2, SuperPopulation) %>% filter(SuperPopulation != 'Genomator') %>% 
  mutate(Percentage = round(n/nrow(df2)*100, 2)) %>% rename(`1KG` = n, `1KG (%)` = Percentage) %>%
  add_row(SuperPopulation = 'Other', `1KG` = 347 + 489, `1KG (%)` = round((347+489)/nrow(df2)*100, 2)) %>% filter(SuperPopulation %in% c('African', 'East Asian', 'European', 'Other')) %>%
  left_join((gen.ethnicity %>% count(PC.Population) %>% mutate(`Genomator (%)` = round(n/10, 2)) %>% rename(Genomator = n)), by = c('SuperPopulation' = 'PC.Population')) %>% rename(Ethnicity = SuperPopulation) %>%
  kable()
    
vkorc1 <- fread('GENOMATOR.pharmacogenetics.raw') %>% select(IID, `16:31096368:C:T_T`) %>%
  left_join(gen.ethnicity %>% select(ID, PC.Population), by = c('IID' = 'ID'))
v.a <- vkorc1 %>% filter(PC.Population == 'African') %>% count(`16:31096368:C:T_T`) %>% mutate(nA = `16:31096368:C:T_T`*n)  %>% pull(nA) %>% 
    sum/((vkorc1 %>% filter(PC.Population == 'African') %>% nrow)*2)*100
v.ea <- vkorc1 %>% filter(PC.Population == 'East Asian') %>% count(`16:31096368:C:T_T`) %>% mutate(nA = `16:31096368:C:T_T`*n) %>% pull(nA) %>% 
  sum/((vkorc1 %>% filter(PC.Population == 'East Asian') %>% nrow)*2)*100
v.e <- vkorc1 %>% filter(PC.Population == 'European') %>% count(`16:31096368:C:T_T`) %>% mutate(nA = `16:31096368:C:T_T`*n)  %>% pull(nA) %>% 
  sum/((vkorc1 %>% filter(PC.Population == 'European') %>% nrow)*2)*100
  
cyp2c19 <- fread('GENOMATOR.pharmacogenetics.raw') %>% select(IID, `10:94780653:G:A_A`, `10:94781859:G:A_A`) %>%
  left_join(gen.ethnicity %>% select(ID, PC.Population), by = c('IID' = 'ID'))

c1.a <- cyp2c19 %>% filter(PC.Population == 'African') %>% count(`10:94781859:G:A_A`) %>% mutate(nA = `10:94781859:G:A_A`*n) %>% pull(nA) %>% 
  sum/((cyp2c19 %>% filter(PC.Population == 'African') %>% nrow)*2)*100
c1.ea <- cyp2c19 %>% filter(PC.Population == 'East Asian') %>% count(`10:94781859:G:A_A`) %>% mutate(nA = `10:94781859:G:A_A`*n) %>% pull(nA) %>% 
  sum/((cyp2c19 %>% filter(PC.Population == 'East Asian') %>% nrow)*2)*100
c1.e <- cyp2c19 %>% filter(PC.Population == 'European') %>% count(`10:94781859:G:A_A`) %>% mutate(nA = `10:94781859:G:A_A`*n) %>% pull(nA) %>% 
  sum/((cyp2c19 %>% filter(PC.Population == 'European') %>% nrow)*2)*100


c2.a <- cyp2c19 %>% filter(PC.Population == 'African') %>% count(`10:94780653:G:A_A`) %>% mutate(nA = `10:94780653:G:A_A`*n) %>% pull(nA) %>% 
  sum/((cyp2c19 %>% filter(PC.Population == 'African') %>% nrow)*2)*100
c2.ea <- cyp2c19 %>% filter(PC.Population == 'East Asian') %>% count(`10:94780653:G:A_A`) %>% mutate(nA = `10:94780653:G:A_A`*n) %>% pull(nA) %>% 
  sum/((cyp2c19 %>% filter(PC.Population == 'East Asian') %>% nrow)*2)*100
c2.e <- cyp2c19 %>% filter(PC.Population == 'European') %>% count(`10:94780653:G:A_A`) %>% mutate(nA = `10:94780653:G:A_A`*n) %>% pull(nA) %>% 
  sum/((cyp2c19 %>% filter(PC.Population == 'European') %>% nrow)*2)*100
  
df <- data.frame(Gene = c(rep('VKORC1 (rs9923231)', 12), rep('CYP2C19*2 (rs4244285)', 12), rep('CYP2C19*3 (rs4986893)', 12)),
                 Source = c(rep(rep(c('Genomator', '1KG', 'HGDP', 'gnomADv4'), 3), 3)),
                 Population = c(rep(rep(c('AFR', 'EAS', 'EUR'), each = 4), 3)), 
                 y = c(round(v.a,2), 4.9, 4.0, 9.97, 
                       round(v.ea,2), 88.48, 90.18, 89.17,
                       round(v.e,2), 38.16, 50.99, 37.79,
                       
                       round(c1.a,2), 16.65, 11.73, 17.84,
                       round(c1.ea,2), 31.31, 27.63, 30.36,
                       round(c1.e,2), 14.29, 17.11, 14.62,
                       
                       round(c2.a,2), 0.16, 1.01, 0.045,
                       round(c2.ea,2), 5.35, 5.91, 8.87,
                       round(c2.e,2), 0, 0.33, 0.01))


p2 <- ggplot(data = df, aes(x = Population, y = y)) + 
  geom_point(aes(colour = Source)) +
  geom_line(aes(group = Source, colour = Source)) +
  facet_grid(. ~ Gene) +
  theme_bw() +
  labs(x = '\nPopulation', y = 'MAF (100%)\n') + 
  scale_colour_manual(name = 'Data Source', values = c('#58A4DA', '#0A0A0A', '#99AA38', '#7F2CCB', '#F5A300')) #Figure 6
  
ggsave('MAF.tiff', p2, units = 'px', height = 1700, width = 3000)
