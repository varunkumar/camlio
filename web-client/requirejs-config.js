requirejs.config({
    baseUrl: '',

    paths: {
       "webrtc-sdk" : "./external/webrtcsdk.min",
       jquery: './external/jquery',
       underscore: './external/lodash'
    }
});

require(["webrtc-sdk"], function () {
    console.log("(require): webrtcsdk.min loaded");
    require(['example'], function() {
        console.log("(require): example webrtc client app loaded");
    });
});
