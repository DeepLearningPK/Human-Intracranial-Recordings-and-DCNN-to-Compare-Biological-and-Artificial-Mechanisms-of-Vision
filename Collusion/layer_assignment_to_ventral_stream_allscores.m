%
% Compute stats of probe to layer assignments
%   

addpath('../Intracranial/lib/mni2name')
addpath('../Intracranial/lib/nifti')


%% Parameters
mapperset = 'rsa_euclidean_meangamma_bipolar_noscram_artif_responsive_brodmann.kendall';
featureset = 'meangamma_bipolar_noscram_artif_responsive';
atlas = 'brodmann';
talareich_level = 5;
nlayers = 8;

% load atlas
if strcmp(atlas, 'initial')
    talareich_level = 5;
    %areas_of_interest = {'brodmann area 17', 'brodmann area 18', 'brodmann area 19', ...
    %                     'brodmann area 37', 'brodmann area 20', 'brodmann area 38', ...
    %                     'brodmann area 28', 'brodmann area 27', 'brodmann area 35'};
    areas_of_interest = {'brodmann area 17', 'brodmann area 18', 'brodmann area 19', ...
                         'brodmann area 37', 'brodmann area 20'};
elseif strcmp(atlas, 'brodmann')
    db = load_nii('lib/mni2name/brodmann.nii');
    areas_of_interest = strtrim(cellstr(num2str(unique(db.img))));
    %areas_of_interest = {'17', '18', '19', '37', '20', '38', '28', '27', '35'};
    %areas_of_interest = {'17', '18', '19', '37', '20'};
elseif strcmp(atlas, 'aicha')
    db = load_nii('lib/mni2name/aicha.nii');
    labels = load('lib/mni2name/aicha.labels.mat');
    areas_of_interest = {}; % TODO
end


%% List of subject for whom we have the mapping
listing = dir(['../../Data/Intracranial/Probe_to_Layer_Maps/' mapperset '/*.txt']);


%% Compute stats
area_id_map = containers.Map();
area_id_map_reverse = {};
stats = zeros(length(areas_of_interest), nlayers);
counts = zeros(length(areas_of_interest), nlayers);
signf_counts = zeros(1, length(areas_of_interest));
total_counts = zeros(1, length(areas_of_interest));

for i = 1:length(areas_of_interest)
    area = areas_of_interest{i};
    area_id_map(area) = i;
    area_id_map_reverse{i} = area;
end

% for each subject
for fid = 1:length(listing)
    [pathstr, name, ext] = fileparts(listing(fid).name);
    subject = name;
    
    % display progress
    disp(['Processing ' num2str(fid) '/' num2str(length(listing)) ': ' subject '...'])
    
    % load the data
    load(['../../Data/Intracranial/Processed/' featureset '/' subject '.mat'])
    
    % use atlas to map probes to areas
    s.probes.mni(isnan(s.probes.mni)) = 0;
    if strcmp(atlas, 'initial')
        [~, areas] = mni2name(s.probes.mni);
        nareas = size(areas, 1);
    elseif strcmp(atlas, 'brodmann')
        [~, areas] = mni2name_brodmann(s.probes.mni, db);
        nareas = length(areas);
    elseif strcmp(atlas, 'aicha')
        [~, areas] = mni2name_aicha(s.probes.mni, db);
        nareas = length(areas);
    end
    
    % load the mapping
    probe_to_layer_map = load(['../../Data/Intracranial/Probe_to_Layer_Maps/' mapperset '/' listing(fid).name]);
    
    % compute stats
    [maxv, maxi] = max(probe_to_layer_map');
    for i = 1:nareas
        
        % pick contrainer key depending on the atlas in use
        if strcmp(atlas, 'initial')
            key = areas{i, talareich_level};
        elseif strcmp(atlas, 'brodmann')
            key = num2str(areas{i});
        end
        
        % keep only areas of interest
        if ~isKey(area_id_map, key)
            continue
        end
        
        % key area id
        area_id = area_id_map(key);
        
        % update counters
        stats(area_id, :) = stats(area_id, :) + (probe_to_layer_map(i, 1:nlayers) .^ 2); 
        %stats(area_id, :) = stats(area_id, :) + (probe_to_layer_map(i, 1:nlayers)); 
        counts(area_id, :) = counts(area_id, :) + (probe_to_layer_map(i, 1:nlayers) > 0);
        signf_counts(area_id) = signf_counts(area_id) + (sum(probe_to_layer_map(i, 1:nlayers)) > 0);
        total_counts(area_id) = total_counts(area_id) + 1;

    end
    
    % clear workspace
    clearvars -except listing talareich_level featureset area_id_map area_id_map_reverse ...
                      stats areas_of_interest mapperset atlas db labels nlayers signf_counts ...
                      total_counts counts
    
end

%% variance explained normalized by the number of probes in the area
varexp = (stats * 100) ./ repmat(signf_counts', 1, nlayers);

%% What to plot
toplot = varexp;
%toplot = stats ./ (269);
%toplot = stats ./ repmat(signf_counts', 1, nlayers) ./ nlayers;

%% Plot heatmap
imagesc(toplot(:, 1:nlayers));
set(gca, 'XTick', 1:nlayers, 'YTick', 1:length(area_id_map_reverse), 'YTickLabel', area_id_map_reverse)
%set(gca, 'Clim', [0.03 0.05])
xlabel('Layer')
set(gca,'Position',[0.35 0.05 0.4 0.9])

% total counts
for i = 1:length(signf_counts)
    text(nlayers + 0.7, i, [num2str(signf_counts(i)) ' / ' num2str(total_counts(i))])
end

% numbers on top of imagesc
strings = toplot(:, 1:nlayers);
textStrings = num2str(strings(:), '%2.2f');
textStrings = strtrim(cellstr(textStrings));
[x,y] = meshgrid(1:nlayers, 1:size(toplot, 1));
hStrings = text(x(:), y(:), textStrings(:), 'HorizontalAlignment', 'center');
%midValue = mean(get(gca,'CLim'));
%textColors = repmat(counts(:) > midValue,1,3);
%set(hStrings,{'Color'},num2cell(textColors,2));

% colorbar
pos=get(gca,'pos');
colorbar('position',[pos(1)+pos(3)+0.1 pos(2) 0.03 pos(4)]);




