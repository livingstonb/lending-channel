% set working directory to: .../LS1/data-linking/code folder
clear
clc

%% load and clean data
% read in WLOC data from MCR data: sparse 2012 data, good 2013Q1-2020Q1
% separate file for 2011-2012: 2011-2020/2011-2012 MCR Data_File 2
% separate file for 2020: 2020/2020-WA_MCR_Company_Level_Information_Lines_of_Credit_records
% separate file for 2019-2020Q1: 2019-2020/Lines of Credit Information

wloc = readtable("../data/2012-2020_MCR_Company_Info_credit_lines");
% reformat quarterly date
qq = cellfun(@(x) str2double(x(2)), wloc.Qtr(:,1));
wloc.Date = datetime(wloc.FiscalYear-1,12,31) + calquarters(qq);
wloc.FiscalYear = [];
wloc.Qtr = [];
% compute usage by credit line
wloc = renamevars(wloc,{'CreditLimit___','RemainingCreditPeriodEnd___'},{'limit','remaining'});
wloc.usage = wloc.limit - wloc.remaining;
% TO_DO: what to do about negative usage when "remaining" > "limit"

%% clean up WLOC provider names
% lower case
wloc.NameID = lower(wloc.NameOfProvider);
countStart = unique(wloc.NameID);
% for full names with commas, keep only part preceding comma
commaIsIn = contains(wloc.NameID,",");
preComma = extractBefore(wloc.NameID(commaIsIn),",");
wloc.NameID(commaIsIn) = preComma;
% for full names with dashes, keep only part preceding dash
dashIsIn = contains(wloc.NameID,"-");
preDash = extractBefore(wloc.NameID(dashIsIn),"-");
wloc.NameID(dashIsIn) = preDash;

% remove generic words
genericWords = ["advance","plc","company","corporation","fincial","corp","corp.","financial services",...
    "loan","lending","inc.","nsm","llc","loans","group","mortgage","n.a.","na","n a ",".","*","/","&","'",...
    "gestation","gestatiol","warehouse","line","adv1","facility","fac","servicing",...
   "credit union","oloc"]; % "bank",
for gg=1:length(genericWords)
    wloc.NameID = erase(wloc.NameID,genericWords(gg));
end

% take out parantheses and their contents
wloc.NameID = regexprep(wloc.NameID, '\(.*?\)', '');
% remove instances of 4 consecutive digits to get rid of years
wloc.NameID = regexprep(wloc.NameID, '\d{4}', '');
% replace double spaces with single spaces
wloc.NameID = strrep(wloc.NameID,'  ',' ');
% remove floating spaces at start or end of strings
wloc.NameID = strtrim(wloc.NameID);
% Use regexprep to remove leading numbers NOT followed by a "s"
wloc.NameID = regexprep(wloc.NameID, '^\d+(?!s)', '');

% down to 1684 from 2248! 
countEnd = unique(wloc.NameID);
% TO-DO: typos with basic similarity score? Levenshtein distance? 
% https://blogs.mathworks.com/cleve/2017/08/14/levenshtein-edit-distance-between-strings/

%% figure out which WLOC providers to focus on

[wloc.NameG,nameList] = findgroups(wloc.NameID);
Y = splitapply(@sum,wloc.usage,wloc.NameG);
examine = cell2table([nameList num2cell(Y)]);
examine.Properties.VariableNames = {'name','total'};
% add back long form names
examine.longName = cell(height(examine),1);
for nn=1:length(nameList)
    thisName = nameList(nn);
    longNames = wloc.NameOfProvider(strcmp(wloc.NameID,thisName));
    examine.longName(strcmp(examine.name,thisName)) = longNames(1); 
end  
examine = sortrows(examine,'total','descend');
% TO-DO: stopped AT row 52: republic bank, last one was row 51: peoples united bank 
% writetable(examine,"../data/nameStubs.xlsx");


%% match mcr WLOC data to provider bal sheet data
% load manually assembled translation file
wloc = readtable("../../data/mcr/wloc_data.xlsx");
stub_rssdid_matches = readtable("../../temp/bank_name_conversion_cleaned.xlsx");

% loop over selected (cleaned) MCR provider names
wloc = addvars(wloc, NaN(size(wloc,1),1),'NewVariableNames','rssdid');
for gg=1:length(fed.MCR)
    idx = contains(wloc.NameID,fed.MCR{gg});
    % fill based on whether dates cols are filled in, because some will have rssd ID but not dates
    if ~isempty(fed.date1(gg)) && ~isnat(fed.date1(gg))
        % only set name & rssdid for the time window given by the two dates
        idx = idx & (wloc.Date >= fed.date1(gg)) & (wloc.Date <= fed.date2(gg));
    end
    % set name, rssd ID, and ticker from call report data
    wloc.fedName(idx) = fed.FedName(gg);
    wloc.rssdid(idx) = fed.rssdid(gg);
    wloc.stock(idx) = fed.ticker(gg);
    
end

% % match to call reports
% ffiec = readtable("names_bank.xlsx");
% ffiec.Name = lower(ffiec.Name);
% z = cellfun(@(x)find(contains(ffiec.Name,x)),wloc.NameID,'UniformOutput',false);
% no_match = cellfun(@isempty,z);
% z(no_match) = {0};
% wloc.num_matches = cellfun(@numel,z);
% wloc.num_matches(no_match) = 0;

% share of total usage
share_explained = sum(wloc.usage .* (~isnan(wloc.rssdid))) / sum(wloc.usage);
fprintf('Share of total usage assigned to BHCs = %f\n',share_explained)