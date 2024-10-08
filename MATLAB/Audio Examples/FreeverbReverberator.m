classdef (StrictDefaults)FreeverbReverberator < matlab.System
%FreeverbReverberator Add reverberation to audio samples using freeverb
%                     algorithm
%   FR = audioexample.FreeverbReverberator returns an audio reverberator
%   that uses the freeverb algorithm to add reverberation effect to each
%   channel of input signal.
%
%   FR = audioexample.FreeverbReverberator('PropertyName', PropertyValue,
%   ...) returns a Freeverb reverberator System object, FR, with each
%   specified property set to the specified value.
%
%   Step method syntax:
%
%   Y = step(FR, X) adds reverberation effect to each channel of the input
%   X, based on the properties set in the object FR.
%
%   System objects may be called directly like a function instead of using
%   the step method. For example, y = step(obj, x) and y = obj(x) are
%   equivalent.
%
%   FreeverbReverberator methods:
%
%   step     - See above description for use of this method
%   release  - Allow property value and input characteristics changes
%   clone    - Create Freeverb reverberator System object with same 
%              property values
%   isLocked - Locked status (logical)
%   reset    - Reset the internal states to initial conditions
%
%   FreeverbReverberator properties:
%
%   RoomSize           - Feedback factor for comb section (reflectivity)
%   StereoWidth        - Stereo width of output audio
%   WetDryMix          - Mix of input audio with output audio
%   Balance            - Left-right channel balance of output
%   Volume             - Volume level of output
%   StereoSpread       - Additional delay for right audio channel
%   CombDelayLength    - Length of delay line of comb filter
%   AllpassDelayLength - Length of delay line of allpass filter
%   CombDamping        - Damping used in lowpass filter of comb section
%
%   This System object FreeverbReverberator is only in support of
%   audioFreeverbReverberationExample. It may change in a future release.

%   Copyright 2014-2019 The MathWorks, Inc.
%#codegen
%#ok<*EMCA>
    properties 
        RoomSize = 0.6032;
        StereoWidth = 1;
        WetDryMix = 0.5;
        Balance = 0.5;
        Volume = 1;
    end
    
    properties(Nontunable)
        StereoSpread = 23;
        CombDelayLength = [1116, 1188, 1277, 1356, 1422, 1491, 1557, 1617];
        AllpassDelayLength = [556, 441, 341, 225];
        CombDamping = 0.25;
    end
    
    properties(Access = private)
        pDryZeroPadded
        pWetZeroPadded
    end
    
    properties (Access = private, Nontunable)
        pAllpassL1
        pAllpassL2
        pAllpassL3
        pAllpassL4
        pAllpassR1
        pAllpassR2
        pAllpassR3
        pAllpassR4
        pCombDelay
        pLowpass
        pSamplesPerFrame
        pMinorFrameSize
        pNumMinorFrames
    end
    %----------------------------------------------------------------------
    % Public methods
    %----------------------------------------------------------------------
    methods
        function obj = FreeverbReverberator(varargin)
            % Constructor
            setProperties(obj, nargin, varargin{:});
        end
        %------------------------------------------------------------------
        function set.RoomSize(obj, value)
            validateattributes(value, {'numeric'}, ...
                {'nonnegative', 'real', 'scalar', '<=', 1},...
                '','RoomSize'); 
            obj.RoomSize = value;
        end
        %------------------------------------------------------------------
        function set.StereoWidth(obj, value)
            validateattributes(value, {'numeric'}, ...
                {'nonnegative', 'real', 'scalar', '<=', 1},...
                '','StereoWidth'); 
            obj.StereoWidth = value;
        end
        %------------------------------------------------------------------
        function set.WetDryMix(obj, value)
            validateattributes(value, {'numeric'}, ...
                {'nonnegative', 'real', 'scalar', '<=', 1},...
                '','WetDryMix'); 
            obj.WetDryMix = value;
        end
        %------------------------------------------------------------------
        function set.Balance(obj, value)
            validateattributes(value, {'numeric'}, ...
                {'nonnegative', 'real', 'scalar', '<=', 1},...
                '','Balance'); 
            obj.Balance = value;
        end
        %------------------------------------------------------------------
        function set.Volume(obj, value)
            validateattributes(value, {'numeric'}, ...
                {'nonnegative', 'real', 'scalar', '<=', 1},...
                '','Volume'); 
            obj.Volume = value;
        end
        %------------------------------------------------------------------
        function set.StereoSpread(obj, value)
            validateattributes(value, {'numeric'}, ...
                {'integer', 'scalar'},...
                '','StereoSpread'); 
            obj.StereoSpread = value;
        end
        %------------------------------------------------------------------
        function set.CombDelayLength(obj, value)
            validateattributes(value, {'numeric'}, ...
                {'nonnegative', 'integer', 'row', '>=', 128, 'numel', 8},...
                '','CombDelayLength'); 
            obj.CombDelayLength = value;
        end
        %------------------------------------------------------------------
        function set.AllpassDelayLength(obj, value)
            validateattributes(value, {'numeric'}, ...
                {'nonnegative', 'integer', 'row', '>=', 128, 'numel', 4},...
                '','AllpassDelayLength'); 
            obj.AllpassDelayLength = value;
        end
        %------------------------------------------------------------------
        function set.CombDamping(obj, value)
            validateattributes(value, {'numeric'}, ...
                {'real', 'scalar', 'finite'},...
                '','CombDamping'); 
            obj.CombDamping = value;
        end
    end
    %----------------------------------------------------------------------
    % Protected methods
    %----------------------------------------------------------------------
    methods (Access = protected)
        function validateInputsImpl(~, u)
            validateattributes(u, {'numeric'}, {'size',[NaN,2]}, ...
                               '', 'input'); 
        end
        %------------------------------------------------------------------
        function setupImpl(obj,dry)
            % Set up comb section
            obj.pCombDelay = dsp.Delay([obj.CombDelayLength obj.CombDelayLength+obj.StereoSpread ]);
            obj.pLowpass = dsp.IIRFilter('Numerator',1-obj.CombDamping, 'Denominator', [1,-obj.CombDamping]);
            
            % Set up allpass section
            allpassFeedback = 0.5;
            APcoeffsL1 = [1, zeros(1, obj.AllpassDelayLength(1)-1), -allpassFeedback];
            APcoeffsL2 = [1, zeros(1, obj.AllpassDelayLength(2)-1), -allpassFeedback];
            APcoeffsL3 = [1, zeros(1, obj.AllpassDelayLength(3)-1), -allpassFeedback];
            APcoeffsL4 = [1, zeros(1, obj.AllpassDelayLength(4)-1), -allpassFeedback];
            APcoeffsR1 = [1, zeros(1, obj.AllpassDelayLength(1)+obj.StereoSpread-1), -allpassFeedback];
            APcoeffsR2 = [1, zeros(1, obj.AllpassDelayLength(2)+obj.StereoSpread-1), -allpassFeedback];
            APcoeffsR3 = [1, zeros(1, obj.AllpassDelayLength(3)+obj.StereoSpread-1), -allpassFeedback];
            APcoeffsR4 = [1, zeros(1, obj.AllpassDelayLength(4)+obj.StereoSpread-1), -allpassFeedback];
            
            obj.pAllpassL1 = dsp.IIRFilter('Numerator', fliplr(APcoeffsL1), ...
                                           'Denominator', APcoeffsL1);
            obj.pAllpassL2 = dsp.IIRFilter('Numerator', fliplr(APcoeffsL2), ...
                                           'Denominator', APcoeffsL2);
            obj.pAllpassL3 = dsp.IIRFilter('Numerator', fliplr(APcoeffsL3), ...
                                           'Denominator', APcoeffsL3);
            obj.pAllpassL4 = dsp.IIRFilter('Numerator', fliplr(APcoeffsL4), ...
                                           'Denominator', APcoeffsL4);
            obj.pAllpassR1 = dsp.IIRFilter('Numerator', fliplr(APcoeffsR1), ...
                                           'Denominator', APcoeffsR1);
            obj.pAllpassR2 = dsp.IIRFilter('Numerator', fliplr(APcoeffsR2), ...
                                           'Denominator', APcoeffsR2);
            obj.pAllpassR3 = dsp.IIRFilter('Numerator', fliplr(APcoeffsR3), ...
                                           'Denominator', APcoeffsR3);
            obj.pAllpassR4 = dsp.IIRFilter('Numerator', fliplr(APcoeffsR4), ...
                                           'Denominator', APcoeffsR4);
            
            % We divide input into chunks of 128 samples for processing, so
            % the frame is never bigger than any delay used in Freeverb
            obj.pSamplesPerFrame = size(dry,1);
            if obj.pSamplesPerFrame>128
                obj.pMinorFrameSize = 128;
                obj.pNumMinorFrames = ceil(obj.pSamplesPerFrame/obj.pMinorFrameSize);
                obj.pDryZeroPadded = zeros(obj.pMinorFrameSize*obj.pNumMinorFrames, size(dry,2),'like',dry);
                obj.pWetZeroPadded = obj.pDryZeroPadded;
            else
                obj.pMinorFrameSize = obj.pSamplesPerFrame;
            end
        end
        %------------------------------------------------------------------
        function resetImpl(obj)
            reset(obj.pAllpassL1);
            reset(obj.pAllpassL2);
            reset(obj.pAllpassL3);
            reset(obj.pAllpassL4);
            reset(obj.pAllpassR1);
            reset(obj.pAllpassR2);
            reset(obj.pAllpassR3);
            reset(obj.pAllpassR4);
            reset(obj.pCombDelay);
            reset(obj.pLowpass);
        end
        %------------------------------------------------------------------
        function releaseImpl(obj)
            release(obj.pAllpassL1);
            release(obj.pAllpassL2);
            release(obj.pAllpassL3);
            release(obj.pAllpassL4);
            release(obj.pAllpassR1);
            release(obj.pAllpassR2);
            release(obj.pAllpassR3);
            release(obj.pAllpassR4);
            release(obj.pCombDelay);
            release(obj.pLowpass);
        end
        %------------------------------------------------------------------
        function audioOut = stepImpl(obj,audioIn)
            % Freeverb algorithm:
            if obj.pSamplesPerFrame<=128
                combOut = parallelComb(obj, audioIn);
                wet = seriesAllPass(obj, combOut);
                audioOut = mixer(obj, audioIn, wet);
            else
                % We divide input into chunks of 128 samples for
                % processing, so the frame is never bigger than any delay
                % used in Freeverb

                obj.pDryZeroPadded(1:obj.pSamplesPerFrame,:) = audioIn;
                for idx = 0:obj.pNumMinorFrames-1
                    combOut = parallelComb(obj, ...
                        obj.pDryZeroPadded(idx*obj.pMinorFrameSize+1 : (idx+1)*obj.pMinorFrameSize, :));
                    obj.pWetZeroPadded(idx*obj.pMinorFrameSize+1 : (idx+1)*obj.pMinorFrameSize, :) = ...
                        seriesAllPass(obj, combOut);
                end
                wet = obj.pWetZeroPadded(1:obj.pSamplesPerFrame,:);
                audioOut = mixer(obj, audioIn, wet);
            end
        end
        %------------------------------------------------------------------
        function out = parallelComb(obj, drySignal)
            in = zeros(obj.pMinorFrameSize,1,'like',drySignal);
            in(1:end) = sum(drySignal,2);
            t = repmat(0.015*in, 1,16);
            scaling = log2(7*obj.RoomSize+1)/log2(8);
            o = output(obj.pCombDelay, t);
            update(obj.pCombDelay, t + scaling*obj.pLowpass(o));
            out = [ sum(o(:,1:8),2) sum(o(:,9:16),2) ];
        end
        %------------------------------------------------------------------
        function out = seriesAllPass(obj, in)
            out = zeros(size(in,1),2, 'like', in);
            out(:,1) = obj.pAllpassL4(obj.pAllpassL3(...
                obj.pAllpassL2(obj.pAllpassL1(in(:,1)))));
            out(:,2) = obj.pAllpassR4(obj.pAllpassR3(...
                obj.pAllpassR2(obj.pAllpassR1(in(:,2)))));
        end
        %------------------------------------------------------------------
        function out = mixer(obj, drySignal, wetSignal)
            wetSignal = wetSignal * ...
                [0.5 + obj.StereoWidth/2, 0.5 - obj.StereoWidth/2
                0.5 - obj.StereoWidth/2, 0.5 + obj.StereoWidth/2];
            reverb = wetSignal * min(.5, obj.WetDryMix) + drySignal * min(.5,(1-obj.WetDryMix));
            out = [reverb(:,1) * 2*(1-obj.Balance) , reverb(:,2) * 2*obj.Balance];
            out = out * obj.Volume;
        end
    end
end
