const pc = new RTCPeerConnection({
  sdpSemantics: 'unified-plan'
});

const gotVideoStream = stream => {
  // BJN.localVideoStream = stream;
  BJN.localVideoStream.removeTrack(BJN.localVideoStream.getVideoTracks()[0]);
  BJN.localVideoStream.addTrack(stream.getVideoTracks()[0]);
};

const gotAudioStream = stream => {
  // BJN.localAudioStream = stream;
  BJN.localAudioStream.removeTrack(BJN.localAudioStream.getAudioTracks()[0]);
  BJN.localAudioStream.addTrack(stream.getAudioTracks()[0]);
};

// connect audio / video
pc.addEventListener('track', function(evt) {
  console.log(evt);
  if (evt.track.kind == 'video') {
    gotVideoStream(evt.streams[0]);
  } else if (evt.track.kind == 'audio') {
    gotAudioStream(evt.streams[0]);
  }
});

function negotiate() {
  pc.addTransceiver('video', { direction: 'recvonly' });
  return pc
    .createOffer()
    .then(function(offer) {
      return pc.setLocalDescription(offer);
    })
    .then(function() {
      // wait for ICE gathering to complete
      return new Promise(function(resolve) {
        if (pc.iceGatheringState === 'complete') {
          resolve();
        } else {
          function checkState() {
            if (pc.iceGatheringState === 'complete') {
              pc.removeEventListener('icegatheringstatechange', checkState);
              resolve();
            }
          }
          pc.addEventListener('icegatheringstatechange', checkState);
        }
      });
    })
    .then(function() {
      const offer = pc.localDescription;
      return fetch('https://localhost:8081/offer', {
        body: JSON.stringify({
          sdp: offer.sdp,
          type: offer.type
        }),
        headers: {
          'Content-Type': 'application/json'
        },
        method: 'POST'
      });
    })
    .then(function(response) {
      return response.json();
    })
    .then(function(answer) {
      return pc.setRemoteDescription(answer);
    })
    .catch(function(e) {
      console.error(e);
    });
}

function clientStart(handler) {
  negotiate();
}

function clientStop() {
  // close peer connection
  setTimeout(function() {
    pc.close();
  }, 500);
}
