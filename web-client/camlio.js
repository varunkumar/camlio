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
  initializeEventListeners();
}

function clientStop() {
  // close peer connection
  setTimeout(function() {
    pc.close();
  }, 500);
}

const configuration = {};

const sendConfiguration = config => {
  fetch('https://localhost:8081/configure', {
    body: JSON.stringify({
      configuration: config
    }),
    headers: {
      'Content-Type': 'application/json'
    },
    method: 'POST'
  });
};

const scenes = [
  'bridge.jpeg',
  'office.jpeg',
  'hussainsagar.jpeg',
  'newyork.jpeg'
];

const overlays = ['arc.png', 'arcesium.png', 'camlio.png'];

const layouts = ['layout-1.svg', 'layout-3.svg'];

const toggleScene = () => {
  const img = document.querySelector('#ctrlScene');
  if (img.parentElement.classList.contains('active')) {
    // Turn off
    $('#controls-extra').html('');
    img.parentElement.classList.remove('active');
    delete configuration.scene;
  } else {
    // Turn on
    configuration.scene = scenes[0];
    $('#controls-extra').html(
      scenes
        .map(scene => {
          return `<img class="scene ${
            configuration.scene === scene ? 'active' : ''
          }" src="./media/scenes/${scene}" data-src="${scene}"></img>`;
        })
        .join('') + '<a href="#" style="display: inline">Browse</a>'
    );
    img.parentElement.classList.add('active');
  }
  sendConfiguration(configuration);
};

const toggleBlur = () => {
  const img = document.querySelector('#ctrlBlur');
  if (img.parentElement.classList.contains('active')) {
    // Turn off
    $('#controls-extra').html('');
    img.parentElement.classList.remove('active');
    delete configuration.blur;
  } else {
    // Turn on
    img.parentElement.classList.add('active');
    configuration.blur = true;
  }
  sendConfiguration(configuration);
};

const toggleOverlay = () => {
  const img = document.querySelector('#ctrlOverlay');
  if (img.parentElement.classList.contains('active')) {
    // Turn off
    $('#controls-extra').html('');
    img.parentElement.classList.remove('active');
    delete configuration.overlay;
  } else {
    // Turn on
    $('#controls-extra').html(
      overlays
        .map(overlay => {
          return `<img class="overlay" src="./media/overlay/${overlay}" data-src="${overlay}"></img>`;
        })
        .join('') + '<a href="#" style="display: inline">Browse</a>'
    );
    img.parentElement.classList.add('active');
    configuration.overlay = [];
  }
  sendConfiguration(configuration);
};

const toggleShare = () => {
  const img = document.querySelector('#ctrlShare');
  if (img.parentElement.classList.contains('active')) {
    // Turn off
    $('#controls-extra').html('');
    img.parentElement.classList.remove('active');
    delete configuration.presentation;
  } else {
    // Turn on
    configuration.presentation = layouts[0];
    $('#controls-extra').html(
      layouts
        .map(layout => {
          return `<img class="layout ${
            configuration.presentation === layout ? 'active' : ''
          }" src="./media/layouts/${layout}" data-src="${layout}"></img>`;
        })
        .join('')
    );
    img.parentElement.classList.add('active');
  }
  sendConfiguration(configuration);
};

const toggleHologram = () => {
  const img = document.querySelector('#ctrlHologram');
  if (img.parentElement.classList.contains('active')) {
    // Turn off
    $('#controls-extra').html('');
    img.parentElement.classList.remove('active');
    delete configuration.hologram;
  } else {
    // Turn on
    img.parentElement.classList.add('active');
    configuration.hologram = true;
  }
  sendConfiguration(configuration);
};

const initializeEventListeners = () => {
  document.querySelector('#ctrlScene').addEventListener('click', toggleScene);
  $('#camliaControls').on('click', '.scene', e => {
    $('.scene').removeClass('active');
    $(e.target).addClass('active');
    configuration.scene = $(e.target).data('src');
    sendConfiguration(configuration);
  });

  $('#camliaControls').on('click', '.layout', e => {
    $('.layout').removeClass('active');
    $(e.target).addClass('active');
    configuration.presentation = $(e.target).data('src');
    sendConfiguration(configuration);
  });
  document.querySelector('#ctrlBlur').addEventListener('click', toggleBlur);
  document
    .querySelector('#ctrlOverlay')
    .addEventListener('click', toggleOverlay);
  document.querySelector('#ctrlShare').addEventListener('click', toggleShare);
  document
    .querySelector('#ctrlHologram')
    .addEventListener('click', toggleHologram);
};
