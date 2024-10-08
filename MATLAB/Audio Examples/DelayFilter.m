classdef (StrictDefaults)DelayFilter < matlab.System 
%DelayFilter Add fractional delay with linear interpolation to input
%
%   DELAY = audioexample.DelayFilter returns DelayFilter System object with
%   default properties.
%
%   DELAY = audioexample.DelayFilter('Property Name','Property Value',...)
%   returns DelayFilter System object with property values specified in
%   name value pairs.
%
%   Step method:
%   
%   Output = DELAY(Delay, Input), returns delayed output based on the
%   input signal and delay value specified. Delay can either be a scalar or
%   vector of length of Input.
%   
% See also: audioexample.Echo, audioexample.Flanger

%   Copyright 2015-2022 The MathWorks, Inc.

%#codegen
    
    %----------------------------------------------------------------------
    % Public, tunable properties
    %----------------------------------------------------------------------
    properties
        %FeedbackLevel Feedback gain
        %   Specify the feedback gain value as a positive scalar. Delay
        %   effects like echo and flanger sound more natural and pronounced
        %   with feedback. Setting FeedbackLevel to 0 disables any
        %   feedback.
        FeedbackLevel = 0
    end
    %----------------------------------------------------------------------
    % Public, non-tunable properties
    %----------------------------------------------------------------------
    properties
        %SampleRate Sampling rate of input audio signal
        %   Specify the sampling rate of the audio signal as a positive
        %   scalar value.  The default value of this property is 44100 Hz.
        SampleRate = 44100
    end
    %----------------------------------------------------------------------
    % Private, non-tunable properties
    %----------------------------------------------------------------------
    properties (Access = private, Nontunable)
        % pDataType property saves the data type of the input data. The
        % purpose of this property is to maintain uniform data type
        % throughout the process.
        pDataType
        
        pNumChannels
    end
    %----------------------------------------------------------------------
    % Private
    %----------------------------------------------------------------------
    properties (Access = private)
        % NumChannels specifies the number of channel in input data. This
        % system object supports multichannel delaying. For multichannel,
        % we must maintain separate delay lines for each channel. This
        % property cannot be changed without calling release method.
        NumChannels

        % Delay line is basically a circular buffer. So, we need write
        % index to keep track of our writing pointer.
        WriteIndex
        
        % ReadIndex is for keeping track of the reading pointer.
        ReadIndex 
        
        % Delay line is the place where our data is stored and accessed
        % sample by sample based on the given delay information.
        DelayLine 
        
        % Feedback has to be done sample by sample. This state vector
        % holds the last set of delayed output samples which in turn
        % becomes the input for the first sample of next frame.
        FeedbackValue
    end
    %----------------------------------------------------------------------
    % Private constant
    %----------------------------------------------------------------------
    properties (Constant, Access = private)
        MaxSampleRate = 192000;
    end
    %----------------------------------------------------------------------
    % Public methods
    %----------------------------------------------------------------------
    methods
        %------------------------------------------------------------------
        % Constructor for the DelayFilter system object.
        function obj = DelayFilter(varargin)
            
            % Setting properties based on name-value pairs.
            setProperties(obj,nargin,varargin{:});
            
            obj.NumChannels = -1;
        end
        %------------------------------------------------------------------
        % The following set functions validate the properties for their
        % class and range. 
        function set.SampleRate(obj,SampleRate)
            validateattributes(SampleRate,{'numeric'},{'scalar','real','>=',0},'DelayFilter','SampleRate');
            obj.SampleRate = SampleRate;
        end
        
        function set.FeedbackLevel(obj,FeedbackLevel)
            validateattributes(FeedbackLevel,{'numeric'},{'scalar','real','>=',0,'<=',1},'DelayFilter','FeedbackLevel');
            obj.FeedbackLevel = FeedbackLevel;
        end
    end
    %----------------------------------------------------------------------
    % Protected methods
    %----------------------------------------------------------------------
    methods (Access = protected)
        %------------------------------------------------------------------
        % Setup function.
        function setupImpl(obj,~,Input)
            
            % Determining the data type of the input signal. This data type
            % will be maintained all throughout the process.
            obj.pDataType = class(Input);
            
            % Number of channels in the input signal.
            obj.NumChannels = size(Input,2);
            
            obj.pNumChannels = size(Input,2);
        end
        
        %------------------------------------------------------------------
        % Reset function.
        function resetImpl(obj)
            % Creating the delay line and casting it to the Input signal
            % data type.
            obj.DelayLine  = cast(zeros(obj.MaxSampleRate*obj.pNumChannels,1),obj.pDataType);
            
            % Creating the write index and casting it to Input signal data
            % type.
            obj.WriteIndex = cast(0,obj.pDataType);
            
            % Creating the read index and casting it to Input signal data
            % type.
            obj.ReadIndex = cast(0,obj.pDataType);
            
            % Creating FeedbackValue vector and casting it to Input signal
            % data type.
            obj.FeedbackValue = cast(zeros(1,obj.pNumChannels),obj.pDataType);
        end
        %------------------------------------------------------------------
        % Step function.
        function output = stepImpl(obj, delayVector, input)
            % Branching according to the coder target. When
            % called from MATLAB, the MEX file will be used.
            if isempty(coder.target)
                DT = class(input);
                delayCast = cast(delayVector,DT);
                delayLine = cast(obj.DelayLine,DT);
                writeIdx = cast(obj.WriteIndex,DT);
                readIdx = cast(obj.ReadIndex,DT);
                feedbackValue = cast(obj.FeedbackValue,DT);
                feedbackLevel = cast(obj.FeedbackLevel,DT);
                sampleRate = cast(obj.SampleRate,DT);
                maxRate = cast(obj.MaxSampleRate,DT);
                [output, obj.WriteIndex, obj.ReadIndex] = audio_DelayFilter( ...
                            input, delayCast, delayLine, writeIdx, readIdx, ...
                            feedbackValue, feedbackLevel, sampleRate, maxRate);
                obj.FeedbackValue = output(end,:);
            else
            % When the coder target isn't MATLAB, this part of branch will
            % be used for code generation.
                InNumRows = size(input,1);
                %% Initialize.
                output = zeros(size(input,1),obj.pNumChannels,'like',input);
                upperBound = 1;
                lowerBound = obj.MaxSampleRate;
                offset = obj.WriteIndex;

                if ~isscalar(delayVector)
                    % obj is a vector.
                    % For every channel.
                    for j = 1:obj.NumChannels
                        obj.WriteIndex = upperBound + offset;
                        obj.ReadIndex = upperBound + offset;
                        
                        % For every sample.
                        for i = 1:InNumRows
                            %% Write into delay line.
                            obj.DelayLine(obj.WriteIndex) = input(i,j)+(obj.FeedbackLevel)*obj.FeedbackValue(1,j);
                            
                            %% Read from delay line.
                            if delayVector(i) > 0
                                intOffset = floor(delayVector(i));
                                floatOffset = delayVector(i) - intOffset;
                            else
                                intOffset = 0;
                                floatOffset = 0;
                            end
                            obj.ReadIndex = obj.ReadIndex - intOffset;
                            
                            if(obj.ReadIndex >= upperBound)
                                % One situation where no we don't need to wrap ReadIndex.
                                if(obj.ReadIndex > upperBound)
                                    output(i,j) = (floatOffset)*(obj.DelayLine(obj.ReadIndex-1))+(1-floatOffset)*(obj.DelayLine(obj.ReadIndex));
                                    obj.FeedbackValue(:,j) = output(i,j);
                                else
                                    output(i,j) = (floatOffset)*(obj.DelayLine(lowerBound))+(1-floatOffset)*(obj.DelayLine(obj.ReadIndex));
                                    obj.FeedbackValue(:,j) = output(i,j);
                                end
                                obj.ReadIndex = obj.ReadIndex + intOffset;
                            else
                                % Another situation where we need to wrap ReadIndex.
                                newOffset1 = abs(obj.ReadIndex - (upperBound));
                                obj.ReadIndex = upperBound;
                                obj.ReadIndex = obj.ReadIndex + intOffset - newOffset1;
                                newOffset1 = lowerBound - newOffset1;
                                newOffset2 = newOffset1 - 1;
                                if (newOffset2 <= 0)
                                    newOffset2 = lowerBound;
                                end
                                output(i,j) = (floatOffset)*(obj.DelayLine(newOffset2))+(1-floatOffset)*(obj.DelayLine(newOffset1));
                                obj.FeedbackValue(:,j) = output(i,j);
                            end
                            
                            %% Work with index variables for the next iteration.
                            if(obj.WriteIndex < lowerBound)
                                obj.WriteIndex = obj.WriteIndex+1;
                            else
                                obj.WriteIndex = upperBound;
                            end
                            if(obj.ReadIndex < lowerBound)
                                obj.ReadIndex = obj.ReadIndex+1;
                            else
                                obj.ReadIndex = upperBound;
                            end
                        end
                        upperBound = lowerBound+1;
                        lowerBound = lowerBound+obj.MaxSampleRate;
                    end
                    
                    %% Update DelayLine status, write and read indices.
                    if(obj.NumChannels>1)
                        obj.WriteIndex = (obj.WriteIndex-(upperBound-obj.MaxSampleRate));
                        obj.ReadIndex = (obj.ReadIndex-(upperBound-obj.MaxSampleRate));
                    else
                        obj.WriteIndex = obj.WriteIndex-1;
                        obj.ReadIndex = obj.ReadIndex-1;
                    end
                else
                    % For every channel.
                    for j = 1:obj.NumChannels
                        
                        obj.WriteIndex = upperBound + offset;
                        obj.ReadIndex = upperBound + offset;
                        
                        % For every sample.
                        for i = 1:InNumRows
                            %% Write into delay line.
                            obj.DelayLine(obj.WriteIndex) = input(i,j)+(obj.FeedbackLevel)*obj.FeedbackValue(1,j);
                            
                            if delayVector(1) > 0
                                intOffset = floor(delayVector(1));
                                floatOffset = delayVector(1) - intOffset;
                            else
                                intOffset = 0;
                                floatOffset = 0;
                            end
                            
                            obj.ReadIndex = obj.ReadIndex - intOffset;
                            
                            if(obj.ReadIndex >= upperBound)
                                % One situation where no we don't need to wrap ReadIndex.
                                if(obj.ReadIndex > upperBound)
                                    output(i,j) = (floatOffset)*(obj.DelayLine(obj.ReadIndex-1))+(1-floatOffset)*(obj.DelayLine(obj.ReadIndex));
                                    obj.FeedbackValue(:,j) = output(i,j);
                                else
                                    output(i,j) = (floatOffset)*(obj.DelayLine(lowerBound))+(1-floatOffset)*(obj.DelayLine(obj.ReadIndex));
                                    obj.FeedbackValue(:,j) = output(i,j);
                                end
                                obj.ReadIndex = obj.ReadIndex + intOffset;
                            else
                                % Another situation where we need to wrap ReadIndex.
                                newOffset1 = abs(obj.ReadIndex - (upperBound));
                                obj.ReadIndex = upperBound;
                                obj.ReadIndex = obj.ReadIndex + intOffset - newOffset1;
                                
                                newOffset1 = lowerBound - newOffset1;
                                newOffset2 = newOffset1 - 1;
                                if (newOffset2 <= 0)
                                    newOffset2 = lowerBound;
                                end
                                
                                output(i,j) = (floatOffset)*(obj.DelayLine(newOffset2))+(1-floatOffset)*(obj.DelayLine(newOffset1));
                                obj.FeedbackValue(:,j) = output(i,j);
                            end
                            
                            %% Work with index variables for the next iteration.
                            if(obj.WriteIndex < lowerBound)
                                obj.WriteIndex = obj.WriteIndex+1;
                            else
                                obj.WriteIndex = upperBound;
                            end
                            if(obj.ReadIndex < lowerBound)
                                obj.ReadIndex = obj.ReadIndex+1;
                            else
                                obj.ReadIndex = upperBound;
                            end
                        end
                        upperBound = lowerBound+1;
                        lowerBound = lowerBound+obj.MaxSampleRate;
                    end
                    
                    %% Update DelayLine status, write and read indices.
                    if(obj.NumChannels>1)
                        obj.WriteIndex = (obj.WriteIndex-(upperBound-obj.MaxSampleRate));
                        obj.ReadIndex = (obj.ReadIndex-(upperBound-obj.MaxSampleRate));
                    else
                        obj.WriteIndex = obj.WriteIndex-1;
                        obj.ReadIndex = obj.ReadIndex-1;
                    end
                end
            end
        end
        
        %------------------------------------------------------------------
        function s = saveObjectImpl(obj)
            % Default implementation saves all public properties
            s = saveObjectImpl@matlab.System(obj);
            if isLocked(obj)
                s.pDataType = obj.pDataType;
                s.pNumChannels = obj.pNumChannels;
                s.NumChannels = obj.NumChannels;
                s.WriteIndex = obj.WriteIndex;
                s.ReadIndex = obj.ReadIndex;
                s.DelayLine = obj.DelayLine;
                s.FeedbackValue = obj.FeedbackValue;
            end
        end
        %------------------------------------------------------------------
        function loadObjectImpl(obj, s, wasLocked)
            % Re-load state if saved version was locked
            if wasLocked
                obj.pDataType = s.pDataType;
                obj.pNumChannels = s.pNumChannels;
                obj.NumChannels = s.NumChannels;
                obj.WriteIndex = s.WriteIndex;
                obj.ReadIndex = s.ReadIndex;
                obj.DelayLine = s.DelayLine;
                obj.FeedbackValue = s.FeedbackValue;
            end
            % Call base class method
            loadObjectImpl@matlab.System(obj, s, wasLocked);
        end

        function validateInputsImpl(obj,~,input)
            validateattributes(input,{'single','double'},{'nonempty'},'Echo','Input');
            
            coder.internal.errorIf(obj.NumChannels ~= -1 && size(input,2) ~= obj.NumChannels, ...
                                                 ['dsp:system',':Shared:numChannels']);
        end
        %------------------------------------------------------------------
        % propagators -- copied from DynamicRangeBase.
        function varargout = IsOutputComplexImpl(~)
            varargout{1} = false;
        end
        
        % Getting the output size. It depends on input size. Index is 2
        % because Input argument is the 3rd argument in the step method.
        function varargout = getOutputSizeImpl(effect)
            outputSize = propagatedInputSize(effect, 2);
            varargout{1} = outputSize;
        end
        
        % Getting the data type. 
        function varargout = getOutputDataTypeImpl(effect)
            outputDT = propagatedInputDataType(effect, 2);
            varargout{1} = outputDT;
        end
        
        % Setting input to accept var size
        function flag = isInputSizeMutableImpl(~, ~)
            flag = true;
        end
        
        % Checking if the output is fixed/var size. 
        function flag = isOutputFixedSizeImpl(effect)
            isFixedSize = propagatedInputFixedSize(effect,2);
            flag{1} = isFixedSize;
        end
    end
end
