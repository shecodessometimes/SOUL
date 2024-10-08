classdef (StrictDefaults)Chorus < matlab.System
%Chorus Add chorus effect to audio signal.
%
%   CHORUS = audioexample.Chorus returns a chorus System object, CHORUS,
%   that adds chorus effect to the audio signal.
%
%   CHORUS = audioexample.Chorus('Name', Value, ...) returns a chorus
%   System object, CHORUS, with each specified property name set to the
%   specified value. You can specify additional name-value pair arguments
%   in any order as (Name1,Value1,...,NameN, ValueN).
%
%   Step method syntax:
%      
%   Y = CHORUS(X) adds chorus effect for the audio input X based on
%   the properties specified in the object CHORUS and returns it as audio
%   output Y. Each column of X is treated as individual channel of input.
%
%   System objects may be called directly like a function instead of using
%   the step method. For example, y = step(obj, x) and y = obj(x) are
%   equivalent.
%
%   Chorus methods:
%
%   step     - See above for the description of the method
%   reset    - Resets the internal state to initial conditions
%   clone    - Create Chorus system object with similar property values
%   isLocked - Locked status (logical)
%   
%   Chorus properties:
%   
%   Delay       - Base delay in seconds
%   Depth       - Amplitude of sine wave modulators
%   Rate        - Frequency of sine wave modulators
%   WetDryMix   - Wet to dry signal ratio
%   SampleRate  - Sample rate of the input audio signal   
%
%   % Example: Add chorus effect to an audio signal.
%
%   fileReader = dsp.AudioFileReader('SamplesPerFrame', 1024,...
%     'PlayCount', 3);
% 
%   player = audioDeviceWriter('SampleRate', fileReader.SampleRate);
% 
%   CHORUS = audioexample.Chorus;
% 
%   while ~isDone(fileReader)
%       Input = fileReader();
%       Output = CHORUS(Input);
%       player(Output);
%   end
% 
%   release(fileReader)
%   release(player)

% Copyright 2015-2018 The MathWorks, Inc.
%#codegen
    
    %----------------------------------------------------------------------
    %   Public, tunable properties.
    %----------------------------------------------------------------------
    properties
        %Delay Base delay
        %   Specify the base delay for chorus effect as positive scalar
        %   value in seconds. Base delay value must be in the range between
        %   0 and 0.1 seconds. The default value of this property is 0.02.
        Delay = 0.02
        
        %Depth Amplitude of sine wave
        %   Specify the amplitude of modulating sine wave as a positive
        %   scalar value. Pass this value as a vector of maximum of two
        %   elements for two taps. These sinewaves are added to the base
        %   delay value to make the delay sinusoidally modulating. This
        %   value must range between 0 to 10. The default value of this
        %   property is [0.01 0.03].
        Depth = [0.01 0.03]
        
        %Rate Frequency of sine wave
        %   Specify the frequency of the sine wave as a positive scalar
        %   value in Hz. Pass this value as a vector of maximum of two
        %   elements for two taps. This property controls the chorus rate.
        %   This value must range from 0 to 10 Hz. The default value of
        %   this property is [0.01 0.02].
        Rate = [0.01 0.02]
        
        %WetDryMix Wet/dry mix
        %   Specify the wet/dry mix ratio as a positive scalar. This value
        %   ranges from 0 to 1. For example, for a value of 0.6, the
        %   ratio will be 60% wet to 40% dry signal (Wet - Signal that has
        %   effect in it. Dry - Unaffected signal). The default value of
        %   this property is 0.5.
        WetDryMix = 0.5
    end
    %----------------------------------------------------------------------
    %   Non-tunable properties.
    %----------------------------------------------------------------------
    properties (Nontunable)
        %SampleRate Sampling rate of the audio signal.
        %   Specify the sampling rate of the audio signal as a positive
        %   scalar value in Hz. The default value of this property is 44100
        %   Hz.
        SampleRate = 44100
    end
    %----------------------------------------------------------------------
    %   Private, non-tunable properties.
    %----------------------------------------------------------------------
    properties (Access = private, Nontunable)        
        %pDataType is the data type of input signal. To maintain similar
        %   data type throughout the process, this property is used to type
        %   cast the variables.
        pDataType
    end
    %----------------------------------------------------------------------
    %   Private properties.
    %----------------------------------------------------------------------
    properties (Access = private)
        %pDelayInSamples is the number of samples required to delay the
        %   input signal.
        pDelayInSamples = 0
        
        %pDelay is the object for fractional delay with linear
        %interpolation and feedback.
        pDelay
        
        %pSineWave1 and pSineWave2 are the oscillators for generating sine
        %waves.
        pSineWave1
        pSineWave2
        
        %pWetDryMix WetDryMix cast to correct data type
        pWetDryMix
    end
    %----------------------------------------------------------------------
    %   Public properties.
    %----------------------------------------------------------------------
    methods
        % Constructor for Chorus system object.
        function obj = Chorus(varargin)
            
            % Set properties according to name-value pairs.
            setProperties(obj,nargin,varargin{:});
        end
        %------------------------------------------------------------------
        % These set functions validate the attributes and limits of the
        % properties of this system object.
        function set.Delay(obj,Delay)
            validateattributes(Delay,{'numeric'},{'scalar','real','>=',0,'<=',0.1},'Chorus','Delay');
            obj.Delay = Delay;
        end
        
        function set.Depth(obj,Depth)
            validateattributes(Depth,{'numeric'},{'real','>=',0,'<=',10},'Chorus','Depth');
            if numel(Depth) == 1
                Depth(2) = 0;
            end
            obj.Depth = Depth(1:2);
        end
        
        function set.Rate(obj,Rate)
            validateattributes(Rate,{'numeric'},{'real','>=',0,'<=',10},'Chorus','Rate');
            if numel(Rate) == 1
                Rate(2) = 0;
            end
            obj.Rate = Rate(1:2);
        end
        
        function set.WetDryMix(obj,WetDryMix)
            validateattributes(WetDryMix,{'numeric'},{'scalar','real','>=',0,'<=',1},'Chorus','WetDryMix');
            obj.WetDryMix = WetDryMix;
        end
        
        function set.SampleRate(obj,SampleRate)
            validateattributes(SampleRate,{'numeric'},{'scalar','real','>',0},'Chorus','SampleRate');
            obj.SampleRate = SampleRate;
        end
    end
    %----------------------------------------------------------------------
    %   Protected methods
    %----------------------------------------------------------------------
    methods (Access = protected)
        function setupImpl(obj,Input)
            % Cache the data type of Input signal.
            obj.pDataType = class(Input);
            
            % Create the oscillator objects.
            obj.pSineWave1 = audioOscillator('Frequency', obj.Rate(1),...
                'Amplitude',obj.Depth(1),...
                'SampleRate',obj.SampleRate, ...
                'OutputDataType', obj.pDataType);
            
            obj.pSineWave2 = audioOscillator('Frequency', obj.Rate(2),...
                'Amplitude',obj.Depth(2),...
                'SampleRate',obj.SampleRate, ...
                'OutputDataType', obj.pDataType);
            
            % Create VariableFractionalDelay object for delay.
            obj.pDelay = dsp.VariableFractionalDelay(...
                'MaximumDelay',65000);
            
            % Set the tunable properties
            processTunedPropertiesImpl(obj);
            
            % Setup oscillators and delay
            setup(obj.pSineWave1);
            setup(obj.pSineWave2);
            % Two delay taps per input channel
            setup(obj.pDelay,Input,zeros(1,1,2));
        end
        %------------------------------------------------------------------
        function resetImpl(obj)
            % Resetting the delay and sine wave objects.
            reset(obj.pDelay)
            reset(obj.pSineWave1)
            reset(obj.pSineWave2)
        end
        %------------------------------------------------------------------
        function Output = stepImpl(obj,Input)
            % Create the delay vector. Delay in samples are added to the
            % sine wave here.
            numRows = size(Input,1);
            
            sin1 = obj.pSineWave1;
            sin2 =  obj.pSineWave2;
            sin1.SamplesPerFrame = numRows;
            sin2.SamplesPerFrame = numRows;
            
            DT = obj.pDataType;
            d = obj.pDelayInSamples*ones(numRows,1,DT);
            DelayVector = zeros(numRows,1,2,DT);
            DelayVector(:,:,1) = d + sin1();
            DelayVector(:,:,2) = d + sin2();

            out = obj.pDelay(Input,DelayVector);

            % Calculate output by adding wet and dry signal in appropriate
            % ratio.
            mix = obj.pWetDryMix;
            Output = (1-mix)*Input + (mix)*sum(out,3);
        end
        %------------------------------------------------------------------
        % When tunable property changes, this function will be called.
        function processTunedPropertiesImpl(obj)
            % When Delay property changes, we have recalculate
            % pDelayInSamples property. Note that to maintain similar data
            % types throughout the process, cast function is used.
            obj.pDelayInSamples = cast(obj.Delay*obj.SampleRate, obj.pDataType);
            
            % Set the amplitude properties of sine wave objects when Depth
            % property changes.
            obj.pSineWave1.Amplitude = obj.Depth(1);
            obj.pSineWave2.Amplitude = obj.Depth(2);
            
            % Set the frequency properties of sine wave objects when Rate
            % property changes.
            obj.pSineWave1.Frequency = obj.Rate(1);
            obj.pSineWave2.Frequency = obj.Rate(2);
            
            % Cast WetDryMix to input data type
            obj.pWetDryMix = cast(obj.WetDryMix, obj.pDataType);
        end
        %------------------------------------------------------------------
        function validateInputsImpl(~,Input)
            % Validate inputs to the step method at initialization.
            validateattributes(Input,{'single','double'},{'nonempty'},'Chorus','Input');

        end
        %------------------------------------------------------------------
        function s = saveObjectImpl(obj)
            s = saveObjectImpl@matlab.System(obj);
            if isLocked(obj)
                s.pDelay = matlab.System.saveObject(obj.pDelay);
                s.pSineWave1 = matlab.System.saveObject(obj.pSineWave1);
                s.pSineWave2 = matlab.System.saveObject(obj.pSineWave2);
                s.pDelayInSamples = obj.pDelayInSamples;
                s.pWetDryMix = obj.pWetDryMix;
                s.pDataType = obj.pDataType;
            end
        end
        %------------------------------------------------------------------
        function loadObjectImpl(obj,s,wasLocked)
            if wasLocked
                obj.pDelay = matlab.System.loadObject(s.pDelay);
                obj.pSineWave1 = matlab.System.loadObject(s.pSineWave1);
                obj.pSineWave2 = matlab.System.loadObject(s.pSineWave2);
                obj.pDelayInSamples = s.pDelayInSamples;
                obj.pWetDryMix = s.pWetDryMix;
                obj.pDataType = s.pDataType;
            end
            loadObjectImpl@matlab.System(obj,s,wasLocked);
        end
        %------------------------------------------------------------------
        function releaseImpl(obj)
            % Release the Delay and sine wave objects
            release(obj.pDelay)
            release(obj.pSineWave1)
            release(obj.pSineWave2)
        end
        %------------------------------------------------------------------
        % Propagators for MATLAB System block
        function flag = IsOutputComplexImpl(~)
            flag = false;
        end
        
        function flag = getOutputSizeImpl(obj)
            flag =  propagatedInputSize(obj, 1);
        end

        function flag = getOutputDataTypeImpl(obj)
            flag = propagatedInputDataType(obj, 1);
        end

        function flag = isOutputFixedSizeImpl(obj)
            flag = propagatedInputFixedSize(obj,1);
        end
    end
end