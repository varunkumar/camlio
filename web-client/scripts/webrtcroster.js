
define(function (require) {
console.log("(webrtcroster.js) Roster Object...");
    var BJN = require("scripts/bjn-global");
	var esc = null;

    var initialize = function() {
		esc  = require("clientSDK/src/clients/EventServiceClient");
	};

    var getParticipant = function(n) {
		var r = null;
		if( (n>=0) && (n<esc.roster.collection.length) ){
			r = esc.roster.collection.at(n);
		}
		return r;
    };

	var getPartyCount = function() {
		return esc.roster.collection.length;
	};

	var isMe = function(x) {
		var m = false;
		if(x && x.id)
			m = (x.id == esc.roster.selfParticipant.id);
		return m;
	};
	var onChange  = function(isOn,attr,cb) {
		if(isOn)
			 esc.roster.collection.bind("change:"+attr,cb);
		else esc.roster.collection.unbind("change:"+attr);
	};
	
	var onJoin = function(isOn,cb) {
		if(isOn)
			 esc.roster.collection.bind("add",cb);
		else esc.roster.collection.unbind("add");
	};

	var onLeave= function(isOn,cb) {
		if(isOn)
			 esc.roster.collection.bind("remove",cb);
		else esc.roster.collection.unbind("remove");
	};

	
	var close = function(){
		esc.roster.collection.unbind("");
	};
	
	
	return {
		initialize     : initialize,
		getParticipant : getParticipant,
		getPartyCount  : getPartyCount,
		isMe           : isMe,
		onChange	   : onChange,
		onJoin		   : onJoin,
		onLeave		   : onLeave,
		close 		   : close
	};
});
