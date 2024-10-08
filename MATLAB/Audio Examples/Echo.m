classdef (StrictDefaults)Echo < matlab.System
%Echo Add echo effect to audio signal.
%
%   ECHO = audioexample.Echo returns an echo System object, ECHO, that adds
%   echo effect to the audio signal.
%
%   ECHO = audioexample.Echo('Name', Value, ...) returns an echo System
%   object, ECHO, with each specified property name set to the specified
%   value. You can specify additional name-value pair arguments in any
%   order as (Name1,Value1,...,NameN, ValueN).
%
%   Step method syntax:
%      
%   Y = ECHO(X) adds echo effect for the audio input X based on the
%   properties specified in the object ECHO and returns it as audio
%   output Y. Each column of X is treated as individual channel of input.
%
%   System objects may be called directly like a function instead of using
%   the step method. For example, y = step(obj, x) and y = obj(x) are
%   equivalent.
%
%   Echo methods:
%
%   step     - See above for the description of the method
%   reset    - Resets the internal state to initial conditions
%   clone    - Create Echo system object with similar property values
%   isLocked - Locked status (logical)
%   
%   Echo properties:
%   
%   Delay         - Base delay in seconds
%   Gain          - Amplitude gain 
%   FeedbackLevel - Feedback gain 
%   WetDryMix     - Wet to dry signal ratio
%   SampleRate    - Sample rate of the input audio signal
%
%   % Example: Add echo effect to an audio signal.
%
%   fileReader = dsp.AudioFileReader('SamplesPerFrame', 1024,...
%     'PlayCount', 3);
% 
%   player = audioDeviceWriter('SampleRate', fileReader.SampleRate);
% 
%   echoEffect = audioexample.Echo;
% 
%   while ~isDone(fileReader)
%       Input = fileReader();
%       Output = echoEffect(Input);
%       player(Output);
%   end
% 
%   release(fileReader)
%   release(player)

% Copyright 2015-2016 The MathWorks, Inc.
%#codegen
    
    %----------------------------------------------------------------------
    %   Public, tunable properties.
    %----------------------------------------------------------------------
    properties
        %Delay Base delay (s)
        %   Specify the base delay for echo effect as positive scalar
        %   value in seconds. Base delay value must be in the range between
        %   0 and 1 seconds. The default value of this property is 0.5.
        Delay = 0.5
        
        %Gain Gain of delay branch
        %   Specify the gain value as a positive scalar. This value must be
        %   in the range between 0 and 1. The default value of this
        %   property is 0.5.
        Gain = 0.5
        
        %FeedbackLevel Feedback gain
        %   Specify the feedback gain value as a positive scalar. This
        %   value must range from 0 to 0.5. Setting FeedbackLevel to 0
        %   turns off the feedback feature. The default value of this
        %   property is 0.35.
        FeedbackLevel = 0.35
        
        %WetDryMix Wet/dry mix
        %   Specify the wet/dry mix ratio as a positive scalar. This value
        %   ranges from 0 to 1. For example, for a value of 0.6, the ratio
        %   will be 60% wet to 40% dry signal (Wet - Signal that has effect
        %   in it. Dry - Unaffected signal).  The default value of this
        %   property is 0.5.
        WetDryMix = 0.5
    end
    %----------------------------------------------------------------------
    %   Public, non-tunable properties.
    %----------------------------------------------------------------------
    properties (Nontunable)
        %SampleRate Sampling rate of input audio signal
        %   Specify the sampling rate of the audio signal as a positive
        %   scalar value.  The default value of this property is 44100 Hz.
        SampleRate = 44100
    end
    %----------------------------------------------------------------------
    %   Private, non-tunable properties.
    %----------------------------------------------------------------------
    properties (Access = private, Nontunable)        
        %pDataType Data type of input signal. To maintain similar
        %   data type throughout the process, this property is used to type
        %   cast the variables.
        pDataType
    end
    %----------------------------------------------------------------------
    %   Private properties.
    %----------------------------------------------------------------------
    properties (Access = private)        
        %pDelayInSamples Number of samples required to delay the
        %   input signal.
        pDelayInSamples
        
        %pDelay is the object for fractional delay with linear
        %interpolation and feedback.
        pDelay
        
        %pGain Gain property cast into correct data type
        pGain
        
        %pWetDryMix WetDryMix property cast into correct data type
        pWetDryMix
    end
    %----------------------------------------------------------------------
    %   Public methods
    %----------------------------------------------------------------------
    methods
        % Constructor for Echo system object.
        function obj = Echo(varargin)
            
            % Set properties according to name-value pair
            setProperties(obj,nargin,varargin{:});
        end
        %------------------------------------------------------------------
        % These set functions validate the attributes and limits of the
        % properties of this system object.
        function set.Delay(obj,Delay)
            validateattributes(Delay,{'numeric'},{'scalar','real','>=',0,'<=',1},'Echo','Delay')
            obj.Delay = Delay;
        end
        
        function set.Gain(obj,Gain)
            validateattributes(Gain,{'numeric'},{'scalar','real','>=',0,'<=',1},'Echo','Gain')
            obj.Gain = Gain;
        end
        
        function set.WetDryMix(obj,WetDryMix)
            validateattributes(WetDryMix,{'numeric'},{'scalar','real','>=',0,'<=',1},'Echo','WetDryMix');
            obj.WetDryMix = WetDryMix;
        end
        
        function set.FeedbackLevel(obj,FeedbackLevel)
            validateattributes(FeedbackLevel,{'numeric'},{'scalar','real','>=',0,'<=',0.5},'Echo','FeedbackLevel')
            obj.FeedbackLevel = FeedbackLevel;
        end
        
        function set.SampleRate(obj,SampleRate)
            validateattributes(SampleRate,{'numeric'},{'scalar','real','>',0},'Echo','SampleRate')
            obj.SampleRate = SampleRate;
        end
    end
    %----------------------------------------------------------------------
    %   Protected methods
    %----------------------------------------------------------------------
    methods (Access = protected)
        function setupImpl(obj,Input)
            
            % Cache the data type of input
            obj.pDataType = class(Input);
            
            % Create the fractional delay object
            obj.pDelay = audioexample.DelayFilter(...
                'SampleRate',obj.SampleRate,...
                'FeedbackLevel',obj.FeedbackLevel);
                        
            % Set the tunable properties
            processTunedPropertiesImpl(obj)
            
            % Setup the DelayFilter object
            setup(obj.pDelay,obj.pDelayInSamples,Input)
        end
        %------------------------------------------------------------------
        function resetImpl(obj)
            reset(obj.pDelay);
        end
        %------------------------------------------------------------------
        function Output = stepImpl(obj,Input)
            % Invoke the pDelay object for calculating delayed
            % signal.
            Output = obj.pDelay(obj.pDelayInSamples, Input);
            
            % Calculate output by adding wet and dry signal in
            % appropriate ratio.
            mix = obj.pWetDryMix;
            Output = (1-mix)*Input + (mix)*(obj.pGain.*Output);
        end
        %------------------------------------------------------------------
        % When a tunable property changes, this function will be called.
        function processTunedPropertiesImpl(obj)
            % When Delay property changes, we have recalculate
            % pDelayInSamples property. Note that to maintain similar data
            % types throughout the process, cast function is used.
            dType = obj.pDataType;
            obj.pDelayInSamples = cast(obj.Delay*obj.SampleRate,obj.pDataType);
            
            % Set feedback level value of pDelay object when FeedbackLevel
            % value changes.
            obj.pDelay.FeedbackLevel = cast(obj.FeedbackLevel, dType);
            
            % Cast Gain and WetDryMix into correct data type
            obj.pGain = cast(obj.Gain, dType);
            obj.pWetDryMix = cast(obj.WetDryMix, dType);
        end
        %------------------------------------------------------------------
        function validateInputsImpl(~,Input)
            % Validate inputs to the step method at initialization.
            validateattributes(Input,{'single','double'},{'nonempty'},'Echo','Input');
        end
        %------------------------------------------------------------------
        function s = saveObjectImpl(obj)
            s = saveObjectImpl@matlab.System(obj);
            if isLocked(obj)
                s.pDelay = matlab.System.saveObject(obj.pDelay);
                s.pDataType = obj.pDataType;
                s.pDelayInSamples = obj.pDelayInSamples;
                s.pGain = obj.pGain;
                s.pWetDryMix = obj.pWetDryMix;
            end
        end
        %------------------------------------------------------------------
        function loadObjectImpl(obj,s,wasLocked)
            if wasLocked
                obj.pDelay = matlab.System.loadObject(s.pDelay);
                obj.pDataType = s.pDataType;
                obj.pDelayInSamples = s.pDelayInSamples;
                obj.pGain = s.pGain;
                obj.pWetDryMix = s.pWetDryMix;
            end
            loadObjectImpl@matlab.System(obj,s,wasLocked);
        end
        %------------------------------------------------------------------
        function releaseImpl(obj)
            release(obj.pDelay)
        end
        %------------------------------------------------------------------
        % Propagators for MATLAB System block
        function flag = IsOutputComplexImpl(~)
            flag = false;
        end
        
        function flag = getOutputSizeImpl(obj)
            flag = propagatedInputSize(obj, 1);
        end

        function flag = getOutputDataTypeImpl(obj)
            flag = propagatedInputDataType(obj, 1);
        end

        function flag = isOutputFixedSizeImpl(obj)
            flag = propagatedInputFixedSize(obj,1);
        end
     end
end