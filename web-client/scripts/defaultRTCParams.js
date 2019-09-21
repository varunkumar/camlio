
/* Default Parameters hash for WebRTC Meeting */

define(function(require){

    var DefaultRTCParams = {
        peerConfig: {
            receiveMedia: {
                offerToReceiveAudio: true,
                offerToReceiveVideo: true
            },
            peerConnectionConfig: {
                iceServers: [],
                forceTurn: false
            },
            peerConnectionConstraints: {
                optional: [
                    {DtlsSrtpKeyAgreement: true}
                ]
            }
        }
    };

    return DefaultRTCParams;

});
