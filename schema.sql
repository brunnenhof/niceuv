BEGIN TRANSACTION;
CREATE TABLE ai_regions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id TEXT NOT NULL,
                region_tag TEXT NOT NULL,
                FOREIGN KEY (game_id) REFERENCES games(game_id),
                UNIQUE(game_id, region_tag)
            );
CREATE TABLE bud (
	ta TEXT,
	value REAL,
	reg TEXT,
	regx INTEGER,
	round INTEGER,
	game_id TEXT
);
INSERT INTO "bud" VALUES('bud',3.823307207220348118e+02,'us',0,0,'START');
INSERT INTO "bud" VALUES('bud',92.17284948069,'af',1,0,'START');
INSERT INTO "bud" VALUES('bud',6.300886135652178837e+02,'cn',2,0,'START');
INSERT INTO "bud" VALUES('bud',2.390622651878522049e+02,'me',3,0,'START');
INSERT INTO "bud" VALUES('bud',3.173180262644625599e+02,'sa',4,0,'START');
INSERT INTO "bud" VALUES('bud',2.923143172253998613e+02,'la',5,0,'START');
INSERT INTO "bud" VALUES('bud',2.448793126225039031e+02,'pa',6,0,'START');
INSERT INTO "bud" VALUES('bud',1.877586501123085441e+02,'ec',7,0,'START');
INSERT INTO "bud" VALUES('bud',5.247842951490454198e+02,'eu',8,0,'START');
INSERT INTO "bud" VALUES('bud',2.261779149745387941e+02,'se',9,0,'START');
INSERT INTO "bud" VALUES('pov',1.514575605770024148e+01,'us',0,0,'START');
INSERT INTO "bud" VALUES('pov',3.653165621280953345e+00,'af',1,0,'START');
INSERT INTO "bud" VALUES('pov',2.496997161563902523e+01,'cn',2,0,'START');
INSERT INTO "bud" VALUES('pov',9.47369923995185558e+00,'me',3,0,'START');
INSERT INTO "bud" VALUES('pov',1.257626975340640918e+01,'sa',4,0,'START');
INSERT INTO "bud" VALUES('pov',1.158391266912434148e+01,'la',5,0,'START');
INSERT INTO "bud" VALUES('pov',9.70224336526114684e+00,'pa',6,0,'START');
INSERT INTO "bud" VALUES('pov',7.440491138579941933e+00,'ec',7,0,'START');
INSERT INTO "bud" VALUES('pov',2.079211025735538953e+01,'eu',8,0,'START');
INSERT INTO "bud" VALUES('pov',8.963625446472073933e+00,'se',9,0,'START');
INSERT INTO "bud" VALUES('ineq',6.058302423080096589e+01,'us',0,0,'START');
INSERT INTO "bud" VALUES('ineq',1.461266248512381339e+01,'af',1,0,'START');
INSERT INTO "bud" VALUES('ineq',99.8798864625561,'cn',2,0,'START');
INSERT INTO "bud" VALUES('ineq',3.789479695980742235e+01,'me',3,0,'START');
INSERT INTO "bud" VALUES('ineq',5.030507901362563672e+01,'sa',4,0,'START');
INSERT INTO "bud" VALUES('ineq',4.633565067649736591e+01,'la',5,0,'START');
INSERT INTO "bud" VALUES('ineq',3.880897346104458734e+01,'pa',6,0,'START');
INSERT INTO "bud" VALUES('ineq',2.976196455431976773e+01,'ec',7,0,'START');
INSERT INTO "bud" VALUES('ineq',8.316844102942155814e+01,'eu',8,0,'START');
INSERT INTO "bud" VALUES('ineq',3.585450178588829573e+01,'se',9,0,'START');
INSERT INTO "bud" VALUES('emp',4.543726817310072619e+01,'us',0,0,'START');
INSERT INTO "bud" VALUES('emp',1.095949686384286003e+01,'af',1,0,'START');
INSERT INTO "bud" VALUES('emp',7.49099148469170757e+01,'cn',2,0,'START');
INSERT INTO "bud" VALUES('emp',2.842109771985556676e+01,'me',3,0,'START');
INSERT INTO "bud" VALUES('emp',3.772880926021922931e+01,'sa',4,0,'START');
INSERT INTO "bud" VALUES('emp',3.475173800737302799e+01,'la',5,0,'START');
INSERT INTO "bud" VALUES('emp',2.910673009578344406e+01,'pa',6,0,'START');
INSERT INTO "bud" VALUES('emp',2.232147341573982757e+01,'ec',7,0,'START');
INSERT INTO "bud" VALUES('emp',6.23763307720661615e+01,'eu',8,0,'START');
INSERT INTO "bud" VALUES('emp',2.689087633941622357e+01,'se',9,0,'START');
INSERT INTO "bud" VALUES('food',2.726236090386043288e+01,'us',0,0,'START');
INSERT INTO "bud" VALUES('food',6.575698118305716377e+00,'af',1,0,'START');
INSERT INTO "bud" VALUES('food',4.494594890815024257e+01,'cn',2,0,'START');
INSERT INTO "bud" VALUES('food',1.705265863191333864e+01,'me',3,0,'START');
INSERT INTO "bud" VALUES('food',2.263728555613153759e+01,'sa',4,0,'START');
INSERT INTO "bud" VALUES('food',2.085104280442381607e+01,'la',5,0,'START');
INSERT INTO "bud" VALUES('food',1.746403805747006644e+01,'pa',6,0,'START');
INSERT INTO "bud" VALUES('food',1.339288404944389654e+01,'ec',7,0,'START');
INSERT INTO "bud" VALUES('food',37.4257984632397,'eu',8,0,'START');
INSERT INTO "bud" VALUES('food',1.613452580364973343e+01,'se',9,0,'START');
INSERT INTO "bud" VALUES('ener',2.726236090386043288e+01,'us',0,0,'START');
INSERT INTO "bud" VALUES('ener',6.575698118305716377e+00,'af',1,0,'START');
INSERT INTO "bud" VALUES('ener',4.494594890815024257e+01,'cn',2,0,'START');
INSERT INTO "bud" VALUES('ener',1.705265863191333864e+01,'me',3,0,'START');
INSERT INTO "bud" VALUES('ener',2.263728555613153759e+01,'sa',4,0,'START');
INSERT INTO "bud" VALUES('ener',2.085104280442381607e+01,'la',5,0,'START');
INSERT INTO "bud" VALUES('ener',1.746403805747006644e+01,'pa',6,0,'START');
INSERT INTO "bud" VALUES('ener',1.339288404944389654e+01,'ec',7,0,'START');
INSERT INTO "bud" VALUES('ener',37.4257984632397,'eu',8,0,'START');
INSERT INTO "bud" VALUES('ener',1.613452580364973343e+01,'se',9,0,'START');
CREATE TABLE games (
                game_id TEXT PRIMARY KEY,
                gm_username TEXT NOT NULL,
                num_rounds INTEGER DEFAULT 3,
                current_round INTEGER DEFAULT 0,
                state TEXT DEFAULT 'setup',
                "accept_decisions" BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            , lang TEXT DEFAULT 'en', langx INTEGER DEFAULT 0, mode TEXT DEFAULT 'light', [state_x] INT NULL DEFAULT 0);
CREATE TABLE human_regions ( 
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  game_id TEXT NOT NULL,
  region_tag TEXT NOT NULL,
  sub_1 INTEGER DEFAULT 0,
  sub_2 INTEGER DEFAULT 0,
  sub_3 INTEGER DEFAULT 0
);
CREATE TABLE "players" ( 
  [player_id] INTEGER AUTO_INCREMENT NULL,
  [username] TEXT NOT NULL,
  [game_id] TEXT NOT NULL,
  [region_tag] TEXT,
  [ministry] TEXT,
  [is_ai] BOOLEAN NULL DEFAULT 0 ,
  [is_logged_in_round1] BOOLEAN NULL DEFAULT 0 ,
  [is_logged_in_round2] BOOLEAN NULL DEFAULT 0 ,
  [is_logged_in_round3] BOOLEAN NULL DEFAULT 0 ,
  [created_at] TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ,
  [lang] TEXT NULL DEFAULT 'en' ,
  [langx] INTEGER NULL DEFAULT 0 ,
  [mode] TEXT NULL DEFAULT 'light' ,
  [state_x] INT NULL DEFAULT 0 ,
   PRIMARY KEY ([player_id]),
  CONSTRAINT [sqlite_autoindex_players_1] UNIQUE ([username])
);
CREATE TABLE plot_results (
                result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id TEXT NOT NULL,
                round INTEGER NOT NULL,
                region_tag TEXT NOT NULL,
                pv_id INTEGER NOT NULL,
                value REAL NOT NULL,
                FOREIGN KEY (game_id) REFERENCES games(game_id),
                FOREIGN KEY (pv_id) REFERENCES plot_variables(pv_id),
                UNIQUE(game_id, round, region_tag, pv_id)
            );
CREATE TABLE plot_variables (
                pv_id INTEGER PRIMARY KEY,
                pv_sdg_nbr INTEGER,
                pv_indicator TEXT NOT NULL,
                pv_vensim_name TEXT NOT NULL,
                pv_green REAL,
                pv_red REAL,
                pv_lowerbetter INTEGER,
                pv_ymin REAL,
                pv_ymax REAL,
                pv_subtitle TEXT,
                pv_ministry TEXT NOT NULL,
                pv_pct INTEGER,
                pv_sdg TEXT
            );
INSERT INTO "plot_variables" VALUES(1,1,'Poverty rate','Fraction of population below existential minimum',5.0,13.0,1,0.0,50.0,'Fraction of population living below $6.85 per day (%)','Poverty',100,'No poverty');
INSERT INTO "plot_variables" VALUES(2,2,'Undernourished fraction','Fraction of population undernourished',3.0,7.0,1,0.0,30.0,'Fraction of population undernourished (%)','Food',100,'No hunger');
INSERT INTO "plot_variables" VALUES(3,2,'Regenerative agriculture','Regenerative cropland fraction',80.0,50.0,0,0.0,100.0,'Proportion of agricultural area worked regeneratively (%)','Food',100,'No hunger');
INSERT INTO "plot_variables" VALUES(4,3,'Average wellbeing index','Average wellbeing index',1.8,1.0,0,0.0,3.0,'Average wellbeing index','Future',1,'Good health and wellbeing');
INSERT INTO "plot_variables" VALUES(5,3,'Life expectancy','Life expectancy at birth',80.0,60.0,0,30.0,110.0,'Life expectancy (years)','Inequality',1,'Good health and wellbeing');
INSERT INTO "plot_variables" VALUES(6,4,'Years in school','Years of schooling',15.0,13.0,0,0.0,18.0,'Years in school','Empowerment',1,'Quality education');
INSERT INTO "plot_variables" VALUES(7,5,'Female labor income share','GenderEquality',48.0,40.0,0,0.0,60.0,'Female pre-tax labor income share (%)','Empowerment',100,'Gender equality');
INSERT INTO "plot_variables" VALUES(8,6,'Safe water access','Safe water',95.0,80.0,0,0.0,100.0,'Fraction of population with access to safe water (%)','Poverty',100,'Access to clean water');
INSERT INTO "plot_variables" VALUES(9,6,'Safe sanitation access','Safe sanitation',90.0,65.0,0,0.0,100.0,'Fraction of population with access to safe sanitation (%)','Poverty',100,'Access to clean sanitation');
INSERT INTO "plot_variables" VALUES(10,7,'Electricity access','Access to electricity',98.0,90.0,0,10.0,100.0,'Fraction of population with access to electricity (%)','Empowerment',100,'Affordable and clean energy');
INSERT INTO "plot_variables" VALUES(11,7,'Renewable energy share','Renewable energy share in the total final energy consumption',80.0,50.0,0,0.0,100.0,'Wind and PV energy share in total energy consumption (%)','Energy',100,'Affordable and clean energy');
INSERT INTO "plot_variables" VALUES(12,7,'Energy intensity','Energy intensity kWh per usd',0.1,0.5,1,0.0,2.0,'Energy intensity: primary energy / GDP (kWh/$)','Energy',1,'Affordable and clean energy');
INSERT INTO "plot_variables" VALUES(13,8,'Worker disposable income','Disposable income pp post tax pre loan impact',25.0,15.0,0,0.0,50.0,'Worker disposable income (1000 $/person-year)','Inequality',1,'Decent work and economic growth');
INSERT INTO "plot_variables" VALUES(16,8,'GDP growth rate','Smoothed RoC in GDPpp',4.0,2.0,0,-5.0,10.0,'Growth rate of GDP per capita (%/yr)','Poverty',100,'Decent work and economic growth');
INSERT INTO "plot_variables" VALUES(17,11,'Emissions per person','Energy footprint pp',0.5,2.0,1,0.0,15.0,'Emissions per person (tCO2/p/y)','Energy',1,'Sustainable cities and communities');
INSERT INTO "plot_variables" VALUES(19,13,'Temperature rise','Temp surface anomaly compared to anfang degC',1.0,1.5,1,0.0,3.0,'Temperature rise (deg C above 1850)','Future',1,'Climate action');
INSERT INTO "plot_variables" VALUES(20,13,'Total GHG emissions','Total CO2 emissions',1.0,5.0,1,0.0,15.0,'Total greenhouse gas emissions per year (GtCO2/yr)','Energy',1,'Climate action');
INSERT INTO "plot_variables" VALUES(21,14,'Ocean pH','pH in surface',8.15,8.1,0,8.0,8.2,'Ocean surface pH','Future',1,'Life below water');
INSERT INTO "plot_variables" VALUES(23,16,'Public services','Public services pp',15.0,8.0,0,0.0,25.0,'Public services per person (1000 $/person-yr)','Inequality',1,'Peace justice and strong institutions');
INSERT INTO "plot_variables" VALUES(24,17,'Trust in institutions','Social trust',1.5,1.0,0,0.0,3.0,'Trust in institutions (1980=1)','Empowerment',1,'Partnership for the Goals');
INSERT INTO "plot_variables" VALUES(25,17,'Govt revenue share','Total government revenue as a proportion of GDP',45.0,30.0,0,0.0,60.0,'Total government revenue as a proportion of GDP (%)','Inequality',100,'Partnership for the Goals');
INSERT INTO "plot_variables" VALUES(26,0,'Population','Population',1000.0,1500.0,1,0.0,2000.0,'Population (million people)','Future',1,'Total population');
INSERT INTO "plot_variables" VALUES(27,10,'Labour share of GDP','Labour share of GDP',60.0,50.0,0,40.0,70.0,'Labour share of GDP (%)','Inequality',100,'Reduced inequalities');
INSERT INTO "plot_variables" VALUES(29,18,'Number of SDGs met','All SDG Scores',16.0,14.0,0,0.0,17.0,'Number of SDGs met - 17 can be met','Future',1,'SDG scores');
INSERT INTO "plot_variables" VALUES(30,9,'Investment share','Local private and govt investment share',40.0,30.0,0,0.0,60.0,'Private and govt investment share (% of GDP)','Poverty',100,'Industry innovation and infrastructure');
INSERT INTO "plot_variables" VALUES(32,12,'Nitrogen use','Nitrogen use per ha',10.0,20.0,1,0.0,50.0,'Nitrogen use (kg/ha-year)','Food',100,'Responsible consumption and production');
INSERT INTO "plot_variables" VALUES(33,15,'Forest area change','RoC in Forest land geglaettet',1.5,0.0,0,-3.0,4.0,'Annual change in forest area (%)','Food',100,'Life on land');
INSERT INTO "plot_variables" VALUES(34,9,'Donor investment share','LPB investment share',30.0,25.0,0,0.0,50.0,'Donor and off balance-sheet investment share (% of GDP)','Inequality',100,'Industry innovation and infrastructure');
INSERT INTO "plot_variables" VALUES(35,0,'Planetary boundaries breached','Planetary risk',0.5,2.0,1,0.0,5.0,'Planetary boundaries breached','Future',1,'Planetary boundaries');
INSERT INTO "plot_variables" VALUES(38,19,'Social trust','Social trust',1.0,0.7,0,0.0,2.0,'Social trust (index)','Future',1,'Social trust');
INSERT INTO "plot_variables" VALUES(39,20,'Social tension','Smoothed Social tension index with trust effect',1.0,1.2,1,0.0,2.0,'Smoothed Social tension index with trust effect (index)','Future',1,'Social tension');
INSERT INTO "plot_variables" VALUES(40,99,'Global social trust','Global_social_trust',1.5,1.0,0,0.0,2.0,'Trust in institutions (1980=1)','GM',1,'');
INSERT INTO "plot_variables" VALUES(41,99,'Global energy intensity','Global Energy intensity kWh per usd',0.25,1.0,1,0.0,3.0,'Energy intensity is primary energy / GDP (kWh/$)','GM',1,'');
INSERT INTO "plot_variables" VALUES(42,99,'Global energy footprint','Global_average_Energy_footprint_pp',0.25,1.0,1,0.0,8.0,'Emissions per person (tCO2/p/y) - global','GM',1,'');
INSERT INTO "plot_variables" VALUES(43,99,'Perceived warming','Temp surface anomaly compared to anfang degC',1.0,1.5,1,0.0,3.0,'Perceived global warming (degC over 1850)','GM',1,'');
INSERT INTO "plot_variables" VALUES(44,99,'Global wellbeing','Global Average wellbeing index',1.8,1.0,0,0.0,3.0,'index - higher is better','GM',1,'');
INSERT INTO "plot_variables" VALUES(45,99,'Global inequality','Global Actual inequality index higher is more unequal',0.9,1.1,1,0.5,1.5,'index - higher is worse','GM',1,'');
INSERT INTO "plot_variables" VALUES(46,99,'Global tension','Global Smoothed Social tension index with trust effect',0.8,1.0,1,0.5,1.5,'index - higher is worse','GM',1,'');
INSERT INTO "plot_variables" VALUES(47,99,'Population below 15k','Global Population below 2p5 kusd p py',500.0,1300.0,1,0.0,3000.0,'Population below 15000 $ per year (Million people)','GM',1,'');
INSERT INTO "plot_variables" VALUES(48,99,'Global population','Global population',1000.0,1500.0,1,0.0,10000.0,'Global Population (Million people)','GM',1,'');
INSERT INTO "plot_variables" VALUES(49,99,'Planetary risk','Planetary_risk',0.5,2.0,1,0.0,5.0,'Planetary boundaries breached','GM',1,NULL);
CREATE TABLE policies (
                pol_id INTEGER PRIMARY KEY,
                pol_tag TEXT NOT NULL UNIQUE,
                pol_name TEXT NOT NULL,
                pol_min REAL NOT NULL,
                pol_max REAL NOT NULL,
                pol_ministry TEXT NOT NULL,
                pol_ministry_tag TEXT NOT NULL
            );
INSERT INTO "policies" VALUES(1,'ExPS','Expand policy space',0.0,100.0,'Poverty','pov');
INSERT INTO "policies" VALUES(2,'LPB','Lending from public bodies (LPB)',0.0,30.0,'Poverty','pov');
INSERT INTO "policies" VALUES(3,'LPBsplit','LPB: Split the use of funds from public lenders',0.0,100.0,'Poverty','pov');
INSERT INTO "policies" VALUES(4,'LPBgrant','LPB: funds given as loans or grants',0.0,100.0,'Poverty','pov');
INSERT INTO "policies" VALUES(5,'FMPLDD','Fraction of credit with private lenders NOT drawn down per y',0.0,90.0,'Poverty','pov');
INSERT INTO "policies" VALUES(6,'TOW','Taxing Owners Wealth',0.0,80.0,'Poverty','pov');
INSERT INTO "policies" VALUES(7,'FPGDC','Cancel debt from public lenders',0.0,100.0,'Poverty','pov');
INSERT INTO "policies" VALUES(8,'Lfrac','Leakage fraction reduction',0.0,100.0,'Poverty','pov');
INSERT INTO "policies" VALUES(9,'SSGDR','Stretch repayment',1.0,5.0,'Poverty','pov');
INSERT INTO "policies" VALUES(10,'XtaxFrac','Extra taxes paid by the super rich',50.0,90.0,'Inequality','ineq');
INSERT INTO "policies" VALUES(11,'StrUP','Strengthen Unions',0.0,3.0,'Inequality','ineq');
INSERT INTO "policies" VALUES(12,'Wreaction','Worker reaction',0.0,3.0,'Inequality','ineq');
INSERT INTO "policies" VALUES(13,'XtaxCom','Introduce a Universal basic dividend',0.0,5.0,'Inequality','ineq');
INSERT INTO "policies" VALUES(14,'ICTR','Increase consumption tax rate',0.0,10.0,'Inequality','ineq');
INSERT INTO "policies" VALUES(15,'IOITR','Increase owner income tax rate',0.0,10.0,'Inequality','ineq');
INSERT INTO "policies" VALUES(16,'IWITR','Increase worker income tax rate',0.0,10.0,'Inequality','ineq');
INSERT INTO "policies" VALUES(17,'Ctax','Introduce a Carbon tax',0.0,100.0,'Inequality','ineq');
INSERT INTO "policies" VALUES(18,'SGRPI','Shift govt spending to investment',0.0,50.0,'Inequality','ineq');
INSERT INTO "policies" VALUES(19,'FEHC','Education to all',0.0,10.0,'Empowerment','emp');
INSERT INTO "policies" VALUES(20,'XtaxRateEmp','Female leadership',0.0,5.0,'Empowerment','emp');
INSERT INTO "policies" VALUES(21,'SGMP','Pensions to all',0.0,10.0,'Empowerment','emp');
INSERT INTO "policies" VALUES(22,'FWRP','Food waste reduction',0.0,90.0,'Food','food');
INSERT INTO "policies" VALUES(23,'FLWR','Regenerative agriculture',0.0,95.0,'Food','food');
INSERT INTO "policies" VALUES(24,'RMDR','Change diets',0.0,95.0,'Food','food');
INSERT INTO "policies" VALUES(25,'RIPLGF','Reduce food imports',0.0,50.0,'Food','food');
INSERT INTO "policies" VALUES(26,'FC','Max forest cutting',0.0,90.0,'Food','food');
INSERT INTO "policies" VALUES(27,'REFOREST','Reforestation',0.0,3.0,'Food','food');
INSERT INTO "policies" VALUES(28,'FTPEE','Energy system efficiency',1.0,2.5,'Energy','ener');
INSERT INTO "policies" VALUES(29,'NEP','Electrify everything',0.0,95.0,'Energy','ener');
INSERT INTO "policies" VALUES(30,'ISPV','Invest in Renewables',50.0,95.0,'Energy','ener');
INSERT INTO "policies" VALUES(31,'CCS','CCS: Carbon capture and storage at source',0.0,80.0,'Energy','ener');
INSERT INTO "policies" VALUES(32,'DAC','Direct air capture',0.0,1.5,'Energy','ener');
CREATE TABLE policy_decisions (
                decision_id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id TEXT NOT NULL,
                round INTEGER NOT NULL,
                region_tag TEXT NOT NULL,
                ministry TEXT NOT NULL,
                pol_id INTEGER NOT NULL,
                value REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, `pol_tag` TEXT, `is_ai` INTEGER,
                FOREIGN KEY (game_id) REFERENCES games(game_id),
                FOREIGN KEY (pol_id) REFERENCES policies(pol_id),
                UNIQUE(game_id, round, region_tag, ministry, pol_id)
            );
CREATE TABLE policy_explanations (
                pol_tag TEXT PRIMARY KEY,
                explanation TEXT NOT NULL,
                FOREIGN KEY (pol_tag) REFERENCES policies(pol_tag)
            );
INSERT INTO "policy_explanations" VALUES('CCS','Percent of fossil use to be equipped with carbon capture and storage (CCS) at source.  This means that you still emit CO2 but it does not get to the atmosphere, where it causes warming,  because you capture it and store it underground.');
INSERT INTO "policy_explanations" VALUES('TOW','0 means no wealth tax,  80 means 80% of accrued owners wealth is taxed away each year,  50: half of it');
INSERT INTO "policy_explanations" VALUES('FPGDC','Cancels a percentage of Govt debt outstanding to public lenders. 0 means nothing is cancelled,  100 all is cancelled,  50 half is cancelled --- in the policy start year');
INSERT INTO "policy_explanations" VALUES('RMDR','Change in diet, esp. a reduction in red meat consumption. 0 means red meat is consumed as before, 50 means 50% is replaced with lab meat, 100 means 100% is replaced with lab meat  i.e. no more red meat is ''produced'' by intensive livestock farming  aka factory farming.');
INSERT INTO "policy_explanations" VALUES('REFOREST','Policy to reforest land, i.e. plant new trees. 0 means no reforestation, 1 means you increase the forest area by 1‰ / yr (that is 1 promille), 3 = you increase the forest area by 3‰ / yr');
INSERT INTO "policy_explanations" VALUES('FTPEE','Annual percentage increase in energy efficiency; 1% per yr is the historical value over the last 40 years. Beware of the power of compound interest!');
INSERT INTO "policy_explanations" VALUES('LPBsplit','0 means all LBP funding goes to consumption (eg child support,  subsidies for food or energy,  etc.)  100 means all goes to public investment like infrastructure,  security,  etc. NOTE This only has an effect if LPB is NOT set to zero');
INSERT INTO "policy_explanations" VALUES('ExPS','Cancels a percentage of Govt debt outstanding to private lenders --- in the policy start year');
INSERT INTO "policy_explanations" VALUES('FMPLDD','Given your credit worthiness  you have an amount you you can borrow from private lenders. Here you choose the fraction of credit you actually draw down each year.');
INSERT INTO "policy_explanations" VALUES('StrUP','In any economy, the national income is shared between owners and workers. This policy changes the share going to workers. 1 multiplies the share with 1%,  2 with 2%,  etc ');
INSERT INTO "policy_explanations" VALUES('Wreaction','In any economy, there is a power struggle between workers and owners about the share of national income each gets. This policy strenghtens the workers negotiation position. 1 by 1%,  2 by 2%,  etc. ');
INSERT INTO "policy_explanations" VALUES('SGMP','To fight poverty in old age  you can introduce pensions for all. The size of the pension is expressed as the percent of the GDP you want to invest. 0 means you invest nothing and leave things as they are. 5 means you invest 5 % of GDP; 10 = 10 % of GDP  money is transferred to workers and paid for by owners');
INSERT INTO "policy_explanations" VALUES('FWRP','Here you decide how much the percentage of ''normal'' waste, which is 30%, is to be reduced. I.e. 100 means  no more waste! 50 means waste is reduced by 50 %,  0 means waste continues as always');
INSERT INTO "policy_explanations" VALUES('ICTR','This policy is an increase in the consumption tax (aka sales tax, value added tax (VAT),  etc. 0 means no increase, 10 means an increase by 10 percentage points, 5 by 5 percentage points; the money raised goes to general govt revenue.');
INSERT INTO "policy_explanations" VALUES('XtaxCom','A universal basic dividend is created when a state taxes common goods  like fishing rights, mining rights, the right to use airwaves  etc. This policy sets this tax as a percent of GDP  i.e.  0 = 0 % of GDP  i.e. nothing; 5 = 5 % of GDP; 3 = 3 % of GDP  money is transferred to general govt tax revenue.');
INSERT INTO "policy_explanations" VALUES('Lfrac','Leakage describes the use of money for illicit purposes: Corruption,  bribery,  etc. The normal leakage is 20%  - so a value of 0 reduction means that those 20% do in fact disappear - a 50 % reduction means 10% disappear and 100% reduction means nothing disappears and everyone in your region is totally honest!');
INSERT INTO "policy_explanations" VALUES('IOITR','This is an increase in the income tax paid by owners. 0 means no increase,  10 means an increase by 10 percentage points, 5 by 5 percentage points; the money raised goes to general govt revenue.');
INSERT INTO "policy_explanations" VALUES('IWITR','This is an increase in the income tax paid by workers. 0 means no increase, 10 means an increase by 10 percentage points, 5 by 5 percentage points; the money raised goes to general govt revenue.');
INSERT INTO "policy_explanations" VALUES('SGRPI','Governments choose how to use their spending: primarily for consumption (eg child support, subsidies for food or energy, etc.) or for public investment (education, health care, infrastructure  etc.) This policy shifts spending from consumption to investment. 0 means no shift, 10= 10% of consumption shifted to investment, 25 = 25 % of consumption shifted to investment, etc');
INSERT INTO "policy_explanations" VALUES('FEHC','The higher the level of education  esp. of women,  in a society,  the lower the birth rate. Thus  education for all lowers the birth rate. By how much? You make an educated guess: 0 means no effect, 10 means a 10% reduction, 5 means a 5% reduction, etc.');
INSERT INTO "policy_explanations" VALUES('XtaxRateEmp','To support women to reach equality costs some money, esp. to close the pay gender gap. How much do you want to spend  as a pct of GDP? 0 means you spend nothing and leave things as they are; 5 means you spend= 5 % of GDP; 3 = 3 % of GDP. Money is transferred to general govt tax revenue');
INSERT INTO "policy_explanations" VALUES('FLWR','Here you decide the percentage of your cropland that is worked regeneratively (low or no tillage,  low or no fertilizers and pesticides  etc.)  50 means 50 % cropland worked is regeneratively, 100 = 100 % of cropland is worked regeneratively, etc. 0 leaves things as they are.');
INSERT INTO "policy_explanations" VALUES('RIPLGF','Reduction in food imports. 0 means no reduction,  10=10% reduction, 50=50% reduction This policy reduces food available from elsewhere but strenghtens local producers');
INSERT INTO "policy_explanations" VALUES('FC','Policy to limit forest cutting. 0 means no limitation on cutting,  10=10% reduction in the maximum amount that can be cut,  50=50% reduction in max cut, etc. all the way to 90 % reduction which is practically a ban on cutting');
INSERT INTO "policy_explanations" VALUES('NEP','Percent of fossil fuel (oil, gas, and coal) *not* used for electricity generation (mobility,  heating,  industrial use  etc.) that you want to electrify.');
INSERT INTO "policy_explanations" VALUES('Ctax','This is the carbon emission tax. 0 means no carbon tax,  25 = 25 $/ton of CO2 emitted  etc.');
INSERT INTO "policy_explanations" VALUES('DAC','Capturing CO2 that is already in the atmosphere and storing it underground   - in GtCO2/yr (Giga tons -  giga is 10^9); In 2020  regional emissions were roughly: USA 5,  Africa  south of Sahara 1,  China 12,  the rest all between 2 and 3 GtCO2/yr. You can capture more than you emit.');
INSERT INTO "policy_explanations" VALUES('XtaxFrac','The percentage of *extra* taxes paid by owners (owners pay 50% of extra taxes even under TLTL)  I.e. 90 means owners pay 90 % of extra taxes,  70 means owners pay 70 % of extra taxes, etc. Extra taxes are those for empowerment and to give women equal pay.');
INSERT INTO "policy_explanations" VALUES('LPBgrant','0 means all LPB funding is given as loans that must be repaid,  100 means all is given as grants that carry no interest and must not be repaid. NOTE This only has an effect if LPB is NOT set to zero');
INSERT INTO "policy_explanations" VALUES('LPB','The percentage of your GDP made available as financing from public bodies (WorldBank,  IMF,  off-balance funding) LPB= Lending from Public Bodies');
INSERT INTO "policy_explanations" VALUES('SSGDR','You can stretch repayment into the future  so that each year you pay less,  but you do have to pay for a longer time. 1 means no stretching - 2 doubles repayment time  - 3 trebles repayment time - and so on');
INSERT INTO "policy_explanations" VALUES('ISPV','Percent of electricity generation from renewable sources (40% is what we managed to achieve in the past)');
CREATE TABLE region_submissions (
                game_id TEXT NOT NULL,
                round_num INTEGER NOT NULL,
                region_tag TEXT NOT NULL,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (game_id, round_num, region_tag),
                FOREIGN KEY (game_id) REFERENCES games(game_id)
            );
CREATE TABLE sessions (
                token         TEXT PRIMARY KEY,
                username      TEXT UNIQUE,
                role          TEXT,
                lang          TEXT    DEFAULT 'en',
                dark          INTEGER DEFAULT 0,
                human_regions TEXT    DEFAULT '',
                setup_done    INTEGER DEFAULT 0,
                game_id       TEXT    DEFAULT '',
                game_token    TEXT    DEFAULT '',
                region        TEXT    DEFAULT '',
                current_round INTEGER DEFAULT 1,
                num_rounds    INTEGER DEFAULT 3,
                submitted     INTEGER DEFAULT 0
            , last_active INTEGER DEFAULT 0);
CREATE INDEX idx_players_username 
            ON players(username)
        ;
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('ai_regions',2612);
INSERT INTO "sqlite_sequence" VALUES('policy_decisions',258849);
INSERT INTO "sqlite_sequence" VALUES('human_regions',408);
COMMIT;