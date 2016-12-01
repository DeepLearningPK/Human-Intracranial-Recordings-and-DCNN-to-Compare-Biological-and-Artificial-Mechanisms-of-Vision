% variables
er = exist('range') == 1;
ef = exist('freqlimits') == 1;
eb = exist('bandname') == 1;
ec = exist('ncycles') == 1;
if er + ef + eb + ec ~= 4
    disp('Required varibles are not set! Please check that you have specified range, freqlimits, bandname, ncycles. Terminating')
    exit
end

% paramters
indata = 'LFP_bipolar_noscram_artif_brodmann';
outdata = [indata '_' bandname '_responsive_' num2str(range(1))];

% load third party code
addpath('lib')
addpath('lib/spectra')

% load subject list
listing = dir(['../../Data/Intracranial/Processed/' indata '/*.mat']);
listing = listing(range);

% matrix to store the final results
results = zeros(0, 6);

% for each subject
for si = 1:length(listing)
    sfile = listing(si);
    disp(['Processing ' sfile.name])
    
    % load the data
    load(['../../Data/Intracranial/Processed/' indata '/' sfile.name]);
    
    % for each probe
    nprobes = length(s.probes.probe_ids);
    for probe = 1:nprobes
        
        % display progress
        fprintf('\r%d / %d', probe, nprobes);
        
        nstim = length(s.stimseq);
        baseline_band_means = zeros(1, nstim);
        fqsignal_band_means = zeros(1, nstim);
        
        % for each stimulus
        for stimulus = 1:length(s.stimseq)
            
            % take the signal
            signal = detrend(squeeze(s.data(stimulus, probe, :)));
            
            % filter the signal
            for f = [50, 100, 150, 200, 250]
                Wo = f / (512 / 2);
                BW = Wo / 50;
                [b,a] = iirnotch(Wo, BW); 
                signal = filter(b, a, signal);
            end
            
            % wavelet transform
            [power, faxis, times, period] = waveletspectrogram(signal', 512, 'freqlimits', freqlimits, 'ncycles', ncycles);
            
            % take baseline for later normalization
            baseline_at = 205; % baseline from -500 to -100
            baseline = power(:, 1:baseline_at);

            % take only part of the signal
            stimulus_at = 256;
            from = stimulus_at + 26;   % 50 ms
            till = stimulus_at + 128;  % 250 ms
            fqsignal = power(:, from:till);
            
            % store frequency means
            baseline_band_means(stimulus) = mean2(baseline);
            fqsignal_band_means(stimulus) = mean2(fqsignal);
            
        end
        
        % test the null hypothesis that baseline = signal in band means
        p = signrank(baseline_band_means, fqsignal_band_means);
        disp([' ' num2str(mean(baseline_band_means)) ' -> ' num2str(mean(fqsignal_band_means))])
        results = [results; range(1)-1+si, probe, p, 0, mean(baseline_band_means), mean(fqsignal_band_means)];
        
    end 
    
    % clear all subject-specific variables
    clearvars -except range freqlimits ncycles indata outdata listing results
    fprintf('\n');
    
end

% store the results
save(['../../Outcome/Probe responsiveness/' outdata], 'results')
