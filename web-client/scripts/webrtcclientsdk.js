
define(function (require) {
console.log("(webrtcclientsdk.js) client Ref Design loading...");
    var _       			= require('underscore');
    var Q 					= require('q');
    var $					= require('jquery');

    var defaultRTCParams 	= require("scripts/defaultRTCParams");
    var BJN 				= require("scripts/bjn-global");
	var oldVol;
    var timer;
    var config = {
        muteParams: {
            localAudio: false,
            localVideo: false
        }
	};
	
	const sdkVersion = {
		major : 1,
		minor : 3,
		build : 0	
	};

/* Original - Chrome only version
    var mediaConstraints =  {
        audio:{
            optional:[],
            mandatory:[]
        },
        video:{
        }
    };
*/
	
    var mediaConstraints=  {
        audio:{
        },
        video:{
        }
    };

	var localVideoEl = null;
	var remoteVideoEl = null;
	var contentVideoEl = null;
	var MediaStarted = false;  // new for ffox
	
	// client callbacks
	var cbVideoMute = null;
    var cbRemoteConnectionStateChange = null;
    var cbLocalConnectionStateChange = null;
	var cbOnError = null;
	var cbContentShareStateChange = null;
	
	/*
	   options : {
		   localVideoEl  : <dom element for local video>,
		   remoteVideoEl : <dom element for remote video>,
		   contentVideoEl: <dom element for content share video>
		   bandWidth     : <100..4096Kbps netwk b/w>,
		   devices       : { A/V devices },
		   evtVideoUnmute  : callback(),
		   evtRemoteConnectionStateChange : callback(),
		   evtLocalConnectionStateChange : callback(),
		   evtOnError : callback(),
		   evtContentShareStateChange : callback()  // ver 1.1.x
	*/
    var initialize = function(options) {
		console.log("bjnrtcsdk initializing");
        localVideoEl = options.localVideoEl;
        remoteVideoEl = options.remoteVideoEl;
		contentVideoEl = options.contentVideoEl;

		cbVideoMute = options.evtVideoUnmute;
		cbRemoteConnectionStateChange = options.evtRemoteConnectionStateChange;
		cbLocalConnectionStateChange = options.evtLocalConnectionStateChange;
		cbOnError = options.evtOnError;
		
		// ver 1.1.x
		if(options.evtContentShareStateChange){
			cbContentShareStateChange = options.evtContentShareStateChange;
		}

        BJN.RTCManager.setBandwidth(options.bandWidth);
		MediaStarted = false;
		startLocalStream();
		
		// get hooks to RTCManager callbacks
		BJN.RTCManager.localVideoStreamChange		= updateSelfView;
		BJN.RTCManager.localAudioStreamChange		= updateAudioPath;
        BJN.RTCManager.remoteEndPointStateChange    = onRemoteConnectionStateChange;
        BJN.RTCManager.localEndPointStateChange     = onLocalConnectionStateChange;
        BJN.RTCManager.remoteStreamChange           = onRemoteStreamUpdated;
        BJN.RTCManager.error                        = onRTCError;
		BJN.RTCManager.contentStreamChange			= onContentStreamUpdated;
		};

	//Get the local A/V stream, this stream will be used to for the webrtc connection
	// stream is an array of stream
	// stream[0] - local audio stream
	// stream[1] - local video stream
    var startLocalStream = function() {

        var streamType = 'local_stream';
        if(MediaStarted)
        	streamType = 'preview_stream';
		
        BJN.RTCManager.getLocalMedia(mediaConstraints, streamType).then(function(stream) {
/* Original - Chrome only version
        RTCManager.getLocalMedia(mediaConstraints, 'local_stream').then(function(stream) {
            BJN.localAudioStream = stream[0];
            BJN.localVideoStream = stream[1];
*/

//---------- New for Firefox ------------------
			for (var i = 0; i < stream.length; i++) {
				if(stream[i].bjn_label === "local_audio_stream") {
					BJN.localAudioStream = stream[i]
				} else if(stream[i].bjn_label === "local_video_stream") {
					BJN.localVideoStream = stream[i];
				}
			}
			
			updateSelfView(BJN.localVideoStream);
			//Uncomment the below line, if we want to change device in-meeting
            MediaStarted = true;
			
			if(cbVideoMute) 
				cbVideoMute();
        }, function(err){
			console.log("getLocalMedia error:\n" + JSON.stringify(err,null,2));
		});
    };

	//Callback for local video stream change, it can be used to render self view when the stream is available
    var updateSelfView = function (localStream) {
        if(localStream) {
			BJN.RTCManager.renderSelfView({
                 stream: localStream,
                 el: localVideoEl
             });
			if(cbVideoMute) 
				cbVideoMute(false);
        } else
			console.log("updateSelfView no stream!!!");
    };
	
	// Callback when audio stream changes.  update GUI if stream is defined	
	var updateAudioPath = function (localStream) {
		if(localStream) {
			console.log("Audio Path Change");
		}
	};


	var changeAudioInput = function(who) {
		var dev = BJN.localDevices.audioIn[ who ].id;
		console.log("Audio Input is changed: " + dev ); 
/*  Original Chrome
		mediaConstraints.audio.optional.push( { sourceId: dev } );
*/
		mediaConstraints.audio.deviceId = dev;
		BJN.RTCManager.stopLocalStreams();
		startLocalStream();
	};

	var changeVideoInput = function(who) {
		var dev = BJN.localDevices.videoIn[ who ].id;
		console.log("Video Input is changed: " + dev );
/*  Original Chrome
		mediaConstraints.video.optional.push( { sourceId: dev } );
*/
		mediaConstraints.video.deviceId = dev;
		BJN.RTCManager.stopLocalStreams();
		startLocalStream();
	};

	var changeAudioOutput = function(who) {
		var dev = BJN.localDevices.audioOut[ who ].id;
		console.log("Audio Output is changed: " + dev );
/*  Original Chrome
		mediaConstraints.audio.optional.push( { sourceId: dev } );
*/
		// 5/30/2017 - bugfix pass mediaElements value as an array rather than discrete object
		BJN.RTCManager.setSpeaker({ speakerId : dev, mediaElements : [remoteVideoEl] });
	};

	var setVideoBandwidth = function(bw){
		console.log("Video BW is changed: " + bw);
		BJN.RTCManager.setBandwidth(bw);
	};
	

        /* ========================= */
        /*      Mute Controls   	 */
        /* ========================= */

	var toggleAudioMute = function(event) {
		var audioMuted = config.muteParams.localAudio ? true : false;
		config.muteParams.localAudio = !audioMuted;
		BJN.RTCManager.muteStreams(config.muteParams);		
		return !audioMuted;
	};

	var toggleVideoMute = function(event) {
		var videoMuted = config.muteParams.localVideo ? true : false;
		config.muteParams.localVideo = !videoMuted;
		BJN.RTCManager.muteStreams(config.muteParams);
		return !videoMuted;
	};

	var setVolume = function(){
	}
	
	

    var joinMeeting = function(meetingParams) {
		if( (meetingParams.numericMeetingId != "") && (meetingParams.displayName != "")) {
			console.log("*** Joining meeting id: " + meetingParams.numericMeetingId);
			BJN.RTCManager.startMeeting(meetingParams);
		}
    };

    // End the meeting
    var leaveMeeting = function(event) {
        BJN.RTCManager.endMeeting();
		console.log("Leaving meeting");
    };


    var onRemoteConnectionStateChange = function(state) {
        console.log('Remote Connection state :: ' + state);
		if(cbRemoteConnectionStateChange) cbRemoteConnectionStateChange(state);
    };

    var onLocalConnectionStateChange = function(state) {
       console.log('Local Connection state :: ' +  state);
	   if(cbLocalConnectionStateChange) cbLocalConnectionStateChange(state);
    };

    var onRemoteStreamUpdated = function(stream) {
        BJN.remoteStream = stream;
        if (stream) {
			console.log('Remote stream updated');
            BJN.RTCManager.renderStream({
                stream: BJN.remoteStream,
                el: remoteVideoEl
            });
        }
    };
	
	var onContentStreamUpdated = function(stream){
        BJN.contentStream = stream;
		if (stream) {
			console.log('Content stream updated');
			BJN.RTCManager.renderStream({
					stream: stream,
					el: contentVideoEl
			});
		} 
		if(cbContentShareStateChange) 
			cbContentShareStateChange(stream != null); 
	};
	
    //Add code to handle error from BJN SDK
    var onRTCError = function(error) {
        console.log("Error has occured :: " + error);
        leaveMeeting();
		if(cbOnError) cbOnError(error);
		
    };
	
	var reportSdkVersion = function(){
		return sdkVersion;
	};
	
	return {
	initialize : initialize,
	toggleVideoMute : toggleVideoMute,
	toggleAudioMute : toggleAudioMute,
	changeAudioInput: changeAudioInput,
	changeAudioOutput: changeAudioOutput,
	changeVideoInput : changeVideoInput,
	setVideoBandwidth: setVideoBandwidth,
	joinMeeting : joinMeeting,
	leaveMeeting : leaveMeeting,
	version : reportSdkVersion
	};

});


