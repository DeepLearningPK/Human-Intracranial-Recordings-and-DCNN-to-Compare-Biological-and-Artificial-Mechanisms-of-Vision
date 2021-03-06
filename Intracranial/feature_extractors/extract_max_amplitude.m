%
% Take all subjects from the Processed/LFP direectory and extract maximal
% LFP value for each (subject, stimulus, probe) triple
%

% load subject list
listing = dir('../../../Data/Intracranial/Processed/LFP/*.mat');

% for each subject
for sfile = listing'

    disp(['Processing ' sfile.name])
    
    % load the data
    load(['../../../Data/Intracranial/Processed/LFP/' sfile.name]);
    
    % output data structure
    maxamp = zeros(length(s.stimseq), length(s.probes.probe_ids));
    
    % for each stimulus
    for stimulus = 1:length(s.stimseq)
    
        % for each probe
        for probe = 1:length(s.probes.probe_ids)
    
            % compute maximum LFP across the whole signal 
            signal = detrend(squeeze(s.data(stimulus, probe, :)));
            baseline = signal(1:205);  % -500 to -400 ms
            poststim = signal(256:665);  % 0 to 800 ms
            baseline_normalized = poststim / std(baseline);
            maxamp(stimulus, probe) = max(abs(baseline_normalized));
            
        end
    end
    
    % store extracted features
    s.data = maxamp;
    save(['../../../Data/Intracranial/Processed/maxamp/' sfile.name], 's');
    
    % clear all subject-specific variables
    clearvars -except listing
    
end
