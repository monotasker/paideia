	//alert("play audio clips is loading or has loaded");
	var paideia_play_audio_clip =  function(given_id,set_media_args,media_supplied,how_many_times){       
		//alert("play audio clip called with " + given_id);
		//if (undefined === $) {alert('jquery does not exist');}
		//else if($)  {alert('jquery does exist');}
		if (how_many_times > 5) return false;
		var target_elt = $(given_id);
		//if (undefined === target_elt) {alert('target elt is undefined');}

		var gotten_id = undefined;
		if (target_elt[0] && target_elt[0].hasAttribute('id')){
			gotten_id = target_elt[0].getAttribute('id');
		}
		if (gotten_id === undefined) {
			 alert('audio not ready, will retry in 2 seconds');
			 return window.setTimeout(paideia_play_audio_clip,2000, given_id,set_media_args,media_supplied, how_many_times + 1);
		}
		//alert('gotten id:' + gotten_id);
		target_elt.jPlayer({
			ready: function () {
				$(this).jPlayer("setMedia", set_media_args).jPlayer('play');
			},
			swfPath: "/paideia/static/js/jquery.jplayer.swf",
			solution: "html, flash",
			supplied: media_supplied,
			wmode: "window",
			useStateClassSkin: true,
			autoBlur: false,
			smoothPlayBar: true,
			keyEnabled: true,
			remainingDuration: true,
			toggleDuration: true,
			preload: "auto"
			//size: {width: '200px', height:'200px', cssClass: 'jp-audio'}
		});
	};

